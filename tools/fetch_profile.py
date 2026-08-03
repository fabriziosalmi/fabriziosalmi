#!/usr/bin/env python3
"""Fetch the public profile data and store it in data/profile.json.

Needs a token in GITHUB_TOKEN (Actions already provides secrets.GITHUB_TOKEN).
No third-party dependencies: urllib only.

    python3 tools/fetch_profile.py [login] [destination]
"""
import json
import os
import sys
import urllib.request

# first:100 is the per-page maximum: past that, repos must be paginated or the
# star total silently stops at the first hundred.
QUERY = """
{
  user(login: "%s") {
    followers { totalCount }
    repositories(first: 100, %s ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false,
                 orderBy: {field: STARGAZERS, direction: DESC}) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes { name stargazerCount forkCount createdAt primaryLanguage { name color } }
    }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount contributionLevel } }
      }
    }
  }
}
"""


def query(token, login, cursor=None):
    after = f'after: "{cursor}",' if cursor else ""
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY % (login, after)}).encode(),
        headers={"Authorization": f"bearer {token}",
                 "Content-Type": "application/json",
                 "User-Agent": "hero-generator"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if "errors" in payload:
        sys.exit(f"GraphQL: {payload['errors']}")
    if not payload.get("data", {}).get("user"):
        sys.exit("response carried no user data")
    return payload


def main():
    login = sys.argv[1] if len(sys.argv) > 1 else "fabriziosalmi"
    dest = sys.argv[2] if len(sys.argv) > 2 else "data/profile.json"
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("GITHUB_TOKEN missing")

    payload = query(token, login)
    repos = payload["data"]["user"]["repositories"]
    page = repos
    while page["pageInfo"]["hasNextPage"]:
        page = query(token, login, page["pageInfo"]["endCursor"])["data"]["user"]["repositories"]
        repos["nodes"].extend(page["nodes"])
    repos.pop("pageInfo", None)

    # Guardrails: this runs at night, unattended, and commits to a public profile.
    # Better to fail the job than to publish a drawing full of zeros.
    u = payload["data"]["user"]
    nodes = u["repositories"]["nodes"]
    now = {
        "repos": len(nodes),
        "stars": sum(n["stargazerCount"] for n in nodes),
        "contrib": u["contributionsCollection"]["contributionCalendar"]["totalContributions"],
        "days": sum(len(w["contributionDays"])
                    for w in u["contributionsCollection"]["contributionCalendar"]["weeks"]),
    }
    for k in ("repos", "stars", "contrib"):
        if now[k] <= 0:
            sys.exit(f"suspicious data: {k} = {now[k]}, writing nothing")
    if now["days"] < 360:
        sys.exit(f"incomplete calendar: {now['days']} days, writing nothing")

    # and it must not collapse against yesterday: stars and repos do not vanish
    if os.path.exists(dest):
        try:
            old = json.load(open(dest))["data"]["user"]
            oldn = old["repositories"]["nodes"]
            was = {"repos": len(oldn), "stars": sum(n["stargazerCount"] for n in oldn)}
            for k in ("repos", "stars"):
                if now[k] < was[k] * 0.8:
                    sys.exit(f"suspicious drop in {k}: {was[k]} -> {now[k]}, writing nothing")
        except (KeyError, ValueError):
            pass  # previous file unreadable: fine, this one becomes the baseline

    os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1, sort_keys=True)
        f.write("\n")

    print(f'{dest}: {now["repos"]} repos, {now["stars"]} stars, {now["contrib"]} contributions')


if __name__ == "__main__":
    main()
