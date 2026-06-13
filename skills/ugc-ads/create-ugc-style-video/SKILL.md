# Skill: Create UGC-Style Video Ad

## What this skill does

Produces a UGC-style talking-head video ad featuring an AI avatar reviewing one or more products. No real creator needed. The output is a 9:16 vertical video ready for Meta, TikTok, and Instagram Reels.

## Pipeline overview

```
1. Gather inputs         → brand info, product images, voice notes, target duration
2. Generate avatar       → NB2 (fal-ai/nano-banana-2/edit) creates a realistic portrait
3. Write scene scripts   → one per product: hook → product intro → benefit → CTA
4. Generate scenes       → Seedance 2.0 (bytedance/seedance-2.0/reference-to-video via FAL)
                           lip-synced natively with generate_audio: true
5. Stitch scenes         → ffmpeg concat
6. Add captions          → Whisper (fal-ai/whisper) word-level timestamps → burn with ffmpeg
7. Add music bed         → ElevenLabs music generation or royalty-free track, mixed at -18dB
8. Final QC              → duration check, caption sync spot-check, audio levels
```

## Inputs

| Input | Type | Default | Notes |
|---|---|---|---|
| `brand_name` | string | required | Brand or product name |
| `product_description` | string | required | 1–3 sentence product pitch |
| `product_images` | list of URLs or local paths | required | Hero images for each product |
| `brand_voice_notes` | string | conversational, first-person, relaxed, creator-style | Override for brand tone |
| `target_duration_per_product` | int (seconds) | 15 | Duration per product scene |
| `hook_duration` | int (seconds) | 8 | Duration of opening hook scene |
| `end_card_duration` | int (seconds) | 4 | Duration of closing CTA card |
| `num_products` | int | 1 | Number of products to feature (1–3) |
| `resolution` | string | `1080p` | Use `720p` for budget mode |
| `avatar_descriptor` | string | auto-generated | e.g. "25-year-old South Asian woman, natural look" |

## Outputs

- `output/final_ad.mp4` — Stitched, captioned, music-mixed vertical video
- `output/avatar_portrait.png` — Avatar portrait used across all scenes
- `output/scenes/` — Individual scene clips before stitch
- `output/captions.srt` — Word-level caption file

## Cost reference

| Item | Approx. cost |
|---|---|
| Avatar portrait (NB2) | ~$0.05 |
| Scene at 1080p / 15s (Seedance) | ~$5–10 |
| Transcription (Whisper via FAL) | ~$0.01/min |
| Music generation (ElevenLabs) | ~$0.05–0.20 |

Typical 3-product ad (hook + 3 scenes + end card): **~$20–35**

---

## Step-by-step instructions for Claude Code

### Phase 1 — Gather inputs

Ask the user for:
- Brand name and product description for each product
- Product hero images (URLs or local files — download if URLs)
- Brand voice notes (or use default: conversational, first-person, relaxed, creator-style)
- Number of products (1–3), resolution preference

### Phase 2 — Generate avatar portrait

Call NB2 to create a realistic human-looking creator portrait. This portrait anchors identity across all scenes — no Soul ID or additional consistency mechanism needed.

```bash
curl -X POST https://fal.run/fal-ai/nano-banana-2/edit \
  -H 'Authorization: Key $FAL_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "portrait of a [ETHNICITY] [GENDER], [AGE RANGE], clean natural look, phone front-camera selfie, soft indoor lighting, looking directly at camera, no makeup, real skin texture, white background",
    "num_images": 1
  }'
```

Save the returned image URL as `AVATAR_URL`. Download and store locally as `output/avatar_portrait.png`.

**Avatar prompt tips:**
- Keep it grounded and real — avoid "model" or "perfect" language
- Soft indoor lighting + white/neutral background = most versatile across scenes
- Vary ethnicity and age to match target audience if desired

### Phase 3 — Write scene scripts

Write one script block per scene: hook, per-product scene(s), end card.

**Structure per product scene (15s target):**
```
[0–3s]  Hook statement — bold claim or relatable problem
[3–8s]  Hold product up + introduce: "So I've been using [PRODUCT] for [X] weeks and..."
[8–13s] Benefit callout: "What I noticed is [specific benefit]. It actually [concrete result]."
[13–15s] CTA: "Link in bio if you want to try it."
```

**Voice rules:**
- First-person, present tense
- Short sentences. Pause beats. No filler words.
- Avoid superlatives ("amazing", "life-changing") — use specifics
- Creator-style: casual contractions, natural rhythm

### Phase 4 — Generate scenes with Seedance 2.0

**⚠️ CRITICAL RULES — read before every API call:**

1. **NEVER pass prior AI-generated video URLs as `image_urls`** — only pass portrait IMAGE URLs. Passing video URLs to Seedance's `image_urls` field triggers a `content_policy_violation` error.
2. **Always use `generate_audio: true`** for native lip-sync. This eliminates the need for a separate ElevenLabs VO step.
3. **Pass product images alongside the avatar portrait** in `image_urls` so Seedance incorporates the product visually.
4. **NSFW / skin contact rule:** Do not show product application directly on skin (e.g., applying cream to face). "Hold and describe" is always safe — the avatar holds the product and speaks to camera.

```bash
curl -X POST https://fal.run/fal-ai/bytedance/seedance-2.0/reference-to-video \
  -H 'Authorization: Key $FAL_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "image_urls": ["AVATAR_URL", "PRODUCT_IMAGE_URL"],
    "prompt": "A creator holds the product and speaks to camera: [SCRIPT_LINE]. UGC iPhone selfie style, warm indoor lighting, natural hand movement, eye contact with camera. Vertical 9:16 framing.",
    "duration": "15",
    "generate_audio": true,
    "resolution": "1080p"
  }'
```

