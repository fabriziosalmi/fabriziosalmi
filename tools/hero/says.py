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

    exits = [0]

    def say(cls, t0, t1, rows, rise=14):
        """One statement: a stack of centred lines that lands, holds, and leaves."""
        win_check(cls, t0, t0 + 0.20, t1 - 0.18, t1)
        # In: a focus pull, not a fade - soft and slightly large, then it snaps.
        # Out: it does not dissolve, it leaves. A hard ease-out shove toward the
        # viewer, directional smear, and the field bends under it. Each statement
        # gets a different push from the same family, so the loop never repeats
        # itself and never contradicts itself either.
        v = exits[0] % 3
        exits[0] += 1
        sx, sy = ((1.34, 1.16), (1.22, 1.30), (1.42, 1.08))[v]
        sk = (-7.5, 5.5, -3.5)[v]
        css.append(f"@keyframes {cls}{{"
                   f"0%,{pc(t0):.2f}%{{opacity:0;transform:translateY({rise}px) scale(1.045);"
                   f"filter:blur(7px)}}"
                   f"{pc(t0+0.20):.2f}%{{opacity:1;transform:translateY(0) scale(1);filter:blur(0)}}"
                   f"{pc(t1-0.30):.2f}%{{opacity:1;transform:translateY(0) scale(1);filter:blur(0);"
                   f"animation-timing-function:cubic-bezier(.16,.86,.3,1)}}"
                   f"{pc(t1-0.12):.2f}%{{opacity:.85;transform:scale({sx:.2f},{sy:.2f}) "
                   f"skewX({sk}deg);filter:url(#warp{v})}}"
                   f"{pc(t1):.2f}%,100%{{opacity:0;transform:scale({sx*1.5:.2f},{sy*1.35:.2f}) "
                   f"skewX({sk*1.6:.1f}deg);filter:url(#warp{v})}}}}")
        css.append(f".{cls}{{opacity:0;animation:{cls} {LOOP:g}s cubic-bezier(.2,1,.3,1) infinite}}")
        g = [f'<g class="t {cls}">']
        for row in rows:
            yy, tx, sz, col, ls, wt = row[:6]
            face = row[6] if len(row) > 6 else (DISPLAY if sz >= 40 else None)
            g.append(txt(CXT, yy, tx, sz, col, ls, "middle", wt,
                         halo=max(3, sz * 0.085), face=face))
            if sz >= 40:
                # one clip of the letterforms, one band of light through it
                gid = f"{cls}g{len(g)}"
                # it has to be over before the exit begins, and the beats are
                # short: it crosses while the type is still snapping into focus
                band = 190 + v * 45
                gs = t0 + 0.17 + v * 0.035
                ge = min(gs + 0.34 + v * 0.05, t1 - 0.34)
                win_check(f"{cls} glint", t0, gs, ge, t1 - 0.30)
                rev = (v == 1)
                # it only has to cross the type, not the canvas: half the
                # distance in the same beat means it can actually be seen
                # from just left of the type to just right of it, and no further:
                # the band spends the whole beat on the letters instead of most
                # of it travelling across empty canvas
                half = 215
                x0, x1 = ((CXT + half, CXT - half - band) if rev
                          else (CXT - half - band, CXT + half))
                css.append(f"@keyframes {gid}{{0%,{pc(gs):.2f}%{{transform:translateX({x0}px)}}"
                           f"{pc(ge):.2f}%,100%{{transform:translateX({x1}px)}}}}")
                css.append(f".{gid}{{animation:{gid} {LOOP:g}s cubic-bezier(.45,0,.25,1) infinite}}")
                g.append(f'<clipPath id="{gid}c">'
                         + txt(CXT, yy, tx, sz, col, ls, "middle", wt, face=face)
                         + f'</clipPath><g clip-path="url(#{gid}c)">'
                         f'<rect class="{gid}" x="0" y="{yy - sz:.0f}" width="{band}" '
                         f'height="{sz * 1.5:.0f}" fill="url(#glint)"/></g>')
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
