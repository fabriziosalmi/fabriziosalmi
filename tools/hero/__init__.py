"""The profile hero: a GitHub panel that comes apart into the public record.

One module per concern, so an experiment stays reversible:

    geometry   canvas, timeline, polar maths
    palette    every colour, GitHub's own where it replicates GitHub
    rng        the seeded LCG - the only randomness permitted
    data       profile.json in, derived views out
    doc        buffers, text helpers, the inverted-window assertion
    motion     the trauma impact model, act shells, phase envelopes
    chrome     the dial
    ring       act 01, the year of contributions
    river      act 02, the repositories
    says       the full-canvas statements
    terminal   the prompt that opens and closes
    wall       GitHub's contribution panel, replicated
    reduced_motion  what a visitor with motion turned off sees
    build      the running order, and nothing else
"""
from .build import build
from .data import load
from .palette import THEMES
