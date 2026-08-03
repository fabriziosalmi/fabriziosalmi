#!/usr/bin/env python3
"""ACT 02. demos/galaxy straightened out for a letterbox: one dot per
stargazer, forks lighter, cluster radius from sqrt(total), points sorted from
the centre, one sun per repo coloured by its language. The spiral became a
timeline because a spiral wastes the corners of a 2.3:1 frame."""
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
    # ------------------------------------------------------------- ACT 2 · RIVER
    riv = S["river"]
    nr = len(riv)
    A0, A1 = ACTW[1]
    rank = {r["name"]: k for k, r in enumerate(sorted(riv, key=lambda r: -r["s"]))[:RIV_NAMED]} \
        if False else {r["name"]: k for k, r in enumerate(sorted(riv, key=lambda r: -r["s"])[:RIV_NAMED])}
    nstep = (SAY_2[1] - 1.15 - SAY_2[0]) / max(RIV_NAMED, 1)
    placed, suns = [], []
    g = ['<g>']   # no act shell here: the clusters carry their own life
    for i, rp in enumerate(riv):
        tot = rp["s"] + rp["f"]
        u = i / max(nr - 1, 1)                 # position = order of birth
        x = RX0 + u * (RX1 - RX0)
        rng = RNG(sum(ord(c) * (k + 3) for k, c in enumerate(rp["name"])))
        cr = 2.6 + math.sqrt(tot) * 1.62
        # the height is chosen, not rolled: of nine candidates take the one that
        # overlaps least with what is already on the river. Without this the big
        # clusters melt into one blob and you cannot tell where one ends.
        room = RAMP - min(cr, RAMP * 0.62)
        best, bp = RCY, 1e9
        for c in range(9):
            cand = RCY + (c / 4.0 - 1.0) * room
            pen = sum(max(0.0, (pr + cr) * 1.05 - math.hypot(abs(px - x), abs(py - cand))) ** 2
                      for (px, py, pr) in placed[-14:] if abs(px - x) < (pr + cr) * 1.05)
            pen += (abs(cand - RCY) / max(room, 1)) ** 2 * 120 + rng.next() * 40
            if pen < bp:
                best, bp = cand, pen
        y = best
        placed.append((x, y, cr))

        pts = []
        for _ in range(tot):
            a_ = rng.next() * 2 * math.pi
            d_ = cr * math.sqrt(rng.uni(0.05, 1.0))
            pts.append((x + d_ * math.cos(a_), y + d_ * math.sin(a_)))
        pts.sort(key=lambda q: math.hypot(q[0] - x, q[1] - y))

        t0 = A0 + 0.12 + u * RIV_BUILD
        k = rank.get(rp["name"])
        # the cluster lights up exactly while its own name is on screen
        fl = SAY_2[0] + k * nstep if k is not None else 999
        suns.append((x, y, 1.4 + math.log1p(tot) * 0.5, t0, rp["color"], k, fl))
        for layer, (cnt, col, wdt) in enumerate(((rp["s"], T["riv_star"], 1.8),
                                                 (rp["f"], T["riv_fork"], 2.4))):
            if not cnt:
                continue
            sub = pts[:cnt] if layer == 0 else pts[rp["s"]:]
            d = "".join(f"M{px:.0f} {py:.0f}h0" for px, py in sub)
            cls = f"r{i}_{layer}"
            # the glue: once a repo has appeared it never fully leaves. It sits
            # at 12% under everything else and comes back up for its own act.
            kf = [f"0%,{pc(t0):.2f}%{{opacity:0;transform:scale(.45)}}",
                  f"{pc(t0+0.4):.2f}%{{opacity:1;transform:scale(1);stroke:{T['riv_lit']}}}",
                  f"{pc(t0+0.85):.2f}%{{opacity:1;stroke:{col}}}"]
            kf += [f"{pc(A1-0.45):.2f}%{{opacity:1;stroke:{col}}}",
                   f"{pc(A1+0.35):.2f}%{{opacity:.26;stroke:{col}}}"]
            if k is not None:
                kf += [f"{pc(fl):.2f}%{{opacity:.26;stroke:{col}}}",
                       f"{pc(fl+0.1):.2f}%{{opacity:1;stroke:{T['riv_lit']};transform:scale(1.06)}}",
                       f"{pc(fl+nstep-0.12):.2f}%{{opacity:1;stroke:{col};transform:scale(1)}}",
                       f"{pc(fl+nstep):.2f}%{{opacity:.26;stroke:{col}}}"]
            kf += [f"{pc(T_BACK[0]):.2f}%{{opacity:.26;stroke:{col}}}",
                   f"{pc(T_BACK[0]+0.5):.2f}%,100%{{opacity:0;transform:scale(.45)}}"]
            win_check(f"river cluster {i}", t0, t0 + 0.4, t0 + 0.85, A1 - 0.45, A1 + 0.35,
                      *((fl, fl + 0.1, fl + nstep) if k is not None else ()),
                      T_BACK[0], T_BACK[0] + 0.5)
            css.append(f"@keyframes {cls}{{" + "".join(kf) + "}")
            css.append(f".{cls}{{opacity:0;transform-box:fill-box;transform-origin:center;"
                       f"animation:{cls} {LOOP:g}s cubic-bezier(.16,1,.3,1) infinite}}")
            g.append(f'<path class="{cls}" d="{d}" stroke="{col}" stroke-width="{wdt}" '
                     f'stroke-linecap="round" fill="none"/>')

    # the sun is the repo itself, coloured by its language (rule from the NORD)
    for si, (sx, sy, sr, st, col, k, fl) in enumerate(suns):
        kf = [f"0%,{pc(st):.2f}%{{opacity:0;transform:scale(.2)}}",
              f"{pc(st+0.26):.2f}%{{opacity:1;transform:scale(1)}}"]
        kf += [f"{pc(A1-0.45):.2f}%{{opacity:1;transform:scale(1)}}",
               f"{pc(A1+0.35):.2f}%{{opacity:.5;transform:scale(1)}}"]
        if k is not None:
            kf += [f"{pc(fl):.2f}%{{opacity:.5;transform:scale(1)}}",
                   f"{pc(fl+0.1):.2f}%{{opacity:1;transform:scale(2.1)}}",
                   f"{pc(fl+nstep-0.12):.2f}%{{opacity:1;transform:scale(1.4)}}",
                   f"{pc(fl+nstep):.2f}%{{opacity:.5;transform:scale(1)}}"]
        kf += [f"{pc(T_BACK[0]):.2f}%{{opacity:.5;transform:scale(1)}}",
               f"{pc(T_BACK[0]+0.5):.2f}%,100%{{opacity:0;transform:scale(.2)}}"]
        win_check(f"river sun {si}", st, st + 0.26, A1 - 0.45, A1 + 0.35,
                  *((fl, fl + 0.1, fl + nstep) if k is not None else ()), T_BACK[0])
        css.append(f"@keyframes rs{si}{{" + "".join(kf) + "}")
        css.append(f".rs{si}{{opacity:0;transform-box:fill-box;transform-origin:center;"
                   f"animation:rs{si} {LOOP:g}s cubic-bezier(.2,1.6,.4,1) infinite}}")
        g.append(f'<circle class="rs{si}" cx="{sx:.0f}" cy="{sy:.0f}" r="{sr:.1f}" fill="{col}"/>')

    # year ticks: where they crowd, that is where the work accelerated
    last_lab = -999.0
    for j, yr in enumerate(sorted({r["year"] for r in riv})):
        u0 = min(i for i, r in enumerate(riv) if r["year"] == yr) / max(nr - 1, 1)
        tx = RX0 + u0 * (RX1 - RX0)
        t0 = A0 + 0.12 + u0 * RIV_BUILD
        show = tx - last_lab > 46
        if show:
            last_lab = tx
        css.append(f"@keyframes rk{j}{{0%,{pc(t0):.2f}%{{opacity:0}}"
                   f"{pc(t0+0.1):.2f}%,{pc(A1-0.4):.2f}%{{opacity:.7}}"
                   f"{pc(A1-0.1):.2f}%,100%{{opacity:0}}}}")
        css.append(f".rk{j}{{opacity:0;animation:rk{j} {LOOP:g}s ease-out infinite}}")
        g.append(f'<g class="rk{j}"><line x1="{tx:.0f}" y1="{RCY+RAMP+20}" x2="{tx:.0f}" '
                 f'y2="{RCY+RAMP+29}" stroke="{mut}" stroke-width="1"/>'
                 + (f'<text x="{tx:.0f}" y="{RCY+RAMP+50}" font-size="20" fill="{mut}" '
                    f'text-anchor="middle">{yr}</text>' if show else "") + "</g>")
    g.append("</g>")
    add("".join(g))

    # the readout of act 02: the year while it builds, then the names, then the total
    for j, yr in enumerate(sorted({r["year"] for r in riv})):
        u0 = min(i for i, r in enumerate(riv) if r["year"] == yr) / max(nr - 1, 1)
        u1 = min([i for i, r in enumerate(riv) if r["year"] > yr] or [nr - 1]) / max(nr - 1, 1)
        t0, t1 = A0 + 0.12 + u0 * RIV_BUILD, A0 + 0.12 + u1 * RIV_BUILD
        css.append(f"@keyframes ry{j}{{0%,{pc(t0):.2f}%{{opacity:0}}"
                   f"{pc(t0+0.05):.2f}%,{pc(max(t1-0.04, t0+0.1)):.2f}%{{opacity:1}}"
                   f"{pc(max(t1, t0+0.14)):.2f}%,100%{{opacity:0}}}}")
        css.append(f".ry{j}{{opacity:0;animation:ry{j} {LOOP:g}s steps(1,end) infinite}}")
        SAYS.append(txt(W // 2, 360, yr, 40, mut, 4, "middle", 700, cls=f"ry{j}", halo=4))

    for nm, k in sorted(rank.items(), key=lambda kv: kv[1]):
        rp = next(r for r in riv if r["name"] == nm)
        t0 = SAY_2[0] + k * nstep
        win_check(f"river name {k}", t0, t0 + 0.14, t0 + nstep - 0.16, t0 + nstep)
        css.append(f"@keyframes rb{k}{{0%,{pc(t0):.2f}%{{opacity:0;transform:translateY(10px)}}"
                   f"{pc(t0+0.14):.2f}%{{opacity:1;transform:translateY(0)}}"
                   f"{pc(t0+nstep-0.16):.2f}%{{opacity:1}}"
                   f"{pc(t0+nstep):.2f}%,100%{{opacity:0;transform:translateY(-7px)}}}}")
        css.append(f".rb{k}{{opacity:0;animation:rb{k} {LOOP:g}s cubic-bezier(.2,1,.3,1) infinite}}")
        sz = 76 if len(nm) <= 11 else (58 if len(nm) <= 16 else 44)
        SAYS.append(f'<g class="rb{k}">'
                    + txt(W // 2, 196, nm, sz, ink, 1, "middle", 700, halo=6)
                    + txt(W // 2, 244, f'{rp["s"]:,} STARS', 30, rp["color"], 3, "middle", 700, halo=4)
                    + "</g>")
