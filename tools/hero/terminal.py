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
    # Typing is a clip rectangle widening in steps(n) - one animation, n chars,
    # no per-letter elements - and the caret steps along with it.
    TSZ, TCH = 23, 23 * 0.6 + 0.6
    TX, TY = LX, 196
    cmd = "$ git clone https://github.com/fabriziosalmi"
    nch = len(cmd)
    css.append(
        f"@keyframes typ{{0%{{transform:scaleX(0)}}"
        f"{pc(T_TERM-0.35):.2f}%,{pc(T_OUT):.2f}%{{transform:scaleX(1)}}"
        f"{pc(LOOP-0.05):.2f}%,100%{{transform:scaleX(1)}}}}")
    css.append(f".typ{{transform-box:fill-box;transform-origin:left;"
               f"animation:typ {LOOP:g}s steps({nch}) infinite}}")
    css.append(
        f"@keyframes car{{0%{{transform:translateX(0)}}"
        f"{pc(T_TERM-0.35):.2f}%,{pc(T_OUT):.2f}%{{transform:translateX({nch*TCH:.0f}px)}}"
        f"{pc(LOOP-0.05):.2f}%,100%{{transform:translateX({nch*TCH:.0f}px)}}}}")
    css.append(f".car{{animation:car {LOOP:g}s steps({nch}) infinite,"
               f"blink 1.06s steps(1,end) infinite}}")
    # the terminal block is present at both ends of the loop and nowhere else
    css.append(
        f"@keyframes term{{0%{{opacity:1}}{pc(T_TERM+0.22):.2f}%{{opacity:1}}"
        f"{pc(T_TERM+0.3):.2f}%,{pc(T_OUT-0.28):.2f}%{{opacity:0}}"
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
    add(f'<clipPath id="tclip"><rect class="typ" x="{TX}" y="{TY-TSZ}" '
        f'width="{nch*TCH:.0f}" height="{TSZ+10}"/></clipPath>')
    add(f'<g clip-path="url(#tclip)">'
        + txt(TX, TY, cmd, TSZ, ink, 0.6, weight=600, halo=3) + "</g>")
    add(f'<rect class="car" x="{TX}" y="{TY-TSZ*0.78:.0f}" width="{TSZ*0.55:.0f}" '
        f'height="{TSZ*0.92:.0f}" fill="{T["warm"]}"/>')

    # the closing lines: what came out, and when it changes
    OUT_L = [(f'  {fmt(S["stars"])} stars · {S["n_repos"]} repos · '
              f'{fmt(S["contrib"])} contributions', mut),
             ("  next render 04:17 UTC — tomorrow this is a different picture", faint)]
    for li, (line, col) in enumerate(OUT_L):
        t0 = T_OUT + 0.35 + li * 0.35
        css.append(f"@keyframes tl{li}{{0%,{pc(t0):.2f}%{{opacity:0;transform:translateX(-6px)}}"
                   f"{pc(t0+0.2):.2f}%,100%{{opacity:1;transform:translateX(0)}}}}")
        css.append(f".tl{li}{{opacity:0;animation:tl{li} {LOOP:g}s cubic-bezier(.2,1,.3,1) infinite}}")
        add(txt(TX, TY + 36 + li * 32, line, 19, col, 0.4, weight=600, cls=f"tl{li}", halo=3))
    add("</g>")
