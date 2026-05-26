---
name: animated-explainer-ad
description: Make a 9:16 ~30–45s animated explainer ad in bright Pixar/Disney 3D where a personified villain (the problem — eczema, stress, dullness, fees) narrates the spot in a single character voice, including their own defeat by the product. Use when the user wants a paid-social ad that teaches a mechanism through cartoon personification, has one ownable claim to anchor on, and has a real product photo for the end card. This skill walks the user through an 8-phase pipeline (intake → character anchors → VO casting → keyframes → scene clips → end card → music → compose), uses FAL (nano-banana for stills, Seedance Pro for i2v) and ElevenLabs (eleven_v3 TTS + music API), and produces a captioned, mixed master mp4. Validated on two real client runs — costs ~$15–25 in API spend per cut, ~2 hours wall time including human review gates.
---

# animated-explainer-ad

A guided workflow for producing animated explainer ads in the "villain-narrates-own-defeat" format. The skill is conversation-driven: the user gives a free-form prompt ("make an ad for Soteri Skin where Eczema is the villain"), and you walk them through gathering inputs, generating assets phase-by-phase, and composing the master. Each phase has a human review gate so the user catches drift before paying for downstream gen.

## When to use this skill

Use when the user asks for any of:

- "Make an animated explainer ad" / "Pixar-style ad" / "cartoon ad" / "villain ad" / "absurdist explainer."
- "Like the Big Chill ad" / "like the Eczema ad" / "in that personified-problem style."
- A paid-social spot where the *mechanism* (pH/LOCK, adaptogen calming cortisol, dual-action cleanser) is the story.
- A 9:16 sound-off-safe ad with no on-camera talent.

Do NOT use when the user wants: photoreal product video, creator/UGC selfie cam, pure typography/data-viz motion graphics, before-after demos, or live-action footage. Reach for a different skill.

## The format

The validated form, derived from two production runs (see `references/case-studies.md`):

- **9:16, 30–45 seconds, 10–13 scenes.** Meta / TikTok / Reels feed-native.
- **Bright Pixar/Disney 3D throughout** — glossy, rounded, toy-like. Never photoreal.
- **Single narrator voice** — the personified villain. Same voice for the whole spot including the defeat. ElevenLabs `eleven_v3`, ≤4 audio tags.
- **Roster ≤4 characters** — villain + hero + 1 human victim + 1 set piece. More than 4 muddies the cause/effect chain.
- **Recurring number/word motif** appearing ≥3 times (teach beat, damage beat, payoff). "pH 4.9", "cortisol hormones."
- **Climax beat is the product's "fix" moment**, not the product appearance. Music resolves on the climax.
- **Real product on the end card.** PIL-composited from a real photo. Never an AI-rendered cartoon bottle.
- **Brand text is never AI-rendered.** Wordmark, claims, end-card copy, diegetic labels (`pH 4.9`, `MOISTURE BARRIER`) are PIL or ffmpeg `drawtext` overlays.
- **Burned word-by-word captions** via libass.
- **Whimsical Pixar/Disney instrumental score** — sneaky → tense → uplift @ hero → resolved tail.

## Pipeline overview

| Phase | What | Output | Approx cost | Gate? |
|---|---|---|---|---|
| 1 | Intake: gather brand + concept + script | `project/brief.md` + `project/storyboard.html` | $0 | ✅ user approves |
| 2 | Character anchors via nano-banana | `project/anchors/<name>.png` (×4) | ~$0.32 | ✅ user approves grid |
| 3 | Voice casting + VO render | `project/audio/vo/vo-<NN>.mp3` (×N) | ~$0.50 | ✅ user picks voice |
| 4 | Scene keyframes via nano-banana with chained anchor refs | `project/keyframes/scene-<NN>.png` | ~$0.66 | ✅ user approves contact sheet |
| 5 | i2v scene clips via Seedance Pro | `project/clips/scene-<NN>.mp4` | ~$15.00 | ✅ user approves preview, then remaining |
| 6 | End card: PIL composite real product + typeset brand | `project/clips/scene-<N+1>.mp4` | $0 | — |
| 7 | Music bed via ElevenLabs music API | `project/audio/music.mp3` | ~$0.20 | — |
| 8 | Compose: retime, concat, mix, burn captions | `project/finals/master.mp4` | $0 | ✅ user ships it |

