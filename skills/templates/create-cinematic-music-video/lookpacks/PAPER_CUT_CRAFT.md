---
look_pack_id: PAPER_CUT_CRAFT
when_to_pick: Y2K, candy-coded, women's CPG / wellness / beverage, kids-adjacent, hand-craft energy, magazine-spread aesthetic. Brands whose visual signature is bold colors + visible craft.
---

# PAPER_CUT_CRAFT — look pack

The `render_keyframes.py` script reads the two fenced blocks below — the first
is injected at the head of every tableau prompt, the second at the tail.

## STYLE_OPENER

```
A saturated PAPER-CUT COLLAGE tableau. Layered cut-paper construction-paper
shapes with visible scissor-cut edges and crisp paper shadows. Bright Y2K
tween-magazine palette (hot pink, cream, candy colors). Hand-drawn ink
doodles (sparkles, stars, hearts) accent the composition. The character is
a PAPER-DOLL figure — flat cut-paper silhouette with cut-paper hair and
limbs, NOT a photoreal human, NOT a 3D render, NOT an illustration.
```

## NEGATIVE_TAIL

```
NO photoreal humans, NO photorealism, NO 3D render, NO AI-illustration
look, NO smooth digital painting, NO oil-painting look. AVOID rendered
text, captions, words, signs, labels. Vertical 9:16 composition.
```

## Palette anchors (per-tableau saturated backgrounds)

- **Hot pink** (#F22BB5) — primary brand accent
- **Cream / paper** (#F5EDE0) — neutral
- **Lavender / violet** (#B89EE6)
- **Lime cherry** (#9CCB3B)
- **Butter yellow** (#FFE082)
- **Sky blue** (#A8D5F2)
- **Tropical coral** (#FF7448)
- **Watermelon red** (#E64564)

Each tableau picks ONE background color from the palette. Bright per-frame
contrast is the pack's signature.

## Music structure default

- BPM 120
- Glittery sugar-pop / candy-pop anthem, confident-warm female vocal
- Plucky synths, claps, four-on-the-floor kick
- Verse → hook → outro (more pop-traditional than a full anthem build)

## Caption style (set these in concept.caption_overrides)

- `font`: ALL CAPS display (Bungee / Arial Black portable fallback)
- `font_size`: 64
- `placement`: mid (mid-frame burst)
- `chunk_size`: 3 (pop-burst feel)
- `accent_hex`: the pack primary (#F22BB5)

## Anti-AI tells

- Visible paper-cut edges (the model loves to render these)
- Crisp shadow under each paper layer
- Hand-drawn ink doodles (marker-line caveats)
- No smooth digital paint
- Saturated flat color (no airbrushed gradients)

## Common keyframe patterns by role

| Tableau role | Default pattern |
|---|---|
| INTRO | Paper-doll figure on a saturated paper bg, hero product mid-frame |
| WIDE_ENSEMBLE | 3-4 paper-doll figures in a row, each with a product variant |
| HOOK_HERO | 4-quadrant split, a paper-doll in each holding a SKU |
| KINETIC_CLOSE | Paper-doll smile / wink, sparkle doodles burst around |
| PRODUCT_HERO | Single product centered, paper halo + ink stars |
| END_CARD | Clean paper-cut backdrop, no text (wordmark composited in build_endcard.py) |
