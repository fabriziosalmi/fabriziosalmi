#!/usr/bin/env python3
"""The only randomness allowed. Seeded from the repo name, so two renders of
the same data draw the same picture down to the pixel."""
class RNG:
    """Seeded LCG, the only randomness allowed: two renders draw the same river."""

    def __init__(self, seed):
        self.s = seed & 0x7FFFFFFF or 1

    def next(self):
        self.s = (1103515245 * self.s + 12345) & 0x7FFFFFFF
        return self.s / 0x7FFFFFFF

    def uni(self, a, b):
        return a + (b - a) * self.next()
