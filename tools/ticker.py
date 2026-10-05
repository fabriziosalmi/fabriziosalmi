#!/usr/bin/env python3
"""The profile strip: one panel of numbers and two charts, in two layouts.

Everything on it is read from data/profile.json, nothing is written by hand.
The text resolves once from noise (CSS only, no JS) and then stands still; the
only thing that keeps moving is the bar for the week still open.

Scramble without a script: every line is drawn FRAMES - 1 times with a few more
characters resolved each time, each copy alive for one tick, then the true text.
The true text is the default state, so with animation off the strip is complete.

Two layouts, same numbers: WIDE (1000x184) for a desktop column, NARROW (480x342)
for a phone, where the wide one would render at five pixels a letter. The README
picks one with a media query on <source>.
"""
import random
import statistics
from datetime import datetime
from xml.sax.saxutils import escape

FONT = 'ui-monospace,"SF Mono",SFMono-Regular,Menlo,Consolas,"DejaVu Sans Mono",monospace'
GLYPHS = "0123456789ABCDEF#%&*+=/<>$"
FRAMES, TICK = 14, 0.05      # noisy frames per line, seconds each
SETTLE = 2.2                 # seconds until nothing but the open week moves
EASE = "cubic-bezier(.2,.7,.2,1)"

THEMES = {
    "dark": dict(panel="#151b23", edge="#3d444d", ink="#f0f6fc", mu="#9198a1", fa="#6e7681",
                 pos="#3fb950", neg="#f85149", bar="#2ea043", hi="#56d364", hair="#3d444d"),
    "light": dict(panel="#f6f8fa", edge="#d1d9e0", ink="#1f2328", mu="#59636e", fa="#8c959f",
                  pos="#1a7f37", neg="#cf222e", bar="#2da44e", hi="#116329", hair="#d1d9e0"),
}

# Geometry. `budget` is how many characters a value may take before it leaves the
# panel in a monospace face 0.6 em wide: tools/test_ticker.py holds every row to it.
WIDE = dict(w=1000, h=184, fs=13, xl=24, xv=112, budget=54, cx0=540, cx1=976,
            ax=9, lb=10, rule=(24, 504, 42))
NARROW = dict(w=480, h=342, fs=13, xl=24, xv=96, budget=46, cx0=24, cx1=456,
              ax=10, lb=10, rule=(24, 456, 38))


def num(n):
    return f"{n:,}"


def sgn(n):
    return f"{n:+,}" if n else "+0"


def tone(n):
    return "p" if n > 0 else ("n" if n < 0 else "m")


def clip(name, n):
    return name if len(name) <= n else name[:n - 1] + "…"


def load(raw):
    """raw: the parsed profile.json. Returns the numbers the strip is made of."""
    u = raw["data"]["user"]
    repos = u["repositories"]["nodes"]
    cal = u["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"]
    langs = {}
    for r in repos:
        p = r["primaryLanguage"] or {}
        c = langs.setdefault(p.get("name") or "Other", [0, p.get("color") or "#8b949e"])
        c[0] += 1
    return dict(
        n=u["repositories"]["totalCount"],
        followers=u["followers"]["totalCount"],
        stars=sum(r["stargazerCount"] for r in repos),
        forks=sum(r["forkCount"] for r in repos),
        stars_by={r["name"]: r["stargazerCount"] for r in repos},
        top=max(repos, key=lambda r: r["stargazerCount"], default=None),
        days=[d for w in weeks for d in w["contributionDays"]],
        weeks=weeks,
        weekly=[sum(d["contributionCount"] for d in w["contributionDays"]) for w in weeks],
        total=cal["totalContributions"],
        langs=sorted(langs.items(), key=lambda kv: -kv[1][0]),
    )


def streak(days):
    s = 0
    for d in reversed(days):
        if d["contributionCount"] == 0:
            break
        s += 1
    return s


def gainer(S, P):
    """The repo that gained the most stars since the previous build, if any did."""
    gain = {n: s - P["stars_by"].get(n, 0) for n, s in S["stars_by"].items()}
    best = max(sorted(gain), key=lambda n: gain[n], default=None)
    return (best, gain[best]) if best and gain[best] > 0 else None


# --- the lines of text --------------------------------------------------------

