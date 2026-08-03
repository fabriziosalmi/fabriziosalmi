#!/usr/bin/env python3
"""The prompt that opens and closes the loop, and the gap it explodes into.
The last line is the point: tomorrow this is a different picture."""
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
    # ============================================================ THE TERMINAL
    # The loop opens on a prompt and closes on one. It says what this is, and
    # the last line says the part that matters: tomorrow it will be different.
    # Typing and crumbling are per glyph. A clip rectangle is cheaper, but it
    # can only wipe: it cannot let a line come apart. Mono is monospaced, so
    # every character position is exact arithmetic - no measuring needed.
    TSZ, TCH = 23, 23 * 0.6 + 0.6
    TX, TY = LX, 196
    cmd = "$ git clone https://github.com/fabriziosalmi"
    nch = len(cmd)
    css.append(
        f"@keyframes car{{0%{{transform:translateX(0)}}"
        f"{pc(T_TERM-0.35):.2f}%,{pc(T_OUT):.2f}%{{transform:translateX({nch*TCH:.0f}px)}}"
        f"{pc(LOOP-0.05):.2f}%,100%{{transform:translateX({nch*TCH:.0f}px)}}}}")
    css.append(f".car{{animation:car {LOOP:g}s steps({nch}) infinite,"
               f"blink 1.06s steps(1,end) infinite}}")

    # the terminal block is present at both ends of the loop and nowhere else
    css.append(
        f"@keyframes term{{0%{{opacity:1}}{pc(T_TERM+0.1):.2f}%{{opacity:1}}"
        f"{pc(T_TERM+0.22):.2f}%,{pc(T_OUT-0.28):.2f}%{{opacity:0}}"
        f"{pc(T_OUT-0.1):.2f}%,100%{{opacity:1}}}}")
    css.append(f".term{{animation:term {LOOP:g}s ease-in-out infinite}}")

    # THE GAP. The terminal does not dissolve into the wall - it distorts, and
    # then the whole frame drops to the page's own colour for a fifth of a
    # second. Nothing is on screen. The story comes out of that nothing, and at
    # the end it goes back in the same way.
    for gi, gt in ((0, T_TERM), (1, T_OUT - 0.5)):
        css.append(f"@keyframes gap{gi}{{0%,{pc(gt):.2f}%{{opacity:0}}"
                   f"{pc(gt+0.16):.2f}%,{pc(gt+0.34):.2f}%{{opacity:1}}"
                   f"{pc(gt+0.62):.2f}%,100%{{opacity:0}}}}")
        css.append(f".gap{gi}{{opacity:0;animation:gap{gi} {LOOP:g}s cubic-bezier(.7,0,.3,1) infinite}}")

    add('<g class="term">')

    def crumble(prefix, text, x0, y0, size, col, t_type0, t_type1, t_fall,
                fall_dur=0.5, back=None, seed=7):
        """A line that types itself in and then falls apart.

        The stagger of the fall is seeded, not left to right: a line that
        crumbles in reading order reads as a wipe. Each glyph gets its own
        drop, spin and delay, and the same seed always produces the same
        collapse - the crumble is part of the artefact, not of the runtime.
        """
        rng = RNG(seed * 977 + len(text))
        step = (t_type1 - t_type0) / max(len(text), 1)
        ch_w = size * 0.6 + 0.6
        for i, ch in enumerate(text):
            if ch == " ":
                continue
            tin = t_type0 + i * step
            lag = rng.uni(0.0, 0.30)          # seeded, so the fall is not a wipe
            dy = rng.uni(26, 74)
            rot = rng.uni(-38, 38)
            fs, fe = t_fall + lag, t_fall + lag + fall_dur
            gone = f"opacity:0;transform:translateY({dy:.0f}px) rotate({rot:.0f}deg)"
            kf = [f"0%,{pc(tin):.2f}%{{opacity:0;transform:translateY(-5px)}}",
                  f"{pc(tin+0.012):.2f}%{{opacity:1;transform:translateY(0) rotate(0);"
                  f"animation-timing-function:steps(1,end)}}",
                  f"{pc(fs):.2f}%{{opacity:1;transform:translateY(0) rotate(0)}}",
                  f"{pc(fe):.2f}%{{{gone}}}"]
            if back is not None:
                kf += [f"{pc(back-0.12):.2f}%{{{gone}}}",
                       f"{pc(back):.2f}%{{opacity:1;transform:translateY(0) rotate(0)}}",
                       f"{pc(LOOP-0.45):.2f}%{{opacity:1;transform:translateY(0) rotate(0)}}",
                       f"{pc(LOOP-0.05):.2f}%,100%{{opacity:0;transform:translateY(-5px)}}"]
            else:
                kf += [f"{pc(LOOP-0.05):.2f}%,100%{{opacity:0;transform:translateY(-5px)}}"]
            cls = f"{prefix}{i}"
            css.append(f"@keyframes {cls}{{" + "".join(kf) + "}")
            css.append(f".{cls}{{opacity:0;animation:{cls} {LOOP:g}s cubic-bezier(.5,0,.75,.4) infinite}}")
            add(txt(x0 + i * ch_w, y0, ch, size, col, 0, weight=600, cls="t " + cls, halo=3))

    # typed, then held long enough to be read, then dropped - and all of it
    # has to finish before the gap covers the frame
    crumble("tc", cmd, TX, TY, TSZ, ink, 0.45, T_TERM - 0.95, T_TERM - 0.62,
            fall_dur=0.34, back=T_OUT - 0.05, seed=11)
    add(f'<rect class="car" x="{TX}" y="{TY-TSZ*0.78:.0f}" width="{TSZ*0.55:.0f}" '
        f'height="{TSZ*0.92:.0f}" fill="{T["warm"]}"/>')

    # the closing lines: what came out, and when it changes
    OUT_L = [(f'  {fmt(S["stars"])} stars · {S["n_repos"]} repos · '
              f'{fmt(S["contrib"])} contributions', mut),
             ("  next render 04:17 UTC — tomorrow this is a different picture", faint)]
    for li, (line, col) in enumerate(OUT_L):
        t0 = T_OUT + 0.3 + li * 0.45
        crumble(f"to{li}_", line, TX, TY + 36 + li * 32, 19, col,
                t0, t0 + 0.5, LOOP - 0.42, fall_dur=0.36, seed=23 + li * 5)

    add("</g>")
