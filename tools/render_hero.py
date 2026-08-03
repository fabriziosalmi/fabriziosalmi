#!/usr/bin/env python3
"""Profile hero: a circular instrument on a transparent canvas, drawn from live data.

Why it is built this way:
  * transparent background + round shape -> it sits on GitHub's own background
    instead of stamping a rectangle over it, so it belongs in both themes.
  * two variants (dark/light) using GitHub's palette, served through <picture>.
  * three acts = three readings of the same real data, refreshed once a day.

Usage:  python3 tools/render_hero.py data/profile.json .
"""
import json
import math
import os
import sys
from datetime import datetime, timezone

# ------------------------------------------------------------------ geometry
W, H = 920, 400
CX, CY, R = 676, 196, 160        # the dial
LX = 56                          # left column

# The loop is a match cut: it opens on a pixel-accurate replica of GitHub's own
# contribution panel, breaks it, flies the data out of the frame, and puts every
# square back where it was. Seconds, not percentages, so the beats stay readable.
LOOP = 15.0
T_WALL = 2.4                     # the wall holds still, long enough to be believed
T_OUT = 1.2                      # the break
ACTW = [(3.6, 6.5), (6.9, 12.2)]   # 01 the ring · 02 the river
T_BACK = (12.5, 13.9)              # everything returns behind the wall
NACT = 2

# The river: the galaxy of demos/galaxy straightened out for a letterbox frame.
# Same model (one dot per star, forks lighter, cluster radius from sqrt(total),
# points sorted from the centre, a sun per repo coloured by language) with the
# spiral swapped for a timeline, because a spiral in a 2.3:1 frame wastes the
# corners and clips at the edges.
RX0, RX1 = 466, 886
RCY, RAMP = 196, 84
RIV_BUILD, RIV_FLASH, RIV_NAMED = 2.6, 3.3, 4

# GitHub's calendar, measured from the real thing: 53 columns, 10px cells,
# 13px pitch, and the palettes lifted from GitHub's own theme stylesheets
# (the ones in every blog post - #9be9a8, #0e4429 - are years out of date).
CELL, PITCH, COLS, ROWS = 10, 13, 53, 7
GRID_W, GRID_H = COLS * PITCH - 3, ROWS * PITCH - 3
WALL_X, WALL_Y = 86, 120         # panel corner
PAD, WD_COL, MO_ROW = 16, 30, 20
GX, GY = WALL_X + PAD + WD_COL, WALL_Y + PAD + MO_ROW
SANS = ('-apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", '
        'Helvetica, Arial, sans-serif')

# names too long to fit inside a sector
SHORT = {"JavaScript": "JS", "TypeScript": "TS", "Jupyter Notebook": "NOTEBOOK", "Dockerfile": "DOCKER",
         "Shell": "SHELL", "C++": "C++", "HTML": "HTML", "CSS": "CSS", "Python": "PYTHON", "Go": "GO",
         "Rust": "RUST", "OTHER": "OTHER"}


def pc(t):
    """seconds -> percentage of the loop"""
    return max(0.0, min(100.0, t / LOOP * 100))


def pol(r, deg, cx=CX, cy=CY):
    a = math.radians(deg - 90)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def fmt(n):
    return f"{n:,}".replace(",", " ")


# ------------------------------------------------------------------ themes
# <picture> picks the variant from the OPERATING SYSTEM preference, but GitHub
# lets you override its theme by hand, so the pick can be wrong. Therefore:
#   - everything structural (rules, borders, small text) uses neutral greys that
#     have contrast against both white and near-black;
#   - large text carries a halo of the opposite tone (paint-order), invisible on
#     the intended background and a lifesaver on the wrong one.
# Net effect: the wrong variant looks worse, never unreadable.
NEUTRAL = "#7d8590"

