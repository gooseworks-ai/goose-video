# Example kickoff prompt — trading-card app (product-flex hook)

Paste this into an agent that has the `imessage-video-ad` skill loaded. The skill walks you through the pipeline (brainstorm → thread → timeline → flat-lay → record → end card → stitch) and pauses at the review gates.

---

Make an iMessage conversation-reveal ad for my **trading-card app** ("Decked"). Playful brand voice. 9:16, ~18s, paid social.

**Angle:** product-flex (result-as-screenshot). I screenshot a graded card I pulled and send it to a friend; they freak out and ask what app it is; I reveal the app and drop a promo code.

**The hook (bubble 1 attachment):** a screenshot of a graded trading card — title "Holo Dragon #149 — PSA 10", value "$4,736.80". Render it locally as an HTML card (don't AI-generate it) into `assets/hook.png`.

**The peer:** "Tyler", gray avatar, initials "TK".

**The thread (me = blue/right, Tyler = gray/left):**
1. me: "yo just pulled this" (+ the attachment above)
2. Tyler: *typing…* → "bro no way"
3. Tyler: "is that on an app"
4. me: "yeah"
5. Tyler: *typing…* → "what app"
6. me: "decked"
7. me: "you can build your own pack and set the odds yourself"
8. me: "then u can ship or sell ur pulls"
9. Tyler: *typing…* → "that's actually insane"
10. me: "ya use code FREEPACK to get a free pack"  ← underline the code
11. Tyler: "bet"

**End card:** glow variant. Real "Decked" wordmark SVG at `assets/brand-logo.svg`, offer line "Use code · FREEPACK · for a free starter pack".

**Flat-lay background:** a warm creator desk (the default in `gen_flat_lay_bg.py` is fine), or I'll supply my own `assets/flat-lay-bg.jpg`.

**Music:** I'll drop a lofi loop at `audio/music-bed.mp3`.

Start by confirming the angle and drafting `threads/full-thread.json` + `timeline.json`, then pause so I can review before you record.
