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
        win_check(cls, t0, t0 + 0.20, t1 - 0.18, t1)
        # a focus pull, not a fade: it arrives soft and slightly large, then
        # snaps. Costs one filter and reads as intent rather than as a transition.
        css.append(f"@keyframes {cls}{{"
                   f"0%,{pc(t0):.2f}%{{opacity:0;transform:translateY({rise}px) scale(1.045);"
                   f"filter:blur(7px)}}"
                   f"{pc(t0+0.20):.2f}%{{opacity:1;transform:translateY(0) scale(1);filter:blur(0)}}"
                   f"{pc(t1-0.18):.2f}%{{opacity:1;transform:translateY(0) scale(1);filter:blur(0)}}"
                   f"{pc(t1):.2f}%,100%{{opacity:0;transform:translateY(-{rise*0.7:.0f}px) scale(.985);"
                   f"filter:blur(5px)}}}}")
        css.append(f".{cls}{{opacity:0;animation:{cls} {LOOP:g}s cubic-bezier(.2,1,.3,1) infinite}}")
        g = [f'<g class="{cls}">']
        for row in rows:
            yy, tx, sz, col, ls, wt = row[:6]
            face = row[6] if len(row) > 6 else (DISPLAY if sz >= 40 else None)
            g.append(txt(CXT, yy, tx, sz, col, ls, "middle", wt,
                         halo=max(3, sz * 0.085), face=face))
        g.append("</g>")
        SAYS.append("".join(g))

    say("sname", *SAY_NAME, [(180, "FABRIZIO SALMI", 84, ink, -1.5, 800),
                             (224, "INFRASTRUCTURE × SECURITY × AI AGENCY", 20, mut, 4.5, 600)])

    F = [(fmt(S["contrib"]), "PUBLIC CONTRIBUTIONS"),
         (str(S["active_days"]), "DAYS OUT OF 366"),
         (fmt(S["peak"]), "PEAK IN ONE DAY")]
    step = (SAY_1[1] - SAY_1[0]) / len(F)
    for fi, (big, lab) in enumerate(F):
        t0 = SAY_1[0] + fi * step
        say(f"sf{fi}", t0, t0 + step, [(214, big, 122, hi[0], -3.5, 800),
                                       (256, lab, 22, ink, 7, 600)])

    say("stot", SAY_2[1] - 1.15, SAY_2[1],
        [(198, f'{sum(r["s"] for r in S["river"]):,}', 122, T["riv_star"], -3.5, 800),
         (238, "STARS", 22, ink, 8, 600),
         (278, f'{sum(r["f"] for r in S["river"]):,} FORKS · '
               f'{len(S["river"])} REPOSITORIES', 20, mut, 3, 600)])
