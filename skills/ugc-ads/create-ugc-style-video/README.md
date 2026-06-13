# create-ugc-style-video

**Produce a UGC-style AI talking-head video ad in minutes. No creator required.**

This skill runs inside [Claude Code](https://claude.ai/code) (or any Goose-compatible agent) and orchestrates the full pipeline: avatar generation → scene production → stitch → captions → music mix → final export.

## What you get

A 9:16 vertical video ad featuring a realistic AI avatar reviewing your product — ready for Meta, TikTok, and Instagram Reels.

```
hook scene (8s) → product scene × N (15s each) → end card (4s)
+ word-level burned captions
+ music bed mixed at -18dB
```

## Prerequisites

- [Claude Code](https://claude.ai/code) or a Goose agent environment
- `ffmpeg` installed locally (`brew install ffmpeg` / `apt install ffmpeg`)
- Python 3.8+ (for any helper scripts)
- API keys — see [.env.example](.env.example)

## Quick start

```bash
# 1. Clone the goose-video repo
git clone https://github.com/gooseworks-ai/goose-video.git
cd goose-video

# 2. Copy and fill in your env vars
cp skills/ugc-ads/create-ugc-style-video/.env.example .env
# Edit .env with your FAL_KEY, ELEVENLABS_API_KEY

# 3. Drop the skill into Claude Code
# Open Claude Code and paste:
# "Load the skill at skills/ugc-ads/create-ugc-style-video/SKILL.md and help me make a UGC ad."

# 4. Give Claude your product info when prompted and let it run
```

## APIs used

| Service | Model / Endpoint | Purpose |
|---|---|---|
| [FAL](https://fal.ai) | `fal-ai/nano-banana-2/edit` | Avatar portrait generation |
| [FAL](https://fal.ai) | `fal-ai/bytedance/seedance-2.0/reference-to-video` | Lip-synced talking-head scene generation |
| [FAL](https://fal.ai) | `fal-ai/whisper` | Word-level transcription for captions |
| [ElevenLabs](https://elevenlabs.io) | Sound Generation API | Music bed (optional) |

## Cost estimate

| Scenario | Approx. cost |
|---|---|
| 1-product ad, 1080p | ~$8–15 |
| 3-product ad, 1080p | ~$20–35 |
| 3-product ad, 720p (budget) | ~$8–15 |

Pricing is API cost only — no platform fees.

## Key rules (read before running)

1. **Never pass AI video URLs to Seedance `image_urls`** — only portrait image URLs. Passing video URLs triggers `content_policy_violation`.
2. **Always use `generate_audio: true`** on Seedance for native lip-sync (no separate VO step needed).
3. **NSFW:** Avoid showing product application on skin. "Hold and describe" (avatar holds product, speaks to camera) is always safe.
4. **Avatar consistency:** Re-use the exact same avatar portrait URL across all scene calls. This is what keeps the face consistent.

## File structure

```
create-ugc-style-video/
├── SKILL.md              ← Full pipeline instructions for Claude Code
├── README.md             ← This file
├── .env.example          ← Required environment variables
├── requirements.txt      ← Python dependencies (for helper scripts)
└── examples/
    └── kickoff.md        ← Example kickoff prompt for Claude Code
```

## Output structure

```
output/
├── avatar_portrait.png   ← AI avatar portrait (anchor for all scenes)
├── scenes/
│   ├── scene_hook.mp4
│   ├── scene_product_1.mp4
│   └── scene_end_card.mp4
├── stitched.mp4          ← Raw concat
├── captioned.mp4         ← With burned captions
├── captions.srt          ← Word-level SRT file
├── music_bed.mp3         ← Generated or sourced music track
└── final_ad.mp4          ← Final deliverable
```

## License

MIT — see repo root LICENSE file.