def r_profile(S):
    return ("profile", [(num(S["n"]), "i"), (" repos  ", "m"), (num(S["stars"]), "i"), (" stars  ", "m"),
                        (num(S["forks"]), "i"), (" forks  ", "m"), (num(S["followers"]), "i"), (" followers", "m")])


def r_top(S, budget):
    t = S["top"]
    if not t:
        return ("top repo", [("none yet", "m")])
    stars, forks = num(t["stargazerCount"]), num(t["forkCount"])
    room = budget - len(f"  {stars} stars  {forks} forks")      # the name gives way, the numbers never do
    return ("top repo", [(clip(t["name"], min(22, room)), "i"), ("  ", "m"), (stars, "i"),
                         (" stars  ", "m"), (forks, "i"), (" forks", "m")])


# The build runs early in the UTC day, so the last day is still open: it is left
# out of every figure that claims to be a day.
def full_days(S):
    return S["days"][:-1]


def r_last(S):
    last = full_days(S)[-1]
    return ("last day", [(num(last["contributionCount"]), "i"), (" contributions on ", "m"), (last["date"], "i")])


def _sum(S, n):
    return num(sum(d["contributionCount"] for d in full_days(S)[-n:]))


def r_window(S):
    return ("window", [(_sum(S, 7), "i"), (" in 7 d  ", "m"), (_sum(S, 30), "i"), (" in 30 d  ", "m"),
                       (num(S["total"]), "i"), (f" in {len(S['weeks'])} w", "m")])


def r_activity(S):
    last = full_days(S)[-1]
    return ("activity", [(num(last["contributionCount"]), "i"), (f" on {last['date'][5:]}  ", "m"),
                         (_sum(S, 7), "i"), (" in 7 d  ", "m"), (_sum(S, 30), "i"), (" in 30 d", "m")])


def r_rhythm(S):
    full = full_days(S)
    return ("rhythm", [(str(streak(full)), "i"), (" d streak  ", "m"),
                       (str(sum(1 for d in full if d["contributionCount"])), "i"), (f"/{len(full)} d active  ", "m"),
                       ("peak ", "m"), (num(max(d["contributionCount"] for d in full)), "i")])


def r_vs(S, P, since, budget, with_gainer):
    ds, df, dw = S["stars"] - P["stars"], S["forks"] - P["forks"], S["followers"] - P["followers"]
    tail = [("  ", "m"), (sgn(df), tone(df)), (" forks  ", "m"), (sgn(dw), tone(dw)), (" followers", "m")]
    plain = [(sgn(ds), tone(ds)), (" stars", "m")] + tail
    g = gainer(S, P) if with_gainer else None
    if g:    # who the stars came from: the name alone when it was all of them
        named = [(sgn(ds), tone(ds)), (" stars (", "m"), (clip(g[0], 12), "i")] \
            + ([(f" +{g[1]}", "p")] if g[1] != ds else []) + [(")", "m")] + tail
        if sum(len(t) for t, _ in named) <= budget:      # the name is the first thing to go
            return (f"vs {since[5:]}", named)
    return (f"vs {since[5:]}", plain)


def rows(S, P, since, wide):
    budget = (WIDE if wide else NARROW)["budget"]
    if wide:
        out = [r_profile(S), r_top(S, budget), r_last(S), r_window(S), r_rhythm(S)]
    else:
        out = [r_top(S, budget), r_activity(S), r_rhythm(S)]
    if P:
        out.append(r_vs(S, P, since, budget, wide))
    return out


# --- drawing ------------------------------------------------------------------

def tspans(chars):
    out, cur, buf = [], None, ""
    for c, k in chars + [("", None)]:
        if k != cur and buf:
            out.append(f'<tspan class="{cur}">{escape(buf)}</tspan>')
            buf = ""
        cur = k
        buf += c
    return "".join(out)


