---
name: create-cinematic-music-video
description: Make a 9:16 ~20-30s cinematic music-video ad for any brand from a single concept.json. An original anthem with real sung vocals and word-level timestamps drives 14 beat-locked tableaux (a 3-act arc, not a montage), each rendered as a still then animated to a clip, with a PIL-typeset end card and burned word-synced captions. Use when the user wants a paid-social spot where craft + emotional arc beat a lookbook montage — fashion, apparel, beverage, lifestyle, CPG, wellness — and original (not licensed) music is fine. Uses FAL (nano-banana for stills, Seedance Pro for image-to-video) and the ElevenLabs Music API. The aesthetic swaps via interchangeable "look packs" (Kodak Portra warm-day, CineStill neon-night, paper-cut craft, gothic dusk). ~$15-25 in API spend per cut, ~15-30 min wall time plus two human review gates.
---

# create-cinematic-music-video

A guided workflow for producing a beat-locked cinematic music-video ad. The
user gives a free-form brief ("make a music-video ad for Aurelia, a running
brand, warm 35mm, the campaign is 'every morning is a comeback'"); you turn it
into a `concept.json`, then walk the pipeline phase-by-phase, pausing at two
human gates so the user catches drift before paying for the full gen batch.

## When to use this skill

Use when the user asks for:
- "Make a music-video ad" / "cinematic spot with an original song" / "an anthem
  ad" / "a beat-synced brand film."
- A brand with cultural ownership of a setting or moment (a tailgate, a 3pm
  energy slump, a summer Friday, a morning run) where the payoff is *emotional*,
  not a feature callout.
- A 20-30s 9:16 paid-social spot (TikTok / Reels / Shorts / Pinterest video).
- A spot where **original** music is acceptable (this skill generates the song).

Do NOT use for:
- UGC talking-head / selfie-cam ads → a different skill.
- Personified-villain cartoon explainers → use `animated-explainer-ad`.
- Pure typography / kinetic motion graphics → a different skill.
- Photoreal product demos or before-after → a different skill.
- Anything that **requires a licensed track** (this skill makes an original).

## The format — three load-bearing pillars

1. **Original anthem with word-level timestamps.** The ElevenLabs Music API
   (`/v1/music/detailed`, `with_timestamps: true`) returns the sung audio *and*
   ~60-90 word-level time anchors per ~28s song. Every visual cut lands on a
   vocal beat. This is the difference between "music video" and "stock music
   with cuts."
2. **14-tableau structure with assigned narrative roles.** Not a montage — a
   3-act arc (anticipation → energy → reflection). Each tableau has a job
   (intro / wide / kinetic-close / hook / product / origin / outro). The
   structure is what separates this from generic AI-music-video slop.
3. **The look pack is the aesthetic swap point.** Kodak-Portra warm-day,
   CineStill neon-night, paper-cut craft, gothic dusk — the *same* molecule
   produces completely different finished films by changing one field. Adding a
   new pack is a one-file change, no code.

Output is platform-ready: 1080×1920, 30fps, h264 + aac, loudnorm to -14 LUFS,
captions burned, ~20-30 MB.

## Setup (run once per machine)

```bash
cd skills/templates/create-cinematic-music-video
pip install -r requirements.txt
cp .env.example .env          # then set FAL_KEY and ELEVENLABS_API_KEY
ffmpeg -version               # any ffmpeg works; libass is auto-detected and
                              # imageio-ffmpeg is the bundled fallback for the burn
```

- **FAL_KEY** — nano-banana (keyframes) + Seedance Pro (image-to-video): https://fal.ai
- **ELEVENLABS_API_KEY** — the Music API (anthem + timestamps): https://elevenlabs.io

Surface any missing key/tool before starting — don't proceed with broken tooling.

## Inputs

Everything lives in one run folder. The agent creates it:

```
<project>/
├── concept.json              ← the single source of truth (schema below)
├── source/lyrics-locked.md   ← the locked lyrics (also referenced by concept.json)
└── storyboard.html           ← Gate 2 review surface (you generate it)
```

Copy `examples/concept.json` + `examples/lyrics-locked.md` as a starting point.

## concept.json schema

```jsonc
{
  "brand": "aurelia",                  // slug
  "run_slug": "run-01-comeback",
  "title": "Comeback",
  "campaign": "every morning is a comeback",
  "duration_s": 28,                    // 20-30
  "look_pack": "KODAK_PORTRA_DAY",     // one of lookpacks/*.md
  "vocal_gender": "female",            // "female" | "male" | "any"
  "palette_anchors": ["honey gold", "cardinal red", "cream"],

  "music": {
    "bpm": 120,
    "vibe": "indie-pop anthem, confident-warm female vocal, cinematic strings",
    "structure_note": "piano verse, drums build at pre-chorus, full band chorus, acoustic outro"
  },

  "lyrics_locked_md": "source/lyrics-locked.md",
  "accent_words": ["comeback", "morning", "Aurelia", "rise"],  // bold-italic in captions

  "caption_overrides": { "placement": "low", "chunk_size": 4, "font": "Georgia", "font_size": 64 },
  "endcard": { "wordmark": "AURELIA", "tagline": "every morning is a comeback",
               "url": "aurelia.run", "accent_hex": "#C99A4E", "font_family": "serif" },

  "tableaux": [
    { "id": "T01", "role": "INTRO", "lyric_anchor": "(intro)",
      "prompt": "Hero subject: a folded cardinal-red jersey on a chair at dawn...",
      "motion_hint": "Dust motes drift. The jersey stays still as hero. 5 seconds.",
      "ref": [] }                      // optional brand/product reference images
    // ... 13 more
  ]
}
```

- **prompt** — object-hero / scene composition. Start with "Hero subject:" not
  "A young woman who…". The look pack's STYLE_OPENER + NEGATIVE_TAIL are injected
  automatically — don't repeat them.
- **motion_hint** — subtle, handheld, no smooth glide.
- **lyric_anchor** — the first words of the lyric line this tableau sits on.
  `derive_timeline.py` matches the anchor's first word against the sung words to
  place the cut. Use `(intro)` for the pre-vocal cold open.

### The 14 tableau roles (structure-locked)

| # | Role | What it is |
|---|---|---|
| 1 | INTRO | Cold open, product-hero hint, often pre-vocal |
| 2 | PERSONAL_BEAT_1 | Character + product close beat |
| 3 | PERSONAL_BEAT_2 | Walk-up / movement |
| 4 | WIDE_ENSEMBLE | Group scene wide, flare |
| 5 | KINETIC_CLOSE_1 | Emotional / kinetic close-up |
| 6 | KINETIC_CLOSE_2 | Secondary energy beat |
| 7 | SUSPENDED_TIME | Slow-mo / abstract frozen beat |
| 8 | HOOK_HERO | Chorus drop — quadrant split / hero frame |
| 9 | KINETIC_PEAK | Biggest energy moment |
| 10 | PRODUCT_HERO | Product alone in moody light |
| 11 | MICRO_MONTAGE | Rapid beat-locked 4-cut inside one slot |
| 12 | ORIGIN_WINK | Brand-history Easter egg |
| 13 | TWILIGHT_OUTRO | Reflective walk-out |
| 14 | END_CARD | Clean text-free backdrop (wordmark composited in post) |

Don't skip slots — a 20s cut compresses each tableau to ~1.4s, it doesn't drop
them. The arc is the format.

## Look packs

A look pack locks the photographic style across all 14 tableaux via two fenced
blocks (`STYLE_OPENER`, injected at the head of every keyframe prompt;
`NEGATIVE_TAIL`, at the tail) plus palette, music-structure, and caption-style
guidance. Built-in packs:

| Pack | When to pick |
|---|---|
| `KODAK_PORTRA_DAY` | Warm afternoon, golden hour, lifestyle, college, summer |
| `CINESTILL_800T_NIGHT` | Neon-noir, winter, urban, nightlife, indoor venues |
| `PAPER_CUT_CRAFT` | Y2K, candy-coded, women's CPG / wellness, hand-craft |
| `CINEMATIC_GOTHIC_DUSK` | Candlelit, twilight, period-drama, gothic gravity |

Add a pack: drop `lookpacks/<NAME>.md` with the two fenced blocks (the scripts
read packs by name — no code change).

---

## Pipeline — phases + gates

The conversational flow below maps 1:1 to the `one_shot.py` state machine
(states `S0`–`S9`). Drive it phase-by-phase for full control, or run the whole
thing with `one_shot.py` (idempotent + resumable; see "Auto mode").

### Phase 1 — Intake + storyboard  (S0 INTAKE, S1 STORYBOARD — **Gate 2**)

Turn the free-form brief into `concept.json` + `source/lyrics-locked.md`. Pick a
look pack. Write all 14 tableaux with object-hero prompts and motion hints. Then
generate `storyboard.html` — a single page rendering the 14 tableaux + music
vibe + look pack as the review surface.

**Hand the storyboard to the user. Wait for explicit approval.** This is the
cheapest gate — changes here are free; after Phase 3 they cost re-rolled
keyframes; after Phase 4, re-rolled clips.

### Phase 2 — Music + timeline  (S2 MUSIC, S3 TIMELINE)

```bash
python scripts/render_music.py    --concept <run>/concept.json   # → music.mp3, words.json
python scripts/derive_timeline.py --concept <run>/concept.json --print   # → timeline.json
```

`render_music.py` calls ElevenLabs `/v1/music/detailed` with `with_timestamps`,
parses the multipart response into `audio/music.mp3` + `audio/music_metadata.json`,
and adapts the word timestamps to `audio/words.json`. `derive_timeline.py` maps
each tableau to a beat-locked in/out from the actual sung words.

### Phase 3 — T01 keyframe  (S4 KF_T01 — **Gate 3**)

```bash
python scripts/render_keyframes.py --concept <run>/concept.json T01
```

One keyframe via FAL nano-banana with the look pack injected. **Open
`assets/keyframes/T01.png`. Wait for approval** that the look pack landed before
committing to the parallel batch. Re-rolls are ~$0.04 each — don't be precious.

### Phase 4 — Keyframe batch + clips  (S5 KF_BATCH, S6 CLIPS)

```bash
python scripts/render_keyframes.py --concept <run>/concept.json   # remaining 13 (parallel, idempotent)
python scripts/render_clips.py     --concept <run>/concept.json   # i2v all (minus end card), de-letterbox
```

`render_clips.py` animates each keyframe with Seedance Pro, applies the
anti-shake/no-letterbox suffix, and auto-fixes letterbox bars. It **skips the
END_CARD tableau** — that slot is a PIL composite, not an i2v clip.

Re-roll a single failure by passing its id: `render_keyframes.py --concept … T08`.

### Phase 5 — End card + captions + compose  (S7 ENDCARD, S8 CAPTIONS, S9 COMPOSE)

```bash
python scripts/build_endcard.py  --concept <run>/concept.json   # → assets/clips/endcard.mp4
python scripts/make_captions.py  --concept <run>/concept.json   # → working/captions.ass
python scripts/compose.py        --concept <run>/concept.json   # → finals/master-final.mp4
```

`build_endcard.py` PIL-typesets the wordmark + tagline over the END_CARD
tableau's (text-free) backdrop and renders a Ken Burns clip. `compose.py`
retimes each clip to its beat slot, concatenates, muxes the music with fades +
loudnorm to -14 LUFS, and burns the captions (auto-generating the `.ass` if
absent). The deliverable is `finals/master-final.mp4`.

**Self-QC: watch the final mp4 before declaring done.** Stills don't catch
caption/hyperframe text collisions. Print the absolute path so the user can find
it.

## Auto mode

```bash
python scripts/one_shot.py --concept <run>/concept.json --continue
```

Walks S0–S9 with no human gates. Risky — you can pay for the full clip batch
before catching look drift. Only use when the user says "just run it." Without
`--continue`, it stops at Gate 2 (after S1) and Gate 3 (after S4); resume with
`--from S2` / `--from S5`. It writes `.state.json` and is fully idempotent, so a
re-run skips completed work.

## Decision rules (apply before generating, not after)

1. **One look pack per run.** The through-line is what makes it read as one ad.
2. **Object-hero / scene framing in prompts**, never "a young woman who…". Safer
   and cleaner.
3. **Never AI-render brand text.** The end-card wordmark/tagline are
   PIL-typeset; the END_CARD tableau prompt is a clean, text-free backdrop. (AI
   image/video models produce text-shaped nonsense — they cannot draw type.)
4. **The TIMELINE is computed per run** from the actual word timestamps. Never
   hard-code timings across runs — ElevenLabs never lands exactly on spec.
5. **Captions = lower-third serif, 4-word chunks** for cinematic packs; word-burst
   3-word mid-frame for paper-cut. Caption style is part of the look pack.
6. **Chorus + outro stay identical across a campaign series**; vary only verse +
   tableaux.
7. **Two human gates — storyboard, T01 keyframe.** Don't skip in non-auto mode.

## Failure modes + recovery

- **Music HTTP 400 `bad_prompt`** — `music.vibe` names a real artist. Use
  descriptive language only ("indie-electronic anthem with female vocal grit").
  The API response includes a `prompt_suggestion`.
- **Few/zero word timestamps** — lyrics too long to sing, or the song came back
  mostly instrumental. Shorten lyrics or regenerate. Captions/beat-sync need the
  words.
- **A keyframe NSFW false-flag or error** — re-roll just that one:
  `render_keyframes.py --concept … T12`. Re-frame as object-hero; drop "young
  woman", "sip", "reach".
- **An i2v clip fails / earthquakes / freezes** — re-roll just that one:
  `render_clips.py --concept … T09`. Letterbox bars are auto-fixed.
- **Caption burn: "No such filter: subtitles"** — your ffmpeg lacks libass.
  `pip install imageio-ffmpeg` (already in requirements) — the burn auto-falls
  back to its static binary.
- **TIMELINE durations don't sum** — re-run `derive_timeline.py`; it re-derives
  from `audio/words.json`.

## What it costs

| Step | Provider | Approx cost |
|---|---|---|
| Music (anthem + timestamps) | ElevenLabs Music | ~$0.50 |
| 14 keyframes | FAL nano-banana | ~$0.60 |
| 13 i2v clips (5s, 1080p) | FAL Seedance Pro | ~$13-20 |
| End card + compose + captions | local ffmpeg | free |
| **Total** | | **~$15-22** |

Wall time ~15-30 min plus ~6-10 min operator review at the two gates.

## References + examples

- `references/case-studies.md` — the three production runs the format is
  validated on, as archetypes + lessons.
- `examples/concept.json` + `examples/lyrics-locked.md` — a complete, runnable
  fictional run ("Aurelia — Comeback"). Copy them into your run folder to start.
- `examples/aurelia-comeback.md` — the same brief as a paste-ready kickoff prompt.
