# goose-video

Open agent skills for AI video production.

Drop a skill folder into any agent that reads `SKILL.md` (Claude Code, Cursor, Goose, Codex CLI, …), then describe the video you want to make. The agent walks you through it.

## Skills

| Skill | What it makes | Validated on |
|---|---|---|
| [`animated-explainer-ad`](./skills/templates/animated-explainer-ad/) | 9:16 ~30–45s absurdist Pixar 3D explainer ad where a personified villain narrates their own defeat by the product. Bright cartoon characters, single-narrator VO, real-product end card, burned captions, whimsical Pixar/Disney score. ~$15–25 per cut. | HUM Nutrition "Big Chill" · Soteri Skin "Eczema, the pH villain" |

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

```bash
git clone https://github.com/gooseworks-ai/goose-video.git
cd goose-video/skills/templates/animated-explainer-ad
pip install -r requirements.txt
cp .env.example .env
# fill in FAL_KEY + ELEVENLABS_API_KEY

# then in your agent, with the skill loaded:
> Make an animated explainer ad for [your brand] where the villain is [your problem]…
```

See each skill's own README for full setup + an example prompt.

## Built by

[GooseWorks](https://gooseworks.ai) — AI coworkers for go-to-market. We use these skills internally for client work; publishing them so others can build on the same patterns.

[@shivsakhuja](https://x.com/shivsakhuja) · [LinkedIn](https://www.linkedin.com/in/shivsakhuja)

## License

MIT — use freely, attribution appreciated.