def scramble(x, y, segs, delay, anchor="start", cls=""):
    chars = [(c, k) for text, k in segs for c in text]
    rng = random.Random("".join(c for c, _ in chars))      # same data, same noise
    n = len(chars)
    done = [1 + int(i / max(n - 1, 1) * (FRAMES - 4)) + rng.randint(0, 2) for i in range(n)]
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    out = []
    for k in range(FRAMES - 1):
        frame = [(c, kk) if (not c.isalnum() or k >= done[i]) else (rng.choice(GLYPHS), "g")
                 for i, (c, kk) in enumerate(chars)]
        out.append(f'<text class="f {cls}" x="{x}" y="{y}"{a} '
                   f'style="animation-delay:{delay + k * TICK:.2f}s">{tspans(frame)}</text>')
    out.append(f'<text class="t {cls}" x="{x}" y="{y}"{a} '
               f'style="animation-delay:{delay + (FRAMES - 1) * TICK:.2f}s">{tspans(chars)}</text>')
    return "".join(out)


def chart(S, T, g, ytitle, base, hmax):
    x0, x1 = g["cx0"], g["cx1"]
    wk = S["weekly"]
    mx = max(wk) or 1
    n = len(wk)
    # a median over whole weeks only: the open one and a clipped first one drag it down
    whole = [v for w, v in zip(S["weeks"][:-1], wk) if len(w["contributionDays"]) == 7]
    med = int(statistics.median(whole)) if whole else 0
    pitch = (x1 - x0) / n
    out = [f'<text class="lb" x="{x0}" y="{ytitle}">contributions per week</text>',
           f'<text class="lb" x="{x1}" y="{ytitle}" text-anchor="end">{n} w · median {num(med)} · max {num(max(wk))}</text>']
    ym = base - med / mx * hmax
    out.append(f'<line x1="{x0}" x2="{x1}" y1="{ym:.1f}" y2="{ym:.1f}" stroke="{T["fa"]}" '
               f'stroke-dasharray="2 3" opacity=".7"/>')
    for i, v in enumerate(wk):
        h = max(v / mx * hmax, 1.2)
        cur = " cur" if i == n - 1 else ""
        out.append(f'<rect class="b{cur}" style="--d:{0.35 + i * 0.012:.2f}s" x="{x0 + i * pitch:.1f}" '
                   f'y="{base - h:.1f}" width="{pitch * 0.74:.1f}" height="{h:.1f}" rx="1"/>')
    out.append(f'<line x1="{x0}" x2="{x1}" y1="{base + .5}" y2="{base + .5}" stroke="{T["hair"]}"/>')
    for i, w in enumerate(S["weeks"]):             # label the week that holds the 1st
        first = next((d["date"] for d in w["contributionDays"] if d["date"].endswith("-01")), None)
        if first:
            name = datetime.strptime(first, "%Y-%m-%d").strftime("%b")
            out.append(f'<text class="ax" x="{x0 + i * pitch:.1f}" y="{base + g["ax"] + 4}">{name}</text>')
    return "".join(out)


