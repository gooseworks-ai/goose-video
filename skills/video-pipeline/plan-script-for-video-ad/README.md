# plan-script-for-video-ad

Write a production-ready 7-beat paid-social video script from a product brief or ad concept.

This skill implements a strict 7-beat framework — COLD-OPEN → HOOK → PIVOT → SOLUTION → OUTCOME → PROOF → CTA — with per-beat word count rules, a hook tier system, and sentence rhythm guidelines. It enforces the structural discipline that separates high-converting paid-social scripts from generic ad copy: concrete scroll-stopping cold opens, Tier 1/2 hooks that make viewers feel seen, time-anchored outcome claims, and CTAs that promise a specific delivered result.

The skill takes a product brief and creative concept and outputs a `script.md` file with all 7 beats labeled, word counts verified, VO paced to target duration, and a full VO track assembled for handoff to recording or AI voiceover generation.

## Quickstart

Copy and paste the prompt below into Claude. Fill in the bracketed fields.

```
Read the skill at skills/video-pipeline/plan-script-for-video-ad/SKILL.md.

I need a 30-second script for the following:

Product: [product name and one-sentence description]
Concept: [creative angle — e.g. "Tier 1 hook on the specific behavior of X, UGC talking-head, target audience Y"]
VO speed: narrator (~2.3 wps)
Proof points:
- [stat or social proof 1]
- [stat or social proof 2]

Please write a 7-beat script following all per-beat rules, check word counts, read for rhythm, then save to script.md.
```

## What You Get

- `script.md` — Full 7-beat script with beat labels, word counts, timing marks, rhythm check, and complete VO track
- Enforced per-beat rules: hook tier validation, time-anchored outcomes, format-before-ingredients in solution beat
- Ready to hand off to `create-voiceover-elevenlabs` for AI VO generation