THEMES = {
    "dark": dict(
        cal=["#151b23", "#033a16", "#196c2e", "#2ea043", "#56d364"],
        # same scale, pushed up: GitHub's L1 reads as a 10px square and
        # vanishes as a 2px spoke, so the squares ignite once they fly
        lit=["#30363d", "#2ea043", "#56d364", "#7ee787", "#aff5b4"],
        ui_border="#3d444d", ui_mut="#9198a1", ui_fg="#f0f6fc",
        ink="#f0f6fc", mut="#9198a1", faint="#7d8590", line=NEUTRAL, hair=NEUTRAL,
        line_op=0.42, hair_op=0.20,
        disc="#ffffff", disc_op=0.022, warm="#e3b341", knock="#0d1117",
        halo="#010409", halo_op=0.55,
        riv_star="#f5c542", riv_fork="#ffedb4", riv_lit="#fff2c8",
        acc=["#3fb950", "#58a6ff", "#d29922"],
        hi=["#56d364", "#79c0ff", "#e3b341"],
        glow=3.4, glow_op=1.0,
    ),
    "light": dict(
        cal=["#eff2f5", "#aceebb", "#4ac26b", "#2da44e", "#116329"],
        lit=["#d0d7de", "#2da44e", "#116329", "#0b4a22", "#04310f"],
        ui_border="#d1d9e0", ui_mut="#59636e", ui_fg="#1f2328",
        ink="#1f2328", mut="#636c76", faint="#6e7681", line=NEUTRAL, hair=NEUTRAL,
        line_op=0.42, hair_op=0.22,
        disc="#000000", disc_op=0.018, warm="#9a6700", knock="#ffffff",
        halo="#ffffff", halo_op=0.72,
        # on white, gold turns to mud: ink dots, like a printed star chart
        riv_star="#4a4032", riv_fork="#8a7a55", riv_lit="#111111",
        acc=["#1a7f37", "#0969da", "#9a6700"],
        hi=["#2da44e", "#218bff", "#bf8700"],
        glow=2.0, glow_op=0.55,
    ),
}


class RNG:
    """Seeded LCG, the only randomness allowed: two renders draw the same river."""

    def __init__(self, seed):
        self.s = seed & 0x7FFFFFFF or 1

    def next(self):
        self.s = (1103515245 * self.s + 12345) & 0x7FFFFFFF
        return self.s / 0x7FFFFFFF

    def uni(self, a, b):
        return a + (b - a) * self.next()


# ------------------------------------------------------------------ data
def load(path):
    u = json.load(open(path))["data"]["user"]
    repos = [r for r in u["repositories"]["nodes"]]
    days = [d for w in u["contributionsCollection"]["contributionCalendar"]["weeks"]
            for d in w["contributionDays"]]
    langs = {}
    for r in repos:
        L = (r["primaryLanguage"] or {}).get("name") or "OTHER"
        langs.setdefault(L, []).append(r)
    return dict(
        repos=repos,
        n_repos=u["repositories"]["totalCount"],
        followers=u["followers"]["totalCount"],
        stars=sum(r["stargazerCount"] for r in repos),
        days=days,
        contrib=u["contributionsCollection"]["contributionCalendar"]["totalContributions"],
        langs=langs,
        top=sorted(repos, key=lambda r: -r["stargazerCount"])[0],
        first_year=min(r["createdAt"] for r in repos)[:4],
        peak=max(d["contributionCount"] for d in days),
        # the river: only repos with at least one star or one fork, oldest first
        river=sorted(
            [{"name": x["name"], "s": x["stargazerCount"], "f": x["forkCount"],
              "born": x["createdAt"], "year": x["createdAt"][:4],
              "color": (x["primaryLanguage"] or {}).get("color") or "#8b949e"}
             for x in repos if x["stargazerCount"] >= 1 or x["forkCount"] >= 1],
            key=lambda r: r["born"]),
        built=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    )


