"""Shared helpers for the create-cinematic-music-video pipeline scripts.

Loads .env from the skill folder root, sets FAL_KEY for fal_client, and exposes
small helpers for project paths, look-pack loading, ffmpeg probes, and locating
a libass-enabled ffmpeg binary for the caption burn.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import sys
import time
from functools import lru_cache
from typing import Any

from dotenv import load_dotenv

# Resolve the skill folder (parent of scripts/) and load .env from there.
SKILL_ROOT = pathlib.Path(__file__).resolve().parent.parent
load_dotenv(SKILL_ROOT / ".env")

# fal_client reads FAL_KEY, not FAL_API_KEY. Alias if only the latter is set.
if "FAL_KEY" not in os.environ and "FAL_API_KEY" in os.environ:
    os.environ["FAL_KEY"] = os.environ["FAL_API_KEY"]


def require_env(name: str) -> str:
    val = os.environ.get(name, "").strip()
    if not val:
        sys.exit(f"ERROR: {name} is not set. Copy .env.example to .env and fill in your keys.")
    return val


def run_root_for(concept_path: str | pathlib.Path) -> pathlib.Path:
    """The run folder is the directory that holds concept.json."""
    return pathlib.Path(concept_path).resolve().parent


def ensure_dir(path: pathlib.Path) -> pathlib.Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_meta(path: pathlib.Path, meta: dict[str, Any]) -> None:
    """Write a sibling .meta.json next to an artifact, with a created_at stamp."""
    meta = {"created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **meta}
    path.with_suffix(path.suffix + ".meta.json").write_text(json.dumps(meta, indent=2))


def ffprobe_duration(path: str | pathlib.Path) -> float:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)]
    )
    return float(out.decode().strip())


def ffprobe_resolution(path: str | pathlib.Path) -> tuple[int, int]:
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "csv=p=0", str(path)]
    )
    w, h = out.decode().strip().split(",")[:2]
    return int(w), int(h)


def info(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def die(msg: str) -> None:
    sys.exit(f"ERROR: {msg}")


# ----- look packs -------------------------------------------------------------

def load_lookpack(pack_id: str, skill_root: pathlib.Path = SKILL_ROOT) -> dict:
    """Read a look-pack markdown file and extract its STYLE_OPENER + NEGATIVE_TAIL.

    A look pack locks the photographic style across every keyframe. The two
    fenced code blocks under the `## STYLE_OPENER` and `## NEGATIVE_TAIL`
    headings are injected at the head and tail of each tableau prompt.
    """
    pack_file = skill_root / "lookpacks" / f"{pack_id}.md"
    if not pack_file.exists():
        avail = ", ".join(p.stem for p in sorted((skill_root / "lookpacks").glob("*.md")))
        die(f"look pack not found: {pack_id}. Available: {avail}")
    text = pack_file.read_text()
    blocks = re.findall(r"```\n([\s\S]+?)\n```", text)
    if len(blocks) < 2:
        die(f"look pack {pack_id} is missing the STYLE_OPENER or NEGATIVE_TAIL fenced block")
    return {"opener": blocks[0].strip(), "tail": blocks[1].strip()}


def compose_keyframe_prompt(pack: dict, tableau_prompt: str) -> str:
    """STYLE_OPENER + tableau.prompt + NEGATIVE_TAIL → one nano-banana prompt."""
    return f"{pack['opener']} {tableau_prompt.strip()} {pack['tail']}"


# ----- captions: libass-enabled ffmpeg ---------------------------------------

@lru_cache(maxsize=1)
def _system_ffmpeg_has_libass() -> bool:
    """True if the ffmpeg on PATH was built with the subtitles/ass filter."""
    try:
        out = subprocess.run(
            ["ffmpeg", "-hide_banner", "-filters"],
            capture_output=True, text=True, check=True,
        ).stdout
    except Exception:
        return False
    return bool(re.search(r"^\s*\S*\s+(?:ass|subtitles)\s", out, re.MULTILINE))


def ffmpeg_with_libass() -> str:
    """Return a path to an ffmpeg binary that can burn ASS subtitles.

    Prefers the system ffmpeg when it ships libass (the common case). Falls
    back to the static binary from the `imageio-ffmpeg` pip package, which is
    always libass-enabled — this is the portable escape hatch for the
    Homebrew-ffmpeg-without-libass situation on macOS.
    """
    if _system_ffmpeg_has_libass():
        return "ffmpeg"
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        die(
            "no libass-enabled ffmpeg found. Either install an ffmpeg with libass "
            "(macOS: `brew install ffmpeg`; Debian/Ubuntu: `apt install ffmpeg`) or "
            "`pip install imageio-ffmpeg` for a bundled static binary."
        )
