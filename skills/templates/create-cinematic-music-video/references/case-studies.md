# Case studies — what the format is validated on

This skill was extracted from three production music-video spots across two
brands (a college-apparel label and a Y2K wellness-beverage label). The runs
are summarised here as archetypes — the point is the lessons, which are baked
into the pipeline and the look packs.

---

## Run A — warm-day apparel anthem (`KODAK_PORTRA_DAY`)

| | |
|---|---|
| Brand type | College / lifestyle apparel |
| Spec | 9:16, 28s, ~25 MB |
| Look pack | `KODAK_PORTRA_DAY` |
| Music | Indie-pop anthem, 120 BPM, female lead, cinematic strings |

**What it taught the molecule.**

- **14-tableau narrative arc beats an 8-tableau montage.** The earlier cut was
  a montage; it read as generic AI music-video slop. Assigning each of 14 slots
  a *narrative role* (intro → energy → reflection) is what made it feel authored.
- **Lower-third serif captions** read as cinematic, not as a TikTok meme.
- **An origin-wink tableau** (a small brand-history Easter egg around tableau
  12) gives the spot a second watch and rewards fans.

---

## Run B — neon-night apparel anthem (`CINESTILL_800T_NIGHT`)

| | |
|---|---|
| Brand type | College / lifestyle apparel (same brand, new campaign) |
| Spec | 9:16, 28s |
| Look pack | `CINESTILL_800T_NIGHT` |
| Music | Indie-electronic, 125 BPM, female vocal grit, stadium drum |

**What it taught the molecule.**

- **The look pack is the swap point.** Same molecule, same 14-role structure,
  a completely different finished product — warm day vs. neon night — by
  changing one field. Halation + cool palette did all the work.
- **Campaign series share a chorus.** When you run a series (Run 01 → Run 02),
  keep the chorus + outro identical and change only the verse + tableaux. The
  repeated hook is what makes a series feel like one campaign.
- **Beat timings vary per song.** ElevenLabs never lands exactly on the spec —
  the hook drifts a few hundred ms. The TIMELINE is always recomputed per run
  from the actual word timestamps. Never hard-code timings.

---

## Run C — craft-pop CPG anthem (`PAPER_CUT_CRAFT`)

| | |
|---|---|
| Brand type | Y2K wellness / beverage CPG |
| Spec | 9:16, 20s, ~19 MB |
| Look pack | `PAPER_CUT_CRAFT` |
| Music | Glittery candy-pop, 120 BPM |

**What it taught the molecule.**

- **Word-burst captions (3-word chunks, mid-frame)** fit a candy-pop CPG spot,
  where the cinematic 4-word lower-third fits apparel. Caption style is part of
  the look pack, not a global constant.
- **Saturated paper-cut craft reads as deliberately made, not AI-rendered** —
  the visible scissor edges and crisp paper shadows are the anti-slop tell.
- **Object-hero framing** ("Hero subject: the product on a saturated paper
  background") keeps the image model out of NSFW false-flags and off
  hallucinated faces.

---

## Cross-run lessons (encoded in the pipeline + look packs)

1. **Original anthem with word timestamps is the whole game.** The word-level
   timestamps are what let every cut land on a vocal beat. That is the
   difference between "music video" and "stock music with cuts."
2. **One look pack per run.** Mixing aesthetics across tableaux breaks the
   through-line that makes the spot read as a single ad.
3. **Never AI-render brand text.** The end-card wordmark/tagline are PIL-typeset
   (`build_endcard.py`); the END_CARD tableau is a clean, text-free backdrop.
4. **Object-hero / scene framing, not "a young woman who…".** Safer prompts,
   cleaner compositions, fewer false rejections.
5. **Suppress nothing on the beat.** The cheapest review surface is the
   storyboard, then the single T01 keyframe — gate there, before the paid batch.
