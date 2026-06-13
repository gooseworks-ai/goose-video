# Skill: Create Video with Veo 3.1

Generate a cinematic short-form video clip using Google Veo 3.1 via the Higgsfield CLI or FAL API. Outputs an MP4 file ready for editing.

---

## When to Use This Skill

Use this skill to generate individual video clips from a creative brief — product B-roll, lifestyle sequences, talking-head backgrounds, motion sequences. Typically used after `plan-script-for-video-ad` to produce visual assets beat by beat.

---

## Prerequisites

- **Higgsfield CLI** installed at `/opt/homebrew/bin/higgsfield` (preferred)
- **OR** FAL API access via `fal-client` Python library
- API key: `HIGGSFIELD_API_KEY` or `FAL_KEY`

---

## Inputs

| Field | Description |
|---|---|
| `subject` | Who or what is the main subject |
| `action` | What the subject is doing — the primary motion |
| `style` | Visual style (cinematic, UGC, product commercial, editorial, etc.) |
| `camera` | Camera motion and framing (handheld, locked, push-in, arc, etc.) |
| `mood` | Emotional tone (warm, energetic, calm, dramatic, etc.) |
| `audio` | Any audio direction (ambient sound, silence, music style) |
| `start_image` | Optional: path to a reference or start frame image |
| `aspect_ratio` | Default: `9:16` |
| `duration` | Default: `4`. Allowed values: `4`, `6`, `8` (seconds) |

---

## Model Selection

**Default model: `veo-3-1-preview`**

Do NOT use `veo-3-1-fast` for production clips.

> **Why:** The fast variant silently rewrites prompts. Your carefully crafted scene description will be substituted with a simplified internal interpretation. You won't know it happened — the clip will just look wrong. Always use `veo-3-1-preview` unless you explicitly need a fast draft preview and don't care about prompt fidelity.

---

## Prompt Composition Rules

### Rule 1: Always verb-led
The CHARACTER and their primary ACTION-VERB must appear in the first 8 words of the prompt.

> ✓ Good: `"Woman OPENS refrigerator door, pulls out a glass bottle, cinematic kitchen morning light"`
> ❌ Bad: `"In a bright modern kitchen with morning light, a woman is shown opening..."`

Write ACTION VERBS in CAPS to weight them for the model.

### Rule 2: Structure
```
[CHARACTER] [ACTION-VERB] [OBJECT/ENVIRONMENT], [camera motion], [lighting], [style], [mood], [audio if relevant]
```

### Rule 3: Banned vocabulary
Never use these words in Veo prompts — they produce flat, lifeless clips:

```
static | locked | subtle | near-static | slow | smooth | gentle | dreamy | slowly | gently | quietly
```

> Instead of "smooth camera movement" → use "fluid dolly push-in"
> Instead of "gentle lighting" → use "soft wrap-around fill light"
> Instead of "slow reveal" → use "deliberate push-in REVEALS product"

### Rule 4: Product B-roll — camera motion only
For product shots where you need the label or branding to stay readable:

- Use **camera-only motion** on a locked subject
- Do NOT prompt for 360-degree product rotation — the model will fabricate label text and distort branding
- Do NOT prompt for close-up text/label reading — same fabrication risk

> ✓ Good: `"Glass bottle of serum SITS on white marble counter, camera ORBITS left 30 degrees, morning window light rakes across surface, commercial product photography style"`
> ❌ Bad: `"Product rotates slowly showing all sides of the label"`

### Rule 5: Duration minimum
Veo 3.1 minimum is **4 seconds**. If you need a shorter clip for editing (e.g., a 1-second cold open), generate at 4 seconds and trim in post.

Allowed durations: `4` / `6` / `8`

---

## Higgsfield CLI — Primary Method

```bash
/opt/homebrew/bin/higgsfield generate create veo3_1 \
  --prompt "YOUR PROMPT HERE" \
  --image /path/to/start-image.jpg \
  --aspect_ratio 9:16 \
  --duration 4 \
  --quality high \
  --wait \
  --wait-timeout 12m
```

### Key flags

| Flag | Description |
|------|-------------|
| `--prompt` | Your verb-led prompt string |
| `--image` | Path to start frame image (use `--image`, NOT `--start-image`) |
| `--aspect_ratio` | `9:16` (vertical), `16:9` (horizontal), `1:1` (square) |
| `--duration` | `4`, `6`, or `8` |
| `--quality` | `high` (default for production), `fast` (draft only) |
| `--wait` | Block until generation complete |
| `--wait-timeout` | Max wait time. Use `12m` for Veo — it can take 6–10 minutes |

