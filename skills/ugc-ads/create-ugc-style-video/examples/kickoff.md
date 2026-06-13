# Example Kickoff Prompt — create-ugc-style-video

Copy and paste this into Claude Code to start a UGC ad session.
Replace the bracketed placeholders with your product details.

---

## Kickoff prompt

```
Load the skill at skills/ugc-ads/create-ugc-style-video/SKILL.md.

I want to make a UGC-style video ad for the following product:

**Brand:** [e.g., Lumē Naturals]
**Product:** [e.g., Hydrating Face Serum]
**Description:** [e.g., A lightweight daily serum with hyaluronic acid and vitamin C. Reduces dryness and brightens skin in 2 weeks.]
**Product images:** [e.g., https://example.com/product-hero.jpg — or tell me you'll upload them]
**Target audience:** [e.g., Women 25–40 interested in clean skincare]
**Brand voice:** [e.g., Conversational, honest, no hype — or leave blank for default]
**Number of products:** [e.g., 1]
**Resolution:** [e.g., 1080p — or 720p for budget mode]

Run the full pipeline from Phase 1 through Phase 8. Ask me for anything you need before starting.
```

---

## What happens next

Claude Code will:

1. Confirm your inputs and ask for any missing details
2. Generate an AI avatar portrait (NB2 via FAL) — you'll see the portrait URL
3. Write scene scripts for hook, product, and end card
4. Generate each scene with Seedance 2.0 (lip-synced natively)
5. Download all clips and stitch with ffmpeg
6. Add word-level captions via Whisper
7. Mix in a music bed via ElevenLabs or royalty-free track
8. Run final QC checks and deliver `output/final_ad.mp4`

---

## Example with real-sounding inputs

```
Load the skill at skills/ugc-ads/create-ugc-style-video/SKILL.md.

I want to make a UGC-style video ad for the following product:

Brand: Bloom & Root
Product: Daily Greens Powder
Description: A once-daily greens powder with 23 whole-food ingredients. 
Mixes clean in water, no chalky taste. Designed for people who struggle to 
eat enough vegetables.
Product images: https://example.com/greens-powder-hero.jpg
Target audience: Health-conscious adults 28–45, busy lifestyle
Brand voice: Real and relatable — like a friend who actually tried it, 
not a wellness influencer
Number of products: 1
Resolution: 1080p

Run the full pipeline. Let me know if you need the images uploaded locally.
```

---

## Tips

- **Product images matter.** Seedance uses them as visual reference for the scene. Use clean product shots on simple backgrounds.
- **Keep scripts punchy.** 15 seconds goes fast. One claim per scene works better than three.
- **For 3-product ads:** You can run this three times with different product inputs and the same avatar URL, or ask Claude to batch all three in one session.
- **Budget mode:** Add "Use 720p resolution" to your kickoff prompt to reduce cost by ~50%.
