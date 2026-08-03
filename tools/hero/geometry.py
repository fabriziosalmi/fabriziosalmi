#!/usr/bin/env python3
"""Canvas, timeline and the small maths everything else measures against.

Times are in seconds because beats are easier to reason about than
percentages; pc() is the only place they become CSS."""
import math

W, H = 920, 400
CX, CY, R = 460, 198, 168        # the dial, centred
LX = 56                          # left column

# The loop is a match cut: it opens on a pixel-accurate replica of GitHub's own
# contribution panel, breaks it, flies the data out of the frame, and puts every
# square back where it was. Seconds, not percentages, so the beats stay readable.
LOOP = 24.0
T_TERM = 2.2                     # the terminal types, then the wall materialises
T_WALL = 4.6                     # the wall holds still, long enough to be believed
T_OUT = 20.9                     # and the terminal comes back to say what happens next
# Drawing beats and text beats alternate: they never share the frame, which is
# what kept the type small. Alone on the canvas a number can be 110px.
ACTW = [(6.0, 8.6), (10.6, 15.4)]   # 01 the ring · 02 the river (drawing only)
SAY_NAME = (4.6, 6.0)               # the name lands while the wall comes apart
SAY_1 = (8.7, 10.5)                 # what the ring was
SAY_2 = (15.9, 19.0)                # what the river was
T_BACK = (19.1, 20.6)               # everything returns behind the wall
NACT = 2

# The river: the galaxy of demos/galaxy straightened out for a letterbox frame.
# Same model (one dot per star, forks lighter, cluster radius from sqrt(total),
# points sorted from the centre, a sun per repo coloured by language) with the
# spiral swapped for a timeline, because a spiral in a 2.3:1 frame wastes the
# corners and clips at the edges.
RX0, RX1 = 72, 866
RCY, RAMP = 198, 96
RIV_BUILD, RIV_FLASH, RIV_NAMED = 3.0, 0.0, 4

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

# Two voices, and the split is semantic, not decorative:
#   mono    -> the terminal and GitHub's own chrome, where mono means something
#   display -> everything the visitor is meant to read, in the system grotesque
# Display type is set the modern way: very large, very tight, very heavy, with
# the label under it small and widely tracked. Mono at 108px is just wide.
DISPLAY = ('-apple-system, BlinkMacSystemFont, "Segoe UI Variable Display", '
           '"Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif')

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
