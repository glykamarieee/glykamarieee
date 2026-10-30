"""Draws the Activity card — GitHub stats and a contribution heatmap, light and
dark — from the GitHub GraphQL API. Runs daily in .github/workflows/profile.yml.

  python scripts/stats.py <login> <out-dir>          (needs GITHUB_TOKEN)
  python scripts/stats.py <login> <out-dir> --demo   (fake data, for previewing)

Writes <out-dir>/analysis-dark.svg and <out-dir>/analysis-light.svg.
"""

import datetime as dt
import json
import os
import random
import sys
import urllib.request

from build import ACCENT, THEMES, W, card, label, svg, t, width

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
    days = [{"date": str(start + dt.timedelta(d)), "contributionCount": max(0, int(rnd.gauss(1, 3)))} for d in range(365)]
    weeks = [{"contributionDays": days[i : i + 7]} for i in range(0, 365, 7)]
    return {
        "followers": {"totalCount": 7},
        "repositories": {"totalCount": 2, "nodes": [{"stargazerCount": 1}]},
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


def render(user, th):
    cc = user["contributionsCollection"]
    cal = cc["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    current, longest = streaks(days)
    stars = sum(r["stargazerCount"] for r in user["repositories"]["nodes"])

    h, pad, gap = 352, 24, 12
    body = [card(0, 0, W, h, th, r=22)]

    # Header
    body.append(t(pad, 42, "Activity", 24, th["text"], 600, ls=-0.6))
    body.append(t(pad, 64, f"Last 12 months · updated {dt.date.today():%b %d, %Y}", 13, th["muted"]))
    live = "Live from GitHub"
    lw = width(live, 12) + 34
    body.append(f'<rect x="{W - pad - lw + 0.5}" y="28.5" width="{lw:.0f}" height="27" rx="13.5" fill="{th["raised"]}" stroke="{th["border"]}"/>')
    body.append(f'<circle cx="{W - pad - lw + 15}" cy="42" r="3.5" fill="{ACCENT}"/>')
    body.append(t(W - pad - lw + 26, 46.5, live, 12, th["text"], 500))

    # KPI tiles
    kpis = [
        ("Contributions", f'{cal["totalContributions"]:,}', f'{cc["restrictedContributionsCount"]} private'),
        ("Commits", f'{cc["totalCommitContributions"]:,}', "this year"),
        ("Current streak", f"{current}", "days in a row"),
        ("Longest streak", f"{longest}", "days"),
    ]
    tw = (W - pad * 2 - gap * 3) / 4
    for i, (name, value, sub) in enumerate(kpis):
        x = pad + i * (tw + gap)
        body.append(card(x, 86, tw, 88, th, r=14, fill=th["raised"]))
        body.append(label(x + 16, 110, name, th))
        body.append(t(x + 16, 148, value, 30, th["text"], 600, ls=-1))
        body.append(t(x + 16 + width(value, 30, mono=True) + 6, 148, sub, 11.5, th["muted"]))  # digits are ~0.6em

    # Heatmap: one column per week, one row per weekday, spanning the card
    first = dt.date.fromisoformat(days[0]["date"])
    cols = ((dt.date.fromisoformat(days[-1]["date"]) - first).days + (first.weekday() + 1) % 7) // 7 + 1
    step = (W - pad * 2 + 3) / cols
    cell = step - 3
    peak = max((d["contributionCount"] for d in days), default=0) or 1
    hx, hy = pad, 194
    cells = []
    for d in days:
        day = dt.date.fromisoformat(d["date"])
        col = ((day - first).days + (first.weekday() + 1) % 7) // 7
        row = (day.weekday() + 1) % 7  # Sunday first, like GitHub
        n = d["contributionCount"]
        level = 0 if n == 0 else 1 + min(3, int(4 * n / peak)) if n < peak else 4  # top quarter = lime
        cells.append(f'<rect x="{hx + col * step:.1f}" y="{hy + row * step:.1f}" width="{cell:.1f}" height="{cell:.1f}" rx="2.5" fill="{th["heat"][level]}"/>')
    body.append(f'<g opacity="0"><animate attributeName="opacity" values="0;1" dur="0.8s" begin="0.2s" fill="freeze"/>{"".join(cells)}</g>')

    # Footer line: repos, stars, followers + legend
    fy = h - 26
    plural = lambda n, word: f"{n} {word}{'' if n == 1 else 's'}"
    facts = " · ".join([plural(user["repositories"]["totalCount"], "public repo"), plural(stars, "star"),
                        plural(user["followers"]["totalCount"], "follower")])
    body.append(t(pad, fy, facts, 12, th["muted"], 400, "m"))
    lx = W - pad - 5 * 14 - 34
    body.append(t(lx - 8, fy, "Less", 11, th["muted"], anchor="end"))
    for i, color in enumerate(th["heat"]):
        body.append(f'<rect x="{lx + i * 14}" y="{fy - 10}" width="10" height="10" rx="2.5" fill="{color}"/>')
    body.append(t(lx + 5 * 14 + 4, fy, "More", 11, th["muted"]))

    return svg(W, h, "".join(body), f"GitHub activity: {cal['totalContributions']} contributions in the last 12 months, current streak {current} days, longest {longest} days", th)


def main():
    login, out = sys.argv[1], sys.argv[2]
    user = demo() if "--demo" in sys.argv else fetch(login)
    os.makedirs(out, exist_ok=True)
    for theme, th in THEMES.items():
        path = os.path.join(out, f"analysis-{theme}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(render(user, th))
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
