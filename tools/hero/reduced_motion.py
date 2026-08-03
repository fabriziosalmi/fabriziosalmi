#!/usr/bin/env python3
"""What a visitor with "reduce motion" sees. Not an afterthought: it is the
most integrated frame of the whole loop, a piece of GitHub's own interface,
and it must never be a hole."""
from .geometry import *
from .rng import RNG
import math


def apply(d):
    css = d.css
    # Anyone with "reduce motion" gets the wall: no motion, no hole, and the most
    # integrated frame of the whole loop - a piece of GitHub's own interface.
    # (Goes last in the stylesheet, after every rule it has to beat.)
    css.append("""
@media (prefers-reduced-motion: reduce){
 *{animation:none!important}
 .dp,.act0,.act1,.act2,.dial0,.dial1,.dial2,.aura0,.aura1,.aura2,
 .pcol0,.pcol1,.pcol2{opacity:0!important}
 .wallui,.wallframe{opacity:1!important}
 .term{opacity:0!important}
}""")
