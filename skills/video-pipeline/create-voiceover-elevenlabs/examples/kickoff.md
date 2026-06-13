# create-voiceover-elevenlabs — kickoff prompt
# Paste this into Claude Code to generate an ElevenLabs voiceover.
# Fill in all bracketed fields before running.

---

Read the skill at skills/video-pipeline/create-voiceover-elevenlabs/SKILL.md.

I need a voiceover for a 30-second paid-social video ad.

**Voice ID:** [your ElevenLabs voice ID]
**Target duration:** 30 seconds
**Output directory:** ./output

**Script:**
[Paste your full VO script here. Include any audio tags if desired,
or leave plain and let Claude add 1–2 light tags if needed.]

**Voice settings:** use defaults (stability=0.34, similarity_boost=0.80, style=0.15, use_speaker_boost=true)
**Model:** eleven_v3

Please:
1. Review the script — add at most 1–2 audio tags where they clearly improve delivery (optional; leave plain if it sounds good)
2. Call the ElevenLabs API with the /with-timestamps endpoint
3. Decode audio_base64 and save to output/voiceover.mp3
4. Extract timing data and save to output/voiceover_timestamps.json
5. Save the rendered script to output/voiceover_script.txt
6. Run ffprobe to measure actual duration
7. If actual duration differs from 30s by more than 0.5 seconds:
   - Calculate atempo = actual_duration / 30.0
   - Apply via FFmpeg: ffmpeg -i voiceover.mp3 -filter:a "atempo=X.XX" voiceover_synced.mp3
8. Report: file paths, raw duration, synced duration (if adjusted), atempo value used
9. Note: character timestamps may be unreliable — recommend verifying with Whisper before using for captions
