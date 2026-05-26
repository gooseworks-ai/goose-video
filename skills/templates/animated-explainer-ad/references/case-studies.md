# Case studies — the two validated production runs

These are the two real client runs that this skill encodes. Cite either as a worked example when briefing a new project.

---

## 1. HUM Nutrition — "Big Chill" cortisol absurdism

**The original.** This is the run that proved the format works and that the skill is reverse-engineered from.

### Brief

| | |
|---|---|
| Brand | HUM Nutrition |
| Product | Big Chill (Rhodiola Rosea supplement) |
| Problem | Stress |
| Mechanism | Rhodiola Rosea calms cortisol |
| Audience | Women 25–45 who feel "wired and tired" |
| Format | 9:16, ~38s (shipped 34.6s), paid social |
| Pattern | Villain narrates own defeat |

### Character roster (4)

| Role | Character | Visual |
|---|---|---|
| Villain | Stress | Red gremlin floating in body cavity, smug, sharp-toothed grin |
| Hero | Big Chill capsule | Tan capsule, descends on golden halo of sparkles |
| Human victim | Pixar woman | ~30s, brunette bob, cream sweater; recurs across damage scenes |
| Set piece | Adrenal beans | Two bean characters at desks under flickering flames |
| (subordinate) | Cortisol minions | Smaller copies of Stress — same army, half size, simpler faces |

Earlier versions (v3, v4) made Cortisol a separate 5th character distinct from Stress; the cause/effect chain muddied. v5 collapsed them — Stress is both villain AND source — and the chain snapped into focus. **Don't repeat this mistake.**

### Voice + script

- **Voice:** Dylo (`JjsQrIrIBD6TZ656NQfi`) — "Young, Fierce and Determined." eleven_v3, speed 1.15.
- **Audio tags:** `[menacing]` ×1, `[sighs]` ×1 — only 2 total, well under the 4 cap.
- **Recurring motif:** "cortisol hormones" — scenes 3, 7, 10.
- **Final line:** "Big Chill, by HUM. Clinically tested. Break the cycle."

### Script (validated)

```
SCENE 01 (3.3s): "I'm stress. I live inside you."
SCENE 02 (4.9s): "I make these two little glands — your adrenal glands — work OVERTIME."
SCENE 03 (4.1s): "They pump out my minions: tiny cortisol hormones."
SCENE 04 (2.0s): "[menacing] They make your hair fall out."
SCENE 05 (1.7s): "They keep you up at night."
SCENE 06 (1.9s): "They put weight on your stomach."
SCENE 07 (1.3s): "They press on your heart."
SCENE 08 (3.8s): "And they turn you into someone you don't want to be."
SCENE 09 (1.9s): "[sighs] Until Big Chill shows up."
SCENE 10 (2.3s): "And my minions stop showing up."
SCENE 11 (3.0s): "And you get to be yourself again."
SCENE 12 (4.4s, end card): "Big Chill, by HUM. Clinically tested. Break the cycle."
```

### Lessons learned

1. **"Adaptogen" and "Rhodiola Rosea" stay off the VO.** End-card type only. The VO uses simple anchor words.
2. **"Hormonal imbalance" never appears.** Vague + Meta-flagged wellness trope.
3. **Cortisol minions visually = smaller copies of Stress.** Same army, instant visual logic.
4. **End card uses the REAL bottle.** v0.7 shipped with an AI cartoon bottle and was reshot with the real `692.jpg`.
5. **Single voice for the WHOLE spot** including the defeat. The comedy is the villain explaining his own loss.

### Cost (~$16 total)

| Phase | Provider | Op | USD |
|---|---|---|---|
| 2 | FAL | nano-banana anchors (×4) | $0.30 |
| 3 | ElevenLabs | eleven_v3 TTS (Dylo, single concatenated stem) | $0.30 |
| 4 | FAL | nano-banana keyframes (×12 + re-rolls) | $0.60 |
| 5 | FAL | Seedance Pro i2v 1080p (×12) | $15.00 |
| 7 | ElevenLabs | music API (48s bed) | $0.20 |

