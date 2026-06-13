# Skill: Plan Script for Video Ad

Write a production-ready 7-beat paid-social video script from a product brief. Output is a `script.md` file with every beat labeled, word counts checked, and rhythm verified.

---

## When to Use This Skill

Use this skill after `generate-ad-concepts` to develop a single concept into a full script, or directly from a brief when you already know the creative direction. Output feeds into `create-video-veo3` (for clip generation) and `create-voiceover-elevenlabs` (for VO recording).

---

## Inputs

| Field | Description |
|---|---|
| `product_brief` | Product name, what it does, audience, proof points, tone |
| `concept` | The specific creative angle (from concepts.md, or described in the brief) |
| `target_duration` | Default: **30 seconds** |
| `vo_speed` | `narrator` (~2.3 wps) or `fast-cuts` (~1.6 wps). Default: `narrator` |

---

## The 7-Beat Structure

Every script follows this exact beat sequence. Timings are for a 30s spot at narrator pace (~2.3 wps = ~69 words total). Adjust proportionally for other durations.

```
COLD-OPEN  │  0–1s   │  Visual scroll-stopper
HOOK       │  1–3s   │  Spoken hook line
PIVOT      │  3–4s   │  Turn from problem to solution
SOLUTION   │  4–15s  │  Product introduction + key benefit
OUTCOME    │ 15–22s  │  Time-anchored appearance/result claim
PROOF      │ 22–28s  │  Social proof sentence
CTA        │ 28–30s  │  Action + delivered outcome
```

---

## Per-Beat Rules

### COLD-OPEN (0–1s)
- **Purpose:** Stop the scroll before the viewer can swipe.
- **Visual:** Show the payoff — the result, the reaction, the transformed state — *before* you've set up the problem. Reward the eye first.
- **Text overlay:** 0–3 words maximum. Or no text at all.
- **What to avoid:** Logo reveals, brand name introductions, slow establishing shots.

> ✓ Good: Extreme close-up of a product being uncapped, liquid catching light, satisfying sound design.
> ✓ Good: A split-second reaction shot — someone's face lighting up — before any context.
> ❌ Bad: "Hi, I'm [name] and today I want to talk to you about..."

---

### HOOK (1–3s)
- **Purpose:** Name who this is for and make them feel seen.
- **Word count:** 10–18 words.
- **Rule:** Use **Tier 1 or Tier 2 hooks only** (see Hook Tier Table below).
- **Delivery:** Conversational, direct address. The viewer should feel like you're reading their mind.

---

### PIVOT (3–4s)
- **Purpose:** Mark the turn from problem/setup to solution.
- **Word count:** ≤6 words.
- **Pattern:** A short, punchy bridge sentence. Often a contrastive setup.

> Examples: "There's actually a better way." / "Until I found this." / "That's when everything changed." / "Meet [Product]."

---

