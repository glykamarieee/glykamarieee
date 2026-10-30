"""Generates the 1-bit, dithered, retro-OS SVGs for the GitHub profile README.

Edit the DATA section, then run:  python scripts/build.py
Everything is drawn as pixels (a built-in 5x7 font + ordered dithering), so it
looks identical everywhere and needs no web fonts or outside services.
"""

import math
from pathlib import Path

# ---------------------------------------------------------------- DATA --

NAME = ["GLYKA MARIE", "AMAHAN"]
ROLE = "DEVELOPER · EDITOR · VIDEOGRAPHER"
PLACE = "CEBU, PH"

ABOUT = [
    ("> WHOAMI", False),
    ("GLYKA MARIE AMAHAN", True),
    ("> CAT ROLE.TXT", False),
    ("DEVELOPER, EDITOR AND VIDEOGRAPHER", True),
    ("> CAT LOCATION.TXT", False),
    ("CEBU, PHILIPPINES", True),
    ("> LS CRAFTS/", False),
    ("CODE/   CUT/   CAPTURE/", True),
    ("> CAT NOW.TXT", False),
    ("LEARNING THREE.JS, COLOR GRADING, DRONE SHOTS", True),
    ("> CAT MOTTO.TXT", False),
    ("EVERY SCROLL, CUT AND FRAME SHOULD SAY SOMETHING.", True),
]

# (category, [(tool, level 1-5)])
STACK = [
    ("CODE", [("HTML & CSS", 5), ("JAVASCRIPT", 4), ("TYPESCRIPT", 4), ("REACT", 4),
              ("NEXT.JS", 4), ("TAILWIND CSS", 4), ("GSAP", 3), ("GIT", 4)]),
    ("CUT", [("PREMIERE PRO", 4), ("AFTER EFFECTS", 3), ("DAVINCI RESOLVE", 3),
             ("CAPCUT", 5), ("COLOR GRADING", 4), ("SOUND DESIGN", 3)]),
    ("CAPTURE", [("CINEMATIC FRAMING", 4), ("CAMERA MOVEMENT", 4), ("DRONE SHOTS", 3),
                 ("NATURAL LIGHT", 4), ("STORYBOARDING", 3), ("PHONE FILMING", 5)]),
]

HEADINGS = ["SNAKE.EXE", "CONTACT.EXE"]  # ANALYSIS.EXE is drawn by scripts/stats.py

# --------------------------------------------------------------- PIXELS --

W = 840  # matches the README column on desktop, so pixels land 1:1
WHITE, BLACK = "#fff", "#000"

FONT = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": [".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "J": ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    " ": ["....."] * 7,
    ".": [".....", ".....", ".....", ".....", ".....", ".##..", ".##.."],
    ",": [".....", ".....", ".....", ".....", ".##..", "..#..", ".#..."],
    "-": [".....", ".....", ".....", "#####", ".....", ".....", "....."],
    "—": [".....", ".....", ".....", "#####", ".....", ".....", "....."],
    "/": ["....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."],
    ":": [".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."],
    "'": ["..#..", "..#..", ".#...", ".....", ".....", ".....", "....."],
    "·": [".....", ".....", ".....", "..#..", ".....", ".....", "....."],
    ">": [".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."],
    "<": ["...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."],
    "_": [".....", ".....", ".....", ".....", ".....", ".....", "#####"],
    "(": ["...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."],
    ")": [".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."],
    "&": [".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"],
    "!": ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    "+": [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    "@": [".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."],
    "|": ["..#.."] * 7,
    "%": ["##..#", "##..#", "...#.", "..#..", ".#...", "#..##", "#..##"],
    "#": [".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."],
    "=": [".....", ".....", "#####", ".....", "#####", ".....", "....."],
    "[": [".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."],
    "]": [".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."],
}

ICONS = {
    "code": [
        "....#.....#....",
        "...#.....#.....",
        "..#......#..#..",
        ".#......#....#.",
        "#.......#.....#",
        ".#.....#.....#.",
        "..#....#....#..",
        "...#..#........",
        "....#.#........",
    ],
    "cut": [
        ".##.......##.",
        "#..#.....#..#",
        "#..#.....#..#",
        ".####...####.",
        ".....#.#.....",
        "......#......",
        ".....#.#.....",
        "....#...#....",
        "...#.....#...",
        "..#.......#..",
    ],
    "capture": [
        "....####.......",
        "###############",
        "#.............#",
        "#....#####..#.#",
        "#...#.....#...#",
        "#...#.....#...#",
        "#...#.....#...#",
        "#....#####....#",
        "#.............#",
        "###############",
    ],
}

BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def runs(cells, x0, y0, p):
    """Merge a set of (col, row) cells into horizontal-run path data."""
    by_row = {}
    for c, r in cells:
        by_row.setdefault(r, []).append(c)
    d = []
    for r, cols in by_row.items():
        cols.sort()
        start = prev = cols[0]
        for c in cols[1:] + [None]:
            if c is not None and c == prev + 1:
                prev = c
                continue
            d.append(f"M{x0 + start * p:g} {y0 + r * p:g}h{(prev - start + 1) * p:g}v{p:g}h-{(prev - start + 1) * p:g}z")
            if c is not None:
                start = prev = c
    return "".join(d)


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def text(s, x, y, scale, fill=WHITE, extra=""):
    cells = []
    for i, ch in enumerate(s.upper()):
        glyph = FONT.get(ch, FONT["?"])
        for r, row in enumerate(glyph):
            for c, bit in enumerate(row):
                if bit == "#":
                    cells.append((i * 6 + c, r))
    return f'<path fill="{fill}" d="{runs(cells, x, y, scale)}"{extra}/>'


def bitmap(rows, x, y, scale, fill=WHITE):
    cells = [(c, r) for r, row in enumerate(rows) for c, bit in enumerate(row) if bit == "#"]
    return f'<path fill="{fill}" d="{runs(cells, x, y, scale)}"/>'


def dither(fn, x0, y0, cols, rows, p, fill=WHITE):
    """fn(col, row) -> brightness 0..1 (None = outside). Ordered 4x4 Bayer dithering."""
    cells = []
    for r in range(rows):
        for c in range(cols):
            b = fn(c, r)
            if b is not None and b > (BAYER[r % 4][c % 4] + 0.5) / 16:
                cells.append((c, r))
    return f'<path fill="{fill}" d="{runs(cells, x0, y0, p)}"/>'


def sphere(cx, cy, radius, p, light=(-0.55, -0.6, 0.58), clip=None):
    lx, ly, lz = light
    n = math.sqrt(lx * lx + ly * ly + lz * lz)
    lx, ly, lz = lx / n, ly / n, lz / n
    size = int(radius * 2 / p) + 1
    x0, y0 = cx - radius, cy - radius

    def fn(c, r):
        px, py = x0 + (c + 0.5) * p, y0 + (r + 0.5) * p
        if clip and not clip(px, py):
            return None
        dx, dy = (px - cx) / radius, (py - cy) / radius
        d2 = dx * dx + dy * dy
        if d2 > 1:
            return None
        dz = math.sqrt(1 - d2)
        lit = max(0.0, dx * lx + dy * ly + dz * lz)
        rim = 0.18 * (1 - dz) ** 3  # faint edge glow on the dark side
        return min(1.0, lit ** 1.4 + rim)

    return dither(fn, x0, y0, size, size, p)


def stars(seed, count, w, h, avoid=None):
    """Deterministic scatter of 1-2px stars; a few twinkle."""
    out = []
    s = seed
    for i in range(count):
        s = (s * 1103515245 + 12345) & 0x7FFFFFFF
        x = s % w
        s = (s * 1103515245 + 12345) & 0x7FFFFFFF
        y = s % h
        if avoid and avoid(x, y):
            continue
        size = 2 if i % 5 else 3
        anim = ""
        if i % 7 == 0:
            anim = f'<animate attributeName="opacity" values="1;0.15;1" dur="{2 + i % 3}s" begin="{(i % 5) * 0.4}s" repeatCount="indefinite"/>'
        out.append(f'<rect x="{x}" y="{y}" width="{size}" height="{size}" fill="{WHITE}">{anim}</rect>')
    return "".join(out)


def window(x, y, w, h, title, body_fill=BLACK):
    """Retro OS window: white frame, white title bar with black pixel title and _ □ x."""
    bar = 30
    parts = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{body_fill}" stroke="{WHITE}" stroke-width="3"/>',
        f'<rect x="{x}" y="{y}" width="{w}" height="{bar}" fill="{WHITE}"/>',
        text(title, x + 12, y + 8, 2, BLACK),
    ]
    for i, glyph in enumerate(["_", "□", "x"]):
        bx = x + w - 3 * 24 - 6 + i * 24
        parts.append(f'<rect x="{bx}" y="{y + 6}" width="18" height="18" fill="{WHITE}" stroke="{BLACK}" stroke-width="2"/>')
        if glyph == "_":
            parts.append(f'<rect x="{bx + 5}" y="{y + 17}" width="8" height="2" fill="{BLACK}"/>')
        elif glyph == "□":
            parts.append(f'<rect x="{bx + 5}" y="{y + 11}" width="8" height="8" fill="none" stroke="{BLACK}" stroke-width="2"/>')
        else:
            parts.append(text("X", bx + 4, y + 8, 2, BLACK))
    return "".join(parts)


