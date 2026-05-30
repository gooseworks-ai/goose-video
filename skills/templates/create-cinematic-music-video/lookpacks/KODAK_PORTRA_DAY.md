---
look_pack_id: KODAK_PORTRA_DAY
when_to_pick: Warm afternoon, autumn / late-summer, golden hour, lifestyle, tailgate, campus, beach, outdoor lifestyle. Warmth without going sweet.
---

# KODAK_PORTRA_DAY — look pack

The `render_keyframes.py` script reads the two fenced blocks below — the first
is injected at the head of every tableau prompt, the second at the tail.

## STYLE_OPENER

```
A cinematic 35mm film photograph shot on Kodak Portra 400. Visible film
grain, warm color profile, slightly blown highlights, soft light leaks
bleeding from the corners, a faint diagonal lens flare. Handheld framing —
not perfectly leveled, lived-in documentary composition. Late afternoon
golden hour light. Cinematic indie-film mood, like a still from an A24 short.
```

## NEGATIVE_TAIL

```
AVOID: studio-glossy AI render, smoothed AI skin, fashion-magazine
airbrush, perfectly symmetric AI faces, plastic-skin look, oversaturated
Instagram filter, sterile lighting, perfect studio backdrop. AVOID rendered
text, captions, words, signs, labels. Vertical 9:16 composition.
```

## Palette anchors (cinematographer brief)

- **Honey gold** (#C99A4E) — primary warm
- **Brand-color pops** — the brand's two strongest accent hues, used sparingly
- **Cream / dust** (#F5EDE0) — neutral
- **Sepia-warm shadows** — not black, brown-shifted
- **Ink** (#1A1612) — deep brown-black, never pure black

## Music structure default

- BPM 120
- Indie-pop anthem with cinematic strings + female lead vocal
- Verse: piano + light kick, intimate
- Pre-chorus: drum builds in, strings rise
- Chorus: full band + cinematic build, hook on the one
- Outro: stripped back to acoustic guitar + vocal

## Caption style (set these in concept.caption_overrides)

- `font`: serif (Georgia portable default; New York / Caslon on macOS)
- `font_size`: 64
- `placement`: low (lower-third)
- `chunk_size`: 4 (cinematic, not pop-burst)
- Accent words rendered bold-italic

## Anti-AI tells (load-bearing)

- Film grain visible at full resolution — DO NOT smooth
- Light leak / diagonal lens flare on hero frames
- Handheld micro-imperfection (≤2° tilt)
- Out-of-focus background bokeh
- Real interior set dressing (posters, polaroids, lived-in clutter)
- Skin texture preserved, NOT airbrushed

## Common keyframe patterns by role

| Tableau role | Default pattern |
|---|---|
| INTRO | Hero object on hanger / table, morning side-light, dust motes |
| PERSONAL_BEAT | Two friends in a doorway / mirror, warm interior |
| WIDE_ENSEMBLE | A group walking down a street toward camera, golden-hour flare |
| KINETIC_CLOSE | Close-up mid-cheer / laugh, motion blur |
| SUSPENDED_TIME | Slow-mo confetti / streamers in brand colors |
| HOOK_HERO | 4-quadrant split, each panel a brand-color mini-shot |
| PRODUCT_HERO | Product alone on hanger in moody warm side-light |
| ORIGIN_WINK | Retro-coded set dressing, slight VHS warmth, heavier grain |
| TWILIGHT_OUTRO | Silhouettes against an orange sky walking out |
| END_CARD | Clean warm backdrop, no text (the wordmark is composited in build_endcard.py) |
