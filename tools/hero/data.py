#!/usr/bin/env python3
"""Reads data/profile.json and derives the views the scene asks for.
No drawing here, no timing: just the numbers."""
from datetime import datetime, timezone
import json

def load(path):
    u = json.load(open(path))["data"]["user"]
    repos = [r for r in u["repositories"]["nodes"]]
    days = [d for w in u["contributionsCollection"]["contributionCalendar"]["weeks"]
            for d in w["contributionDays"]]
    langs = {}
    for r in repos:
        L = (r["primaryLanguage"] or {}).get("name") or "OTHER"
        langs.setdefault(L, []).append(r)
    return dict(
        repos=repos,
        n_repos=u["repositories"]["totalCount"],
        followers=u["followers"]["totalCount"],
        stars=sum(r["stargazerCount"] for r in repos),
        days=days,
        contrib=u["contributionsCollection"]["contributionCalendar"]["totalContributions"],
        langs=langs,
        top=sorted(repos, key=lambda r: -r["stargazerCount"])[0],
        first_year=min(r["createdAt"] for r in repos)[:4],
        peak=max(d["contributionCount"] for d in days),
        active_days=sum(1 for d in days if d["contributionCount"] > 0),
        # the river: only repos with at least one star or one fork, oldest first
        river=sorted(
            [{"name": x["name"], "s": x["stargazerCount"], "f": x["forkCount"],
              "born": x["createdAt"], "year": x["createdAt"][:4],
              "color": (x["primaryLanguage"] or {}).get("color") or "#8b949e"}
             for x in repos if x["stargazerCount"] >= 1 or x["forkCount"] >= 1],
            key=lambda r: r["born"]),
        built=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    )
