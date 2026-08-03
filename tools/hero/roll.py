#!/usr/bin/env python3
"""The roll call: every public repository, by name, accelerating.

Ninety-eight names replace each other in the same spot, each one held a little
less than the one before, until the list stops being readable and becomes a
texture — which is the honest way to show a number this size. You can read the
first ones; by the end you can only feel how many there are.

The ones that earned something come up in full white and full weight; the ones
that did not stay grey and thin. No language colours here — fifteen hues in a
three-second run reads as decoration, and the language already says what it has
to say in the river, on the suns, where it carries information instead of
sparkle. Nothing else is on screen while a name is: the frame belongs to one
thing at a time.

The cadence is a power law, not a constant step: t(i) = T·(i/n)^0.62 spaces the
early names apart and packs the late ones, so the acceleration is felt rather
than announced.

Every name is set to the same measure. Ninety-eight names of ninety-eight
different widths flashing in one spot makes the eye jump on every frame; fitted
to a common width the run becomes a pulse instead of a stutter, and the varying
size reads as a fact about the name (long ones are set smaller) rather than as
noise. Mono, because the advance width is exact arithmetic and because these
are identifiers - this beat is a listing, not a headline.

They arrive from below and leave upward, one hard step each: at nineteen
milliseconds a tween is a smear, but a jump has direction, and direction is
what makes a fast list feel like it is moving rather than blinking.
"""
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
    # names all the way to the flash: the count was one more thing to read at
    # the end of a run whose whole point is that you stop reading
    span = (t1 - 0.42) - t0

    for i, rp in enumerate(repos):
        nm = rp["name"]
        lit = rp["stargazerCount"] > 0 or rp["forkCount"] > 0
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
        # one measure for all of them: size follows from the name's length
        sz = max(25.0, min(92.0, MEASURE / (len(nm) * 0.6 + 0.4)))
        css.append(f"@keyframes rl{i}{{"
                   f"0%,{pc(a):.3f}%{{opacity:0;transform:translateY(11px)}}"
                   f"{pc(on):.3f}%{{opacity:1;transform:translateY(0);"
                   f"animation-timing-function:steps(1,end)}}"
                   f"{pc(off):.3f}%{{opacity:1;transform:translateY(0)}}"
                   f"{pc(b):.3f}%,100%{{opacity:0;transform:translateY(-11px)}}}}")
        css.append(f".rl{i}{{opacity:0;animation:rl{i} {LOOP:g}s linear infinite}}")
        # the name itself lights up, in the colour of its own language. A dot
        # beside it would be a second thing on screen, and the frame belongs to
        # one thing at a time.
        SAYS.append(f'<g class="rl{i}">'
                    + txt(W / 2, 216, nm, round(sz, 1), ink if lit else faint, 0.4,
                          "middle", 700 if lit else 400, halo=5)
                    + "</g>")

    # a rule the names sit on, the exact measure they are fitted to: something
    # still to hold the eye while everything above it flickers
    css.append(f"@keyframes rlr{{0%,{pc(t0):.2f}%{{opacity:0;transform:scaleX(.2)}}"
               f"{pc(t0+0.22):.2f}%,{pc(t0+span):.2f}%{{opacity:.5;transform:scaleX(1)}}"
               f"{pc(t1-0.3):.2f}%,100%{{opacity:0;transform:scaleX(.2)}}}}")
    css.append(f".rlr{{opacity:0;transform-box:fill-box;transform-origin:center;"
               f"animation:rlr {LOOP:g}s cubic-bezier(.2,1,.3,1) infinite}}")
    SAYS.append(f'<rect class="rlr" x="{W/2 - MEASURE/2:.0f}" y="238" '
                f'width="{MEASURE}" height="1.5" fill="{mut}"/>')