def languages(S, g, ytitle, ybar, ylegend):
    x0, x1 = g["cx0"], g["cx1"]
    tot = sum(v[0] for _, v in S["langs"]) or 1
    top = S["langs"][:5]
    rest = tot - sum(v[0] for _, v in top)
    items = [(k, v[0], v[1]) for k, v in top] + ([("Other", rest, "#8b949e")] if rest > 0 else [])
    out = [f'<text class="lb" x="{x0}" y="{ytitle}">languages · repos</text>']
    x, span = x0, x1 - x0
    for i, (_, c, col) in enumerate(items):
        w = c / tot * span
        out.append(f'<rect class="s" style="--d:{0.5 + i * 0.07:.2f}s" x="{x:.1f}" y="{ybar}" '
                   f'width="{max(w - 1.5, 1):.1f}" height="8" rx="1.5" fill="{col}"/>')
        x += w
    for i, (k, c, col) in enumerate(items):
        cx, cy = x0 + (i % 3) * span / 3, ylegend + (i // 3) * 17
        out.append(f'<rect x="{cx:.1f}" y="{cy - 8}" width="8" height="8" rx="2" fill="{col}"/>')
        out.append(scramble(cx + 14, cy, [(k, "i"), (f" {c}", "m")], 0.9 + i * 0.1, cls="sm"))
    return "".join(out)


def style(T, g):
    return "".join([
        f'text{{font-family:{FONT};font-size:{g["fs"]}px;white-space:pre}}',
        f'.sm{{font-size:11px}}.kpi{{font-size:22px;font-weight:600}}',
        f'.lb{{font-size:{g["lb"]}px;letter-spacing:.09em;text-transform:uppercase;fill:{T["mu"]}}}',
        f'.ax{{font-size:{g["ax"]}px;fill:{T["mu"]};opacity:.85}}',
        f'.i{{fill:{T["ink"]}}}.m{{fill:{T["mu"]}}}.p{{fill:{T["pos"]}}}.n{{fill:{T["neg"]}}}.g{{fill:{T["fa"]}}}',
        f'.b{{fill:{T["bar"]};transform-box:fill-box;transform-origin:50% 100%;'
        f'animation:g .7s {EASE} backwards;animation-delay:var(--d)}}',
        f'.b.cur{{fill:{T["hi"]};animation:g .7s {EASE} backwards var(--d),br 2.4s ease-in-out 1.8s infinite}}',
        f'.s{{transform-box:fill-box;transform-origin:0 50%;animation:h .6s {EASE} backwards;animation-delay:var(--d)}}',
        '.f{opacity:0;animation:b .05s step-end 1}.t{animation:p .001s step-end backwards}',
        '@keyframes b{from,to{opacity:1}}@keyframes p{from{opacity:0}}',
        '@keyframes g{from{transform:scaleY(0)}}@keyframes h{from{transform:scaleX(0)}}',
        '@keyframes br{50%{opacity:.4}}',
        '@media (prefers-reduced-motion:reduce){*{animation:none!important}}',
    ])


def describe(S, lines):
    """Plain text for screen readers: the same numbers, as sentences."""
    return " ".join(f"{lab}: {''.join(t for t, _ in segs)}." for lab, segs in lines)


def build(S, P, since, T, wide=True):
    g = WIDE if wide else NARROW
    lines = rows(S, P, since, wide)
    asof = S["days"][-1]["date"]            # the calendar ends on the day it was read
    label = (f"Profile data: {S['n']} repositories, {S['stars']} stars, {S['followers']} followers, "
             f"{S['total']} contributions in the last {len(S['weeks'])} weeks.")
    right = g["w"] - g["xl"]
    head = scramble(right if not wide else g["xv"] + 18, 28 if not wide else 30,
                    [(f"data as of {asof}", "m")], 0.2, anchor="end" if not wide else "start")
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" xml:space="preserve" viewBox="0 0 {g["w"]} {g["h"]}" '
           f'role="img" aria-label="{escape(label)}"><title>fabriziosalmi, profile data</title>'
           f'<desc>{escape(describe(S, lines))}</desc><style>{style(T, g)}</style>',
           f'<rect x=".5" y=".5" width="{g["w"] - 1}" height="{g["h"] - 1}" rx="8" fill="{T["panel"]}" stroke="{T["edge"]}"/>',
           f'<text x="{g["xl"]}" y="{30 if wide else 28}" class="i" style="font-weight:600">fabriziosalmi</text>',
           head,
           f'<line x1="{g["rule"][0]}" x2="{g["rule"][1]}" y1="{g["rule"][2]}" y2="{g["rule"][2]}" stroke="{T["hair"]}"/>']
    if wide:
        y0, step = 64, 21
    else:
        for i, (lab, val) in enumerate([("repos", num(S["n"])), ("stars", num(S["stars"])),
                                        ("forks", num(S["forks"])), ("followers", num(S["followers"]))]):
            x = g["xl"] + i * 108
            out.append(scramble(x, 70, [(val, "i")], 0.25 + i * 0.1, cls="kpi"))
            out.append(f'<text class="lb" x="{x}" y="86">{lab}</text>')
        y0, step = 116, 20
    for k, (lab, segs) in enumerate(lines):
        y = y0 + k * step
        out.append(f'<text class="lb" x="{g["xl"]}" y="{y}">{escape(lab)}</text>')
        out.append(scramble(g["xv"], y, segs, (0.3 if wide else 0.65) + k * 0.12))
    if wide:
        out += [chart(S, T, g, 30, 94, 48), languages(S, g, 122, 128, 156)]
    else:
        out += [chart(S, T, g, 200, 246, 38), languages(S, g, 280, 286, 312)]
    out.append("</svg>")
    return "".join(out)