### SOLUTION (4–15s)
- **Purpose:** Introduce the product and its core mechanism.
- **Word count:** 25–35 words.
- **Rule:** Name the **FORMAT** (what kind of thing it is) before the **INGREDIENTS** (what's in it or how it works).

> ❌ Wrong: "The magnesium glycinate, ashwagandha, and L-theanine formula that..."
> ✓ Right: "It's a nightly sleep supplement with magnesium glycinate, the most bioavailable form, plus ashwagandha and L-theanine..."

- **Sentence style:** Comma-joined flowing sentences. Avoid bullet-point rhythm in spoken copy.

---

### OUTCOME (15–22s)
- **Purpose:** Paint the future state — what life looks like after using the product.
- **Word count:** 15–22 words.
- **Rule:** Must be **time-anchored** — when does the viewer see results?

> ✓ Good: "By week two, most people wake up without an alarm and actually feel rested."
> ❌ Bad: "You'll feel so much better." (no time anchor, no specificity)

- **Rule:** Make an **appearance or behavioral claim**, not just an emotional one.

---

### PROOF (22–28s)
- **Purpose:** Provide a reason to believe — social validation, numbers, or a credible voice.
- **Word count:** 12–18 words.
- **Rule:** One flowing sentence. No bullet points. No lists.

> ✓ Good: "Over 40,000 people have switched to this routine in the last six months alone."
> ✓ Good: "Our customers rate it 4.8 stars — and 87% reported better sleep within the first week."
> ❌ Bad: "Great reviews! Thousands of happy customers! 5 stars!"

---

### CTA (28–30s)
- **Purpose:** Give the viewer a specific action and a reason to take it now.
- **Word count:** 10–15 words.
- **Pattern:** `[Action verb] + [specific delivered outcome]`

> ✓ Good: "Try Aura Labs risk-free — your first good night's sleep is one tap away."
> ✓ Good: "Click below and get 20% off your first bottle, shipped tomorrow."
> ❌ Bad: "Shop now." / "Check out our website." (no delivered outcome)

---

## Hook Tier Table

Use this table to classify and select hooks. **Only Tier 1 and Tier 2 are acceptable for paid-social scripts.**

| Tier | Name | Pattern | Example |
|------|------|---------|---------|
| **1** | Specific viewer behavior | `YOU EVER catch yourself [doing specific thing]?` | "You ever catch yourself lying awake at 2am doing math about how much sleep you'll get?" |
| **2** | Named-audience direct address | `If you're a [specific person], [specific thing is true]` | "If you're a mom who hasn't slept through the night since 2019, this is for you." |
| 3 | Concrete number/stat | Opens with a specific, surprising number | "In a survey of 1,200 women, 74% said they wake up more tired than when they went to bed." |
| 4 | Founder origin story | First-person struggle that led to the product | "I spent three years trying every sleep hack before I figured out what was actually missing." |
| **5** | Generic question | Vague open-ended question | "Having trouble sleeping?" — **Never use this tier.** |

**Rule:** Never use Tier 5. Tier 3 and 4 are acceptable only when Tier 1 and 2 don't fit the concept. Default to Tier 1 or 2.

---

## Sentence Rhythm Rules

Paid-social VO has a rhythm. Flat, uniform sentences cause viewers to zone out. Follow these rules:

1. **Mix long and short.** Long = 12–20 words. Short = ≤6 words.
2. **Max 2 consecutive short sentences.** Two punchy shorts in a row = emphasis. Three in a row = choppy.
3. **Use natural connectives.** The words `and`, `so`, `but`, `actually`, `look` signal spoken-word flow. They're not errors — they're rhythm.
4. **Read it aloud.** If you stumble, rewrite. If you inhale awkwardly, break up the sentence.

> Example of good rhythm (narrator pace):
> "Most sleep supplements just knock you out — that's not sleep, that's sedation. [short] This is different. [very short] It works with your body's natural magnesium cycle, so you drift off without grogginess and actually wake up feeling like a person again."

---

## VO Speed Reference

| Mode | Words per second | 30s word budget | 60s word budget |
|------|-----------------|-----------------|-----------------|
| Narrator (default) | ~2.3 wps | ~69 words | ~138 words |
| Fast-cuts | ~1.6 wps | ~48 words | ~96 words |

**Important:** These are soft targets. Always read aloud and time with a stopwatch or metronome. Trim or expand beats as needed to hit the target duration within ±2 seconds.

---

## Workflow

```
Step 1 — Gather inputs
  Confirm: product brief, creative concept, target duration, VO speed.

Step 2 — Select hook tier
  Identify whether the concept calls for a Tier 1 (behavior) or Tier 2 (named audience) hook.
  Draft 2–3 hook options. Select the most specific one.

Step 3 — Draft 7 beats
  Write each beat in order: COLD-OPEN → HOOK → PIVOT → SOLUTION → OUTCOME → PROOF → CTA.
  Apply per-beat rules (word counts, time anchors, format-before-ingredients, etc.).

Step 4 — Check word count
  Count words in HOOK (10–18), SOLUTION (25–35), OUTCOME (15–22), PROOF (12–18), CTA (10–15).
  Flag any beat that's outside range and revise.

Step 5 — Read aloud rhythm check
  Read entire VO track aloud at the selected VO speed.
  Note any stumbles, awkward pauses, or monotone stretches.
  Apply sentence rhythm rules (mix long/short, connectives).

Step 6 — Save output
  Write to script.md with full beat labels and timing marks.
```

---

## Output Format: `script.md`

```markdown
# Script: [Product / Concept Name]
**Duration:** [Xs]
**VO Speed:** [narrator / fast-cuts] (~X.X wps)
**Hook Tier:** [1 / 2]
**Total VO Words:** [N]
**Date:** [YYYY-MM-DD]

---

## COLD-OPEN [0–1s]
**Visual:** [specific scene description]
**Text overlay (if any):** [0–3 words or "none"]

---

## HOOK [1–3s]
**Tier:** [1 / 2]
**VO:** "[hook line]"
**Word count:** [N]

---

## PIVOT [3–4s]
**VO:** "[pivot line]"
**Word count:** [N]

---

## SOLUTION [4–15s]
**VO:** "[solution copy]"
**Word count:** [N]
**Visual notes:** [optional — what's on screen during this beat]

---

## OUTCOME [15–22s]
**VO:** "[outcome copy — must include time anchor]"
**Word count:** [N]
**Time anchor:** "[the specific timing phrase used]"

---

## PROOF [22–28s]
**VO:** "[proof sentence]"
**Word count:** [N]

---

## CTA [28–30s]
**VO:** "[CTA line]"
**Word count:** [N]
**Action:** [what the viewer should do]
**Delivered outcome:** [what they get]

---

## Full VO Track

> [COLD-OPEN: visual only / no VO]
> [HOOK VO]
> [PIVOT VO]
> [SOLUTION VO]
> [OUTCOME VO]
> [PROOF VO]
> [CTA VO]

---

## Rhythm Check
**Total words:** [N]
**Estimated duration at X.X wps:** [Xs]
**Long sentences (12–20w):** [N]
**Short sentences (≤6w):** [N]
**Consecutive short sentences (max 2):** [pass / flag]
```

---

## Example Kickoff Prompt

```
I need a 30-second script for the following concept.

Product: Aura Labs magnesium glycinate sleep supplement
Concept: "The 2am Math Problem" — a Tier 1 hook opening on the specific behavior of lying awake calculating remaining sleep time. UGC talking-head format. Target: women 28–45 who've tried melatonin and been disappointed.
VO speed: narrator (~2.3 wps)
Proof point: 87% of users fell asleep faster in week 1, 4.8-star rating, 40,000 customers

Please write a 7-beat script following the full per-beat rules in SKILL.md, check word counts for each beat, then save to script.md.
```