### Outputs

- `master-v0.9-rough.mp4` — 34.6s, 9:16, 1080×1920, captioned, scored.
- Compose script: `compose_v09_master.sh` — per-scene `tpad=stop_mode=clone`, libass burn, VO -14 LUFS + music -26 LUFS @ 0.70 gain, amix.

---

## 2. Soteri Skin — "Eczema, the pH villain"

**The second proof.** Built explicitly as "the exact pattern of Big Chill" — confirms the format generalises beyond the original run.

### Brief

| | |
|---|---|
| Brand | Soteri Skin |
| Product | Baby Eczema Relief Cream (Powered by pH/LOCK®) |
| Problem | Eczema |
| Mechanism | pH/LOCK at 4.9 (the moisture barrier as pH problem) |
| Audience | Parents of babies (ages 0–5) with eczema-prone skin |
| Format | 9:16, ~38s target (shipped 45.1s with atempo 1.3), paid social |
| Pattern | Villain narrates own defeat |

### Character roster (4)

| Role | Character | Visual |
|---|---|---|
| Villain | Eczema | Knee-high gremlin, rough coral-red sandpapery skin with tiny spikes, frizzy dark-red tuft, jagged grin |
| Hero | Soteri | Smooth plump rounded cream-white, gentle glow, eucalyptus-green cape, padlock crest on chest ("pH") |
| Human victim | The baby | ~12 months, chubby rosy cheeks, soft wisps of hair, cream onesie |
| Set piece | Moisture barrier | Wall of rounded peachy-tan skin-cell bricks, each a small plump character with a cute face |

**The pH meter is a graphic prop, not a character.** A round gauge — green/acidic on left (~4.9), red/alkaline on right. Don't count it toward the roster.

### Voice + script

- **First pick (rejected):** Tom (`mdzEgLpu0FjTwYs5oot0`). The read was 54s against a 38s target; villain delivery dragged.
- **Final pick:** Austin (`Bj9UqZbhQsanLzgalpEG`) — Texan, raspy, characterful. eleven_v3, speed 1.12.
- **Voice casting cost:** $0.15 for the 6-voice A/B pass. **Do not skip this.**
- **Audio tags:** `[whispers]` `[menacing]` `[nervous]` `[sighs]` — exactly 4 (at the cap).
- **Recurring motif:** "pH 4.9" — scenes 5, 6, 10.

### Script (validated)

```
SCENE 01 (3.1s): "[whispers] Psst. I'm Eczema. I live on your baby's skin."
SCENE 02 (5.4s): "See this wall? The moisture barrier — it keeps water in, and trouble out."
SCENE 03 (1.4s): "So I break it."
SCENE 04 (3.4s): "Here's my little secret — it's really a pH problem."
SCENE 05 (4.6s): "Healthy baby skin sits slightly acidic — right around 4.9."
SCENE 06 (3.9s): "[menacing] I push it higher... and the whole wall cracks apart."
SCENE 07 (3.4s): "Moisture escapes. The skin goes dry, red, itchy."
SCENE 08 (2.4s): "And nobody in that house sleeps tonight."
SCENE 09 (2.6s): "[nervous] Until Soteri Skin shows up."
SCENE 10 (4.6s) ⭐ CLIMAX: "Its pH lock snaps it right back to 4.9 — and the wall seals shut."
SCENE 11 (6.3s): "[sighs] Soft skin. Calm baby. And me? Nowhere left to live."
SCENE 12 (4.0s, end card): "That's Soteri Skin. Steroid-free, made for the littlest skin."
```

### Drift caught at human gates

- **Phase 4 (keyframes):** Eczema grew bat-wings in scenes 08 + 09 — the model interpreted "gremlin" as "winged imp" once anchor weight dropped. **6 keyframes re-rolled** with explicit "no wings" constraints. Originals preserved under `_rejected-v1/`.
- **Phase 5 (clips):** Seedance letterboxed scenes 01, 02, 04 with cinematic black bars on 9:16 output. **De-letterboxed in post** (`scale=1088:1920,crop=1080:1920`).
- **Phase 3 (VO):** Tom read was 54s (40% over target). Rejected by operator, recast to Austin. Even Austin came in long — applied compose-stage `atempo=1.3` as the documented fallback.

