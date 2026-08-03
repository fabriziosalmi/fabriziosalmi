#!/usr/bin/env python3
"""An eye at the centre of the ring, where the spiral used to be.

It looks around first — in jumps, not in sweeps, because that is what eyes do:
six saccades around the rim of its own socket, each held still and then flicked
to the next. Then the pupil dilates the way a cat's does when something moves,
goes red, and burns to white before the frame tears.

Nothing here is decoration: the eye is the only thing on screen that behaves
like it is watching the data rather than displaying it.
"""
import math

from .geometry import LOOP, pc


def render(d, cx, cy, t0, t1):
    css, add, T = d.css, d.add, d.T
    line = d.line

    look_end = t0 + (t1 - t0) * 0.52      # saccades
    dilate = look_end + 0.30              # the pupil opens
    red = dilate + 0.34                   # and colour drains into it
    white = red + 0.26                    # then it burns

    # the socket, and the iris that never moves
    add(f'<circle class="act0" cx="{cx}" cy="{cy}" r="30" fill="{T["disc"]}" '
        f'fill-opacity="{0.10 if d.th == "dark" else 0.035}" stroke="{line}" stroke-width="1"/>')
    add(f'<circle class="act0" cx="{cx}" cy="{cy}" r="17" fill="none" '
        f'stroke="{T["warm"]}" stroke-width="1.4" opacity="0.55"/>')

    # the pupil. Six looks, each one a jump: steps(1,end) holds the position and
    # then snaps, which is how a saccade reads. A tween would read as a machine.
    N = 6
    kf = [f"0%,{pc(t0):.2f}%{{transform:translate(0,0) scale(1);fill:{T['ink']}}}"]
    for i in range(N):
        a = math.radians(-58 + i * 360 / N * 1.31)
        r = 7.5 if i % 2 else 5.0
        t = t0 + (look_end - t0) * (i + 1) / (N + 1)
        kf.append(f"{pc(t):.2f}%{{transform:translate({r*math.cos(a):.1f}px,"
                  f"{r*math.sin(a):.1f}px) scale(1);fill:{T['ink']};"
                  f"animation-timing-function:steps(1,end)}}")
    kf += [f"{pc(look_end):.2f}%{{transform:translate(0,0) scale(1);fill:{T['ink']}}}",
           f"{pc(dilate):.2f}%{{transform:translate(0,0) scale(1.85);fill:{T['ink']}}}",
           f"{pc(red):.2f}%{{transform:translate(0,0) scale(2.05);fill:#e5484d}}",
           f"{pc(white):.2f}%{{transform:translate(0,0) scale(2.35);fill:#ffffff}}",
           f"{pc(t1):.2f}%,100%{{transform:translate(0,0) scale(1);fill:{T['ink']}}}"]
    css.append("@keyframes pup{" + "".join(kf) + "}")
    css.append(f".pup{{transform-box:fill-box;transform-origin:center;"
               f"animation:pup {LOOP:g}s cubic-bezier(.3,0,.2,1) infinite}}")
    add(f'<circle class="act0 pup" cx="{cx}" cy="{cy}" r="6.5" fill="{T["ink"]}"/>')

    # the glare it picks up once it is wide open
    css.append(f"@keyframes pupg{{0%,{pc(red):.2f}%{{opacity:0}}"
               f"{pc(white):.2f}%{{opacity:.9}}{pc(t1):.2f}%,100%{{opacity:0}}}}")
    css.append(f".pupg{{opacity:0;animation:pupg {LOOP:g}s ease-out infinite}}")
    add(f'<circle class="act0 pupg" cx="{cx}" cy="{cy}" r="26" fill="none" '
        f'stroke="#ffffff" stroke-width="2" filter="url(#gl)"/>')
