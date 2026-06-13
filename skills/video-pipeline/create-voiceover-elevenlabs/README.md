# create-voiceover-elevenlabs

Generate expressive AI voiceover from a script using ElevenLabs, with character-level timing data for video sync.

This skill handles the full voiceover generation workflow: shaping a script with light audio tag markup, calling the ElevenLabs `/with-timestamps` API using `eleven_v3` (the most expressive model), decoding the audio, saving timing data, and measuring actual duration against target. It also includes the atempo correction workflow — a critical step that most integrations skip and that causes VO/video sync drift in production.

Two important known limitations are encoded directly into the skill: character timestamps from `eleven_v3` are unreliable due to alignment model failure around expressive tags (always verify with Whisper for caption use), and duration is non-deterministic with 5–15% variance run-to-run (always render video to fixed duration first, then atempo the VO to match).

## Quickstart

Copy and paste the prompt below into Claude. Fill in the bracketed fields.

```
Read the skill at skills/video-pipeline/create-voiceover-elevenlabs/SKILL.md.

I need a voiceover for a paid-social video script.

Script:
[paste your full VO script here]

Voice ID: [your ElevenLabs voice ID]
Target duration: [X seconds, or "none"]
Output directory: ./output

Please:
1. Optionally add 1–2 light audio tags where they improve delivery
2. Call the ElevenLabs API with eleven_v3 and default voice settings
3. Save voiceover.mp3, voiceover_timestamps.json, and voiceover_script.txt
4. Measure duration with ffprobe
5. If duration differs from target by more than 0.5s, calculate and apply atempo correction
6. Report final file paths and durations
```

## What You Get

- `voiceover.mp3` — Rendered AI voiceover
- `voiceover_timestamps.json` — Character-level timing data (verify with Whisper before using for captions)
- `voiceover_script.txt` — Exact script as sent to the API
- `voiceover_synced.mp3` — Atempo-adjusted version if target duration was provided and correction was needed
