#!/usr/bin/env python3
"""The roll call: every public repository, by name, accelerating.

Ninety-eight names replace each other in the same spot, each one held a little
less than the one before, until the list stops being readable and becomes a
texture — which is the honest way to show a number this size. You can read the
first ones; by the end you can only feel how many there are.

The ones that earned something light up in the colour of their own language,
weight and all. The ones that did not stay grey and thin. Nobody is hidden, and
nothing else is on screen while a name is: the frame belongs to one thing.

The cadence is a power law, not a constant step: t(i) = T·(i/n)^0.62 spaces the
early names apart and packs the late ones, so the acceleration is felt rather
than announced.
"""
from . import icons
from .geometry import *


def render(d):
    S, T = d.S, d.T
    css, add, txt = d.css, d.add, d.txt
    ink, mut, faint = d.ink, d.mut, d.faint
    win_check = d.win_check
    SAYS = d.says

    t0, t1 = ROLL
    repos = sorted(S["repos"], key=lambda r: r["createdAt"])
    n = len(repos)
    # the last stretch belongs to the count, alone, and then to the flash:
    # nothing shares the frame with the names while they run
    span = (t1 - 0.95) - t0

    for i, rp in enumerate(repos):
        nm = rp["name"]
        lit = rp["stargazerCount"] > 0 or rp["forkCount"] > 0
        col = (rp["primaryLanguage"] or {}).get("color") or mut
        # power law: the early names breathe, the late ones stack up
        a = t0 + span * (i / n) ** 0.62
        b = t0 + span * ((i + 1) / n) ** 0.62
        # the "still lit" stop has to stay strictly inside its own window. A
        # floor on the hold time does not: past 22ms of cadence it lands after
        # the stop that turns the name off, CSS reorders the two, and the name
        # comes back on and never leaves. Every keyframe time gets checked now,
        # not just the ends.
        on = a + 0.008
        off = a + min(0.022 * 0.82, (b - a) * 0.62)
        win_check(f"roll {i}", a, on, off, b)
        sz = 46 if len(nm) <= 14 else (36 if len(nm) <= 20 else 29)
        css.append(f"@keyframes rl{i}{{0%,{pc(a):.3f}%{{opacity:0}}"
                   f"{pc(on):.3f}%{{opacity:1;animation-timing-function:steps(1,end)}}"
                   f"{pc(off):.3f}%{{opacity:1}}"
                   f"{pc(b):.3f}%,100%{{opacity:0}}}}")
        css.append(f".rl{i}{{opacity:0;animation:rl{i} {LOOP:g}s linear infinite}}")
        # the name itself lights up, in the colour of its own language. A dot
        # beside it would be a second thing on screen, and the frame belongs to
        # one thing at a time.
        SAYS.append(f'<g class="rl{i}">'
                    + txt(W / 2, 214, nm, sz, col if lit else faint, -0.5, "middle",
                          800 if lit else 500, halo=5, face=DISPLAY)
                    + "</g>")

    # the count lands after the last name, on an empty frame
    c0 = t0 + span + 0.06
    css.append(f"@keyframes rlc{{0%,{pc(c0):.2f}%{{opacity:0;transform:scale(.86)}}"
               f"{pc(c0+0.14):.2f}%,{pc(t1-0.42):.2f}%{{opacity:1;transform:scale(1)}}"
               f"{pc(t1-0.3):.2f}%,100%{{opacity:0;transform:scale(1.1)}}}}")
    css.append(f".rlc{{opacity:0;transform-box:fill-box;transform-origin:center;"
               f"animation:rlc {LOOP:g}s cubic-bezier(.2,1.5,.4,1) infinite}}")
    icons.install(css, "rli", c0 + 0.04, "repo")
    SAYS.append('<g class="rlc">'
                + txt(W / 2 - 22, 222, str(n), 92, ink, -2, "end", 800, halo=5, face=DISPLAY)
                + icons.repo(W / 2 + 20, 200, 26, mut, "rli") + "</g>")
