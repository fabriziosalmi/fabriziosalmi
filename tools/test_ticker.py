#!/usr/bin/env python3
"""Edge cases for the profile strip.  python3 -m unittest discover -s tools"""
import os
import re
import sys
import unittest
import xml.dom.minidom
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import ticker
from ticker import NARROW, THEMES, WIDE, build, load, rows


def raw(counts=None, repos=None, followers=10, first_week_days=7):
    """A profile.json with 53 weeks ending on a fixed Sunday-started week."""
    start = date(2025, 9, 21)
    counts = counts or [3] * (53 * 7)
    weeks, i = [], 0
    for w in range(53):
        n = first_week_days if w == 0 else 7
        days = []
        for _ in range(n):
            days.append({"date": (start + timedelta(days=i)).isoformat(), "contributionCount": counts[i],
                         "contributionLevel": "NONE"})
            i += 1
        weeks.append({"contributionDays": days})
    repos = [{"name": "alpha", "stargazerCount": 5, "forkCount": 1, "createdAt": "2025-01-01T00:00:00Z",
              "primaryLanguage": {"name": "Python", "color": "#3572A5"}}] if repos is None else repos
    return {"data": {"user": {
        "followers": {"totalCount": followers},
        "repositories": {"totalCount": len(repos), "nodes": repos},
        "contributionsCollection": {"contributionCalendar": {
            "totalContributions": sum(counts[:i]), "weeks": weeks}}}}}


def render(S, P=None, since="2026-10-04", wide=True, th="dark"):
    doc = build(S, P, since, THEMES[th], wide)
    xml.dom.minidom.parseString(doc)          # well-formed, or the profile shows a broken image
    return doc


class Strip(unittest.TestCase):
    def test_every_layout_and_theme_is_valid(self):
        S = load(raw())
        for th in THEMES:
            for wide in (True, False):
                render(S, load(raw(followers=8)), wide=wide, th=th)

    def test_no_activity_at_all(self):
        doc = render(load(raw(counts=[0] * 371)))
        self.assertIsNone(re.search(r'="-?(nan|inf)"|[xy]="[^"]*(nan|inf)', doc))

    def test_no_repositories(self):
        render(load(raw(repos=[])), wide=True)
        render(load(raw(repos=[])), wide=False)

    def test_negative_delta_is_red_and_zero_is_muted(self):
        S, P = load(raw(followers=8)), load(raw(followers=10))
        line = "".join(t + k for t, k in dict(rows(S, P, "2026-10-04", True))["vs 10-04"])
        self.assertIn("-2", line)
        self.assertTrue(any(k == "n" for _, k in dict(rows(S, P, "2026-10-04", True))["vs 10-04"]))
        self.assertTrue(any(t == "+0" and k == "m" for t, k in dict(rows(S, P, "2026-10-04", True))["vs 10-04"]))

    def test_gainer_is_named_and_only_when_it_gained(self):
        a = {"name": "alpha", "stargazerCount": 5, "forkCount": 1, "createdAt": "x", "primaryLanguage": None}
        b = dict(a, name="beta", stargazerCount=2)
        S = load(raw(repos=[a, dict(b, stargazerCount=4)]))
        P = load(raw(repos=[a, b]))
        txt = "".join(t for t, _ in dict(rows(S, P, "2026-10-04", True))["vs 10-04"])
        self.assertIn("(beta)", txt)
        self.assertNotIn("(", "".join(t for t, _ in dict(rows(S, S, "2026-10-04", True))["vs 10-04"]))

    def test_first_week_clipped_by_the_window_does_not_pull_the_median(self):
        S = load(raw(counts=[10] * 371, first_week_days=3))
        self.assertIn("median 70", render(S))      # a whole week is 70, whatever the clipped one holds

    def test_rows_stay_inside_the_panel_in_the_worst_case(self):
        big = [{"name": "n" * 40, "stargazerCount": 999_999, "forkCount": 99_999, "createdAt": "x",
                "primaryLanguage": None}]
        small = [dict(big[0], stargazerCount=999_000)]       # a +999 day: already absurd
        S = load(raw(counts=[9_999] * 371, repos=big, followers=99_999))
        P = load(raw(counts=[9_999] * 371, repos=small, followers=99_000))
        for wide, g in ((True, WIDE), (False, NARROW)):
            for label, segs in rows(S, P, "2026-10-04", wide):
                n = len("".join(t for t, _ in segs))
                self.assertLessEqual(n, g["budget"], f"{'wide' if wide else 'narrow'} {label}: {n} chars")

    def test_same_data_same_drawing(self):
        S = load(raw())
        self.assertEqual(render(S), render(S))

    def test_true_text_is_the_default_state(self):
        # animation off (or unsupported): the noisy frames are invisible, the true text is not
        doc = render(load(raw()))
        self.assertIn(".f{opacity:0;", doc)
        self.assertNotIn(".t{opacity:0", doc)
        self.assertIn("prefers-reduced-motion", doc)

    def test_one_animation_never_ends(self):
        self.assertEqual(render(load(raw())).count("infinite"), 1)


if __name__ == "__main__":
    unittest.main()
