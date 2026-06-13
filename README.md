# goose-video

Open agent skills for AI video production and Meta advertising.

Drop a skill folder into any agent that reads `SKILL.md` (Claude Code, Cursor, Goose, Codex CLI, …), then describe what you want to make or run. The agent reads the skill and executes.

## Skills

### 🎬 Meta Ads — run Meta campaigns from the terminal

| Skill | What it does |
|---|---|
| [`setup-meta-ads`](./skills/meta-ads/setup-meta-ads/) | Install the Meta Ads CLI, authenticate, validate ad account + page + IG access end-to-end. Run this first. |
| [`create-meta-ad`](./skills/meta-ads/create-meta-ad/) | Create a full campaign → ad set → creative → ad in one conversational session. Supports image and video creatives. Defaults to PAUSED. |
| [`add-creative-to-adset`](./skills/meta-ads/add-creative-to-adset/) | Push a new creative variant into an existing running ad set — for A/B testing hooks, copy, and formats. |
| [`track-meta-ad-performance`](./skills/meta-ads/track-meta-ad-performance/) | Pull Meta Ads insights at any scope (account / campaign / ad set / ad), format a readable report, and flag CTR / CPC / frequency anomalies automatically. |
| [`explain-meta-ad-setup`](./skills/meta-ads/explain-meta-ad-setup/) | Walk the full campaign tree, pull 7d performance, and produce a skimmable audit with TL;DR + watch items. |

**Quickstart:**

```
Clone https://github.com/gooseworks-ai/goose-video into ./goose-video, then
read ./goose-video/skills/meta-ads/setup-meta-ads/SKILL.md and walk me through
setting up my Meta Ads CLI. I'll need ACCESS_TOKEN and AD_ACCOUNT_ID.
```

---

### 🎥 Video Pipeline — make AI video ads with Claude Code

| Skill | What it does |
|---|---|
| [`generate-ad-concepts`](./skills/video-pipeline/generate-ad-concepts/) | Turn a product brief into N distinct ad concepts — each with hook, script outline, format, audience, and CTA. |
| [`plan-script-for-video-ad`](./skills/video-pipeline/plan-script-for-video-ad/) | Write a full 30s paid-social script: 7-beat arc (cold-open → hook → pivot → solution → outcome → proof → CTA), rhythm rules, hook tier table, and CTA formula. |
| [`create-video-veo3`](./skills/video-pipeline/create-video-veo3/) | Generate cinematic video clips with Google Veo 3.1 via Higgsfield CLI or FAL. Includes prompt rules, banned vocab, product B-roll safety rules, and cost guide. |
| [`create-voiceover-elevenlabs`](./skills/video-pipeline/create-voiceover-elevenlabs/) | Generate ElevenLabs v3 voiceover with timing data, audio tags, and naturalness controls. Includes known limitations and atempo correction workflow. |

**Quickstart:**

```
Clone https://github.com/gooseworks-ai/goose-video into ./goose-video, then
read ./goose-video/skills/video-pipeline/generate-ad-concepts/SKILL.md and
walk me through generating ad concepts.

My product: [describe your product and problem it solves]
Target audience: [who it's for]
```

---

### 🎭 UGC Ads — AI avatars reviewing your product

| Skill | What it does |
|---|---|
| [`create-ugc-style-video`](./skills/ugc-ads/create-ugc-style-video/) | Full pipeline: AI avatar portrait (NB2/FAL) → lip-synced talking-head scenes (Seedance 2.0) → ffmpeg stitch → captions → music bed. Outputs a 9:16 vertical ad ready for Meta, TikTok, and IG Reels. |

**Quickstart:**

```
Clone https://github.com/gooseworks-ai/goose-video into ./goose-video, then
read ./goose-video/skills/ugc-ads/create-ugc-style-video/SKILL.md and walk
me through making a UGC-style video ad.

My product: [describe your product]
Product images: [local paths or URLs]
```

---

### ✨ Templates

| Skill | What it makes | Validated on |
|---|---|---|
| [`animated-explainer-ad`](./skills/templates/animated-explainer-ad/) | 9:16 ~30–45s absurdist Pixar 3D explainer ad. Bright cartoon characters, single-narrator VO, real-product end card. ~$15–25 per cut. | HUM Nutrition · Soteri Skin |

---

## How a skill is structured

Each skill is a self-contained folder:

```
<skill>/
├── SKILL.md          ← agent reads this to drive the workflow
├── README.md         ← human-facing intro
├── .env.example      ← API keys needed
├── requirements.txt  ← Python deps
├── examples/         ← ready-to-paste kickoff prompts
```

The agent reads `SKILL.md` to know:
- when to invoke this skill (trigger phrases, use cases)
- what inputs to gather from the user
- how to walk the production pipeline step-by-step
- what commands to run and with what arguments
- when to pause for human review

Scripts are kept small, single-purpose, and provider-grounded. No giant config schemas — the agent stitches them.

## API keys you'll need

| Skill bundle | Keys required |
|---|---|
| Meta Ads | `ACCESS_TOKEN` (Meta System User token), `AD_ACCOUNT_ID` |
| Video Pipeline | `HIGGSFIELD_API_KEY` or `FAL_KEY`, `ELEVENLABS_API_KEY` |
| UGC Ads | `FAL_KEY`, `ELEVENLABS_API_KEY` (for music), `KLAP_API_KEY` (optional, for captions) |

See each skill's `.env.example` for the full list.

## Built by

[**GooseWorks**](https://gooseworks.ai) — AI agents that make videos and run ads. We use these skills internally for client work; publishing them so others can build on the same patterns.

- **Shiv Sakhuja** — [@shivsakhuja](https://x.com/shivsakhuja) · [LinkedIn](https://www.linkedin.com/in/shivsakhuja)
- **Himanshu Bamoria** — [@0xhbam](https://x.com/0xhbam) · [LinkedIn](https://linkedin.com/in/hbamoria)
- **Akhil Bisht** — [LinkedIn](https://www.linkedin.com/in/akhil-bisht/)
- **Soham Mehta** — [@sohamehta_](https://x.com/sohamehta_) · [LinkedIn](https://www.linkedin.com/in/sohamehta/)

## License

MIT — use freely, attribution appreciated.
