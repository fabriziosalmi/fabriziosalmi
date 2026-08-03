#!/usr/bin/env python3
"""The statements. Each one owns the whole canvas for its beat: nothing has to
shrink to make room for a drawing, so a number can be 108px."""
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
    # ============================================================ left column


    # ---- the statements. Each one owns the whole canvas for its beat, centred,
    #      so nothing has to shrink to make room for a drawing.
    CXT = W // 2

    def say(cls, t0, t1, rows, rise=14):
        """One statement: a stack of centred lines that lands, holds, and leaves."""
        win_check(cls, t0, t0 + 0.18, t1 - 0.16, t1)
        css.append(f"@keyframes {cls}{{0%,{pc(t0):.2f}%{{opacity:0;transform:translateY({rise}px)}}"
                   f"{pc(t0+0.18):.2f}%{{opacity:1;transform:translateY(0)}}"
                   f"{pc(t1-0.16):.2f}%{{opacity:1;transform:translateY(0)}}"
                   f"{pc(t1):.2f}%,100%{{opacity:0;transform:translateY(-{rise*0.7:.0f}px)}}}}")
        css.append(f".{cls}{{opacity:0;animation:{cls} {LOOP:g}s cubic-bezier(.2,1,.3,1) infinite}}")
        g = [f'<g class="{cls}">']
        for (yy, tx, sz, col, ls, wt) in rows:
            g.append(txt(CXT, yy, tx, sz, col, ls, "middle", wt, halo=max(3, sz * 0.09)))
        g.append("</g>")
        SAYS.append("".join(g))

    say("sname", *SAY_NAME, [(178, "FABRIZIO SALMI", 76, ink, 5, 700),
                             (222, "INFRASTRUCTURE × SECURITY × AI AGENCY", 21, mut, 2, 600)])

    F = [(fmt(S["contrib"]), "PUBLIC CONTRIBUTIONS"),
         (str(S["active_days"]), "DAYS OUT OF 366"),
         (fmt(S["peak"]), "PEAK IN ONE DAY")]
    step = (SAY_1[1] - SAY_1[0]) / len(F)
    for fi, (big, lab) in enumerate(F):
        t0 = SAY_1[0] + fi * step
        say(f"sf{fi}", t0, t0 + step, [(212, big, 108, hi[0], 2, 700),
                                       (252, lab, 24, ink, 5, 600)])

    say("stot", SAY_2[1] - 1.15, SAY_2[1],
        [(196, f'{sum(r["s"] for r in S["river"]):,}', 108, T["riv_star"], 2, 700),
         (236, "STARS", 24, ink, 6, 600),
         (276, f'{sum(r["f"] for r in S["river"]):,} FORKS · '
               f'{len(S["river"])} REPOSITORIES', 22, mut, 2, 600)])
