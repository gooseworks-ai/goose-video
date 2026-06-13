# Skill: Generate Ad Concepts

Generate a structured ad-concepts document from a brand brief. Produces a `concepts.md` file with a Strategic Foundation and N distinct creative concepts, each fully specified for production.

---

## When to Use This Skill

Use this skill at the start of any paid-social video campaign when you need to develop multiple creative directions from a brand brief before writing individual scripts. Output is a single `concepts.md` file that feeds directly into the `plan-script-for-video-ad` skill.

---

## Inputs

### Required
| Field | Description |
|---|---|
| `brand_name` | The brand or product name |
| `product` | What the product does and what problem it solves |
| `target_audience` | Primary audience (demographics, psychographics, pain points) |
| `platform` | Default: **IG Reels / TikTok 9:16** |
| `num_concepts` | Number of concepts to generate. Default: **5** |

### Optional
| Field | Description |
|---|---|
| `existing_ad_analysis` | Notes on what has worked or failed in past ads |
| `competitor_ads` | Reference competitor ads or angles to differentiate from |
| `tone` | Brand tone (e.g. clinical, warm, witty, bold, conversational) |
| `proof_points` | Any stats, testimonials, or differentiators to incorporate |

---

## Concept Schema

Every concept must include **all** of the following fields:

### 1. Premise
The angle or creative idea in 1–2 sentences. What makes this concept distinctly different from the others?

### 2. Format
Choose one:
- UGC talking-head
- Product demo
- Motion graphics / kinetic text
- Before/after transformation
- Testimonial / social proof
- Founder story
- Day-in-the-life / POV
- Educational / explainer

### 3. Length + Aspect Ratio
Examples: `15s / 9:16`, `30s / 9:16`, `60s / 9:16`

### 4. Audience
Who this specific concept targets — may be a sub-segment of the main audience.

### 5. Hook (First 0–3 Seconds)
A **concrete scene description** — what the viewer sees and/or hears in the first 3 seconds. Not a theme. Not a topic. A specific, filmable moment.

> ❌ Bad: "Opens with something relatable about skincare"
> ✓ Good: "Close-up of a phone screen showing a DM: 'What is that foundation you're wearing?' Cut to creator's face."

### 6. Beats
A numbered, beat-by-beat production outline. Minimum 4 beats, maximum 8. Each beat = one visual moment or VO section with approximate timing.

```
1. [0-3s] Hook: ...
2. [3-6s] Problem setup: ...
3. [6-15s] Product solution: ...
4. [15-22s] Outcome / proof: ...
5. [22-28s] Social proof: ...
6. [28-30s] CTA: ...
```

### 7. VO / Copy
The exact lines to speak or display on screen, in order. Label each as `(VO)` or `(TEXT OVERLAY)`.

### 8. Suggested Assets
A specific list of images, clips, or footage needed to produce this concept.

Examples:
- Lifestyle shot of product on bathroom counter, morning light
- Screen recording of phone showing before/after photos
- UGC-style selfie video of real user reaction
- B-roll: close-up of ingredients being poured

### 9. CTA + End Card
The exact call-to-action text and what appears on the end card (link, offer, brand logo).

### 10. Why It Works
2–4 sentences: what psychological mechanism, platform behavior, or audience insight makes this concept effective.

---

## Strategic Foundation

Before generating concepts, write a **Strategic Foundation** section:

```markdown
## Strategic Foundation

**Core Message:** [One sentence — what single idea should viewers walk away with?]

**Proof Pillars:** [2–4 specific claims that support the core message. Each must trace to the brief.]
- Pillar 1: ...
- Pillar 2: ...
- Pillar 3: ...

**Primary Audience:** [Who they are, what they want, what pain they feel]

**Tone:** [e.g. Direct and warm. Confident without being clinical.]

**Platform Context:** [How people consume this format — e.g. "Thumb-stopping 9:16 autoplay, sound-on majority, 3-second drop-off risk"]
```

---

## Quality Rules

1. **Hooks must be filmable moments** — a specific visual + audio scene, not a vague emotion or topic.
2. **Concepts must be genuinely distinct** — different format, different emotional hook, different audience angle. Not just the same idea reworded.
3. **Every claim must trace to the brief** — no invented proof points, no fabricated statistics.
4. **Beats must have timestamps** — approximate timing keeps production grounded.
5. **VO must be production-ready** — write actual lines, not descriptions of lines.
6. **Vary across at least 3 dimensions**: format type, primary emotion (curiosity / aspiration / fear / humor / trust), and audience sub-segment.

---

## Workflow

```
Step 1 — Gather inputs
  Ask for required fields. Note optionals.
  If existing ad analysis is provided, note what NOT to repeat.
  If competitor references are provided, note angles to differentiate from.

Step 2 — Write Strategic Foundation
  Synthesize core message, proof pillars, audience, tone, platform context.
  Do not generate concepts until foundation is written.

Step 3 — Generate N concepts
  For each concept (1 through N):
    - Assign a distinct format
    - Write all 10 schema fields
    - Check: is this hook a concrete scene?
    - Check: is this concept distinct from all previous ones?
    - Check: does every claim trace to the brief?

Step 4 — Diversity check
  Review all concepts together.
  Ensure variation across: format type, emotional hook, audience sub-segment.
  Flag and revise any two concepts that are too similar.

Step 5 — Save output
  Write to concepts.md in the current working directory.
  Include: date, brand, product, platform, num_concepts at top of file.
```

---

## Output Format: `concepts.md`

```markdown
# Ad Concepts: [Brand Name]
**Product:** [product description]
**Platform:** [platform]
**Date:** [YYYY-MM-DD]
**Concepts:** [N]

---

## Strategic Foundation
[foundation section]

---

## Concept 1: [Short Title]
[all 10 schema fields]

---

## Concept 2: [Short Title]
[all 10 schema fields]

...
```

---

## Example Kickoff Prompt

```
I need ad concepts for a new DTC product.

Brand: Aura Labs
Product: A magnesium glycinate sleep supplement that helps adults fall asleep faster and stay asleep — without grogginess the next morning.
Target audience: Women 28–45 who are high-achieving professionals, moms, or both. They've tried melatonin and been disappointed. They're skeptical of supplements but desperate for real sleep.
Platform: IG Reels + TikTok, 9:16
Number of concepts: 5
Tone: Warm, direct, science-backed without being clinical
Proof points: 87% of users fell asleep faster in week 1 (survey data), no next-day grogginess, magnesium glycinate is the most bioavailable form, 3rd-party tested

Please generate a Strategic Foundation and 5 distinct ad concepts following the full concept schema.
Save the output to concepts.md.
```
