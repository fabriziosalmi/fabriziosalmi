#!/usr/bin/env python3
"""The dial: disc, tick crown, progress arc. Act 01 only - a circle around
a horizontal river is the wrong frame, so it leaves with its act."""
from .geometry import *
from .rng import RNG
import math


def render(d):
    S, T, th = d.S, d.T, d.th
    css, add, txt, esc = d.css, d.add, d.txt, d.esc
    ink, mut, faint = d.ink, d.mut, d.faint
    line, hair, acc, hi = d.line, d.hair, d.acc, d.hi
    win_check, impact, stagger = d.win_check, d.impact, d.stagger
    SQUARES, SAYS = d.squares, d.says
    G = d.G
    # ============================================================ the dial
    add('<g class="act0">')   # the dial belongs to act 01 only
    add(f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="url(#discG)" stroke="{line}" stroke-opacity="{T["line_op"]}" stroke-width="1"/>')
    add(f'<circle cx="{CX}" cy="{CY}" r="{R-10}" fill="none" stroke="{hair}" stroke-opacity="{T["hair_op"]}" stroke-width="1"/>')

    # tick crown, turning very slowly
    tk = ['<g class="spin">']
    for i in range(96):
        ang = i * 360 / 96
        r0 = R + 4
        r1 = R + (13 if i % 8 == 0 else 8)
        x0, y0 = pol(r0, ang)
        x1, y1 = pol(r1, ang)
        tk.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{line}" '
                  f'stroke-width="{1.4 if i%8==0 else 0.9}" opacity="{0.9 if i%8==0 else 0.45}"/>')
    tk.append("</g>")
    add("".join(tk))

    # progress arc: one full turn per loop, one colour per act
    CIRC = 2 * math.pi * (R + 18)
    css.append(f"@keyframes prog{{0%,{pc(ACTW[0][0]):.2f}%{{stroke-dashoffset:{CIRC:.0f}}}"
               f"{pc(ACTW[-1][1]):.2f}%,100%{{stroke-dashoffset:0}}}}")
    css.append(f".prog{{stroke-dasharray:{CIRC:.0f};animation:prog {LOOP:g}s linear infinite}}")
    for a in range(NACT):
        t0, t1 = ACTW[a]
        css.append(f"@keyframes pc{a}{{0%,{pc(t0):.2f}%{{opacity:0}}{pc(t0+0.01):.2f}%,"
                   f"{pc(t1):.2f}%{{opacity:.95}}{pc(t1+0.01):.2f}%,100%{{opacity:0}}}}")
        css.append(f".pcol{a}{{opacity:0;animation:pc{a} {LOOP:g}s steps(1,end) infinite}}")
        add(f'<g class="pcol{a}"><circle class="prog" cx="{CX}" cy="{CY}" r="{R+18}" fill="none" '
            f'stroke="{hi[a]}" stroke-width="2" stroke-linecap="round" '
            f'transform="rotate(-90 {CX} {CY})" filter="url(#gl)"/></g>')

    add("</g>")   # end of the dial chrome
