# imessage-video-ad

> A portable agent skill that turns a short brief into a 9:16 social-native **iMessage conversation reveal** ad. Bubbles pop in over time, the composer types char-by-char, real Apple iMessage SFX hit on every send/receive, a lofi bed sits underneath, and a brand end card delivers a promo code. One continuous Playwright recording (no scene-cuts), assembled to a master MP4 plus 9:16 / 1×1 variants. ~$0.20–0.65 per cut.

## What it makes

A 17–22 second 9:16 paid-social ad that recreates a believable iMessage thread: someone screenshots a result/product and sends it to a friend, the friend reacts ("wait what app is that"), and the conversation surfaces the brand + a CTA code (FREEPACK / FIRSTPACK / WELCOME10). It renders **framed** by default — a visible iPhone bezel + Dynamic Island + status bar, sitting on a flat-lay desk background.

The conversational delivery feels far less ad-like than a hard CTA card, which is why these convert.

## How it works

You give an agent that reads `SKILL.md` a brief:

> "Make an iMessage ad for my trading-card app. The hook is a screenshot of a graded card worth $4,736. The peer ('Tyler') reacts and asks what app it is; I reveal you can build your own pack and set the odds, then drop code FREEPACK. Playful brand voice."

The skill walks the pipeline with review gates:

1. **Brainstorm the angle** — pick the strongest hook from the concept catalog.
2. **Script the thread** — write `threads/full-thread.json` (the bubbles as data) + the hook screenshot.
3. **Define the timeline** — `timeline.json` schedules every pop / typing / composer / scroll event and the SFX cues.
4. **Flat-lay background** — generate the desk the phone sits on (`gen_flat_lay_bg.py`, FAL ~$0.19) or supply your own.
5. **Record** — one continuous Playwright session → `master-chat.mp4` + a deterministic SFX cue list.
6. **End card** — generated with the [`goose-graphics`](https://skills.gooseworks.ai/styles) skill by default (`--style pixel-haze --format tweet`; bundled HTML templates as fallback) → static brand slate.
7. **Stitch** — crossfade chat → end card, layer the SFX deterministically, mix the music bed.
8. **Export** — 9:16 1080-wide + 1×1 variants for Meta.

## Quickstart

```bash
# 1. Copy this folder into your project space
cp -R imessage-video-ad/ my-ad-skill/
cd my-ad-skill/

# 2. Install dependencies
npm install                       # Playwright (Node)
pip install -r requirements.txt   # FAL client (Python) — only for the flat-lay bg
npx playwright install chromium   # one-time browser download

# 3. (optional) Set API keys for the flat-lay background generator
cp .env.example .env
# Edit .env with your FAL_KEY

# 4. Drop the skill into an agent that reads SKILL.md (Claude Code, Cursor, Goose, …) and say:
```

> Read SKILL.md and walk me through an iMessage video ad. The brand is "<brand>",
> the hook is <what gets screenshotted>, the peer is "<name>", and the CTA code
> is <CODE>. Make a project folder, draft the thread + timeline, show me the
> storyboard, and pause at each review gate before recording.

You also need: a hook screenshot (the image attached in bubble 1), the real brand
logo SVG, and a lofi/hip-hop music loop at `<project>/audio/music-bed.mp3`.

## Requirements

- **Node** + Playwright (`npm install` here, then `npx playwright install chromium`)
- **Python 3** + `fal-client` (only for the flat-lay background step)
- **ffmpeg / ffprobe** on your PATH
- A **FAL_KEY** if you want the script to generate the flat-lay desk background

## Project layout the scripts expect

```
<project>/
  threads/full-thread.json     the script as data
  timeline.json                recording schedule + SFX cues (copy examples/timeline.example.json)
  flat-lay-prompt.txt          (optional) brand-specific desk prompt
  assets/
    flat-lay-bg.jpg            framed background (generated or supplied)
    <hook>.png                 the screenshot attached in bubble 1
    brand-logo.svg             real brand wordmark for the end card
    hero.png                   (photo-bg end card only)
  audio/music-bed.mp3          your lofi/hip-hop bed
  clips/                       created by the scripts
  edits/                       created by the scripts
```

## License

MIT — use freely, attribution appreciated.
