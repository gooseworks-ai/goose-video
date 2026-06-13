# create-video-veo3 — kickoff prompt
# Paste this into Claude Code to generate a video clip with Veo 3.1.
# Fill in all bracketed fields before running.

---

Read the skill at skills/video-pipeline/create-video-veo3/SKILL.md.

I need to generate a video clip for a paid-social ad.

**Subject:** [who or what — e.g. "young woman in her late 20s", "30ml amber glass dropper bottle"]
**Action:** [what the subject is doing — e.g. "reaching into cabinet and pulling out a bottle", "sitting on white marble"]
**Style:** [visual style — e.g. "UGC talking-head", "commercial skincare photography", "cinematic lifestyle"]
**Camera:** [motion and framing — e.g. "handheld follows her hand", "slider drift left on locked subject", "push-in to face"]
**Mood:** [e.g. "warm morning energy", "premium and clean", "relaxed evening ritual"]
**Audio:** [e.g. "natural ambient sound", "soft room tone", "none specified"]
**Start image:** [path/to/reference.jpg OR "none"]
**Aspect ratio:** 9:16
**Duration:** 4
**Output path:** output/[clip-name].mp4

Please:
1. Compose a verb-led prompt (CHARACTER + ACTION-VERB in first 8 words, no banned vocabulary)
2. If this is a product shot, use camera-only motion (no 360 rotation)
3. Run the Higgsfield CLI with --quality high --wait --wait-timeout 12m
4. Download and verify the MP4 at the output path
5. Note the prompt and any issues for iteration
