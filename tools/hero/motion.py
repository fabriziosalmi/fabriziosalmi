#!/usr/bin/env python3
"""How things move, and how hard they get hit.

The impact is the trauma model space23 already uses (Squirrel Eiserloh, GDC
2016): the offset is trauma**2, not trauma, and the noise is three sines at
decorrelated frequencies because pure random dithers. It is sampled here and
baked into keyframes, so the game-feel ships as a deterministic artefact
instead of as a runtime.
"""
from .geometry import *
import math


def install(d):
    """Impact system, act shells, phase envelopes. Everything that decides WHEN."""
    css = d.css
    T = d.T
    def impact(name, t0, amp=1.0, dur=0.5, steps=22, hitstop=0.07, chroma=True,
               chaos=False):
        """One impact, sampled and baked into keyframes.

        Trauma model (Squirrel Eiserloh, GDC 2016), the same one space23 uses:
        the offset is trauma**2, not trauma — a non-linear response that hits
        hard on the peaks and settles fast. The noise is three sines at
        decorrelated frequencies (poor man's Perlin-1D); pure random dithers.

        hitstop: the first milliseconds are frozen with steps(1,end). It is the
        freeze frame of the hit — without it the blow never lands.

        chaos: the middle impact only. Colour drops to greyscale, two hard
        flashes (a negative and a white blowout) with a glow, then colour comes
        back. Two frames in total: any longer and it turns into a nightclub.
        """
        ks = []
        if hitstop:
            frz = (f"transform:translate({2.5*amp:.1f}px,0) scale(1.012);"
                   f"filter:contrast(1.5) brightness(1.25)")
            ks.append((t0, frz + ";animation-timing-function:steps(1,end)"))
            ks.append((t0 + hitstop, frz))
        for i in range(1, steps + 1):
            u = i / steps
            t = t0 + hitstop + u * dur
            tr = (1.0 - u) ** 1.6                      # decadimento del trauma
            e = tr * tr * amp                          # trauma**2: the non-linearity
            nx = (math.sin(u * 31.7) + math.sin(u * 19.3) * .7 + math.sin(u * 47.1) * .4) / 2.1
            ny = (math.sin(u * 27.1 + 1.7) + math.sin(u * 41.9 + .6) * .6) / 1.6
            nr = math.sin(u * 23.3 + 2.4)
            dx, dy = nx * 15 * e, ny * 7 * e
            rot, sk = nr * 1.5 * e, nr * 1.9 * e
            sc = 1 + e * 0.035
            f = []
            if chaos:
                # colour falls and climbs back: nothing survives past the window
                g = max(0.0, 1.0 - u / 0.55)
                if g > 0.01:
                    f.append(f"grayscale({g:.2f})")
                if i == 3:                       # the negative, a single frame
                    f.append("invert(1)")
                    f.append("url(#liq1)")
                elif i == 5:                     # the blowout, with the glow
                    f.append("url(#liq2)")
                    f.append("brightness(2.1) contrast(.72) "
                             "drop-shadow(0 0 7px rgba(255,255,255,.6))")
                elif i == 1:
                    f.append("url(#liq0)")
                    f.append("brightness(1.45) contrast(1.35) "
                             "drop-shadow(0 0 5px rgba(255,255,255,.42))")
            if e > 0.08:
                f.append(f"blur({e*2.6:.2f}px)")
                f.append(f"contrast({1+e*1.1:.2f}) brightness({1+e*0.45:.2f})")
                if chroma:
                    f.append(f"drop-shadow({e*5:.1f}px 0 rgba(255,0,64,.85)) "
                             f"drop-shadow({-e*5:.1f}px 0 rgba(0,224,255,.85))")
            # the two flashes must be hard cuts, not fades
            hard = ";animation-timing-function:steps(1,end)" if (chaos and i in (3, 5)) else ""
            ks.append((t, f"transform:translate({dx:.2f}px,{dy:.2f}px) "
                          f"rotate({rot:.2f}deg) skewX({sk:.2f}deg) scale({sc:.4f});"
                          f"filter:{' '.join(f) if f else 'none'}" + hard))
        ks.append((t0 - 0.001, "transform:translate(0,0);filter:none"))
        ks.append((t0 + hitstop + dur + 0.02, "transform:translate(0,0);filter:none"))
        return ks
    # FOUR IMPACTS, one per transition. Each has its own amplitude: the wall
    # coming apart hits harder than a change of act.
    IMPACTS = [("ia", T_TERM - 0.12, 0.85),                    # the terminal blows
               ("ib", T_OUT - 0.62, 0.8),                      # and re-forms
               ("i0", T_WALL, 1.0),                            # the wall breaks
               ("i1", ACTW[0][1], 0.78),                       # ring -> river
               ("i2", ACTW[1][0] + RIV_BUILD + 0.7, 0.62),    # the middle tear
               ("i3", T_BACK[0], 0.9)]                         # back behind the wall
    marks = [(0.0, "transform:translate(0,0);filter:none")]
    for nm, t0, amp in IMPACTS:
        marks += impact(nm, t0, amp=amp, dur=0.42 + amp * 0.16, chaos=(nm == "i2"))
    marks.append((LOOP, "transform:translate(0,0);filter:none"))
    marks.sort(key=lambda m: m[0])
    css.append("@keyframes tear{"
               + "".join(f"{pc(t):.3f}%{{{d}}}" for t, d in marks) + "}")
    css.append(f".tear{{transform-box:view-box;transform-origin:center;"
               f"animation:tear {LOOP:g}s linear infinite}}")

    # the wall flashing through the middle gap stays: best moment of the loop
    G = (0.0, 0.0, 0.0, 0.0)
    _mid = ACTW[1][0] + RIV_BUILD + 0.7
    G = (pc(_mid - 0.02), pc(_mid + 0.06), pc(_mid + 0.20), pc(_mid + 0.30))

    # act shells: hard opacity windows, quick cut
    for a in range(NACT):
        t0, t1 = ACTW[a]
        # every act lives and dies inside its window: 0% and 100% always off
        css.append(
            f"@keyframes act{a}{{0%{{opacity:0}}"
            f"{pc(t0):.2f}%{{opacity:0}}{pc(t0+0.35):.2f}%{{opacity:1}}{pc(t1-0.45):.2f}%{{opacity:1}}"
            f"{pc(t1-0.05):.2f}%{{opacity:0}}100%{{opacity:0}}}}")
        css.append(f".act{a}{{opacity:0;animation:act{a} {LOOP:g}s linear infinite}}")
        # same window as the act, plus a breath: 1.04 -> 1 -> 0.97.
        # Without it the three acts are just three slides taped together.
        css.append(
            f"@keyframes dial{a}{{0%{{opacity:0;transform:scale(1.04)}}"
            f"{pc(t0):.2f}%{{opacity:0;transform:scale(1.04)}}"
            f"{pc(t0+0.35):.2f}%{{opacity:1}}"
            f"{pc(t0+0.9):.2f}%,{pc(t1-0.45):.2f}%{{opacity:1;transform:scale(1)}}"
            f"{pc(t1-0.05):.2f}%{{opacity:0;transform:scale(.97)}}"
            f"100%{{opacity:0;transform:scale(1.04)}}}}")
        css.append(f".dial{a}{{opacity:0;transform-origin:{CX}px {CY}px;"
                   f"animation:dial{a} {LOOP:g}s cubic-bezier(.2,.9,.3,1) infinite}}")
        css.append(f"@keyframes aura{a}{{0%,{max(pc(t0-0.6),0):.2f}%{{opacity:0}}"
                   f"{pc(t0+0.8):.2f}%,{pc(t1-0.8):.2f}%{{opacity:1}}{pc(t1):.2f}%,100%{{opacity:0}}}}")
        css.append(f".aura{a}{{opacity:0;animation:aura{a} {LOOP:g}s ease-in-out infinite}}")
    def stagger(name, a, n, frm, to, dur=0.75, spread=1.25, lag=0.15,
                ease="cubic-bezier(.16,1,.3,1)", out_at=None):
        """n classes .name0..n-1, staggered inside act a."""
        t0, t1 = ACTW[a]
        for k in range(n):
            s = t0 + lag + spread * k / max(n - 1, 1)
            e = s + dur
            oa = out_at if out_at is not None else t1 - 0.5
            css.append(f"@keyframes {name}{k}{{0%,{pc(s):.2f}%{{{frm}}}"
                       f"{pc(e):.2f}%,{pc(oa):.2f}%{{{to}}}"
                       f"{pc(t1-0.1):.2f}%,100%{{{frm}}}}}")
            css.append(f".{name}{k}{{animation:{name}{k} {LOOP:g}s {ease} infinite}}")
    # The data phase: everything that only exists once the wall is broken.
    # While the wall stands, this is all at zero - the panel is the whole picture.
    css.append(
        f"@keyframes dp{{0%,{pc(T_WALL+0.2):.2f}%{{opacity:0}}"
        f"{pc(ACTW[0][0]):.2f}%,{pc(T_BACK[0]):.2f}%{{opacity:1}}"
        f"{pc(T_BACK[0]+0.5):.2f}%,100%{{opacity:0}}}}")
    css.append(f".dp{{opacity:0;animation:dp {LOOP:g}s ease-in-out infinite}}")
    # the panel labels do the exact opposite
    css.append(
        f"@keyframes wallui{{0%,{pc(T_WALL_IN-0.2):.2f}%{{opacity:0}}"
        f"{pc(T_WALL_IN):.2f}%,{pc(T_WALL):.2f}%{{opacity:1}}"
        f"{pc(T_WALL+0.5):.2f}%,{pc(T_BACK[1]-0.5):.2f}%{{opacity:0}}"
        f"{pc(T_BACK[1]):.2f}%,{pc(T_OUT):.2f}%{{opacity:1}}"
        f"{pc(T_OUT+0.45):.2f}%,100%{{opacity:0}}}}")
    css.append(f".wallui{{animation:wallui {LOOP:g}s ease-in-out infinite}}")
    # The frame outlives its own labels: it stays up while the data flies out of
    # it, which is the whole point of a frame-breaking shot.
    css.append(
        f"@keyframes wallframe{{0%,{pc(T_WALL_IN-0.2):.2f}%{{opacity:0}}"
        f"{pc(T_WALL_IN):.2f}%,{pc(T_WALL+0.6):.2f}%{{opacity:1}}"
        f"{pc(ACTW[0][0]+0.4):.2f}%,{pc(T_BACK[0]-0.3):.2f}%{{opacity:0}}"
        f"{pc(T_BACK[1]-0.8):.2f}%,{pc(T_OUT):.2f}%{{opacity:1}}"
        f"{pc(T_OUT+0.45):.2f}%,100%{{opacity:0}}}}")
    css.append(f".wallframe{{animation:wallframe {LOOP:g}s ease-in-out infinite}}")

    d.impact, d.stagger, d.G = impact, stagger, G


def auras(d):
    """The colour wash under each act - the only thing that is pure atmosphere."""
    add, T = d.add, d.T
    # ============================================================ colour auras
    for a in range(NACT):
        add(f'<g class="aura{a}"><circle cx="{CX}" cy="{CY}" r="{R}" fill="url(#au{a})" filter="url(#soft)"/>'
            f'<circle cx="{LX+120}" cy="300" r="150" fill="url(#au{a})" filter="url(#soft)" opacity="0.45"/></g>')
