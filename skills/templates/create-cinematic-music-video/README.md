# create-cinematic-music-video

> A portable agent skill that turns a one-line brief into a polished 9:16
> cinematic music-video ad: an original anthem with real sung vocals, 14
> beat-locked tableaux, and burned word-synced captions. ~$15–25 per cut.

## What it makes

A 20–30 second 9:16 paid-social spot built around an **original song** (not a
montage over stock music). The lyrics are sung with word-level timestamps, so
every visual cut lands on a vocal beat. Fourteen tableaux carry a 3-act arc —
anticipation → energy → reflection — and the whole aesthetic swaps by changing
one field (the "look pack"). Captioned, mixed to -14 LUFS, ready to upload to
TikTok / Reels / Shorts / Pinterest.

The same pipeline, four built-in looks:

| Look pack | Vibe |
|---|---|
| `KODAK_PORTRA_DAY` | Warm 35mm golden-hour film — lifestyle, college, summer |
| `CINESTILL_800T_NIGHT` | Neon-noir tungsten night — urban, winter, nightlife |
| `PAPER_CUT_CRAFT` | Saturated paper-cut collage — Y2K, candy CPG, wellness |
| `CINEMATIC_GOTHIC_DUSK` | Candlelit twilight gravity — period-drama, gothic |

See [`references/case-studies.md`](./references/case-studies.md) for the runs the
format is validated on.

## How it works

You give Claude (or any agent that reads `SKILL.md`) a free-form brief:

> "Make a cinematic music-video ad for Aurelia, a running brand. Warm 35mm
> golden-hour film. The campaign is 'every morning is a comeback' — a morning
> run as a small act of self-renewal. Original anthem, female vocal."

The skill walks you through the pipeline with two human review gates:

1. **Intake + storyboard** — brief → `concept.json` + lyrics + `storyboard.html` for approval.
2. **Music + timeline** — ElevenLabs sings the anthem with word timestamps; the cut timeline is derived from the actual beats.
3. **T01 keyframe** — one FAL nano-banana still to confirm the look pack landed (gate).
4. **Keyframe batch + clips** — the remaining stills, then Seedance Pro animates each into a clip.
5. **End card + captions + compose** — PIL-typeset wordmark, word-synced captions, ffmpeg retime + mix + burn → `finals/master-final.mp4`.

You can also run it all at once (`scripts/one_shot.py --concept … --continue`),
but the gates are there for a reason — the cheapest place to catch look drift is
the storyboard and the single T01 keyframe, before you pay for the batch.

## Quickstart

```bash
# 1. Copy this folder into your project
cp -R create-cinematic-music-video/ my-music-video/
cd my-music-video/

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set API keys
cp .env.example .env
# Edit .env with your FAL_KEY and ELEVENLABS_API_KEY

# 4. Start from the worked example
mkdir -p projects/aurelia-comeback/source
cp examples/concept.json     projects/aurelia-comeback/concept.json
cp examples/lyrics-locked.md projects/aurelia-comeback/source/lyrics-locked.md

# 5. Drop the skill into an agent that reads SKILL.md (Claude Code, Cursor, Goose,
#    Codex CLI, ...) and paste examples/aurelia-comeback.md — or run it directly:
python scripts/one_shot.py --concept projects/aurelia-comeback/concept.json
# (pauses at the storyboard gate and the T01 keyframe gate; resume with --from)
```

## Requirements

- **Python 3.10+** with `fal_client`, `Pillow`, `requests`, `python-dotenv`,
  `PyYAML`, `imageio-ffmpeg` (see `requirements.txt`).
- **ffmpeg** — any build. libass is auto-detected; if your ffmpeg lacks it, the
  caption burn falls back to the `imageio-ffmpeg` static binary automatically.
- **FAL API key** — nano-banana (keyframes) + Seedance Pro (image-to-video): https://fal.ai
- **ElevenLabs API key** — the Music API (original anthem + word timestamps): https://elevenlabs.io

## What's in this folder

```
create-cinematic-music-video/
├── SKILL.md                 ← the skill spec (agent reads this to drive the workflow)
├── README.md                ← you are here
├── .env.example             ← API keys template
├── requirements.txt         ← Python deps
├── scripts/
│   ├── lib.py               ← shared helpers (env, FAL, look packs, libass-ffmpeg finder)
│   ├── render_music.py      ← ElevenLabs Music /detailed → music.mp3 + word timestamps
│   ├── derive_timeline.py   ← per-tableau beat-locked in/out from the sung words
│   ├── render_keyframes.py  ← FAL nano-banana keyframes (parallel, look-pack injection)
│   ├── render_clips.py      ← FAL Seedance Pro i2v (parallel, auto de-letterbox)
│   ├── build_endcard.py     ← PIL-typeset wordmark/tagline + Ken Burns clip
│   ├── make_captions.py     ← word-synced ASS caption generator
│   ├── compose.py           ← retime to beats + mux music + burn captions → master
│   └── one_shot.py          ← idempotent state-machine driver (gates + resume)
├── lookpacks/               ← the four aesthetic packs (STYLE_OPENER + NEGATIVE_TAIL)
├── examples/                ← a complete runnable fictional run + a kickoff prompt
└── references/
    └── case-studies.md      ← the validated production runs (as archetypes)
```

## Why this format works

- **It's a song, not a montage.** Word-level timestamps mean the cuts ride the
  vocal — the spot feels authored, not assembled.
- **A 3-act arc, not a feature list.** Fourteen assigned roles (intro → energy →
  reflection) give the spot a shape an AI montage never has.
- **The look pack is the swap point.** One field turns a warm-day apparel anthem
  into a neon-night one. New aesthetics are one file, no code.
- **Sound-off safe** — burned word-synced captions carry the hook in a muted feed.
- **Brand text stays crisp** — the end-card wordmark is composited, never
  AI-rendered (image models can't draw clean type).

## What it doesn't do

- UGC talking-head / selfie-cam ads → use a different skill.
- Personified-villain cartoon explainers → use `animated-explainer-ad`.
- Pure typography / motion graphics, photoreal product demos, before-afters → different skills.
- Anything that requires a **licensed** track — this skill generates an original.

## Credit

Built from the production playbook of [GooseWorks](https://gooseworks.ai) — the
patterns are encoded from real client music-video runs. If you ship something
with this skill, we'd love to see it.