### Cost ($17.60 total)

| Phase | Provider | Op | Units | USD |
|---|---|---|---|---|
| 2 | FAL | nano-banana anchor (4 characters) | 4 | $0.32 |
| 3 | ElevenLabs | voice casting A/B (6 voices, scene-01) | 6 | $0.15 |
| 3 | ElevenLabs | eleven_v3 TTS — Tom (rejected) | 12 | $0.30 |
| 3 | ElevenLabs | eleven_v3 TTS — Austin re-render | 12 | $0.30 |
| 3 | ElevenLabs | scene-11 trim re-render | 1 | $0.03 |
| 4 | FAL | nano-banana keyframes (11 + 6 re-rolls) | 17 | $0.66 |
| 5 | FAL | Seedance Pro i2v 1080p (preview ×5) | 5 | $6.30 |
| 5 | FAL | Seedance Pro i2v 1080p (remaining ×7, ~31s) | 31s | $9.30 |
| 7 | ElevenLabs | music API (48s bed) | 1 | $0.20 |

### End card

- Real product image: `raw-materials/product-endcard.jpg` (cropped from the studio photo to remove "Harvard PhD" marketing badges).
- Brand background sampled from the product photo's own edge for seamless paste.
- Typeset layer (PIL):
  - "Soteri Skin" wordmark (Arial Bold 100, brand green `#2E6F5E`)
  - "Baby Eczema Relief Cream" subline (Arial Bold 46, lighter green `#3E8A73`)
  - "Powered by pH/LOCK® Technology" (Arial 35, grey)
  - "Steroid-Free · Fragrance-Free · Ages 0–5" (Arial 35, grey)
  - CTA pill: "soteriskin.com" on coral `#E8674C` background, white Arial Bold 43

### Lessons learned

1. **Voice casting A/B is worth the $0.15.** Tom was the "obvious" pick on paper; Austin actually delivered.
2. **Negative constraints on anchors must be tight.** "No wings, no horns, no tail" would have caught the bat-wing drift at phase 2 instead of phase 4.
3. **De-letterbox check is mandatory on every Seedance clip.** ~25% of clips need it.
4. **VO came back long (Soteri-specific):** speed=1.20 + drop 2 audio tags + script trim would have hit 38s without atempo=1.3. Worth doing if shooting for tight runtime.
5. **End card sampled-bg recipe is seamless.** `prod.getpixel((6, 6))` → use as canvas fill. No visible paste edge.

---

## Compose recipe (works for both runs)

```bash
# Per-scene retime
ffmpeg -y -i scene-NN.mp4 \
  -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,setsar=1,tpad=stop_mode=clone:stop_duration=<pad>" \
  -t <target_dur> \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -r 30 -an seg-NN.mp4

# Concat
ffmpeg -f concat -safe 0 -i concat.txt -c copy video.mp4

# VO with atempo compensation
ffmpeg -i vo-NN.mp3 -af "atempo=1.3,apad" -t <target> -ar 44100 -ac 2 vo-NN.wav

# Mix VO (-14 LUFS) + music (-26 LUFS @ 0.62 gain, ducked)
ffmpeg -i vo-track.wav -i music.wav \
  -filter_complex "[0:a]loudnorm=I=-14:TP=-1.5:LRA=11[vo]; \
                   [1:a]loudnorm=I=-26:TP=-3:LRA=11,volume=0.62[mus]; \
                   [vo][mus]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[a]" \
  -map "[a]" mix.wav

# Burn captions + mux
ffmpeg -i video.mp4 -i mix.wav -vf "ass=captions.ass" \
  -map 0:v -map 1:a -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 192k -shortest master.mp4
```

This recipe is what `scripts/compose.sh` automates.
