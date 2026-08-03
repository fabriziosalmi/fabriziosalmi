#!/usr/bin/env python3
"""Render the profile hero from data/profile.json.

    python3 tools/render_hero.py data/profile.json .

The work lives in tools/hero/ - one module per concern. Start at hero/build.py
if you want to see the running order, or at hero/geometry.py if you want to
change when things happen.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hero import THEMES, build, load

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "data/profile.json"
    outdir = sys.argv[2] if len(sys.argv) > 2 else "."
    S = load(src)
    for th, T in THEMES.items():
        doc = build(S, th, T)
        p = os.path.join(outdir, f"hero-{th}.svg")
        open(p, "w", encoding="utf-8").write(doc)
        print(p, len(doc), "bytes")
