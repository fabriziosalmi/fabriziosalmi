#!/usr/bin/env python3
"""Render the profile strip from data/profile.json.

    python3 tools/render_hero.py data/profile.json .

Writes hero-{dark,light}.svg (wide) and hero-m-{dark,light}.svg (phone). The drawing lives in tools/ticker.py.
The "vs <date>" line compares against the last committed profile.json that
differs from the one being rendered, so a same-day rerun or a night without a
commit still says something true.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ticker import THEMES, build, load


def previous(path):
    """(profile, commit date) of the newest committed copy that differs, or (None, '')."""
    here, name = os.path.dirname(os.path.abspath(path)), os.path.basename(path)
    try:
        cur = json.load(open(path))
        log = subprocess.run(["git", "log", "-n", "10", "--format=%H %cs", "--", name], cwd=here,
                             capture_output=True, text=True, check=True).stdout.split("\n")
        for line in filter(None, log):
            sha, date = line.split()
            old = json.loads(subprocess.run(["git", "show", f"{sha}:./{name}"], cwd=here,
                                            capture_output=True, text=True, check=True).stdout)
            if old != cur:
                return load(old), date
    except (OSError, ValueError, subprocess.CalledProcessError):
        pass
    return None, ""


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "data/profile.json"
    outdir = sys.argv[2] if len(sys.argv) > 2 else "."
    S = load(json.load(open(src)))
    P, since = previous(src)
    for th, T in THEMES.items():
        for wide, name in ((True, f"hero-{th}.svg"), (False, f"hero-m-{th}.svg")):
            doc = build(S, P, since, T, wide)
            p = os.path.join(outdir, name)
            open(p, "w", encoding="utf-8").write(doc)
            print(p, len(doc.encode()), "bytes", f"(vs {since})" if P else "(no previous)")
