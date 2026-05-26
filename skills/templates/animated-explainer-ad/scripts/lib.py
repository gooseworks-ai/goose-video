"""Shared helpers for the animated-explainer-ad pipeline scripts.

Loads .env from the skill folder root, sets FAL_KEY for fal_client, exposes
small helpers for project paths and HTTP retries.
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import time
from typing import Any

from dotenv import load_dotenv

# Resolve the skill folder (parent of scripts/) and load .env from there.
SKILL_ROOT = pathlib.Path(__file__).resolve().parent.parent
load_dotenv(SKILL_ROOT / ".env")

# fal_client reads FAL_KEY, not FAL_API_KEY. Alias if needed.
if "FAL_KEY" not in os.environ and "FAL_API_KEY" in os.environ:
    os.environ["FAL_KEY"] = os.environ["FAL_API_KEY"]


def require_env(name: str) -> str:
    val = os.environ.get(name, "").strip()
    if not val:
        sys.exit(f"ERROR: {name} is not set. Copy .env.example to .env and fill in your keys.")
    return val


def project_path(project: str, *parts: str) -> pathlib.Path:
    p = pathlib.Path(project).resolve()
    p.mkdir(parents=True, exist_ok=True)
    for part in parts:
        p = p / part
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def write_meta(path: pathlib.Path, meta: dict[str, Any]) -> None:
    """Write a sibling .meta.json next to an artifact, with timestamps + provenance."""
    meta = {"created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **meta}
    meta_path = path.with_suffix(path.suffix + ".meta.json")
    meta_path.write_text(json.dumps(meta, indent=2))


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
    w, h = out.decode().strip().split(",")
    return int(w), int(h)


def info(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def die(msg: str) -> None:
    sys.exit(f"ERROR: {msg}")