# ------------------------------------------------------------------ generator
def build(S, th, T):
    ink, mut, faint = T["ink"], T["mut"], T["faint"]
    line, hair = T["line"], T["hair"]
    acc, hi = T["acc"], T["hi"]
    css, out = [], []
    add = out.append
    SQUARES = []

    def esc(s):
        return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def txt(x, y, s, size=15, fill=None, ls=2.0, anchor="start", weight=600, cls="", op=None,
            halo=0):
        """halo = width of the opposite-tone outline painted under the glyph:
        invisible on the intended background, readable on the wrong one."""
        c = f' class="{cls}"' if cls else ""
        o = f' opacity="{op}"' if op is not None else ""
        h = (f' paint-order="stroke" stroke="{T["halo"]}" stroke-opacity="{T["halo_op"]}" '
             f'stroke-width="{halo}" stroke-linejoin="round"' if halo else "")
        return (f'<text{c} x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill or mut}" '
                f'font-weight="{weight}" letter-spacing="{ls}" text-anchor="{anchor}"{o}{h}>{esc(s)}</text>')

    # ============================================================ header
    add(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
        f'role="img" aria-labelledby="ti de" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">')
    add('<title id="ti">Fabrizio Salmi — infrastructure, security, AI agency</title>')
    add(f'<desc id="de">A circular instrument cycling three readings of live GitHub data: '
        f'{fmt(S["contrib"])} contributions over 366 days, {S["n_repos"]} public systems across '
        f'{len(S["langs"])} languages, and {fmt(S["stars"])} stars compounding since 2017.</desc>')
    add("<defs>")
    d = []
    for i, c in enumerate(acc):
        d.append(f'<radialGradient id="au{i}"><stop offset="0%" stop-color="{c}" stop-opacity="{0.30 if th=="dark" else 0.16}"/>'
                 f'<stop offset="70%" stop-color="{c}" stop-opacity="0.04"/>'
                 f'<stop offset="100%" stop-color="{c}" stop-opacity="0"/></radialGradient>')
    d.append(f'<radialGradient id="discG"><stop offset="0%" stop-color="{T["disc"]}" stop-opacity="{T["disc_op"]*2.2:.3f}"/>'
             f'<stop offset="100%" stop-color="{T["disc"]}" stop-opacity="{T["disc_op"]:.3f}"/></radialGradient>')
    d.append(f'<linearGradient id="shine" x1="0" y1="0" x2="1" y2="0">'
             f'<stop offset="0%" stop-color="{ink}" stop-opacity="0"/>'
             f'<stop offset="50%" stop-color="{ink}" stop-opacity="{0.9 if th=="dark" else 0.55}"/>'
             f'<stop offset="100%" stop-color="{ink}" stop-opacity="0"/></linearGradient>')
    d.append(f'<filter id="gl" x="-90%" y="-90%" width="280%" height="280%">'
             f'<feGaussianBlur stdDeviation="{T["glow"]}" result="b"/>'
             f'<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')
    d.append('<filter id="soft" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="28"/></filter>')
    # RGB split for the tear: the three channels come apart by a few pixels.
    # screen on dark, multiply on light, or the aberration washes the page out.
    # on white, multiply is the physically right blend but it muddies fast:
    # half the offset there, or the small type turns to porridge
    bl = "screen" if th == "dark" else "multiply"
    dxs = 4 if th == "dark" else 2
    d.append(
        '<filter id="rgb" x="-5%" y="-5%" width="110%" height="110%">'
        '<feColorMatrix in="SourceGraphic" type="matrix" values="1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0" result="r"/>'
        f'<feOffset in="r" dx="-{dxs}" dy="0" result="ro"/>'
        '<feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 1 0" result="g"/>'
        '<feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 1 0" result="b"/>'
        f'<feOffset in="b" dx="{dxs}" dy="0" result="bo"/>'
        f'<feBlend in="ro" in2="g" mode="{bl}" result="rg"/>'
        f'<feBlend in="rg" in2="bo" mode="{bl}"/></filter>')
    d.append(f'<clipPath id="disc"><circle cx="{CX}" cy="{CY}" r="{R-6}"/></clipPath>')
    add("".join(d))

    css.append(f"""
text{{font-family:ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,monospace}}
.wallui text{{font-family:{SANS}}}
.g{{transform-box:fill-box;transform-origin:center}}
.spin{{transform-origin:{CX}px {CY}px;animation:spin 150s linear infinite}}
.spinf{{transform-origin:{CX}px {CY}px;animation:spin 26s linear infinite}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
.blink{{animation:blink 2.2s steps(1,end) infinite}}
@keyframes blink{{0%,55%{{opacity:1}}56%,100%{{opacity:.15}}}}
.shim{{animation:shim 3s cubic-bezier(.45,0,.15,1) infinite}}
@keyframes shim{{0%{{transform:translateX(-300px)}}34%,100%{{transform:translateX(560px)}}}}
""")

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
                elif i == 5:                     # the blowout, with the glow
                    f.append("brightness(2.1) contrast(.72) "
                             "drop-shadow(0 0 7px rgba(255,255,255,.6))")
                elif i == 1:
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
    IMPACTS = [("i0", T_WALL, 1.0),                            # the wall breaks
               ("i1", ACTW[0][1], 0.78),                       # ring -> river
               ("i2", (ACTW[1][0] + ACTW[1][1]) / 2, 0.62),    # the middle tear
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
    _mid = (ACTW[1][0] + ACTW[1][1]) / 2
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
        f"@keyframes wallui{{0%,{pc(T_WALL):.2f}%{{opacity:1}}"
        f"{pc(T_WALL+0.5):.2f}%,{pc(T_BACK[1]-0.5):.2f}%{{opacity:0}}"
        f"{pc(T_BACK[1]):.2f}%,100%{{opacity:1}}}}")
    css.append(f".wallui{{animation:wallui {LOOP:g}s ease-in-out infinite}}")
    # The frame outlives its own labels: it stays up while the data flies out of
    # it, which is the whole point of a frame-breaking shot.
    css.append(
        f"@keyframes wallframe{{0%,{pc(T_WALL+0.6):.2f}%{{opacity:1}}"
        f"{pc(ACTW[0][0]+0.4):.2f}%,{pc(T_BACK[0]-0.3):.2f}%{{opacity:0}}"
        f"{pc(T_BACK[1]-0.8):.2f}%,100%{{opacity:1}}}}")
    css.append(f".wallframe{{animation:wallframe {LOOP:g}s ease-in-out infinite}}")

    add('<g class="dp">')

    # ============================================================ colour auras
    for a in range(NACT):
        add(f'<g class="aura{a}"><circle cx="{CX}" cy="{CY}" r="{R}" fill="url(#au{a})" filter="url(#soft)"/>'
            f'<circle cx="{LX+120}" cy="300" r="150" fill="url(#au{a})" filter="url(#soft)" opacity="0.45"/></g>')

    # ============================================================ left column
    add(f'<g class="spinf" style="transform-origin:{LX+9}px 46px"><text x="{LX+9}" y="46" font-size="19" '
        f'fill="{T["warm"]}" text-anchor="middle" dominant-baseline="central">꩜</text></g>')
    add(txt(LX + 28, 51, "INDEPENDENT RESEARCH · GENOVA, IT", 14, mut, 2.8, weight=700, halo=2.6))

    add(f'<clipPath id="nc"><text x="{LX}" y="128" font-size="56" font-weight="700" letter-spacing="2">FABRIZIO</text>'
        f'<text x="{LX}" y="186" font-size="56" font-weight="700" letter-spacing="2">SALMI</text></clipPath>')
    add(txt(LX, 128, "FABRIZIO", 56, ink, 2, weight=700, halo=5))
    add(txt(LX, 186, "SALMI", 56, ink, 2, weight=700, halo=5))
    add(f'<g clip-path="url(#nc)"><rect class="shim" x="-300" y="80" width="300" height="120" fill="url(#shine)" opacity="0.9"/></g>')
    add(txt(LX + 2, 216, "INFRASTRUCTURE × SECURITY × AI AGENCY", 14, mut, 2.4, halo=2.6))

    # divider
    add(f'<line x1="{LX}" y1="240" x2="{LX+400}" y2="240" stroke="{hair}" stroke-opacity="{T["hair_op"]}" stroke-width="1"/>')

    # ---- current reading (changes with the act)
    READ = [
        ("01", "SIGNAL", fmt(S["contrib"]),
         f'PUBLIC CONTRIBUTIONS · 366 DAYS · PEAK {fmt(S["peak"])}'),
        ("02", "COMPOUND", "", ""),      # the river brings its own text
    ]
    for a, (num, name, val, sub) in enumerate(READ):
        g = [f'<g class="act{a}">']
        if not val:                      # act 02: the river draws its own text
            g.append(txt(LX, 272, num, 17.5, hi[a], 1.4, weight=700, halo=3))
            g.append(txt(LX + 40, 272, name, 17.5, ink, 3.6, weight=700, halo=3))
            g.append("</g>")
            add("".join(g))
            continue
        g.append(txt(LX, 272, num, 17.5, hi[a], 1.4, weight=700, halo=3))
        g.append(txt(LX + 40, 272, name, 17.5, ink, 3.6, weight=700, halo=3))
        g.append(f'<rect x="{LX}" y="282" width="{2.6*len(val)*13:.0f}" height="0" fill="none"/>')
        g.append(txt(LX, 322, val, 42, hi[a], 1.0, weight=700, halo=4.5))
        g.append(txt(LX, 344, sub, 13, faint, 1.5, halo=2.4))
        g.append("</g>")
        add("".join(g))

    add(f'<circle class="blink" cx="{LX+5}" cy="376" r="3.2" fill="{T["warm"]}"/>')
    add(txt(LX + 18, 380, f'ON AIR SINCE 2008 · {S["built"]}', 13, faint, 1.8, halo=2.4))

    # ============================================================ the dial
    add('<g class="act0">')   # the dial belongs to act 01 only
    add(f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="url(#discG)" stroke="{line}" stroke-opacity="{T["line_op"]}" stroke-width="1"/>')
    add(f'<circle cx="{CX}" cy="{CY}" r="{R-10}" fill="none" stroke="{hair}" stroke-opacity="{T["hair_op"]}" stroke-width="1"/>')

    # tick crown, turning very slowly
    tk = ['<g class="spin">']
    for i in range(96):
        ang = i * 360 / 96
        r0 = R + 4
        r1 = R + (13 if i % 8 == 0 else 8)
        x0, y0 = pol(r0, ang)
        x1, y1 = pol(r1, ang)
        tk.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{line}" '
                  f'stroke-width="{1.4 if i%8==0 else 0.9}" opacity="{0.9 if i%8==0 else 0.45}"/>')
    tk.append("</g>")
    add("".join(tk))

    # progress arc: one full turn per loop, one colour per act
    CIRC = 2 * math.pi * (R + 18)
    css.append(f"@keyframes prog{{0%,{pc(ACTW[0][0]):.2f}%{{stroke-dashoffset:{CIRC:.0f}}}"
               f"{pc(ACTW[-1][1]):.2f}%,100%{{stroke-dashoffset:0}}}}")
    css.append(f".prog{{stroke-dasharray:{CIRC:.0f};animation:prog {LOOP:g}s linear infinite}}")
    for a in range(NACT):
        t0, t1 = ACTW[a]
        css.append(f"@keyframes pc{a}{{0%,{pc(t0):.2f}%{{opacity:0}}{pc(t0+0.01):.2f}%,"
                   f"{pc(t1):.2f}%{{opacity:.95}}{pc(t1+0.01):.2f}%,100%{{opacity:0}}}}")
        css.append(f".pcol{a}{{opacity:0;animation:pc{a} {LOOP:g}s steps(1,end) infinite}}")
        add(f'<g class="pcol{a}"><circle class="prog" cx="{CX}" cy="{CY}" r="{R+18}" fill="none" '
            f'stroke="{hi[a]}" stroke-width="2" stroke-linecap="round" '
            f'transform="rotate(-90 {CX} {CY})" filter="url(#gl)"/></g>')

    add("</g>")   # end of the dial chrome

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
            f"0%,{pc(out_s):.2f}%{{transform:translate(0,0);opacity:1;fill:var(--c0)}}"
            f"{pc(out_e):.2f}%,{pc(ACTW[0][1]-0.3):.2f}%{{transform:var(--t);opacity:1;fill:var(--c1)}}"
            f"{pc(ACTW[1][0]+0.2):.2f}%,{G[0]:.1f}%{{transform:var(--t);opacity:0;fill:var(--c1)}}"
            f"{G[1]:.1f}%{{transform:translate(0,0);opacity:.92;fill:var(--c0);animation-timing-function:steps(1,end)}}"
            f"{G[2]:.1f}%{{transform:translate(0,0);opacity:.92;fill:var(--c0)}}"
            f"{G[3]:.1f}%,{pc(ACTW[-1][1]-0.2):.2f}%{{transform:var(--t);opacity:0;fill:var(--c1)}}"
            f"{pc(back_s):.2f}%{{transform:var(--t);opacity:1}}"
            f"{pc(back_e):.2f}%,100%{{transform:translate(0,0);opacity:1;fill:var(--c0)}}}}")
        css.append(f".fly{k}{{transform-box:fill-box;transform-origin:center;"
                   f"animation:fly{k} {LOOP:g}s cubic-bezier(.5,0,.2,1) infinite}}")

    sq = ['<g>']
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
        sq.append(f'<rect class="fly{int(col/COLS*NF)%NF}" x="{cx0-CELL/2:.0f}" y="{cy0-CELL/2:.0f}" '
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

    # ------------------------------------------------------------- ACT 2 · RIVER
    riv = S["river"]
    nr = len(riv)
    A0, A1 = ACTW[1]
    rank = {r["name"]: k for k, r in enumerate(sorted(riv, key=lambda r: -r["s"]))[:RIV_NAMED]} \
        if False else {r["name"]: k for k, r in enumerate(sorted(riv, key=lambda r: -r["s"])[:RIV_NAMED])}
    placed, suns = [], []
    g = [f'<g class="dial1">']
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
        fl = A0 + RIV_FLASH + (k * 0.34 if k is not None else 999)
        suns.append((x, y, 1.4 + math.log1p(tot) * 0.5, t0, rp["color"], k, fl))
        for layer, (cnt, col, wdt) in enumerate(((rp["s"], T["riv_star"], 1.8),
                                                 (rp["f"], T["riv_fork"], 2.4))):
            if not cnt:
                continue
            sub = pts[:cnt] if layer == 0 else pts[rp["s"]:]
            d = "".join(f"M{px:.0f} {py:.0f}h0" for px, py in sub)
            cls = f"r{i}_{layer}"
            kf = [f"0%,{pc(t0):.2f}%{{opacity:0;transform:scale(.45)}}",
                  f"{pc(t0+0.4):.2f}%{{opacity:1;transform:scale(1);stroke:{T['riv_lit']}}}",
                  f"{pc(t0+0.85):.2f}%{{opacity:1;stroke:{col}}}"]
            if k is not None:
                kf += [f"{pc(fl):.2f}%{{opacity:1;stroke:{col}}}",
                       f"{pc(fl+0.08):.2f}%{{opacity:1;stroke:{T['riv_lit']};transform:scale(1.05)}}",
                       f"{pc(fl+0.36):.2f}%{{opacity:1;stroke:{col};transform:scale(1)}}"]
            kf += [f"{pc(A1-0.45):.2f}%{{opacity:1;stroke:{col}}}",
                   f"{pc(A1-0.1):.2f}%,100%{{opacity:0;transform:scale(.45)}}"]
            css.append(f"@keyframes {cls}{{" + "".join(kf) + "}")
            css.append(f".{cls}{{opacity:0;transform-box:fill-box;transform-origin:center;"
                       f"animation:{cls} {LOOP:g}s cubic-bezier(.16,1,.3,1) infinite}}")
            g.append(f'<path class="{cls}" d="{d}" stroke="{col}" stroke-width="{wdt}" '
                     f'stroke-linecap="round" fill="none"/>')

    # the sun is the repo itself, coloured by its language (rule from the NORD)
    for si, (sx, sy, sr, st, col, k, fl) in enumerate(suns):
        kf = [f"0%,{pc(st):.2f}%{{opacity:0;transform:scale(.2)}}",
              f"{pc(st+0.26):.2f}%{{opacity:1;transform:scale(1)}}"]
        if k is not None:
            kf += [f"{pc(fl):.2f}%{{opacity:1;transform:scale(1)}}",
                   f"{pc(fl+0.09):.2f}%{{opacity:1;transform:scale(1.9)}}",
                   f"{pc(fl+0.38):.2f}%{{opacity:1;transform:scale(1)}}"]
        kf += [f"{pc(A1-0.45):.2f}%{{opacity:1;transform:scale(1)}}",
               f"{pc(A1-0.1):.2f}%,100%{{opacity:0;transform:scale(.2)}}"]
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
                 + (f'<text x="{tx:.0f}" y="{RCY+RAMP+46}" font-size="14" fill="{mut}" '
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
        add(txt(LX, 330, yr, 46, ink, 1, weight=700, cls=f"ry{j}", halo=4))

    for nm, k in sorted(rank.items(), key=lambda kv: kv[1]):
        rp = next(r for r in riv if r["name"] == nm)
        t0 = A0 + RIV_FLASH + k * 0.34
        css.append(f"@keyframes rb{k}{{0%,{pc(t0):.2f}%{{opacity:0;transform:translateY(7px)}}"
                   f"{pc(t0+0.08):.2f}%{{opacity:1;transform:translateY(0)}}"
                   f"{pc(t0+0.28):.2f}%{{opacity:1}}"
                   f"{pc(t0+0.4):.2f}%,100%{{opacity:0;transform:translateY(-6px)}}}}")
        css.append(f".rb{k}{{opacity:0;animation:rb{k} {LOOP:g}s cubic-bezier(.2,1,.3,1) infinite}}")
        sz = 30 if len(nm) <= 14 else (24 if len(nm) <= 19 else 20)
        add(f'<g class="rb{k}">' + txt(LX, 306, nm, sz, ink, 0.5, weight=700, halo=3)
            + txt(LX, 344, f'{rp["s"]:,}', 26, rp["color"], 1, weight=700, halo=3) + "</g>")

    ts = A0 + RIV_FLASH + RIV_NAMED * 0.34 + 0.1
    tot_s = sum(r["s"] for r in riv)
    tot_f = sum(r["f"] for r in riv)
    css.append(f"@keyframes rt{{0%,{pc(ts):.2f}%{{opacity:0;transform:scale(.93)}}"
               f"{pc(ts+0.24):.2f}%,{pc(A1-0.35):.2f}%{{opacity:1;transform:scale(1)}}"
               f"{pc(A1-0.1):.2f}%,100%{{opacity:0;transform:scale(.93)}}}}")
    css.append(f".rt{{opacity:0;transform-box:fill-box;transform-origin:left center;"
               f"animation:rt {LOOP:g}s cubic-bezier(.2,1.5,.4,1) infinite}}")
    add('<g class="rt">'
        + txt(LX, 322, f"{tot_s:,}", 52, T["riv_star"], 1, weight=700, halo=5)
        + txt(LX, 348, "STARS", 16, ink, 6, weight=600, halo=3)
        + txt(LX, 380, f"{tot_f:,}", 24, T["riv_fork"], 1, weight=700, halo=3)
        + txt(LX + 24 * 0.62 * len(f"{tot_f:,}") + 13, 380, "FORKS", 14, mut, 3, halo=3)
        + "</g>")


    add("</g>")   # end of the data phase
    add(SQUARES[0])   # the calendar squares: present in every phase

    # fixed hub: one anchor for the eye, identical across all three acts
    css.append(f"""
.hubr{{transform-origin:{CX}px {CY}px;animation:hubr 3s cubic-bezier(.3,0,.2,1) infinite}}
@keyframes hubr{{0%{{transform:scale(1);opacity:.55}}6%{{transform:scale(1.5);opacity:0}}100%{{transform:scale(1.5);opacity:0}}}}
""")
    add('<g class="dp act0">')
    for a in range(NACT):
        add(f'<circle class="hubr pcol{a}" cx="{CX}" cy="{CY}" r="30" fill="none" stroke="{hi[a]}" stroke-width="1.4"/>')
    add(f'<circle cx="{CX}" cy="{CY}" r="30" fill="{T["disc"]}" fill-opacity="{0.10 if th=="dark" else 0.035}" '
        f'stroke="{line}" stroke-width="1"/>')
    add(f'<g class="spinf" style="transform-origin:{CX}px {CY}px"><text x="{CX}" y="{CY}" font-size="26" '
        f'fill="{T["warm"]}" text-anchor="middle" dominant-baseline="central">꩜</text></g>')
    add("</g>")

    # ============================================================== THE WALL
    # A replica of GitHub's own contribution panel, down to the 10px cells on a
    # 13px pitch, the 53 columns, the palette read out of GitHub's stylesheets
    # and the exact wording of its footer. It is the first frame and the last:
    # the drawing opens as a piece of the interface and closes back into one.
    ui_b, ui_m, ui_f = T["ui_border"], T["ui_mut"], T["ui_fg"]
    PW = PAD * 2 + WD_COL + GRID_W
    PH = PAD * 2 + MO_ROW + GRID_H + 26
    w = ['<g class="wallui">']
    w.append(f'<text x="{WALL_X}" y="{WALL_Y-14}" font-size="16" fill="{ui_f}" '
             f'font-weight="400">{S["contrib"]:,} contributions in the last year</text>')
    w.append("</g>")
    w.append(f'<g class="wallframe"><rect x="{WALL_X}" y="{WALL_Y}" width="{PW}" height="{PH}" rx="6" '
             f'fill="none" stroke="{ui_b}" stroke-width="1"/></g>')
    w.append('<g class="wallui">')
    # month labels, one above the first week of each month
    seen_m = None
    for c in range(COLS):
        d0 = days[min(c * ROWS, len(days) - 1)]["date"]
        m = d0[:7]
        if m != seen_m and int(d0[8:10]) <= 7:
            seen_m = m
            lab = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][int(d0[5:7]) - 1]
            w.append(f'<text x="{GX + c*PITCH}" y="{GY-6}" font-size="12" fill="{ui_m}">{lab}</text>')
    for r_, lab in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        w.append(f'<text x="{GX-8}" y="{GY + r_*PITCH + 9}" font-size="12" fill="{ui_m}" '
                 f'text-anchor="end">{lab}</text>')
    w.append(f'<text x="{WALL_X+PAD}" y="{WALL_Y+PH-12}" font-size="12" fill="{ui_m}">'
             f'Learn how we count contributions</text>')
    lx4 = WALL_X + PW - PAD - 5 * (CELL + 3) - 74
    w.append(f'<text x="{lx4}" y="{WALL_Y+PH-12}" font-size="12" fill="{ui_m}">Less</text>')
    for n in range(5):
        w.append(f'<rect x="{lx4 + 30 + n*(CELL+3)}" y="{WALL_Y+PH-21}" width="{CELL}" height="{CELL}" '
                 f'rx="2" fill="{T["cal"][n]}"/>')
    w.append(f'<text x="{lx4 + 30 + 5*(CELL+3) + 4}" y="{WALL_Y+PH-12}" font-size="12" fill="{ui_m}">More</text>')
    w.append("</g>")
    add("".join(w))

    add("</svg>")

    # Anyone with "reduce motion" gets the wall: no motion, no hole, and the most
    # integrated frame of the whole loop - a piece of GitHub's own interface.
    # (Goes last in the stylesheet, after every rule it has to beat.)
    css.append("""
@media (prefers-reduced-motion: reduce){
 *{animation:none!important}
 .dp,.act0,.act1,.act2,.dial0,.dial1,.dial2,.aura0,.aura1,.aura2,
 .pcol0,.pcol1,.pcol2{opacity:0!important}
 .wallui,.wallframe{opacity:1!important}
}""")

    head, defs_open, gradients, rest = out[:3], out[3], out[4], out[5:]
    return "\n".join(head + [defs_open, gradients, "<style>" + "\n".join(css) + "</style>", "</defs>",
                             '<g class="tear">'] + rest[:-1] + ["</g>", rest[-1]])


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "data/profile.json"
    outdir = sys.argv[2] if len(sys.argv) > 2 else "."
    S = load(src)
    for th, T in THEMES.items():
        doc = build(S, th, T)
        p = os.path.join(outdir, f"hero-{th}.svg")
        open(p, "w", encoding="utf-8").write(doc)
        print(p, len(doc), "bytes")
