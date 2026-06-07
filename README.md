# goose-video

Open agent skills and a setup CLI for AI video and static ad production with [Gooseworks](https://gooseworks.ai).

This repo contains:

1. **Agent skills** — drop-in `SKILL.md` workflows for Claude Code, Cursor, Codex, etc.
2. **`goose-video` CLI** — authenticates with Gooseworks, installs the `ads-remix` skill into Claude Code, and registers the `gooseworks` MCP server so generation runs on your machine.

---

## CLI — run Gooseworks ads locally

The in-app ads chat runs the agent loop inside a cloud sandbox (expensive: sandbox + agent tokens, billed to Gooseworks). The CLI moves setup local: you run `goose-video login` once, then paste instructions into Claude Code. Gooseworks still brokers media generation (FAL / Higgsfield / ElevenLabs) through its proxies — billed to ad credits.

```
goose-video (this machine)                 Gooseworks cloud
  ├─ Claude Code (your ANTHROPIC key) ───── agent tokens on YOUR key
  ├─ ads-remix skill (installed by login) ◀── master skill ships in this repo
  ├─ app-mcp client ───────────────────────▶ app-mcp /mcp   (data + files + renders)
  └─ media calls ──────────────────────────▶ fal/hf/11labs proxies (billed to credits)
```

One token does everything: the `cal_*` API token from `goose-video login` authenticates both app-mcp and the media proxies.

### Install

```bash
git clone https://github.com/gooseworks-ai/goose-video.git
cd goose-video
npm install
npm link            # dev: global `goose-video` on your PATH
# end users (once published): npx goose-video@latest login
```

### Commands

| command   | what it does |
|-----------|--------------|
| `login`   | browser loopback auth → agent-scoped `cal_` token; installs `ads-remix` skill + registers MCP |
| `logout`  | clears `~/.goose-video/config.json` |
| `whoami`  | lists your ad brands via app-mcp |
| `credits` | shows the agent's credit balance |
| `update`  | re-pulls recipe skills + refreshes the installed skill |

After `login`, open Claude Code and paste an instruction, e.g.:

```
Use the ads-remix skill to remix template <id> for my brand https://acme.com —
research the brand, create the project, and generate the final ad.
```

Browse remixable templates at [gooseworks.ai/remix](https://gooseworks.ai/remix).

### Config

Stored at `~/.goose-video/config.json` (mode 0600). Override with `--api-base`, `--mcp-url`, `--web-url`, or env `GOOSE_VIDEO_API_BASE` / `GOOSE_VIDEO_MCP_URL` / `GOOSE_VIDEO_WEB_URL`.

---

## Agent skills

Drop a skill folder into any agent that reads `SKILL.md`, then describe the video you want to make.

| Skill | What it makes | Validated on |
|---|---|---|
| [`animated-explainer-ad`](./skills/templates/animated-explainer-ad/) | 9:16 ~30–45s absurdist Pixar 3D explainer ad where a personified villain narrates their own defeat by the product. ~$15–25 per cut. | HUM Nutrition "Big Chill" · Soteri Skin "Eczema, the pH villain" |

More coming. If you ship something using one of these, we'd love to see it.

### How a skill is structured

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

### Quickstart (animated explainer)

Paste into Claude Code:

```
Clone https://github.com/gooseworks-ai/goose-video into ./goose-video, then
read the skill at ./goose-video/skills/templates/animated-explainer-ad/SKILL.md
and walk me through it to make an animated explainer ad.

Before starting:
  1. cd into ./goose-video/skills/templates/animated-explainer-ad
  2. pip install -r requirements.txt
  3. Help me create a .env from .env.example — FAL_KEY + ELEVENLABS_API_KEY

Then ask me for: the brand, product, villain problem, ownable mechanism, and audience.
Follow the SKILL.md 8-phase pipeline and pause at each human review gate.
```

See each skill's README for full setup details.

---

## Built by

[**GooseWorks**](https://gooseworks.ai) — AI agents that make videos and run ads.

- **Shiv Sakhuja** — [@shivsakhuja](https://x.com/shivsakhuja)
- **Himanshu Bamoria** — [@0xhbam](https://x.com/0xhbam)
- **Akhil Bisht** — [LinkedIn](https://www.linkedin.com/in/akhil-bisht/)
- **Soham Mehta** — [@sohamehta_](https://x.com/sohamehta_)

## License

MIT — use freely, attribution appreciated.
