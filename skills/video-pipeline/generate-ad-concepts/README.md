# generate-ad-concepts

Turn a brand brief into a structured set of production-ready ad concepts for short-form video.

This skill takes a product description, target audience, and platform context and outputs a `concepts.md` document containing a Strategic Foundation and N fully-specified creative concepts — each with a concrete hook, numbered beat outline, VO copy, required assets, and CTA. It's designed to feed directly into the `plan-script-for-video-ad` skill, where individual concepts get developed into full 7-beat scripts.

The skill enforces a quality bar that most AI-generated concept work misses: hooks must be filmable scenes (not vague themes), every concept must be genuinely distinct across format, emotional angle, and audience sub-segment, and all claims must trace back to the brief. The output is a single `concepts.md` file ready for stakeholder review or script development.

## Quickstart

Copy and paste the prompt below into Claude. Fill in the bracketed fields.

```
I need ad concepts for a new DTC product.

Brand: [brand name]
Product: [what it does and what problem it solves]
Target audience: [who they are, what they want, what pain they feel]
Platform: IG Reels + TikTok, 9:16
Number of concepts: 5
Tone: [e.g. warm and direct / clinical and confident / playful]
Proof points: [any stats, testimonials, or differentiators]

Please read SKILL.md for the full concept schema and quality rules, then:
1. Write a Strategic Foundation
2. Generate 5 distinct ad concepts, each with all 10 schema fields
3. Save the output to concepts.md
```

## What You Get

- `concepts.md` — Strategic Foundation + N concepts, each fully specified for production
- Each concept includes: Premise, Format, Length + Aspect Ratio, Audience, Hook (first 3s), Beats, VO/Copy, Suggested Assets, CTA + End Card, Why It Works