**Total:** ~$15–25 per cut. Wall time ~2 hours including reviews.

## Setup (run once per machine)

Before phase 1, confirm the user has:

```bash
# 1. Python deps
pip install -r requirements.txt

# 2. API keys in .env (copy from .env.example)
cp .env.example .env
# Edit .env to set FAL_KEY and ELEVENLABS_API_KEY

# 3. ffmpeg installed
ffmpeg -version
```

If anything's missing, surface it before starting phase 1 — don't proceed with broken tooling.

---

## Phase 1 — Intake (gather brand + concept + script)

**Goal:** turn a free-form user prompt into a locked brief + storyboard, with a 10–13 scene VO script the user has approved.

### Step 1: extract from the user's opening prompt

Parse what they've given you. Typical prompt: *"Make an animated explainer ad for [brand] where the villain is [problem] and the hero is [product]. The mechanism is [X]."*

Extract whatever's there:

- **brand** — name (e.g. "Soteri Skin")
- **product** — exact product + variant (e.g. "Baby Eczema Relief Cream")
- **problem** — one word ideally (e.g. "Eczema", "Stress", "Dullness")
- **mechanism** — the ownable claim (e.g. "pH/LOCK at 4.9", "Rhodiola Rosea calms cortisol")
- **audience** — who's watching (e.g. "parents of babies with eczema")

### Step 2: ask for what's missing (one batch of questions)

Use a single batched question to fill gaps. Do **not** drag the user through a 10-question interview. The minimum you need before drafting the script:

- brand, product, problem, mechanism, audience (above)
- **product hero image path** — absolute path to a real product photo (≥1000×1000, clean background). Non-negotiable: see Decision Rule "real product on end card."
- **brand palette** — 2–4 hex colours (primary + accent + CTA). Ask if the user has brand guidelines; otherwise infer reasonable defaults from the product photo and confirm.
- **recurring motif** — the number or word the script will anchor on (must appear ≥3 times). Often equals the mechanism's key value ("pH 4.9", "30-day reset").
- **target duration** — default 38s. Range 30–45.

### Step 3: propose the character roster

Based on the brand + problem + mechanism, propose 3–4 characters and confirm with the user. **Strict cap: ≤4.** A graphic prop (a pH meter, a clock face) is NOT a character — don't count it.

The 4-role template:

1. **Villain** = the personified problem. Single narrator. Visual descriptor: ~2 lines (silhouette + skin + face + vibe).
2. **Hero** = the personified product, visually *opposite* the villain. (Eczema is spiky-red; Soteri is smooth-cream-green.)
3. **Human victim** = the person the user watching identifies with. The baby, the frazzled woman, the stressed founder.
4. **Set piece** = what the villain attacks. The moisture barrier brick wall, the adrenal beans, the collagen scaffold.

If the brand has minions (subordinate creatures spawned by the villain), make them visually *smaller copies of the villain* — same army, same palette. Big Chill v3/v4 made them visually distinct and the cause/effect chain muddied; v5 collapsed them and it snapped into focus.

### Step 4: draft the 12-scene spine

Use this canonical structure (adapt scene counts if the user asks for a shorter cut):

