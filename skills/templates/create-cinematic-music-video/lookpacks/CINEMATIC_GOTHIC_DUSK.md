---
look_pack_id: CINEMATIC_GOTHIC_DUSK
when_to_pick: Gothic cinema, candlelight + mist, twilight forest, formal-wear figures, period drama, hunt/feast register. Anywhere the brief needs Yorgos Lanthimos or Robert Eggers cinematic gravity — not warm-cream lifestyle.
---

# CINEMATIC_GOTHIC_DUSK — look pack

The `render_keyframes.py` script reads the two fenced blocks below — the first
is injected at the head of every tableau prompt, the second at the tail.

## STYLE_OPENER

```
A cinematic 35mm film photograph shot on Kodak Vision3 500T tungsten
emulsion, pushed one stop. Deep deep shadows, candle-amber highlights,
visible silver-halide film grain, soft halation around practical light
sources. Anamorphic-lens-like vertical flare on highlights. Locked camera
or slow dolly only — no smooth glide, no AI float. The world is a misty
European twilight forest or a candlelit interior — never sunlit, never
bright. Composition: nearly symmetrical with an intentional small offset.
Cinematic gravity in the manner of Robert Eggers or Yorgos Lanthimos —
formal, slightly absurd, deeply dim.
```

## NEGATIVE_TAIL

```
AVOID: studio-glossy AI render, smoothed AI skin, fashion-magazine
airbrush, bright sunny day, blue sky, beach, suburb, daytime, modern
office, neon, tropical, sports stadium, plastic-toy aesthetic. AVOID
rendered text, captions, words, signs, labels, hex codes, color swatches,
design-mockup chrome, multiple panels, contact-sheet grids. Vertical 9:16
composition.
```

## Palette anchors (cinematographer brief)

- **Candle-amber** (#C99A4E) — practical light source, primary warm
- **Ivory** (#E8DCC0) — formal-wear linens, candles, fog
- **Iron-black** (#0E0B08) — deepest shadow, never pure black
- **Oxblood** (#6E1F1F) — brand accent, velvet drapery
- **Forest-dusk green** (#2A3D2E) — birch / pine, moss
- **Cold-blue mist** (#5A6D7A) — fog, distant atmosphere, never bright

## Music structure default

- BPM 72–84 (build via instrumentation, not BPM)
- Cinematic gothic-folk orchestral — cello + viola lead, low strings, soft harpsichord
- A single wordless female vocal floats over the strings, restrained
- Verse: solo cello + harpsichord
- Pre-chorus: viola + cello + vocal hum enters
- Chorus: full strings + sung vocal hook
- Outro: solo cello + harpsichord with vocal whisper

## Caption style (set these in concept.caption_overrides)

- `font`: serif (Cormorant Garamond / Georgia fallback)
- `font_size`: 60
- `placement`: low (lower-third)
- `chunk_size`: 3 (cinematic-gravity short cuts)
- `accent_hex`: candle-amber (#C99A4E)

## Anti-AI tells (load-bearing)

- Silver-halide film grain visible at full resolution — DO NOT smooth
- Halation around candle / lantern / window light
- Practical light only — every source diegetic (no AI key + fill)
- Real skin texture, deep face shadows, NEVER airbrushed
- Mist + atmosphere read as real depth, not a cheap filter
- Formal-wear fabric texture preserved (velvet, silk, wool)

## Common keyframe patterns by role

| Tableau role | Default pattern |
|---|---|
| INTRO | Wide locked exterior — manor, cathedral, mist at twilight |
| PERSONAL_BEAT | Black-gloved hand or formal forearm, prop reveal |
| WIDE_ENSEMBLE | Formal-dressed group walking through fog / forest, lanterns |
| KINETIC_CLOSE | Profile or back-of-head in candlelight, breath visible |
| SUSPENDED_TIME | Fog parts; a held cinematic clearing |
| HOOK_HERO | A glowing window in the dark — the destination |
| PRODUCT_HERO | Plated subject in candlelight, the object of the hunt |
| ORIGIN_WINK | Engraved plaque, family crest, gothic-script Easter egg |
| TWILIGHT_OUTRO | Dawn light leaking into a dark interior, empty chairs |
| END_CARD | Single candle + clean dim backdrop, no text (wordmark composited in build_endcard.py) |