> ⚠️ **Critical:** Veo uses `--image` not `--start-image`. The `--start-image` flag is for other models. Using the wrong flag will error or silently ignore your image.

### Cost
- ~22 credits per clip at `--quality high`
- Approximately $0.44/clip at standard credit pricing

---

## FAL API — Fallback Method

Use FAL only if Higgsfield CLI is unavailable.

> ⚠️ **Known issue:** The FAL `fal-ai/veo3/image-to-video` endpoint may return 422 errors. If this happens, retry once. If it fails again, switch to the Higgsfield CLI.

```python
import fal_client
import os

result = fal_client.run(
    "fal-ai/veo3/image-to-video",
    arguments={
        "prompt": "YOUR PROMPT HERE",
        "image_url": "https://... or file://...",
        "aspect_ratio": "9:16",
        "duration": "4",
    }
)

video_url = result["video"]["url"]
# Download the MP4
import urllib.request
urllib.request.urlretrieve(video_url, "output/clip.mp4")
print(f"Saved to output/clip.mp4")
```

---

## Workflow

```
Step 1 — Read the brief
  Identify: subject, action, style, camera, mood, audio, start image (if any).

Step 2 — Compose prompt
  Start with CHARACTER + ACTION-VERB in the first 8 words.
  Add: camera motion, lighting, style, mood, audio direction.
  Check: no banned vocabulary. All motion verbs active and specific.

Step 3 — Review start image (if provided)
  If a start image is provided, it will be passed via --image to anchor the first frame.
  Note: the model will animate FROM this image — ensure it matches the intended scene.

Step 4 — Run generation
  Use Higgsfield CLI (preferred).
  Set --wait and --wait-timeout 12m.
  If Higgsfield fails, try FAL API.

Step 5 — Download and verify
  Confirm MP4 downloaded to output directory.
  Check: does clip match the intended subject + action?
  Check: is there any label/text fabrication on product?
  Check: is duration correct?

Step 6 — Log the generation
  Note the prompt used, model, duration, quality, cost, output path.
  If clip needs to be regenerated, note what to change in the prompt.
```

---

## Output

- `output/[clip-name].mp4` — Generated clip
- Log entry (optional): prompt, model, duration, quality, credits used, timestamp

---

## Common Issues and Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| Clip ignores prompt | Using `veo-3-1-fast` (rewrites prompts) | Switch to `veo-3-1-preview` |
| Label text is garbled | Prompted 360 rotation or close text read | Use camera-only motion on locked subject |
| `--image` flag ignored | Wrong flag name | Use `--image` not `--start-image` for Veo |
| FAL returns 422 | Known API instability | Retry once; fall back to Higgsfield CLI |
| Clip is too short for edit point | Hit Veo's 4s minimum | Generate at 4s; trim in post |
| Generation times out | Veo can take 6–10 min | Set `--wait-timeout 12m` |

---

## Prompt Template

```
[SUBJECT] [ACTION-VERB] [OBJECT], [camera motion], [lighting description], [visual style], [mood], [audio]
```

### Example prompts

**Product B-roll (camera motion only):**
```
Glass dropper bottle SITS on white quartz surface, camera DRIFTS slowly left on slider, warm afternoon backlight RIMS the glass, commercial skincare photography, clean and premium feel, soft ambient room tone
```

**Lifestyle / UGC:**
```
Young woman REACHES into medicine cabinet and PULLS out a small amber bottle, handheld camera FOLLOWS her hand, warm bathroom vanity light, candid UGC style, morning routine energy, natural ambient sound
```

**Transformation B-roll:**
```
Woman's face in close-up TILTS toward camera light, camera PUSHES IN slowly, radiant skin under soft window light, editorial beauty photography, confident and luminous mood, no dialogue
```

---

## Environment Variables

```bash
# Required (one of these)
HIGGSFIELD_API_KEY=your_higgsfield_api_key
FAL_KEY=your_fal_api_key
```

---

## Example Kickoff Prompt

```
I need to generate a 4-second product B-roll clip for a skincare serum.

Subject: A 30ml amber glass dropper bottle
Action: Sitting on white marble, camera drifting left
Style: Commercial skincare photography, clean and premium
Camera: Slow slider push left, camera only — no product rotation
Mood: Warm, luminous, premium morning feel
Audio: Soft ambient room tone
Aspect ratio: 9:16
Duration: 4 seconds
Start image: product-reference.jpg

Please compose a verb-led prompt following all rules in SKILL.md (no banned vocab, camera-only motion for product), then run the Higgsfield CLI and save the output to output/product-broll-01.mp4.
```