| # | Beat | VO contains | Caption | Diegetic label |
|---|---|---|---|---|
| 01 | Villain intro | "I'm [villain]. I live [where]." | "I'm [villain]." | — |
| 02 | Teach the set piece | Names the mechanism's home (the barrier, the scaffold, the glands) | "Meet the [set piece]." | [SET PIECE NAME] |
| 03 | Damage primer | "So I break it" / "I make it work overtime" | "So I break it." | — |
| 04 | Reveal the secret | "Here's my little secret — it's really a [mechanism] problem" (optional — skip if mechanism is obvious from teach) | "It's really a [X] problem." | — |
| 05 | Teach the number motif | "Healthy [X] sits at [MOTIF]" | "Healthy = [MOTIF]" | [MOTIF] |
| 06 | Damage: mechanism breaks | "I push [X] higher and the wall cracks" | "[X] goes wrong → bad thing." | — |
| 07 | Damage list item | "And then [bad thing 1]" | "[bad thing 1]." | — |
| 08 | Damage peak | "And nobody [sleeps / can focus / feels good] anymore" | "[peak damage]." | — |
| 09 | Hero arrives | "[nervous] Until [PRODUCT] shows up" | "Until [PRODUCT] shows up." | — |
| 10 | **CLIMAX: the fix** | "Its [mechanism] snaps it right back to [MOTIF]" | "[MECHANISM] → [MOTIF]" | [MECHANISM] · [MOTIF] |
| 11 | Defeat + payoff | "[Calm victim]. And me? Nowhere left to live." | "[Calm state]." | — |
| 12 | End card | "That's [PRODUCT]. [Claim 1]. [Claim 2]." | end card type | end card |

The damage list (scenes 6–8) scales 1–4 items based on how many things the villain does. Most brands have 1–3; a 4-item damage list is rare.

### Step 5: write the per-scene script

For each scene write:

- `vo` — the spoken line (≤15 words usually; villain delivery is slow). Audio tags `[whispers] [menacing] [nervous] [sighs]` — **≤4 across the whole script.** eleven_v3 inflates pauses around tags by ~400ms each.
- `caption` — the burned caption (shorter than the VO; e.g. VO "Healthy baby skin sits slightly acidic — right around 4.9." → caption "Healthy skin = pH 4.9").
- `visual` — one sentence describing what's on screen, in present tense, focused on the *action*, not the static composition.
- `characters` — which roster members appear (used to thread the right anchor refs in phase 4).
- `diegetic_label` (optional) — composited type that names the mechanism. Brand text NEVER AI-rendered (Decision Rule 7).
- `duration_target_sec` — your estimate of how long the scene needs. Refined in phase 3 once VO is rendered.

### Step 6: lock the brief

