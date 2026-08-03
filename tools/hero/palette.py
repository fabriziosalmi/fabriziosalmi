#!/usr/bin/env python3
"""Every colour used anywhere, in one place, so an aesthetic experiment is
one file wide (demos/galaxy, palette.py, same idea).

The calendar values are GitHub's own, read out of its theme stylesheets:
the ones circulating in blog posts are years out of date."""
# <picture> picks the variant from the OPERATING SYSTEM preference, but GitHub
# lets you override its theme by hand, so the pick can be wrong. Therefore:
#   - everything structural (rules, borders, small text) uses neutral greys that
#     have contrast against both white and near-black;
#   - large text carries a halo of the opposite tone (paint-order), invisible on
#     the intended background and a lifesaver on the wrong one.
# Net effect: the wrong variant looks worse, never unreadable.
# Display type is set in pure white and pure black, not in GitHub's greys.
# Raising the contrast of the largest thing on screen costs nothing and is the
# cheapest luxury signal there is; the greys stay for everything secondary.
NEUTRAL = "#7d8590"

THEMES = {
    "dark": dict(
        cal=["#151b23", "#033a16", "#196c2e", "#2ea043", "#56d364"],
        # same scale, pushed up: GitHub's L1 reads as a 10px square and
        # vanishes as a 2px spoke, so the squares ignite once they fly
        lit=["#30363d", "#2ea043", "#56d364", "#7ee787", "#aff5b4"],
        ui_border="#3d444d", ui_mut="#9198a1", ui_fg="#f0f6fc",
        ink="#ffffff", mut="#9198a1", faint="#7d8590", line=NEUTRAL, hair=NEUTRAL,
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
        ink="#000000", mut="#636c76", faint="#6e7681", line=NEUTRAL, hair=NEUTRAL,
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
