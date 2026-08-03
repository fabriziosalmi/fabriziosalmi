#!/usr/bin/env python3
"""A replica of GitHub's contribution panel, measured from the real thing:
53 columns, 10px cells on a 13px pitch, palette out of GitHub's own
stylesheets. It is the first frame of the loop and the last."""
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
    days = S["days"]      # the month labels come from the same calendar
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

