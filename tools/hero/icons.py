#!/usr/bin/env python3
"""Three marks instead of three words: star, fork, repository.

Drawn from geometry rather than pasted as octicon path data. A five-pointed
star is trigonometry, a fork is three nodes and two arcs, a repository is a
book — computing them keeps the file deterministic, lets the weight match the
type it sits under, and removes the risk of a mistyped path rendering as
garbage on someone else's profile.

Each one has an entrance of its own: the star turns into place, the fork draws
its own branches, the book opens. They leave with whatever statement carries
them.
"""
import math

from .geometry import LOOP, pc


def _pts(cx, cy, r, n, rot=-90):
    return [(cx + r * math.cos(math.radians(rot + i * 360 / n)),
             cy + r * math.sin(math.radians(rot + i * 360 / n))) for i in range(n)]


def star(cx, cy, r, fill, cls):
    """Five points, outer radius r, inner radius at the golden ratio."""
    o = _pts(cx, cy, r, 5)
    i = _pts(cx, cy, r * 0.382, 5, rot=-90 + 36)
    d = "M" + " L".join(f"{p[0]:.1f},{p[1]:.1f} L{q[0]:.1f},{q[1]:.1f}"
                        for p, q in zip(o, i)) + " Z"
    return f'<path class="{cls}" d="{d}" fill="{fill}"/>'


def fork(cx, cy, r, col, cls):
    """Two branches leaving one trunk, three nodes: the shape everyone knows."""
    top, dx, dy = cy - r, r * 0.72, r * 0.62
    n = r * 0.30
    return (f'<g class="{cls}">'
            f'<path d="M{cx:.1f},{cy+r*0.18:.1f} L{cx:.1f},{cy-r*0.1:.1f} '
            f'C{cx:.1f},{top+dy:.1f} {cx-dx:.1f},{top+dy:.1f} {cx-dx:.1f},{top:.1f} '
            f'M{cx:.1f},{cy-r*0.1:.1f} '
            f'C{cx:.1f},{top+dy:.1f} {cx+dx:.1f},{top+dy:.1f} {cx+dx:.1f},{top:.1f}" '
            f'fill="none" stroke="{col}" stroke-width="{r*0.30:.1f}" stroke-linecap="round"/>'
            f'<circle cx="{cx-dx:.1f}" cy="{top:.1f}" r="{n:.1f}" fill="{col}"/>'
            f'<circle cx="{cx+dx:.1f}" cy="{top:.1f}" r="{n:.1f}" fill="{col}"/>'
            f'<circle cx="{cx:.1f}" cy="{cy+r*0.62:.1f}" r="{n:.1f}" fill="{col}"/></g>')


def repo(cx, cy, r, col, cls):
    """A book: a spine on the left, a cover, and the gap between them."""
    w, h = r * 1.62, r * 1.9
    x, y = cx - w / 2, cy - h / 2
    sp = w * 0.22
    return (f'<g class="{cls}">'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{r*0.18:.1f}" fill="none" stroke="{col}" stroke-width="{r*0.26:.1f}"/>'
            f'<path d="M{x+sp:.1f},{y:.1f} L{x+sp:.1f},{y+h:.1f}" stroke="{col}" '
            f'stroke-width="{r*0.26:.1f}" stroke-linecap="round"/></g>')


def install(css, cls, t0, kind):
    """The entrance. Everything leaves with the statement that carries it."""
    if kind == "star":
        kf = (f"0%,{pc(t0):.2f}%{{opacity:0;transform:rotate(-72deg) scale(.2)}}"
              f"{pc(t0+0.34):.2f}%,100%{{opacity:1;transform:rotate(0) scale(1)}}")
        ease = "cubic-bezier(.24,1.5,.4,1)"
    elif kind == "fork":
        kf = (f"0%,{pc(t0):.2f}%{{opacity:0;transform:scale(.35) translateY(6px)}}"
              f"{pc(t0+0.3):.2f}%,100%{{opacity:1;transform:scale(1) translateY(0)}}")
        ease = "cubic-bezier(.24,1.6,.4,1)"
    else:
        kf = (f"0%,{pc(t0):.2f}%{{opacity:0;transform:scaleX(.15)}}"
              f"{pc(t0+0.3):.2f}%,100%{{opacity:1;transform:scaleX(1)}}")
        ease = "cubic-bezier(.2,1.4,.35,1)"
    css.append(f"@keyframes {cls}{{{kf}}}")
    # the box matters: without it the origin is the centre of the canvas and the
    # mark swings in from somewhere else entirely on its way to landing
    css.append(f".{cls}{{opacity:0;transform-box:fill-box;transform-origin:center;"
               f"animation:{cls} {LOOP:g}s {ease} infinite}}")