Run one API call per scene. Save each returned video URL and download locally as `output/scenes/scene_[N].mp4`.

**For the hook scene:**
```bash
-d '{
  "image_urls": ["AVATAR_URL"],
  "prompt": "A creator looks directly into camera and says: [HOOK_LINE]. Close-up selfie framing, expressive face, UGC style. Vertical 9:16.",
  "duration": "8",
  "generate_audio": true,
  "resolution": "1080p"
}'
```

**For the end card:** Generate a static image overlay or a brief 4s clip with CTA text. If generating a clip:
```bash
-d '{
  "image_urls": ["AVATAR_URL"],
  "prompt": "Creator gives a thumbs up and points at camera, smiling. Text overlay reads: [CTA_TEXT]. UGC iPhone style. Vertical 9:16.",
  "duration": "4",
  "generate_audio": true,
  "resolution": "1080p"
}'
```

**Budget mode (720p):** Replace `"resolution": "1080p"` with `"resolution": "720p"`. Cost drops to ~$2–5 per scene.

### Phase 5 — Stitch scenes with ffmpeg

Create a concat list and stitch all scenes in order:

```bash
# Write concat list
cat > output/concat_list.txt << EOF
file 'scenes/scene_hook.mp4'
file 'scenes/scene_product_1.mp4'
file 'scenes/scene_product_2.mp4'
file 'scenes/scene_end_card.mp4'
EOF

# Stitch
ffmpeg -f concat -safe 0 -i output/concat_list.txt \
  -c:v libx264 -c:a aac -movflags +faststart \
  output/stitched.mp4
```

### Phase 6 — Add captions

**Step 6a — Get word-level timestamps from Whisper:**

```bash
curl -X POST https://fal.run/fal-ai/whisper \
  -H 'Authorization: Key $FAL_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "audio_url": "FILE_URL_OF_STITCHED_VIDEO",
    "chunk_level": "word",
    "language": "en"
  }'
```

This returns word-level timestamps. Parse into `.srt` or use directly with `drawtext`.

**Step 6b — Burn captions with ffmpeg:**

For simple single-line burn-in (bold white with black outline):
```bash
ffmpeg -i output/stitched.mp4 \
  -vf "subtitles=output/captions.srt:force_style='FontName=Arial,FontSize=18,Bold=1,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,Outline=2,Alignment=2'" \
  -c:a copy \
  output/captioned.mp4
```

Positioning note: `Alignment=2` centers captions in the lower third — safe for 9:16 vertical.

### Phase 7 — Add music bed

**Option A — ElevenLabs music generation:**
```bash
curl -X POST https://api.elevenlabs.io/v1/sound-generation \
  -H 'xi-api-key: $ELEVENLABS_API_KEY' \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "upbeat lo-fi background music, warm and chill, suitable for a product review video",
    "duration_seconds": [TOTAL_DURATION],
    "prompt_influence": 0.4
  }' \
  --output output/music_bed.mp3
```

**Option B — Royalty-free track:** Download a track from Pixabay, Freepd, or ccMixter and trim to length.

**Mix music at -18dB under VO:**
```bash
ffmpeg -i output/captioned.mp4 -i output/music_bed.mp3 \
  -filter_complex "[1:a]volume=-18dB[music];[0:a][music]amix=inputs=2:duration=first[aout]" \
  -map 0:v -map "[aout]" \
  -c:v copy -c:a aac \
  output/final_ad.mp4
```

### Phase 8 — Final QC

Run these checks before delivering:

```bash
# Check duration
ffprobe -v quiet -print_format json -show_format output/final_ad.mp4 | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Duration: {float(d[\"format\"][\"duration\"]):.1f}s')"

# Check audio levels (should peak around -6dBFS, music around -24dBFS)
ffmpeg -i output/final_ad.mp4 -af "volumedetect" -f null /dev/null 2>&1 | grep max_volume

# Spot-check caption sync
ffplay output/final_ad.mp4  # manual review
```

**QC checklist:**
- [ ] Total duration matches target (hook + scenes + end card)
- [ ] Avatar face is consistent across all scenes
- [ ] Captions are legible and roughly synced
- [ ] Music is clearly below VO (not competing)
- [ ] No content_policy_violation errors hit during generation
- [ ] Product is visible in product scenes
- [ ] Vertical 9:16 framing throughout

---

## Error handling

| Error | Cause | Fix |
|---|---|---|
| `content_policy_violation` on Seedance | Passed a video URL to `image_urls` | Only pass portrait image URLs, never video URLs |
| Avatar looks inconsistent across scenes | Used different prompts | Re-use the exact same `AVATAR_URL` from Phase 2 in all scene calls |
| `generate_audio` not syncing | Audio prompt too long / complex | Break into shorter script chunks, one sentence per scene |
| ffmpeg concat audio/video drift | Scenes have different audio tracks | Add `-async 1` to ffmpeg concat command |
| Whisper returns no word timestamps | Video audio too quiet | Re-check audio levels; Whisper needs clear VO |

---

## Environment variables

See `.env.example` for all required variables.

| Variable | Required | Purpose |
|---|---|---|
| `FAL_KEY` | Yes | FAL API access (NB2, Seedance, Whisper) |
| `ELEVENLABS_API_KEY` | Yes (for music gen) | Music bed generation |
| `KLAP_API_KEY` | No | Optional: Klap for caption styling |
