# animated-explainer-ad

> A portable agent skill that turns a one-line prompt into a polished 9:16 animated explainer ad in bright Pixar/Disney 3D, with a personified villain who narrates their own defeat. Validated on two production client runs. ~$15–25 per cut.

## What it makes

A 30–45 second 9:16 paid-social ad where the *problem* (eczema, stress, dullness, hidden fees) shows up as a cute cartoon villain, narrates the whole spot, watches the product defeat them, and packs their bags. Captioned, mixed, ready to upload to Meta / TikTok / Reels.

Two reference outputs:

| Brand | Concept | Spec | Cost |
|---|---|---|---|
| HUM Nutrition | "Big Chill" — Stress as villain, cortisol minions, Big Chill capsule descending on a halo | 34.6s, 9:16 | ~$16 |
| Soteri Skin | "Eczema, the pH villain" — Eczema gremlin attacking the moisture barrier, pH/LOCK at 4.9 | 45.1s, 9:16 | ~$17.60 |

See [`references/case-studies.md`](./references/case-studies.md) for the full breakdowns.

## How it works

You give Claude (or any agent that reads `SKILL.md`) a free-form prompt:

> "Make an animated explainer ad for Soteri Skin. The villain is Eczema, the hero is Soteri (a cream that locks pH at 4.9), and the audience is parents of babies with eczema. Real product photo is at `./product.jpg`."

The skill walks you through 8 phases with human review gates at the key decision points:

1. **Intake** — clarifying questions + script draft → `storyboard.html` for approval.
2. **Character anchors** — nano-banana renders 4 anchor PNGs → grid for approval.
3. **Voice casting + VO** — A/B 3–6 ElevenLabs voices on scene 01 → render full script in chosen voice.
4. **Keyframes** — per-scene nano-banana stills with chained character refs → contact sheet for approval.
5. **Scene clips** — Seedance Pro i2v with auto de-letterbox → preview gate, then remaining batch.
6. **End card** — PIL composite of your real product photo + typeset brand layer.
7. **Music** — ElevenLabs music API generates a whimsical Pixar bed.
8. **Compose** — ffmpeg retimes clips to VO, mixes audio with ducking, burns captions.

You can also run in autopilot mode (`./scripts/auto.sh "your prompt" ./project/`), but the human gates are there for a reason — both reference runs caught character drift (bat-wings, wrong palette) at gate 2 or 4 and re-rolled before paying for clips.

## Quickstart

```bash
# 1. Clone or copy this folder into your project
cp -R animated-explainer-ad/ my-ad/
cd my-ad/

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set API keys
cp .env.example .env
# Edit .env with your FAL_KEY and ELEVENLABS_API_KEY

# 4. Drop the skill into an agent that reads SKILL.md
#    (Claude Code, Cursor, Goose, Codex CLI, ...)
#    Then say something like:

> /skill animated-explainer-ad

> Make an animated explainer ad for my brand "Lumeo Skin", a serum
> for skin dullness. The villain is "Dullness" — a sleepy grey
> gremlin who sits on the collagen scaffold and makes it sag.
> The hero is Lumeo. The mechanism is a 30-day collagen reset.
> Audience: women 25-45 noticing their skin going flat.
> Product photo at ./lumeo-bottle.jpg.

# The agent walks you through phases 1-8.
```

## Requirements

- **Python 3.10+** with `fal_client`, `Pillow`, `pyyaml`, `requests` (see `requirements.txt`).
- **ffmpeg** with libass support (`brew install ffmpeg` on macOS).
- **FAL API key** for nano-banana (stills) and Seedance Pro (i2v): https://fal.ai
- **ElevenLabs API key** for `eleven_v3` TTS and music API: https://elevenlabs.io
- **A real product photo** — ≥1000×1000, clean or simple background. Non-negotiable: the end card must be a real product photo, not an AI-rendered cartoon bottle.

## What's in this folder

```
animated-explainer-ad/
├── SKILL.md                ← the skill spec (agent reads this to drive the workflow)
├── README.md               ← you are here
├── .env.example            ← API keys template
├── requirements.txt        ← Python deps
├── scripts/
│   ├── lib.py              ← shared helpers (env, FAL upload, project paths)
│   ├── render_anchor.py    ← Phase 2: character anchor via FAL nano-banana
│   ├── render_vo.py        ← Phase 3: ElevenLabs eleven_v3 TTS + silence-trim
│   ├── measure_vo.py       ← Phase 3: per-scene VO duration → scene_timing.json
│   ├── render_keyframe.py  ← Phase 4: nano-banana keyframe with chained anchor refs
│   ├── render_clip.py      ← Phase 5: Seedance Pro i2v + auto de-letterbox
│   ├── build_endcard.py    ← Phase 6: PIL composite + Ken Burns
│   ├── render_music.py     ← Phase 7: ElevenLabs music API
│   ├── make_captions.py    ← Phase 8: libass .ass generator
│   ├── compose.sh          ← Phase 8: ffmpeg compose + mix + burn
│   └── auto.sh             ← runs all 8 phases with no human gates
├── examples/
│   ├── soteri-eczema.md    ← the Soteri brief as a kickoff prompt
│   ├── hum-big-chill.md    ← the Big Chill brief as a kickoff prompt
│   └── lumeo-dullness.md   ← a minimal-info kickoff prompt
└── references/
    └── case-studies.md     ← the two validated production runs
```

## Why this format works

- **Pattern-interrupt hook.** A baby-skincare ad that opens on a gleeful villain whispering "I'm Eczema" earns the next 35 seconds in a feed of identical before-and-after spots.
- **It teaches the ownable mechanism.** Most eczema creams "just moisturise"; Soteri's mechanism is that eczema is a *pH* problem and pH/LOCK fixes the cause. Cartoon personification makes an abstract chemistry point visual and sticky.
- **Recurring number/word motif** ("pH 4.9", "cortisol hormones") gives one concept three repetitions, which is what memory needs.
- **Villain narrates their own defeat** is inherently shareable. The comedy is the villain losing. Keeps potentially heavy topics (eczema, stress, weight gain) light.
- **Sound-off safe** — burned word-by-word captions carry the message in muted feed.

## What it costs

For a 12-scene 1080p cut:

| Phase | Provider | Cost |
|---|---|---|
| 2 — Character anchors (×4) | FAL nano-banana | ~$0.32 |
| 3 — Voice casting (3-6 A/B) | ElevenLabs eleven_v3 | ~$0.15 |
| 3 — VO render (×12 lines) | ElevenLabs eleven_v3 | ~$0.30 |
| 4 — Keyframes (×11) | FAL nano-banana | ~$0.66 |
| 5 — Scene clips (×11 at 4-6s) | FAL Seedance Pro 1080p | ~$15.00 |
| 7 — Music bed | ElevenLabs music API | ~$0.20 |
| **Total** | | **~$16.50** |

Add ~10–15% for re-rolls during human gates. Wall time ~2 hours including reviews.

## What it doesn't do

- Photoreal product demos → use a different tool.
- Creator/UGC selfie cam ads → use a different tool.
- Pure typography motion graphics → use a different tool.
- Live-action / talking head / before-after → use a different tool.
- Topics where personification is tone-deaf (terminal illness, grief). Don't make a cute villain out of cancer.

## Credit

Built from the production playbook of [GooseWorks](https://gooseworks.ai) — the patterns are encoded from two real client runs. If you ship something with this skill, would love to see it: [@shivsakhuja](https://x.com/shivsakhuja).
