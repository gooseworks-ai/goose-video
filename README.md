# goose-video

Open agent skills for AI video production.

Drop a skill folder into any agent that reads `SKILL.md` (Claude Code, Cursor, Goose, Codex CLI, …), then describe the video you want to make. The agent walks you through it.

## Skills

| Skill | What it makes | Validated on |
|---|---|---|
| [`animated-explainer-ad`](./skills/templates/animated-explainer-ad/) | 9:16 ~30–45s absurdist Pixar 3D explainer ad where a personified villain narrates their own defeat by the product. Bright cartoon characters, single-narrator VO, real-product end card, burned captions, whimsical Pixar/Disney score. ~$15–25 per cut. | HUM Nutrition "Big Chill" · Soteri Skin "Eczema, the pH villain" |
| [`create-cinematic-music-video`](./skills/templates/create-cinematic-music-video/) | 9:16 ~20–30s cinematic music-video ad built on an original anthem with real sung vocals + word-level timestamps. 14 beat-locked tableaux in a 3-act arc, swappable "look packs" (warm 35mm, neon night, paper-cut, gothic), PIL-typeset end card, burned word-synced captions. ~$15–25 per cut. | Apparel anthem (Kodak Portra) · Apparel anthem (CineStill night) · CPG anthem (paper-cut) |

More coming. If you ship something using one of these, would love to see it.

## How a skill is structured

Each skill is a self-contained folder:

```
<skill>/
├── SKILL.md          ← agent reads this to drive the workflow
├── README.md         ← human-facing intro
├── .env.example      ← API keys needed
├── requirements.txt  ← Python deps
├── scripts/          ← deterministic glue (FFmpeg + provider SDKs)
├── examples/         ← ready-to-paste kickoff prompts
└── references/       ← worked case studies
```

The agent reads `SKILL.md` to know:
- when to invoke this skill (trigger phrases, use cases)
- what inputs to gather from the user
- how to walk the production pipeline phase-by-phase
- when to pause for human review
- what scripts to call and with what arguments

Scripts are kept small, single-purpose, and provider-grounded. No giant config schemas — the agent stitches them.

## Quickstart

Paste this into Claude Code (or any agent that can run shell + read files):

```
Clone https://github.com/gooseworks-ai/goose-video into ./goose-video, then
read the skill at ./goose-video/skills/templates/animated-explainer-ad/SKILL.md
and walk me through it to make an animated explainer ad.

Before starting:
  1. cd into ./goose-video/skills/templates/animated-explainer-ad
  2. pip install -r requirements.txt
  3. Help me create a .env from .env.example — I'll need a FAL_KEY (https://fal.ai)
     and ELEVENLABS_API_KEY (https://elevenlabs.io).

Then ask me for: the brand, the product, the problem we're personifying as the
villain, the ownable mechanism, and the audience. From there, follow the SKILL.md
8-phase pipeline (intake → anchors → VO → keyframes → clips → end card → music →
compose) and pause at each human review gate so I can approve before paying for
the next phase.
```

See each skill's own README for full setup details and additional example prompts.

## Built by

[**GooseWorks**](https://gooseworks.ai) — AI agents that make videos and run ads. We use these skills internally for client work; publishing them so others can build on the same patterns.

- **Shiv Sakhuja** — [@shivsakhuja](https://x.com/shivsakhuja) · [LinkedIn](https://www.linkedin.com/in/shivsakhuja)
- **Himanshu Bamoria** — [@0xhbam](https://x.com/0xhbam) · [LinkedIn](https://linkedin.com/in/hbamoria)
- **Akhil Bisht** — [LinkedIn](https://www.linkedin.com/in/akhil-bisht/)
- **Soham Mehta** — [@sohamehta_](https://x.com/sohamehta_) · [LinkedIn](https://www.linkedin.com/in/sohamehta/)

## License

MIT — use freely, attribution appreciated.
