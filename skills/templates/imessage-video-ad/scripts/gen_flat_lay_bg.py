#!/usr/bin/env python3
"""Generate the flat-lay desk background for the FRAMED (Variant B) iMessage ad.

The framed recorder composites the iPhone onto this background, so the CENTER
vertical column must stay EMPTY for the phone to sit on cleanly.

Endpoint: fal-ai/gpt-image-1 (quality=high, 1024x1536) — ~$0.19/run.
Output:   <project>/assets/flat-lay-bg.jpg (+ .meta.json)

The default PROMPT is a warm wooden creator desk. To restyle for the brand's
register (finance desk, kitchen, gym corner, …) drop a one-paragraph prompt in
<project>/flat-lay-prompt.txt — keep the hard rules: empty center column,
vertical 9:16, no people/phones/text.

Usage:
  python3 scripts/gen-flat-lay-bg.py --project ./my-ad
  python3 scripts/gen-flat-lay-bg.py --out ./my-ad/assets/flat-lay-bg.jpg
"""
import argparse
import json
import os
import sys
import urllib.request

try:
    from dotenv import load_dotenv  # optional convenience
except Exception:  # pragma: no cover
    load_dotenv = None

# --- Default flat-lay scene. Override per project via flat-lay-prompt.txt. -----
DEFAULT_PROMPT = """Top-down flat-lay photograph of a warm wooden desk surface, shot from directly above, filling the frame. Calm, end-of-workday composition. Arrange a few tasteful items gently AROUND the edges, leaving the CENTER completely clear:

LEFT EDGE: a closed laptop in space-gray on a thin leather sleeve, soft shadow.
RIGHT EDGE: a ceramic mug of dark coffee seen from above, maybe a faint steam wisp.
TOP EDGE: a small closed leather notebook with a pen resting across it, slightly cropped.
BOTTOM EDGE: a small plant in a terracotta pot, just the top leaves peeking into frame.

Composition: vertical 9:16 portrait. The entire CENTER vertical column (middle ~60% of the width, top to bottom) must be EMPTY wooden surface — clear, soft, slightly out of focus — so an iPhone-shaped object can sit centered with a natural shadow.

Palette: warm honey/walnut wood, cream ceramic, dark coffee, tan leather, terracotta, sage green, late-afternoon warmth. Mood: premium editorial magazine flat-lay, calm and resolved — NOT stocky, NOT chaotic.

NO people, NO hands, NO phones, NO text, NO logos, NO scattered papers or clutter. Subtle wood grain, nothing busy that competes with the phone overlay. Photographic realism, full-frame DSLR look, top-down 90°, shallow DOF at the outer edges, warm color science, no AI-art polish."""


def load_fal_key():
    if load_dotenv:
        # Load the skill-folder .env (scripts/.. = skill root) without overriding real env.
        skill_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        load_dotenv(os.path.join(skill_root, ".env"))
    key = os.environ.get("FAL_KEY") or os.environ.get("FAL_API_KEY")
    if not key:
        sys.exit("ERROR: no FAL_KEY in env or .env. Copy .env.example to .env and fill FAL_KEY.")
    return key


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", help="project dir; writes <project>/assets/flat-lay-bg.jpg")
    ap.add_argument("--out", help="explicit output path (overrides --project)")
    args = ap.parse_args()

    out = args.out
    prompt = DEFAULT_PROMPT
    if args.project:
        proj = os.path.abspath(args.project)
        out = out or os.path.join(proj, "assets", "flat-lay-bg.jpg")
        prompt_file = os.path.join(proj, "flat-lay-prompt.txt")
        if os.path.exists(prompt_file):
            prompt = open(prompt_file).read().strip()
            print(f"Using brand prompt from {prompt_file}")
    if not out:
        ap.error("pass --project or --out")

    os.environ["FAL_KEY"] = load_fal_key()
    import fal_client  # requires `pip install -r requirements.txt`

    print("Submitting fal-ai/gpt-image-1 (quality=high, 1024x1536, ~$0.19)...")
    res = fal_client.subscribe(
        "fal-ai/gpt-image-1/text-to-image",
        arguments={"prompt": prompt, "image_size": "1024x1536", "quality": "high", "num_images": 1},
    )
    url = res["images"][0]["url"]
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    urllib.request.urlretrieve(url, out)
    json.dump({"model": "fal-ai/gpt-image-1/text-to-image", "image_size": "1024x1536",
               "quality": "high", "source_url": url, "cost_estimate_usd": 0.19},
              open(out + ".meta.json", "w"), indent=2)
    print("saved", out)


if __name__ == "__main__":
    main()
