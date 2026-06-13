---
name: imessage-video-ad
description: Produce a 9:16 social-native ad that recreates an iMessage conversation reveal — bubbles pop in over time, composer types char-by-char, real Apple iMessage SFX hit on every send/receive, music bed underneath, brand end card with a FREEPACK-style CTA code. One continuous Playwright recording (no scene-cuts/glitches), assembled to a master MP4 plus 9:16 / 1×1 export variants.
---

# imessage-video-ad

Use this skill when an ad concept calls for an authentic iMessage thread reveal: someone screenshots a product/result, sends it to a friend, the friend reacts and asks what app/service it is, and the conversation surfaces the brand + a CTA code.

Everything this skill needs is bundled in this folder — the iMessage HTML renderer (`scripts/generate.js` + `scripts/templates/`), both end-card templates, the Apple SFX (`assets/sfx/`), and the example thread/timeline. No external skill dependencies.

## Setup (once)

```bash
npm install                       # Playwright
npx playwright install chromium   # browser binary
pip install -r requirements.txt   # FAL client (flat-lay background step only)
cp .env.example .env              # add FAL_KEY if generating the flat-lay bg
```

`ffmpeg` and `ffprobe` must be on your PATH. All scripts run **in place** and take a `--project <dir>` so one copy of the skill drives many ads.

## Output format — FRAMED (Variant B) is the standard

Renders the **framed** look by default: a visible iPhone bezel + Dynamic Island + status bar, sitting on a flat-lay desk background (1080×1920). The old **full-bleed** (edge-to-edge chat) look is **DEPRECATED** — reachable only via `--full-bleed` for backward reproduction.

Framed requires a background at `<project>/assets/flat-lay-bg.jpg` — generate it with `scripts/gen_flat_lay_bg.py` (State 3.5) or supply your own. Dark threads (`theme: "dark"`) render dark natively in frame mode, so no manual theme injection is needed.

## When to use

- Reaction/discovery ads where the punchline is the *recipient's* curiosity ("what app is that?", "wait this is real?")
- Promo-code reveals (FREEPACK / FIRSTPACK / WELCOME10) — the conversational delivery feels far less ad-like than a hard CTA card alone
- Any time the brief mentions "fake DM", "screenshot of a chat", "iMessage style", "Tyler/peer"

This skill is for a **multi-bubble timeline animated to video**. If the chat is just one static beat (a single screenshot), you don't need video — render the HTML once and screenshot it.

## Inputs

1. **`brief`** (required) — what the ad is selling, the CTA code, the peer's name (e.g. "Tyler"), the screenshot subject
2. **`project`** — a working directory for this ad (holds `threads/`, `timeline.json`, `assets/`, `audio/`, outputs)
3. **`peer_persona`** — name + 2-letter monogram + avatar bg color (hex)
4. **`screenshot_asset`** — the image that gets sent in the first attachment bubble
5. **`bubbles`** — the conversation, authored into `threads/full-thread.json`
6. **`timeline`** — event schedule authored into `timeline.json` (composer drives, typing, pops, scrolls, SFX)
7. **`end_card`** — real brand logo SVG + offer line + code
8. **`music`** — a lofi/hip-hop loop at `<project>/audio/music-bed.mp3`

The `full-thread.json` schema is the iMessage-mockup schema (see `examples/full-thread.example.json`), extended with `theme: "dark"`, a conversation header, attachment bubbles, and inline `[[link:CODE]]` markers.

## Critical knowledge — read before producing your first ad

These are mistakes that have already been made and fixed in production builds. Do not re-introduce them.

### 0. Use the real brand wordmark on the end card, never styled text

CSS approximations of brand wordmarks look amateur even when typeface and kerning are close. Drop the official SVG at `<project>/assets/brand-logo.svg` (sources: Wikimedia Commons, `brandfetch.com/<brand>.com`, brand press kit) and pass it via `--logo`. `scripts/render-end-card.js` injects it into the `<!--{{BRAND_LOGO_SVG}}-->` placeholder. Your only job is to color the paths. See `references/end-card-recipe.md`.

