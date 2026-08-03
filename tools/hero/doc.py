#!/usr/bin/env python3
"""The document under construction: buffers, text helpers, and the one assertion
that keeps the whole thing honest.

win_check exists because CSS sorts keyframes by percentage. A window that closes
before it opens does not fail - it silently draws two things on top of each
other, which is the class of bug that cost us three rounds of chasing ghosts
across the timeline.
"""
from .geometry import *


class Doc:
    """Everything a scene module needs, and nothing it does not."""

    def __init__(self, S, th, T):
        self.S, self.th, self.T = S, th, T
        self.css, self.out = [], []
        self.squares, self.says = [], []
        self.G = (0.0, 0.0, 0.0, 0.0)
        self.impact = self.stagger = None
        self.ink, self.mut, self.faint = T["ink"], T["mut"], T["faint"]
        self.line, self.hair = T["line"], T["hair"]
        self.acc, self.hi = T["acc"], T["hi"]

    def add(self, s):
        self.out.append(s)

    @staticmethod
    def esc(s):
        return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def txt(self, x, y, s, size=15, fill=None, ls=2.0, anchor="start", weight=600,
            cls="", op=None, halo=0, face=None):
        """halo = width of the opposite-tone outline painted under the glyph:
        invisible on the intended background, readable on the wrong one."""
        T = self.T
        c = f' class="{cls}"' if cls else ""
        o = f' opacity="{op}"' if op is not None else ""
        ff = f' font-family=\'{face}\'' if face else ""
        h = (f' paint-order="stroke" stroke="{T["halo"]}" stroke-opacity="{T["halo_op"]}" '
             f'stroke-width="{halo}" stroke-linejoin="round"' if halo else "")
        return (f'<text{c} x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill or self.mut}" '
                f'font-weight="{weight}" letter-spacing="{ls}" text-anchor="{anchor}"{o}{h}{ff}>'
                f'{self.esc(s)}</text>')

    @staticmethod
    def win_check(label, *ts):
        """Keyframe times must be non-decreasing. CSS sorts keyframes by
        percentage, so a window that closes before it opens does not fail -
        it silently draws two things on top of each other."""
        for i in range(len(ts) - 1):
            assert ts[i] <= ts[i + 1] + 1e-9, (
                f"{label}: inverted window, {ts[i]:.2f}s comes after {ts[i+1]:.2f}s")
        return True

    def header(self):
        S, T, th = self.S, self.T, self.th
        add = self.add
        css = self.css
        ink, mut, faint = self.ink, self.mut, self.faint
        acc, hi = self.acc, self.hi
        fmt_ = fmt
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

        # Gooey + directional motion blur, for the one moment the squares are in
        # the air. feGaussianBlur softens them, feColorMatrix drives the alpha
        # back up so the blobs re-harden and fuse like mercury; the blur is
        # directional (7 across, 2 down) so the flight reads as speed, not fog.
        d.append('<filter id="melt" x="-25%" y="-25%" width="150%" height="150%">'
                 '<feGaussianBlur in="SourceGraphic" stdDeviation="4.5 1.4" result="b"/>'
                 '<feColorMatrix in="b" type="matrix" result="g" values="'
                 '1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 28 -12"/>'
                 '<feBlend in="SourceGraphic" in2="g"/></filter>')
        # Liquid displacement for the tear. baseFrequency and scale cannot be
        # animated from CSS, so three fixed states are baked and switched at the
        # hard-cut samples: the distortion moves without a line of JavaScript.
        for li, (bf, sc, sd) in enumerate(((".009 .035", 22, 3),
                                           (".021 .012", 15, 11),
                                           (".006 .052", 28, 29))):
            d.append(f'<filter id="liq{li}" x="-12%" y="-12%" width="124%" height="124%">'
                     f'<feTurbulence type="fractalNoise" baseFrequency="{bf}" numOctaves="2" '
                     f'seed="{sd}" result="t"/>'
                     f'<feDisplacementMap in="SourceGraphic" in2="t" scale="{sc}" '
                     f'xChannelSelector="R" yChannelSelector="G"/></filter>')        # RGB split for the tear: the three channels come apart by a few pixels.
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

    def preamble(self):
        css, T = self.css, self.T
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

    def assemble(self):
        out, css = self.out, self.css
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
