"""Draws ANALYSIS.EXE — GitHub stats in the same 1-bit pixel style — from the
GitHub GraphQL API. Runs daily in .github/workflows/profile.yml.

  python scripts/stats.py <login> <out.svg>          (needs GITHUB_TOKEN)
  python scripts/stats.py <login> <out.svg> --demo   (fake data, for previewing)
"""

import datetime as dt
import json
import os
import random
import sys
import urllib.request

from build import BLACK, WHITE, W, svg, text, text_width, window

QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, first: 100) {
      totalCount
      nodes { stargazerCount }
    }
    contributionsCollection {
      totalCommitContributions
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount date } }
      }
    }
  }
}
"""


def fetch(login):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        data = json.load(res)
    if "errors" in data:
        raise SystemExit(data["errors"])
    return data["data"]["user"]


def demo():
    rnd = random.Random(4)
    start = dt.date.today() - dt.timedelta(days=364)
    days = [{"date": str(start + dt.timedelta(d)), "contributionCount": max(0, int(rnd.gauss(2, 3)))} for d in range(365)]
    weeks = [{"contributionDays": days[i : i + 7]} for i in range(0, 365, 7)]
    return {
        "followers": {"totalCount": 12},
        "repositories": {"totalCount": 6, "nodes": [{"stargazerCount": 3}]},
        "contributionsCollection": {
            "totalCommitContributions": 210,
            "restrictedContributionsCount": 40,
            "contributionCalendar": {"totalContributions": sum(d["contributionCount"] for d in days), "weeks": weeks},
        },
    }


def streaks(days):
    """Current streak (today may still be empty) and longest streak, in days."""
    counts = [d["contributionCount"] for d in days]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    current = 0
    tail = counts[:-1] if counts and counts[-1] == 0 else counts
    for c in reversed(tail):
        if not c:
            break
        current += 1
    return current, longest


def render(user):
    cal = user["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    current, longest = streaks(days)
    stars = sum(r["stargazerCount"] for r in user["repositories"]["nodes"])
    rows = [
        ("CONTRIBUTIONS", cal["totalContributions"]),
        ("COMMITS", user["contributionsCollection"]["totalCommitContributions"]),
        ("PRIVATE WORK", user["contributionsCollection"]["restrictedContributionsCount"]),
        ("CURRENT STREAK", f"{current} D"),
        ("LONGEST STREAK", f"{longest} D"),
        ("PUBLIC REPOS", user["repositories"]["totalCount"]),
        ("STARS", stars),
        ("FOLLOWERS", user["followers"]["totalCount"]),
    ]

    h = 360
    body = [window(1, 1, W - 2, h - 2, "ANALYSIS.EXE — LAST 12 MONTHS")]

    # Left: the numbers, dotted leaders like an old system report
    x, y, col_w = 28, 56, 330
    for i, (label, value) in enumerate(rows):
        val = str(value)
        body.append(f'<g opacity="0"><set attributeName="opacity" to="1" begin="{0.2 + i * 0.12:.2f}s" fill="freeze"/>')
        body.append(text(label, x, y, 2, "#9a9a9a"))
        vx = x + col_w - text_width(val, 2)
        dots_from = x + text_width(label, 2) + 8
        for dx in range(dots_from, vx - 8, 8):
            body.append(f'<rect x="{dx}" y="{y + 12}" width="2" height="2" fill="#5a5a5a"/>')
        body.append(text(val, vx, y, 2))
        body.append("</g>")
        y += 30

    # Right: contributions per week as dithered-looking pixel bars
    weeks = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in cal["weeks"]]
    gx, gy, gw, gh = 392, 64, W - 392 - 28, 210
    peak = max(weeks) or 1
    bar = gw / len(weeks)
    body.append(text("CONTRIBUTIONS / WEEK", gx, gy - 10 - 14, 2, "#9a9a9a"))
    body.append(f'<rect x="{gx}" y="{gy + gh}" width="{gw}" height="2" fill="{WHITE}"/>')
    for i, total in enumerate(weeks):
        bh = round(gh * total / peak / 4) * 4  # snap to 4px steps for a pixel look
        if not bh:
            continue
        bx = gx + i * bar
        fill = WHITE if total >= peak * 0.5 else "#9a9a9a" if total >= peak * 0.2 else "#5a5a5a"
        body.append(
            f'<rect x="{bx:.1f}" y="{gy + gh - bh}" width="{max(bar - 2, 2):.1f}" height="{bh}" fill="{fill}">'
            f'<animate attributeName="height" values="0;{bh}" dur="0.5s" begin="{0.3 + i * 0.015:.2f}s" fill="freeze"/>'
            f'<animate attributeName="y" values="{gy + gh};{gy + gh - bh}" dur="0.5s" begin="{0.3 + i * 0.015:.2f}s" fill="freeze"/></rect>'
        )
    first, last = days[0]["date"], days[-1]["date"]
    body.append(text(first.replace("-", "."), gx, gy + gh + 12, 2, "#9a9a9a"))
    body.append(text(last.replace("-", "."), gx + gw - text_width(last, 2), gy + gh + 12, 2, "#9a9a9a"))

    stamp = f"UPDATED {dt.date.today():%Y.%m.%d}"
    body.append(text(stamp, x, h - 34, 2, "#5a5a5a"))
    return svg(W, h, "".join(body), f"GitHub stats: {cal['totalContributions']} contributions in the last year, current streak {current} days")


def main():
    login, out = sys.argv[1], sys.argv[2]
    user = demo() if "--demo" in sys.argv else fetch(login)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(render(user))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
