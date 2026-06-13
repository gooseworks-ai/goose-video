# create-video-veo3

Generate cinematic short-form video clips using Google Veo 3.1 via the Higgsfield CLI or FAL API.

This skill handles the full clip generation workflow: composing verb-led prompts according to Veo's specific requirements, running the Higgsfield CLI (or FAL API as a fallback), and downloading the resulting MP4. It encodes the hard-won operational knowledge for working with Veo 3.1 in production — including which model variant to use, what vocabulary to avoid, how to handle product B-roll without label fabrication, and what to do when generation fails.

The skill is designed for generating individual beats from a paid-social script, but works for any short-form clip generation task. Output is a single MP4 file ready for assembly in your video editor.

## Quickstart

Copy and paste the prompt below into Claude. Fill in the bracketed fields.

```
Read the skill at skills/video-pipeline/create-video-veo3/SKILL.md.

I need to generate a video clip.

Subject: [who or what — e.g. "young woman", "amber glass bottle"]
Action: [what they're doing — e.g. "opening a cabinet", "sitting on white marble while camera moves left"]
Style: [visual style — e.g. "UGC lifestyle", "commercial skincare photography", "cinematic editorial"]
Camera: [framing and motion — e.g. "handheld follows action", "locked with slow left drift", "push-in on face"]
Mood: [e.g. "warm and energetic", "clean and premium", "calm morning ritual"]
Audio: [e.g. "ambient kitchen sound", "soft room tone", "none"]
Start image: [path/to/image.jpg or "none"]
Aspect ratio: 9:16
Duration: 4 seconds
Output: output/[clip-name].mp4

Please compose a verb-led prompt following all rules in the skill, then run the Higgsfield CLI to generate the clip.
```

## What You Get

- `output/[clip-name].mp4` — Generated clip at your specified aspect ratio and duration
- Prompt log entry for reproducibility and iteration
- Guidance on what to fix if the clip doesn't match intent