def svg(w, h, body, label):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'shape-rendering="crispEdges" role="img" aria-label="{label}">'
        f'<rect width="{w}" height="{h}" fill="{BLACK}"/>{body}</svg>'
    )


def blink(dur="1.06s"):
    return f'<animate attributeName="opacity" values="1;0" dur="{dur}" repeatCount="indefinite" calcMode="discrete"/>'


# ------------------------------------------------------------- SCENES --

def header():
    h = 380
    wx, wy, ww, wh = 150, 70, 470, 250
    inside = lambda px, py: not (wx - 4 <= px <= wx + ww + 4 and wy - 4 <= py <= wy + wh + 4)
    body = [
        stars(7, 140, W, h, avoid=lambda x, y: not inside(x, y)),
        sphere(705, 300, 190, 4, clip=inside),
        sphere(78, 330, 46, 3, light=(0.6, -0.5, 0.6), clip=inside),
        window(wx, wy, ww, wh, "GLYKA_MARIE.EXE"),
    ]
    y = wy + 52
    for line in NAME:
        body.append(text(line, wx + 26, y, 6))
        y += 56
    body.append(text(ROLE, wx + 26, y + 6, 2))
    prompt = f"> {PLACE}"
    body.append(text(prompt, wx + 26, y + 34, 2))
    cx = wx + 26 + text_width(prompt, 2) + 6
    body.append(f'<rect x="{cx}" y="{y + 34}" width="10" height="14" fill="{WHITE}">{blink()}</rect>')
    # Loading bar that fills, holds, and starts over
    bx, by, bw = wx + 26, wy + wh - 34, ww - 52
    body.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="16" fill="none" stroke="{WHITE}" stroke-width="2"/>')
    steps = ";".join(str(round((bw - 8) * i / 12)) for i in list(range(13)) + [12, 12, 0])
    body.append(f'<rect x="{bx + 4}" y="{by + 4}" width="0" height="8" fill="{WHITE}">'
                f'<animate attributeName="width" values="{steps}" dur="4.8s" repeatCount="indefinite" calcMode="discrete"/></rect>')
    return svg(W, h, "".join(body), "Glyka Marie Amahan — developer, editor, videographer, Cebu PH")


def about():
    line_h = 26
    h = 30 + 28 + len(ABOUT) * line_h + 50
    body = [window(1, 1, W - 2, h - 2, "ABOUT.TXT — TERMINAL")]
    t = 0.3
    y = 30 + 26
    defs = []
    for i, (line, out) in enumerate(ABOUT):
        x = 28 if not out else 52
        width = text_width(line, 2) + 2
        n = max(1, len(line))
        step = 0.035 if not out else 0.018
        dur = n * step
        vals = ";".join(str(round(width * k / n)) for k in range(n + 1))
        defs.append(
            f'<clipPath id="l{i}"><rect x="{x}" y="{y - 2}" height="20" width="0">'
            f'<animate attributeName="width" values="{vals}" begin="{t:.2f}s" dur="{dur:.2f}s" fill="freeze" calcMode="discrete"/>'
            f"</rect></clipPath>"
        )
        body.append(f'<g clip-path="url(#l{i})">{text(line, x, y, 2, WHITE if out else "#9a9a9a")}</g>')
        t += dur + (0.15 if not out else 0.35)
        y += line_h
    cursor_x = 28
    body.append(text(">", cursor_x, y, 2, "#9a9a9a"))
    body.append(f'<rect x="{cursor_x + 18}" y="{y}" width="10" height="14" fill="{WHITE}" opacity="0">'
                f'<set attributeName="opacity" to="1" begin="{t:.2f}s"/>'
                f'<animate attributeName="visibility" values="visible;hidden" dur="1.06s" begin="{t:.2f}s" repeatCount="indefinite" calcMode="discrete"/></rect>')
    return svg(W, h, f"<defs>{''.join(defs)}</defs>" + "".join(body), "About Glyka: developer, editor and videographer from Cebu, Philippines")


