#!/usr/bin/env bash
# Autopilot — walks phases 1-8 with no human gates. For demos and quick iteration.
# Risky: pays for clips before catching character drift. Default mode is phased
# (with human review at each gate); only run auto when explicitly requested.
#
# This is a *scaffold*. The intake step (Phase 1 — drafting the brief from a
# free-form prompt) requires an LLM. In autopilot we read a pre-written
# brief.md instead of doing that interactively.
#
# Usage:
#   bash scripts/auto.sh ./my-ad/
#
# Prerequisites in ./my-ad/:
#   brief.md            ← character roster + per-scene script
#   inputs/product.jpg  ← real product photo
#
# This script does NOT generate brief.md. To generate one from a free-form
# prompt, drive the skill via an agent (Claude Code / Cursor / Goose) and
# let it walk through Phase 1 interactively, then call auto.sh for the rest.

set -euo pipefail

PROJECT="${1:?usage: auto.sh <project-dir>}"
PROJECT="$(cd "$PROJECT" && pwd)"
SKILL="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS="$SKILL/scripts"

BRIEF="$PROJECT/brief.md"
[ -f "$BRIEF" ] || { echo "ERROR: $BRIEF not found. Run Phase 1 (intake) via an agent first."; exit 1; }

cat <<EOF
========================================
animated-explainer-ad — autopilot
========================================
Project: $PROJECT
Brief:   $BRIEF
SKILL:   $SKILL

This will run phases 2-8 with no human gates.
Estimated cost: ~\$15-25 in API spend.
Estimated wall time: ~30-60 min.

Press Enter to proceed, Ctrl-C to abort.
EOF
read -r _

# The brief.md format is markdown with YAML frontmatter listing characters,
# voice, scenes, etc. Parse it with python.
PARSE="
import re, json, sys, pathlib
text = pathlib.Path('$BRIEF').read_text()
m = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
if not m:
    sys.exit('brief.md missing YAML frontmatter')
import yaml  # only used here; pip install pyyaml if needed
data = yaml.safe_load(m.group(1))
json.dump(data, sys.stdout)
"
META=$(python3 -c "$PARSE" 2>/dev/null || {
  echo "ERROR: failed to parse brief.md frontmatter. Install pyyaml: pip install pyyaml" >&2
  exit 1
})

echo "[autopilot] phase 2: character anchors"
python3 -c "
import json, subprocess
m = json.loads('''$META''')
for name, c in m.get('characters', {}).items():
    subprocess.check_call(['python3', '$SCRIPTS/render_anchor.py',
        '--project', '$PROJECT',
        '--name', name,
        '--descriptor', c['descriptor'],
        '--negative', c.get('negative', '')])
"

echo "[autopilot] phase 3: VO"
python3 -c "
import json, subprocess
m = json.loads('''$META''')
voice = m['voice']
for s in m['scenes']:
    sid = str(s['scene']).zfill(2)
    slug = s.get('slug', '')
    out = f\"$PROJECT/audio/vo/vo-{sid}{('-' + slug) if slug else ''}.mp3\"
    subprocess.check_call(['python3', '$SCRIPTS/render_vo.py',
        '--voice-id', voice['id'],
        '--text', s['vo'],
        '--out', out,
        '--speed', str(voice.get('speed', 1.12))])
"
python3 "$SCRIPTS/measure_vo.py" --project "$PROJECT"

echo "[autopilot] phase 4: keyframes"
python3 -c "
import json, subprocess
m = json.loads('''$META''')
for s in m['scenes']:
    sid = str(s['scene']).zfill(2)
    refs = ['$PROJECT/anchors/' + c + '.png' for c in s.get('characters', [])]
    subprocess.check_call(['python3', '$SCRIPTS/render_keyframe.py',
        '--project', '$PROJECT',
        '--scene', sid,
        '--visual', s['visual'],
        '--refs', *refs])
"

echo "[autopilot] phase 5: scene clips"
python3 -c "
import json, subprocess
m = json.loads('''$META''')
for s in m['scenes']:
    sid = str(s['scene']).zfill(2)
    subprocess.check_call(['python3', '$SCRIPTS/render_clip.py',
        '--project', '$PROJECT',
        '--scene', sid,
        '--keyframe', f'$PROJECT/keyframes/scene-{sid}.png',
        '--motion', s.get('motion', s['visual']),
        '--duration', str(int(s.get('clip_duration_sec', 4)))])
"

echo "[autopilot] phase 6: end card"
python3 -c "
import json, subprocess
m = json.loads('''$META''')
ec = m['end_card']
last = max(int(s['scene']) for s in m['scenes'])
endcard_id = str(last + 1).zfill(2)
args = ['python3', '$SCRIPTS/build_endcard.py',
        '--project', '$PROJECT',
        '--product', ec['product_image'],
        '--wordmark', ec['wordmark'],
        '--subline', ec['subline'],
        '--cta', ec['cta'],
        '--primary', ec.get('primary', '#2E6F5E'),
        '--cta-color', ec.get('cta_color', '#E8674C'),
        '--scene', endcard_id]
for cl in ec.get('claims', []):
    args.extend(['--claim', cl])
subprocess.check_call(args)
"

echo "[autopilot] phase 7: music"
python3 -c "
import json, subprocess
m = json.loads('''$META''')
mus = m.get('music', {})
subprocess.check_call(['python3', '$SCRIPTS/render_music.py',
    '--out', '$PROJECT/audio/music.mp3',
    '--duration', str(mus.get('duration_sec', 48)),
    '--prompt', mus.get('prompt', 'whimsical Pixar/Disney instrumental, NOT cinematic, NOT moody.')])
"

echo "[autopilot] phase 8: captions + compose"
python3 -c "
import json, pathlib
m = json.loads('''$META''')
caps = '\n'.join(s.get('caption', '') for s in m['scenes'])
pathlib.Path('$PROJECT/captions.txt').write_text(caps)
"
python3 "$SCRIPTS/make_captions.py" --project "$PROJECT" --captions-file "$PROJECT/captions.txt"
bash "$SCRIPTS/compose.sh" "$PROJECT"

echo
echo "========================================"
echo "AUTOPILOT COMPLETE"
echo "Master: $PROJECT/finals/master.mp4"
echo "========================================"