### 1. Use the real Apple iMessage SFX, not generic notification sounds

**The "iMessage feel" is 70% the SFX.** Generic notification sounds break the illusion immediately. The Apple sounds are CC0 (from BigSoundBank) and pre-bundled, loudness-normalized to ~-9 LUFS / peak 0dB, at:

- `assets/sfx/imessage-send.mp3` — Apple "Message Sent"
- `assets/sfx/imessage-receive.mp3` — Apple "Note", trimmed to 1.4s with a 400ms fade-out

`stitch.sh` reads these automatically. Reuse them — don't re-download.

### 2. NEVER play SFX on the typing indicator

The typing-dots bubble appearing is a **silent state change** — iOS does not chime when someone starts typing. Only fire `receive` SFX when the *actual text bubble* lands (i.e. on `typing-swap`). In `timeline.json`, every `typing-pop` event must have `sfx: null`.

### 3. Record the entire chat as ONE continuous Playwright session

Do **not** record scene-by-scene and concat — every page reload causes a micro-flicker, and "scrolling" has to be faked by removing older bubbles (which looks janky). `scripts/record-master.js` implements the continuous pattern: render the full thread with every message `data-pending` (hidden), then a single embedded driver walks the timeline on `requestAnimationFrame`, unhiding + popping each event on schedule, with custom-eased auto-scroll. SFX cues are computed **deterministically from the timeline** (never via `performance.now()` inside the page — it races `setContent`'s load event and drops cues).

### 4. Pop-pending must remove rows from layout, not just hide them

If pending only set `opacity: 0`, every bubble pre-allocates its height at frame 0, so the auto-scroll has nothing to scroll to and bubbles "pop into pre-allocated holes" instead of arriving. The bundled `chat.css` uses `display: none` via `data-pending="1"` so the conversation grows naturally:

```css
.row[data-pending="1"], .delivered-caption[data-pending="1"] { display: none !important; }
```

### 5. End card stays static — no Ken-Burns, no zoom-pan

The brand slate must land hard. `render-end-card.js` ffmpeg's the PNG to a fixed-frame MP4 at the framed 1080×1920 (no zoompan). `stitch.sh` scales the end card to the chat's resolution and crossfades chat → end card with a **300ms** `xfade` (longer feels mushy, shorter feels like a hard cut).

### 6. ffmpeg amix divides by N inputs by default

If you `amix` music + silent base + N SFX without `normalize=0`, every input is divided by the count and the audio sounds mysteriously quiet. The bundled `stitch.sh` uses `amix=inputs=N:duration=first:dropout_transition=0:normalize=0` then `volume=2.5,alimiter=limit=0.95`. See `references/audio-recipe.md`.

### 7. Music bed: lofi/hip-hop, 60Hz highpass, ~-10dB

Keep the bed unobtrusive — `volume=0.30` + `highpass=f=60`, fading out 1.5s before the end so the CTA reveal lands in (relative) silence. Supply your bed at `<project>/audio/music-bed.mp3` (any ~80–95bpm no-vocal loop).

### 8. Hook screenshot — render it locally, mimic the real app

Most iMessage hooks are screenshots of *some other app* (Strava, a cancellation email, a card-grade summary). Generating these via AI is overkill and unreliable. Write an HTML file that mimics the real app's UI and screenshot it with Playwright. Mimic the *actual UI patterns* (brand strip, real stats grid, "Public · 2h ago"), not just the vibe — abstract gradients read as AI slop. See `examples/strava-card.example.html`.

### 9. Pacing curve — not flat 700ms gaps

Real iMessage banter has rhythm: one-word reactions 250–450ms apart; sentence reveals 600–900ms; a ~600ms beat of silence before the final reaction so it lands. The timeline in `examples/timeline.example.json` is a good starting point — adjust event times rather than redesigning.

## Concept catalog

Most iMessage ads fit one of these six angles. Strongest hooks: a specific number, a small act of self-trust, or a physically novel product mechanic.

| Angle | Hook (the attachment) | Reveal |
|---|---|---|
| **Result-as-screenshot** | a number that brags by itself — race time, app summary, dashboard, FTP score | "X mins a day. that's it." |
| **Setup flex** | photo of your space — tiny apartment, race-kit corner, home gym in a closet | "this is the whole gym" |
| **Cancellation moment** | confirmation receipt — gym cancellation email, subscription cancelled page | "$X → $Y, do the math" |
| **Feature-as-punchline** | short clip of the feature in motion — rotating screen, transforming product | the mechanic *is* the brand |
| **Friend-asks-friend (inverse)** | the peer initiates with the wow — "how are you doing this 😭" | you reply with the brand |
| **Receipt-as-hook** | mundane financial document — credit-card statement, App Store receipt | small act of self-trust |

Pick the strongest angle for the brand voice *before* writing copy. Most "the script is fine but feels off" feedback comes from picking the wrong angle. Catching that here is 30 seconds; catching it after recording is 30 minutes.

## End-card variants — which to pick

Pick by brand voice, not aesthetic preference. See `references/end-card-recipe.md`.

| `--variant` | Template | When to pick |
|---|---|---|
| `glow` (default) | `scripts/end-card.html` (abstract glow + product) | Brand voice is playful or product-led. Hook is a *thing*. |
| `photo-bg` | `scripts/end-card-photo-bg.html` (athlete/persona photo) | Brand voice is grounded or lifestyle-led. Hook is a *person*. Requires `--hero`. |

## Workflow

### State 0 — Brainstorm angles (skip only if direct port of a reference)

Generate 4–5 concept angles from the catalog. For each: one-line hook (what gets screenshotted), an 8–14 bubble script as a markdown table, why it works in one sentence. Show the menu; lock the angle before writing the full script.

### State 1 — Capture the script + screenshot asset

Write (or transcribe from a reference) the verbatim text of every bubble, who sends each, where typing indicators belong, the composer-text snippets, and the exact CTA code. Render the hook screenshot locally (knowledge #8) into `<project>/assets/`.

### State 2 — Build `threads/full-thread.json`

Use `examples/full-thread.example.json` as the template. Key fields:

- `theme: "dark"` (mandatory for this format)
- `header.style: "conversation"` and `header.unread: <number>` (the unread badge)
- First message is usually `{type: "attachment", from: "me", src, title, subtitle}` — the screenshot the chat is about
- Inline `[[link:CODE]]` markers where iOS would auto-detect a code/email/URL — they render with the link-detector underline

### State 3 — Define `timeline.json`

Copy `examples/timeline.example.json` to `<project>/timeline.json` and adapt it. The `events` array is the **single source of truth** for both the recording schedule and the SFX cue list. `t` is absolute seconds. Kinds: `pop`, `typing-pop` (always `sfx: null`), `typing-swap` (`sfx: 'receive'`), `composer`, `composer-clear`, `scroll`, `noop`. Full reference: `references/timeline-schema.md`.

### State 3.5 — Generate the flat-lay background (framed default)

```bash
python3 scripts/gen_flat_lay_bg.py --project ./my-ad      # FAL gpt-image-1, ~$0.19
```

Drop a brand-specific prompt at `<project>/flat-lay-prompt.txt` to override the default desk (keep the empty-center rule). Or supply your own `<project>/assets/flat-lay-bg.jpg` and skip this step.

### State 4 — Record + end card + stitch

```bash
# 1) Record the chat as ONE continuous video → clips/master-chat.mp4 + .sfx.json
node scripts/record-master.js --project ./my-ad

# 2) Render the end card (static) → clips/scene-09-endcard.mp4
node scripts/render-end-card.js --project ./my-ad --logo ./my-ad/assets/brand-logo.svg
#    photo-bg variant: add  --variant photo-bg --hero ./my-ad/assets/hero.png

# 3) Stitch chat + end card with crossfade + music + SFX → edits/master-final.mp4
bash scripts/stitch.sh ./my-ad
```

### State 5 — Export variants

```bash
ffmpeg -y -i ./my-ad/edits/master-final.mp4 -vf "scale=1080:1920:flags=lanczos" \
  -c:v libx264 -pix_fmt yuv420p -c:a copy -movflags +faststart ./my-ad/meta-upload/master-9x16-1080.mp4
ffmpeg -y -i ./my-ad/edits/master-final.mp4 -vf "crop=720:720:0:280" \
  -c:v libx264 -pix_fmt yuv420p -c:a copy -movflags +faststart ./my-ad/meta-upload/master-1x1-720.mp4
```

### State 6 — Review

Play the master against the brief. Re-time individual events by editing `timeline.json` and re-running step 4.1 — no other steps need re-running.

## Quality checks

Before declaring the ad shippable:

- [ ] **FRAMED:** the iPhone bezel + Dynamic Island + status bar are visible, the chat sits inside the phone screen, the flat-lay desk shows around it (NOT full-bleed). Output is 1080×1920.
- [ ] Audio peaks at 0dB (`ffmpeg -af volumedetect`); mean roughly -10 to -12dB
- [ ] **No SFX on any `typing-pop`** — verify in `clips/master-chat.sfx.json`
- [ ] No micro-flicker — only ONE cut in the whole video: chat → end card (crossfade)
- [ ] All bubbles popped in script order; composer types and clears per `composer` event (no ghost text after a send)
- [ ] The CTA code is link-detector underlined in its bubble (`[[link:CODE]]` marker present)
- [ ] End card is **static** — no Ken-Burns drift
- [ ] Chat→end-card crossfade is 300ms; the last bubble gets ~600ms to breathe first

## Failure modes — and the fix

| Symptom | Cause | Fix |
|---|---|---|
| Glitchy / micro-flicker between bubbles | Recorded scene-by-scene with reloads | Use the continuous `record-master.js` (one session, one timeline) |
| SFX too quiet, audio weak | `amix` divided by N inputs | `:normalize=0` on amix + `volume=2.5,alimiter=limit=0.95` (already in `stitch.sh`) |
| Bubbles pre-allocate space, conversation doesn't grow | Pending hid via `opacity:0` not `display:none` | Use `data-pending="1"` → `display:none` (already in `chat.css`) |
| End card drifts / feels like filler | Ken-Burns zoompan | Use the static `scale=720:1280` invocation in `render-end-card.js` |
| Typing dots flash for 1 frame and skip | typing-pop → typing-swap gap too short | Hold ~700–1000ms between them |
| CTA code not underlined | Missing `[[link:CODE]]` marker | Wrap the code/email/URL in the marker in `full-thread.json` |
| Receiver avatar clipped at viewport top | conv-header stack overflows when `position: fixed` | The full-bleed `styleOverride` pads the header to `min-height: 110px` and anchors `.center` from `top: 14px`. Don't shrink without re-testing. |
| End-card logo looks like styled text | Used a CSS fallback instead of the real SVG | Drop the real SVG and pass `--logo`; the renderer injects it |
| Hook screenshot looks like AI slop | Abstract gradient instead of the real app's UI | Mimic the actual app — see `examples/strava-card.example.html` |

## Reference flows

Two production builds validated this format. Both share the same recorder, stitch script, renderer, and SFX — the only differences are the four parameters the templates expose (end-card variant, brand logo SVG, hook asset, and the timeline):

- **Playful / product-flex** — abstract-glow end card, gray peer avatar, screenshot-of-a-thing hook (e.g. a graded card with a price). ~20s.
- **Grounded / result-flex** — photo-background end card with a real wordmark, indigo peer avatar, a locally-rendered app-summary hook (e.g. a Strava finish-line card). ~19s.