def filmstrip():
    h = 230
    body = []
    # Sprocket holes that run past like film through a gate
    holes = "".join(f'<rect x="{x}" y="0" width="14" height="10" fill="{WHITE}"/>' for x in range(0, W + 40, 28))
    for y in (14, h - 24):
        body.append(f'<g transform="translate(0 {y})"><g>{holes}'
                    f'<animateTransform attributeName="transform" type="translate" values="0 0;-28 0" dur="0.6s" repeatCount="indefinite"/></g></g>')
    frames = [("01", "CODE", "code"), ("02", "CUT", "cut"), ("03", "CAPTURE", "capture")]
    fw, gap = 252, 18
    x = (W - (fw * 3 + gap * 2)) // 2
    for i, (num, label, icon) in enumerate(frames):
        fy, fh = 38, h - 76
        body.append(f'<rect x="{x}" y="{fy}" width="{fw}" height="{fh}" fill="{BLACK}" stroke="{WHITE}" stroke-width="3"/>')
        rows = ICONS[icon]
        scale = 6
        iw, ih = len(rows[0]) * scale, len(rows) * scale
        # A quick flicker per frame, staggered (discrete: each value holds until the next keyTime)
        at = 0.3 + i * 0.2
        body.append(f'<g>{bitmap(rows, x + (fw - iw) // 2, fy + 18, scale)}'
                    f'<animate attributeName="opacity" values="1;0.2;1" keyTimes="0;{at:.2f};{at + 0.04:.2f}" dur="3s" repeatCount="indefinite" calcMode="discrete"/></g>')
        cap = f"{num} {label}"
        body.append(text(cap, x + (fw - text_width(cap, 3)) // 2, fy + 18 + ih + 18, 3))
        x += fw + gap
    return svg(W, h, "".join(body), "Three crafts: code, cut, capture")


def stack():
    cols = len(STACK)
    pad, gap = 24, 16
    cw = (W - pad * 2 - gap * (cols - 1)) // cols
    item_h = 44
    rows = max(len(items) for _, items in STACK)
    h = 30 + 30 + 34 + rows * item_h + 20
    body = [window(1, 1, W - 2, h - 2, "STACK.EXE — TOOLS & LEVELS")]
    seg, seg_gap, segs = 20, 4, 10
    for ci, (cat, items) in enumerate(STACK):
        x = pad + ci * (cw + gap)
        y = 30 + 26
        body.append(text(f"[{cat}]", x, y, 3))
        body.append(f'<rect x="{x}" y="{y + 28}" width="{cw}" height="2" fill="{WHITE}"/>')
        y += 46
        for ii, (tool, level) in enumerate(items):
            body.append(text(tool, x, y, 2))
            by = y + 20
            filled = level * 2
            for s in range(segs):
                sx = x + s * (seg + seg_gap)
                body.append(f'<rect x="{sx}" y="{by}" width="{seg}" height="10" fill="none" stroke="#5a5a5a" stroke-width="1"/>')
            begin = 0.4 + ci * 0.25 + ii * 0.08
            for s in range(filled):
                sx = x + s * (seg + seg_gap)
                body.append(f'<rect x="{sx}" y="{by}" width="{seg}" height="10" fill="{WHITE}" opacity="0">'
                            f'<set attributeName="opacity" to="1" begin="{begin + s * 0.05:.2f}s"/></rect>')
            y += item_h
    return svg(W, h, "".join(body), "Tech stack: code, editing and filming tools with skill levels")


def heading(title):
    h = 40
    body = window(1, 1, W - 2, 36, title)
    return svg(W, h, body, title)


def footer():
    h = 200

    def ground(c, r):
        # Dithered horizon: brightness rises toward the bottom, with a slow wave
        y = r / 49
        wave = 0.08 * math.sin(c / 14) + 0.05 * math.sin(c / 5.3)
        return max(0.0, (y - 0.35 + wave) * 1.6)

    body = [
        stars(3, 60, W, 90),
        dither(ground, 0, 0, W // 4, 50, 4),
    ]
    msg = "THANKS FOR STOPPING BY"
    sub = "GLYKA.EXE · SESSION END"
    body.append(f'<rect x="{(W - text_width(msg, 3)) // 2 - 20}" y="52" width="{text_width(msg, 3) + 40}" height="70" fill="{BLACK}" stroke="{WHITE}" stroke-width="3"/>')
    body.append(text(msg, (W - text_width(msg, 3)) // 2, 64, 3))
    body.append(text(sub, (W - text_width(sub, 2)) // 2, 98, 2, "#9a9a9a"))
    return svg(W, h, "".join(body), "Thanks for stopping by")


def main():
    out = Path(__file__).resolve().parent.parent / "assets"
    out.mkdir(exist_ok=True)
    files = {
        "header.svg": header(),
        "about.svg": about(),
        "crafts.svg": filmstrip(),
        "stack.svg": stack(),
        "footer.svg": footer(),
    }
    for title in HEADINGS:
        files[f"heading-{title.split('.')[0].lower()}.svg"] = heading(title)
    for name, content in files.items():
        (out / name).write_text(content, encoding="utf-8")
        print(f"{name:24} {len(content) / 1024:6.1f} KB")


if __name__ == "__main__":
    main()
