---
look_pack_id: CINESTILL_800T_NIGHT
when_to_pick: Night, winter, indoor venues, urban, neon, nightlife, arenas, after-hours. Energy with edge — not warmth.
---

# CINESTILL_800T_NIGHT — look pack

The `render_keyframes.py` script reads the two fenced blocks below — the first
is injected at the head of every tableau prompt, the second at the tail.

## STYLE_OPENER

```
A cinematic 35mm film photograph shot on CineStill 800T tungsten-balanced
film. High ISO grain (heavier than daytime film), halation rings around
bright light sources, slight magenta-purple shift in shadows, sodium-lamp
amber pools spilling onto cool indigo dark. Handheld framing — not perfectly
leveled, lived-in night documentary composition. Urban winter night — brick,
snow, street lamps, neon signage glowing through frosted windows. Cinematic
indie-noir mood, like a still from a neon-night A24 short.
```

## NEGATIVE_TAIL

```
AVOID: studio-glossy AI render, smoothed AI skin, fashion-magazine
airbrush, perfectly symmetric AI faces, plastic-skin look, oversaturated
Instagram filter, sterile lighting, perfect studio backdrop, daylit
exterior, golden-hour warmth. AVOID rendered text, captions, words, signs,
labels. Vertical 9:16 composition.
```

## Palette anchors

- **Deep indigo / navy** (#1F2342) — primary cool base
- **Neon magenta / hot pink** (#E63878) — primary accent, halated
- **Sodium amber** (#E08038) — warm street-lamp pools
- **Brand-color pops** — the brand's strongest accent hue
- **Fluorescent purple-white** — interior arena / venue tone
- **Inky cool-black** (#0B0C12) — pure shadows

## Music structure default

- BPM 125
- Indie-electronic anthem with female vocal grit
- Verse: dark synth pad foundation, light kick
- Pre-chorus: drums punch in, synth build, anticipation
- Chorus: full electronic-band drop, big stadium drum, electric-guitar bite
- Outro: stripped back to synth pad + vocal

## Caption style (set these in concept.caption_overrides)

- `font`: serif (campaign consistency with KODAK pack)
- `font_size`: 60 (smaller — text reads larger on a darker background)
- `placement`: low (lower-third)
- `chunk_size`: 4
- `accent_hex`: the neon magenta accent (#E63878) for bold-italic accent words

## Anti-AI tells

- Halation rings around every bright light source — DO NOT remove
- Heavier grain than KODAK_PORTRA_DAY (higher ISO)
- Visible breath in cold-air scenes
- Snow specks if winter exterior
- Real interior venue clutter (posters, fences, seating)
- Magenta cast in shadows (not neutral / not warm)

## Common keyframe patterns by role

| Tableau role | Default pattern |
|---|---|
| INTRO | Hero garment in a room at night, desk-lamp warm pool, neon through window |
| PERSONAL_BEAT | Coat opening to reveal product, cold breath, neon spill behind |
| WIDE_ENSEMBLE | Group walking a snowy path under street lamps |
| KINETIC_CLOSE | Cheer close-up in a venue, fluorescent purple, halation |
| SUSPENDED_TIME | Slow-mo confetti in cool neon colors (no gold) |
| HOOK_HERO | 4-quadrant split across four night settings |
| PRODUCT_HERO | Product on hanger in tungsten side-light, magenta rim |
| ORIGIN_WINK | Period-coded interior, the origin object in hand |
| TWILIGHT_OUTRO | Silhouettes under sodium-lamp pools, breath visible |
| END_CARD | Clean tungsten-lit backdrop, no text (wordmark composited in build_endcard.py) |
