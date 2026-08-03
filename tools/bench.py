#!/usr/bin/env python3
"""Measure the artefact and keep the measurement.

    python3 tools/bench.py            # measure, compare, append
    python3 tools/bench.py --dry      # measure and compare, write nothing

Every row lands in data/bench.jsonl, one JSON object per line, tagged with the
commit it was taken at. The point is not the absolute numbers — it is the shape
of the curve across iterations, so a change that quietly doubles the runtime
cost shows up as a number instead of as a feeling six months later.

What is worth watching, in order:

  animated    elements carrying a CSS animation. This is the runtime bill: the
              browser recomputes style for each of them on every frame.
  filter_refs how many times a filter is switched on. Filters rasterise; they
              are the most expensive thing here and the easiest to leave on.
  gzip        what actually crosses the wire. raw is vanity.
  keyframes   rule count. Cheap to render, but it is the honest proxy for how
              much choreography is hand-authored versus shared.
"""
import gzip as gz
import hashlib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "data", "bench.jsonl")


def measure(path):
    t = open(path, encoding="utf-8").read()
    raw = t.encode()
    css = t[t.index("<style>"):t.index("</style>")]
    body = t[t.index("</defs>"):]
    return {
        "bytes_raw": len(raw),
        "bytes_gzip": len(gz.compress(raw, 9)),
        "elements": len(re.findall(r"<(rect|circle|path|text|line|g|use)[ >]", body)),
        "animated": len(re.findall(r'class="', body)),
        "keyframes": len(re.findall(r"@keyframes ", css)),
        "rules": css.count("}.") + len(re.findall(r"\n\.", css)),
        "filters_defined": len(re.findall(r"<filter ", t)),
        "filter_refs": len(re.findall(r"filter:url\(", css)) + len(re.findall(r'filter="url\(', body)),
        "sha": hashlib.sha256(raw).hexdigest()[:12],
    }


def git(*args, default="?"):
    try:
        return subprocess.run(["git", "-C", ROOT, *args], capture_output=True,
                              text=True, check=True).stdout.strip() or default
    except Exception:
        return default


def main():
    dry = "--dry" in sys.argv
    dark = measure(os.path.join(ROOT, "hero-dark.svg"))
    geo = open(os.path.join(ROOT, "tools", "hero", "geometry.py"), encoding="utf-8").read()
    loop = float(re.search(r"^LOOP = ([0-9.]+)", geo, re.M).group(1))

    row = {"commit": git("rev-parse", "--short", "HEAD"),
           "tag": git("describe", "--tags", "--abbrev=0", default=""),
           "loop_s": loop, **dark}

    prev = None
    if os.path.exists(LOG):
        lines = [l for l in open(LOG, encoding="utf-8").read().splitlines() if l.strip()]
        if lines:
            prev = json.loads(lines[-1])

    keys = ["bytes_raw", "bytes_gzip", "elements", "animated", "keyframes",
            "rules", "filters_defined", "filter_refs", "loop_s"]
    print(f"  {'':<16}{'ora':>12}{'prima':>12}{'delta':>12}")
    for k in keys:
        now = row[k]
        was = prev.get(k) if prev else None
        if was in (None, 0):
            delta = "—"
        else:
            d = (now - was) / was * 100
            delta = "=" if abs(d) < 0.05 else f"{d:+.1f}%"
        print(f"  {k:<16}{now:>12,}{(f'{was:,}' if was is not None else '—'):>12}{delta:>12}"
              .replace(",", " "))
    print(f"  {'sha':<16}{row['sha']:>12}{(prev['sha'] if prev else '—'):>12}")

    if not dry:
        os.makedirs(os.path.dirname(LOG), exist_ok=True)
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, sort_keys=True) + "\n")
        print(f"\n  registrato in {os.path.relpath(LOG, ROOT)}")


if __name__ == "__main__":
    main()
