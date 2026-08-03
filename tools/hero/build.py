#!/usr/bin/env python3
"""Orchestrates one render. Nothing is drawn here — this file only says in what
order the scene happens, which is the one thing worth reading at a glance.

    terminal → wall → break → ring → say → river → say → back → terminal

Add a beat by adding a module and a line, not by growing an existing one
(demos/galaxy, principle 5).
"""
from .doc import Doc
from .geometry import *
from . import motion, chrome, eye, ring, river, roll, says, terminal, wall, reduced_motion


def build(S, th, T):
    d = Doc(S, th, T)

    d.header()             # <svg>, title, description, gradients and filters
    d.preamble()           # the base stylesheet
    motion.install(d)      # impacts, act shells, phase envelopes

    d.add('<g class="dp">')          # the data phase: everything past the wall
    motion.auras(d)
    says.render(d)                   # statements are buffered, drawn last
    chrome.render(d)                 # the dial, act 01 only
    ring.render(d)                   # act 01: the calendar becomes a year
    roll.render(d)                   # every public repository, by name, accelerating
    river.render(d)                  # act 02: the repositories, one dot per star
    d.add("</g>")

    d.add(d.squares[0])              # the calendar squares live in every phase
    _hub(d)
    d.add("".join(d.says))           # every statement rides on top of every drawing

    terminal.render(d)               # the prompt that opens and closes the loop
    wall.render(d)                   # GitHub's own panel, replicated
    _gap(d)

    reduced_motion.apply(d)          # what a visitor with motion turned off sees
    return d.assemble()


def _hub(d):
    """The eye. It used to be a spiral; a spiral does not watch anything."""
    d.add('<g class="dp">')
    for a in range(NACT):
        d.add(f'<circle class="hubr pcol{a}" cx="{CX}" cy="{CY}" r="30" fill="none" '
              f'stroke="{d.hi[a]}" stroke-width="1.4"/>')
    d.css.append(f"""
.hubr{{transform-origin:{CX}px {CY}px;animation:hubr 3s cubic-bezier(.3,0,.2,1) infinite}}
@keyframes hubr{{0%{{transform:scale(1);opacity:.55}}6%{{transform:scale(1.5);opacity:0}}
 100%{{transform:scale(1.5);opacity:0}}}}
""")
    eye.render(d, CX, CY, ACTW[0][0] + 0.2, ACTW[0][1])
    d.add("</g>")


def _gap(d):
    """The two blank frames the story is projected through, above everything."""
    d.add(f'<rect class="gap0" width="{W}" height="{H}" fill="{d.T["knock"]}" pointer-events="none"/>')
    d.add(f'<rect class="gap1" width="{W}" height="{H}" fill="{d.T["knock"]}" pointer-events="none"/>')
    d.add(f'<rect class="gap2" width="{W}" height="{H}" fill="{d.T["knock"]}" pointer-events="none"/>')
    d.add("</svg>")