Write everything to `project/brief.md` — frontmatter + character descriptors + scene table. Generate `project/storyboard.html` — a single HTML page that renders the scene table with placeholders where keyframes/clips will land. Use the minimal storyboard template provided below (or load the user's `references/case-studies.md` examples).

**Hand the storyboard to the user. Wait for explicit approval** of the script + scene table + character descriptors. This is the cheapest gate — script changes here are free; after phase 4 they cost re-rolled keyframes; after phase 5 they cost re-rolled clips.

Once approved, commit `project/brief.md` and move to phase 2.

---

## Phase 2 — Character anchors

**Goal:** lock the visual identity of each character before any scene generation. Catches drift early.

For each character in the brief, call:

```bash
python scripts/render_anchor.py \
  --project project/ \
  --name <character-name> \
  --descriptor "<descriptor from brief>" \
  --negative "<negative constraints — 'no wings, no horns, no tail'>" \
  --out project/anchors/<name>.png
```

The script:
- Wraps the descriptor in the validated Pixar-3D prompt prefix: `"character portrait, neutral background, full body, glossy Pixar/Disney 3D, soft global illumination, shallow depth of field, toy-like, rounded forms"`.
- Hits FAL nano-banana at 1024×1024 portrait.
- Normalises to 1080×1920 with padding.
- Writes a `.meta.json` next to the PNG with the exact prompt used.

After all anchors render, assemble a contact sheet (script auto-emits `project/anchors/_grid.png`) and hand to the user.

**Wait for explicit approval.** Catch drift here. Common issues:
- Villain reads as creepy/uncanny instead of comedic. Fix: re-render with "comedic, smug, pesky, never scary" in the descriptor.
- Hero looks generic. Fix: add the emblem/cape/distinguishing accent.
- Character has an unintended feature (Soteri's Eczema initially grew bat-wings — a "gremlin" interpretation drift). Fix: add to `--negative`.

Re-rolls of a single anchor cost ~$0.08. Don't be precious about re-rendering until the user is happy.

Write `project/anchors/LOCKED.json` once approved:

```json
{
  "characters": {
    "eczema": {
      "role": "villain",
      "anchor": "eczema.png",
      "descriptor": "..."
    }
  },
  "scene_threads": {
    "scene-01": ["eczema"],
    "scene-02": ["eczema", "moisture_barrier"]
  }
}
```

`scene_threads` is derived from the brief's per-scene `characters` field. Phase 4 reads this to know which anchor PNGs to pass as chained refs for each scene.

---

## Phase 3 — Voice casting + VO render

**Goal:** pick a single villain narrator voice the user is happy with, then render all VO lines.

### Step 1: voice casting A/B

Shortlist 3–6 candidate ElevenLabs voices. Default shortlist for cartoon-villain:

| Voice | ID | Vibe |
|---|---|---|
| Austin | `Bj9UqZbhQsanLzgalpEG` | Texan, raspy, authentic — validated on Soteri |
| Dylo | `JjsQrIrIBD6TZ656NQfi` | Young, fierce — validated on Big Chill |
| Tom | `mdzEgLpu0FjTwYs5oot0` | Cartoon-villain character voice (rejected on Soteri) |
| Adam | `pNInz6obpgDQGcFmaJgB` | Deep narrative — for slower, more deliberate villains |
| Bella | `EXAVITQu4vr4xnSDxMaL` | Female villain option |

For each candidate, render scene 01:

```bash
python scripts/render_vo.py \
  --voice-id <id> \
  --text "<scene-01 VO from brief>" \
  --out project/audio/casting/<voice-name>-scene-01.mp3 \
  --speed 1.12
```

Play all candidates back to the user (just list the file paths — user opens in QuickTime). **Wait for them to pick one.**

Both reference runs rejected their first voice pick. Don't skip this step.

### Step 2: render all VO lines

In the chosen voice, render every scene's VO line:

```bash
for scene in <scenes from brief>:
  python scripts/render_vo.py \
    --voice-id <chosen> \
    --text "<scene.vo>" \
    --out project/audio/vo/vo-<NN>-<slug>.mp3 \
    --speed 1.12
```

The script applies silence-trim (`silenceremove start=0.05s end=0.12s`) per line so they cut cleanly in the compose phase.

### Step 3: measure VO durations + update scene timing

After all VO renders:

```bash
python scripts/measure_vo.py --project project/
```

This writes `project/scene_timing.json` with the actual VO duration per scene. The compose script reads this. If total VO duration > `target_duration_sec × 1.15`, warn the user and offer two fixes:

1. **Re-render at speed 1.18–1.20** (fast — single re-render).
2. **Trim the script** (better — chronic speed-up reads as rushed).

The compose-stage `atempo=1.3` is available as a last resort but flag it loudly; it's a smell.

---

## Phase 4 — Scene keyframes

**Goal:** generate one keyframe PNG per scene (excluding the end card) using nano-banana with the locked character anchors as chained refs. This is what catches character drift before you spend on Seedance clip gen.

For each scene 01..N-1:

```bash
python scripts/render_keyframe.py \
  --project project/ \
  --scene <NN> \
  --visual "<scene.visual from brief>" \
  --negative "no text, no signage, no labels, no brand names" \
  --refs project/anchors/<char1>.png project/anchors/<char2>.png \
  --out project/keyframes/scene-<NN>.png
```

The script:
- Builds a nano-banana prompt: `"<visual>. Pixar 3D, glossy, rounded, soft global illumination, shallow DOF, toy-like."` + the negative constraints.
- Passes the character anchor PNGs as nano-banana `medias` refs (chained-ref strategy).
- Generates at the highest supported portrait resolution.
- Normalises raw output to 1080×1920 (nano sometimes returns 768×1344; the script auto-crops + scales).
- Saves raw to `project/keyframes/_raw/scene-<NN>.png`, normalised to the main path, meta to `<NN>.meta.json`.

Once all keyframes render, the script emits `project/keyframes/_grid.png` — a contact sheet of all keyframes at thumbnail size. Hand to user.

**Wait for explicit approval** of the contact sheet. Common issues:
- Character drift (villain morphs across scenes). Fix: re-roll with a tighter negative constraint.
- Wrong scale (character too small / too large in frame). Fix: add "low-angle shot of <character>" or "wide framing showing <character> small" to the visual.
- Anachronistic background (modern device when the world is cartoon). Fix: add to negative constraints.

Re-rolls cost ~$0.08 per keyframe. Budget 2–4 re-rolls in a 12-scene cut.

**Brand text contamination guard:** never include the brand name in any keyframe prompt. Nano-banana will hallucinate "SOTERY SKINS" signage in backgrounds. Brand text lives only on the PIL-composited end card (phase 6) and the burned captions (phase 8).

---

## Phase 5 — Scene clips (i2v with preview gate)

**Goal:** animate each keyframe into a 3–7s scene clip via Seedance Pro i2v. Use a preview gate to catch motion issues before committing the remaining budget.

### Step 1: preview gate

Pick 3–4 scenes that cover all characters + the climax (e.g. for a 12-scene cut: scenes 01, 06, 10, 11 — covers all 4 characters and the climax). Generate:

```bash
python scripts/render_clip.py \
  --project project/ \
  --scene <NN> \
  --keyframe project/keyframes/scene-<NN>.png \
  --motion-prompt "<scene.visual + action verbs from brief>" \
  --duration <scene.duration_target_sec> \
  --out project/clips/scene-<NN>.mp4
```

The script:
- Wraps the motion prompt in the validated anti-shake suffix: `"Pixar 3D animation style preserved. NO shake, NO wobble, NO earthquake. Smooth steady camera. Full-frame vertical 9:16, NO letterbox, NO black bars."`
- Submits to FAL `fal-ai/bytedance/seedance/v1/pro/image-to-video` at 1080p, 9:16, duration 3–7s.
- Downloads the result.
- Runs the de-letterbox check (samples a mid-clip frame; if top/bottom 5% rows are solid black, re-encodes `scale=1088:1920,crop=1080:1920` and archives the original under `_letterboxed/`).

Hand preview clip paths to user. **Wait for approval** of motion + character consistency before committing remaining budget.

Common issues:
- Earthquake camera. Fix: anti-shake suffix didn't take — try adding "static camera, no movement" to the motion prompt.
- Character doesn't move (frozen still). Fix: add explicit action verbs ("turns head," "raises arm," "leans toward camera").
- Character morphs mid-clip. Fix: shorten duration (3s instead of 5s) and re-render.
- Letterbox bars. Fix: the de-letterbox script handles this automatically; if it's still happening, the auto-detect threshold needs tuning.

### Step 2: remaining clips

Generate the rest in parallel batches of 4 (FAL queue ceiling):

```bash
python scripts/render_clip.py --project project/ --scene 02 --keyframe ... &
python scripts/render_clip.py --project project/ --scene 03 --keyframe ... &
python scripts/render_clip.py --project project/ --scene 04 --keyframe ... &
python scripts/render_clip.py --project project/ --scene 05 --keyframe ... &
wait
```

Each clip costs ~$1.30 at 1080p Seedance Pro. Budget ~$15 for a 12-scene cut, +$3 buffer for re-rolls.

---

## Phase 6 — End card

**Goal:** PIL composite of the real product photo over the brand background with typeset wordmark + claims + CTA pill. NEVER an AI-rendered cartoon bottle.

```bash
python scripts/build_endcard.py \
  --project project/ \
  --product <absolute path to real product photo> \
  --wordmark "<brand>" \
  --subline "<product>" \
  --claims "<claim 1>" "<claim 2>" \
  --cta "<url>" \
  --primary "#2E6F5E" \
  --accent "#E8674C" \
  --out project/clips/scene-<N+1>.mp4 \
  --duration 4.0
```

The script:
- Loads the product photo.
- Samples its edge background colour (or uses the brand `primary` if `--seamless` is off).
- Builds a 1080×1920 canvas, centres the product at ~1015px tall.
- Types brand wordmark (bold, large), product subline, claim rows, CTA pill — all via PIL `ImageDraw.text`.
- Saves `project/endcard/endcard.png`.
- Encodes a 4s Ken Burns clip (1.00 → 1.04 zoom) to `project/clips/scene-<N+1>.mp4`.

No human gate here — the script's output is deterministic from inputs.

---

## Phase 7 — Music (parallel with phase 6)

**Goal:** generate the whimsical Pixar/Disney instrumental bed via ElevenLabs music API.

```bash
python scripts/render_music.py \
  --prompt "whimsical Pixar/Disney instrumental — pizzicato strings, light woodwinds, xylophone. Sneaky for villain intro → light tension through damage → warm uplift at hero arrival → soft resolved tail. NOT cinematic, NOT moody." \
  --duration <target_duration_sec + 5> \
  --out project/audio/music.mp3
```

If the bed returns moody/cinematic instead of whimsical, re-roll with sharper negatives: `"NOT cinematic, NOT moody, NOT dark, NOT orchestral, NOT trailer-style. Pixar/Disney comedy score, light, playful."` Cost per re-roll: ~$0.20.

---

## Phase 8 — Compose (final master)

**Goal:** retime each scene clip to its VO line duration, concat, mix VO + music with ducking, burn captions, mux to `project/finals/master.mp4`.

```bash
bash scripts/compose.sh project/
```

The script reads `project/scene_timing.json` + `project/brief.md` and:

1. **Per-scene video segments.** For each scene clip: `scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1`, then `tpad=stop_mode=clone:stop_duration=<pad>` if VO is longer than the clip, then `trim=duration=<target>`. Re-encode `libx264 -preset medium -crf 18 -pix_fmt yuv420p -r 30 -an`. (All segments MUST be 30fps or concat demuxer silently drops frames.)
2. **Concat video.** `ffmpeg -f concat -safe 0 -i concat.txt -c copy video.mp4`.
3. **VO track.** For each line: `atempo=<compensation>,apad -t <target> -ar 44100 -ac 2`. Concat to `vo-track.wav`.
4. **Music bed.** `afade=t=in:st=0:d=0.6,afade=t=out:st=<TOTAL-1.4>:d=1.4 -t <TOTAL>`.
5. **Mix.** `[0:a]loudnorm=I=-14:TP=-1.5:LRA=11[vo]; [1:a]loudnorm=I=-26:TP=-3:LRA=11,volume=0.62[mus]; [vo][mus]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[a]`.
6. **Captions.** Generate `audio/captions.ass` via `scripts/make_captions.py` (libass; Arial 64, white, 6px outline, bottom-third MarginV=330). Scene-by-scene cues, end-card scene has no caption (its own typeset copy carries it).
7. **Burn + mux.** `ffmpeg -i video.mp4 -i mix.wav -vf "ass=audio/captions.ass" -map 0:v -map 1:a -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -shortest finals/master.mp4`.

After compose, run the self-QC:

```bash
ffprobe -v error -show_entries format=duration -of csv=p=0 project/finals/master.mp4
ffmpeg -i project/finals/master.mp4 -af "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json" -f null - 2>&1 | tail -20
```

Expected: integrated loudness in [-14.5, -13.5] LUFS, true peak ≤ -1.5 dBFS.

Hand `project/finals/master.mp4` to user. **Wait for ship-it.**

---

## Auto mode

For demos / quick iteration where the user wants to skip the human gates:

```bash
bash scripts/auto.sh "<free-form prompt>" project/
```

This walks phases 1–8 with no human gates. Auto-picks defaults for everything. Risky — you can pay for clips before catching character drift. Only use when the user explicitly says "just run it."

---

## Decision rules (apply before generating, not after)

These are encoded from two production runs. Skip them at your peril.

1. **Roster ≤4 characters.** Villain + hero + 1 victim + 1 set piece. A graphic prop is NOT a character.
2. **The villain narrates their own defeat.** Single voice for the entire spot. Do NOT add a hero-side narrator at the climax.
3. **Motif appears ≥3 times.** Teach + damage + payoff.
4. **Bright Pixar 3D, glossy and toy-like, never photoreal.** Every keyframe prompt prefixed with the Pixar-3D style block.
5. **Voice casting is two-step: shortlist → A/B render scene 01 → operator pick.** Both reference runs rejected their first voice pick.
6. **TTS speed ≥1.12, eleven_v3, ≤4 audio tags.** Each `[tag]` adds ~400ms pause.
7. **Brand text is NEVER AI-rendered.** Wordmark, claims, end-card copy, diegetic labels — PIL/drawtext only.
8. **End card uses the REAL product image, composited.** Never an AI dummy bottle.
9. **Anti-shake suffix on every i2v prompt.** Seedance defaults to gratuitous shake.
10. **De-letterbox guard on every clip.** Seedance letterboxes ~25% of 9:16 outputs.
11. **Whimsical Pixar/Disney score, NOT cinematic, NOT moody.** ElevenLabs music sometimes drifts dark.
12. **Climax beat is the "fix" moment, not the hero entrance.** Music resolves on the climax.
13. **No cure claims.** Villain-as-character can leave ("nowhere left to live"); product copy stays softened ("helps correct and lock").
14. **5 human gates** — brief, anchors, keyframes, preview clips, final master. Do not skip in non-auto mode.
15. **Run order: VO first, then keyframes, then clips.** VO duration drives per-scene timing.
16. **Storyboard is the single review surface.** Every artifact lands on `project/storyboard.html`.

## Failure modes

- **Roster bloat (>4 characters)** muddies the cause/effect chain. Fix: collapse subordinate characters into the villain (minions = smaller copies of the villain, same army).
- **Photoreal characters in a cartoon spot** read as uncanny-valley horror. Fix: explicit Pixar-3D style prefix on every prompt.
- **Character drift across scenes** (bat-wings appear in scene 3, skin tone shifts). Fix: re-roll affected keyframes with explicit negative constraints; verify anchors are passed as `medias` refs.
- **Seedance letterboxes 9:16 output** with cinematic bars. Hits ~25% of clips. Fix: anti-shake suffix + auto de-letterbox (the `render_clip.py` script handles this).
- **Earthquake camera in i2v output.** Fix: anti-shake suffix on every prompt.
- **VO read comes back 40% longer than design target.** Fix in order: push speed to 1.18–1.20 → drop audio tags → re-cast → compose-stage atempo 1.3 (last resort).
- **AI-rendered brand text in backgrounds.** Fix: never mention the brand name in any keyframe prompt; negative-constrain "no text, no signage, no labels."
- **Cartoon dummy bottle on the end card.** Both reference runs hit this. Fix: real product photo is a required input; reject end card without it.
- **Cure claims slip into VO.** Fix: keep villain-as-character story device separate from product copy; route any claim through legal if regulated.
- **Music returns moody/cinematic.** Fix: re-roll with "NOT cinematic, NOT moody, NOT dark" in the prompt.
- **Concat demuxer silently drops frames** on framerate mismatch. Fix: re-encode every segment to libx264/crf 18/yuv420p/30fps before concat.
- **Loudness peaks clip > 0 dBFS** when VO + music + SFX stack. Fix: lower music gain to 0.55 when scenes get dense.

## Validated case studies

See `references/case-studies.md` for the two production runs that validated this format:

1. **HUM Nutrition — "Big Chill" cortisol absurdism** (the reference): Stress-as-villain, cortisol minions, Dylo voice, ~34.6s shipped.
2. **Soteri Skin — "Eczema, the pH villain"**: Eczema-as-villain, pH/LOCK mechanism, Austin voice, ~45.1s shipped, ~$17.60 total cost.

Both files include the full brief, scene table, voice settings, and cost breakdown. Use either as a worked example when briefing a new project.

## Examples

See `examples/` for ready-to-paste prompts that kick off a new run:

- `examples/soteri-eczema.md` — the Soteri brief as a conversational kickoff.
- `examples/hum-big-chill.md` — the Big Chill brief as a conversational kickoff.
- `examples/lumeo-dullness.md` — a synthesised "skincare for dullness" brief showing the minimum-information kickoff.

Each is a single user prompt you'd paste to start phase 1. The skill walks the rest.
