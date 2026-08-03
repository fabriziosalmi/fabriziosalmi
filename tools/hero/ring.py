#!/usr/bin/env python3
"""ACT 01. The 366 calendar squares do not get redrawn as a chart: each <rect>
keeps its cell and carries the one transform that turns it into a spoke, so
the match cut cannot drift."""
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
    # ------------------------------------------------------------ ACT 1 · SIGNAL
    # The 366 squares are not redrawn as bars: they ARE the bars. Each <rect>
    # lives at its calendar cell and carries the single transform that turns it
    # into a spoke of the ring, so the match cut cannot drift by a pixel.
    days = S["days"]
    vals = sorted(d["contributionCount"] for d in days)
    mx = vals[int(len(vals) * 0.96)] or max(vals) or 1   # clip at p96, see below
    r0 = 58
    LEVEL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2,
             "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}

    NF = 18
    for k in range(NF):
        out_s = T_WALL + 0.95 * k / (NF - 1)
        out_e = out_s + 0.8
        back_s = T_BACK[0] + 0.55 * k / (NF - 1)
        back_e = back_s + 0.75
        css.append(
            f"@keyframes fly{k}{{"
            f"0%,{pc(T_WALL_IN-0.2):.2f}%{{transform:translate(0,0);opacity:0;fill:var(--c0)}}"
            f"{pc(T_WALL_IN):.2f}%,{pc(out_s):.2f}%{{transform:translate(0,0);opacity:1;fill:var(--c0)}}"
            f"{pc(out_e):.2f}%,{pc(ACTW[0][1]-0.3):.2f}%{{transform:var(--t);opacity:1;fill:var(--c1)}}"
            # the ring drops to glue as soon as its act ends, instead of drifting
            # down over two seconds on top of the statements
            f"{pc(ACTW[0][1]+0.35):.2f}%{{transform:var(--t);opacity:.2;fill:var(--c1)}}"
            f"{pc(ACTW[1][0]-0.3):.2f}%{{transform:var(--t);opacity:.2;fill:var(--c1)}}"
            f"{pc(ACTW[1][0]+0.2):.2f}%,{G[0]:.1f}%{{transform:var(--t);opacity:0;fill:var(--c1)}}"
            f"{G[1]:.1f}%{{transform:translate(0,0);opacity:.92;fill:var(--c0);animation-timing-function:steps(1,end)}}"
            f"{G[2]:.1f}%{{transform:translate(0,0);opacity:.92;fill:var(--c0)}}"
            f"{G[3]:.1f}%,{pc(ACTW[-1][1]-0.2):.2f}%{{transform:var(--t);opacity:0;fill:var(--c1)}}"
            # they stay out until the very moment they fly home: without this the
            # opacity ramps 0->1 across four seconds and the ring quietly comes
            # back up underneath the river's statements
            f"{pc(back_s-0.25):.2f}%{{transform:var(--t);opacity:0}}"
            f"{pc(back_s):.2f}%{{transform:var(--t);opacity:1}}"
            f"{pc(back_e):.2f}%,{pc(T_OUT):.2f}%{{transform:translate(0,0);opacity:1;fill:var(--c0)}}"
            f"{pc(T_OUT+0.45):.2f}%,100%{{transform:translate(0,0);opacity:0;fill:var(--c0)}}}}")
        css.append(f".fly{k}{{animation:fly{k} {LOOP:g}s cubic-bezier(.5,0,.2,1) infinite}}")

    # the flight is the only moment the filter is on: a gooey pass while they
    # are in the air, off the instant they land. (Filters cost; a filter that
    # runs for 26 seconds to be seen for one is the definition of waste.)
    css.append(
        f"@keyframes melt{{0%,{pc(T_WALL-0.05):.2f}%{{filter:none}}"
        f"{pc(T_WALL):.2f}%,{pc(T_WALL+1.25):.2f}%{{filter:url(#melt)}}"
        f"{pc(T_WALL+1.5):.2f}%,{pc(T_BACK[0]-0.05):.2f}%{{filter:none}}"
        f"{pc(T_BACK[0]):.2f}%,{pc(T_BACK[1]-0.15):.2f}%{{filter:url(#melt)}}"
        f"{pc(T_BACK[1]):.2f}%,100%{{filter:none}}}}")
    css.append(f".melt{{animation:melt {LOOP:g}s steps(1,end) infinite}}")
    sq = ['<g class="melt">']
    for i2, dd in enumerate(days):
        col, row = i2 // ROWS, i2 % ROWS
        cx0 = GX + col * PITCH + CELL / 2
        cy0 = GY + row * PITCH + CELL / 2
        v = dd["contributionCount"]
        lv = LEVEL.get(dd.get("contributionLevel", "NONE"), 0)
        h = min(1.0, (v / mx) ** 0.62) * (R - 20 - r0)
        if h < 1.8:
            h = 1.8
        ang = i2 * 360 / len(days)
        tx, ty = pol(r0 + h / 2, ang)
        sc = f"translate({tx-cx0:.1f}px,{ty-cy0:.1f}px) rotate({ang:.1f}deg) scale(.24,{h/CELL:.3f})"
        sq.append(f'<rect class="t fly{int(col/COLS*NF)%NF}" x="{cx0-CELL/2:.0f}" y="{cy0-CELL/2:.0f}" '
                  f'width="{CELL}" height="{CELL}" rx="2" fill="{T["cal"][lv]}" '
                  f'style="--t:{sc};--c0:{T["cal"][lv]};--c1:{T["lit"][lv]}"/>')
    sq.append("</g>")
    SQUARES[:] = ["".join(sq)]   # emitted outside the data phase: they always exist

    # the act-1 extras stay in the dial: month ticks and today, on the ring
    g = [f'<g class="dial0" clip-path="url(#disc)">']
    for i2, dd in enumerate(days):
        ang = i2 * 360 / len(days)
        if dd["date"][8:10] == "01":
            x0, y0 = pol(R - 14, ang)
            x1, y1 = pol(R - 6, ang)
            g.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{mut}" '
                     f'stroke-width="1" opacity="0.45"/>')
    ang = (len(days) - 1) * 360 / len(days)
    x0, y0 = pol(R - 26, ang)
    x1, y1 = pol(R - 8, ang)
    g.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{hi[0]}" '
             f'stroke-width="2" stroke-linecap="round" filter="url(#gl)"/>')
    g.append("</g>")
    add("".join(g))
