"""Generates the modern monochrome SVGs for the GitHub profile README, in a
light and a dark version each (the README swaps them with <picture>).

Edit the DATA section, then run:  python scripts/build.py
Text is set in Geist, embedded in every SVG, so it renders the same everywhere.
"""

import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- DATA --

NAME = ["Glyka Marie", "Amahan"]
STATUS = "Available for projects"
TAGLINE = ["Developer, editor & videographer", "based in Cebu, Philippines."]

ABOUT = [  # the about card, line by line
    "I write the code, cut the film and",
    "frame the shot — so every scroll, edit",
    "and moment feels like a story worth",
    "staying for.",
]
BASED_IN = ("Cebu, Philippines", "GMT+8 · open to remote work")
LEARNING = ["Three.js & WebGL", "Color grading", "Motion graphics"]

CRAFTS = [  # (title, one-liner)
    ("Code", "Interfaces that feel alive."),
    ("Cut", "Edits with rhythm and story."),
    ("Capture", "Shots worth keeping."),
]

# (craft, [(tool, level 1-5)]) — level 5 tools are highlighted as daily drivers
STACK = [
    ("Code", [("HTML & CSS", 4), ("JavaScript", 4), ("TypeScript", 4), ("React", 4),
              ("Next.js", 4), ("Tailwind CSS", 4), ("GSAP", 3), ("Git", 4)]),
    ("Cut", [("Premiere Pro", 4), ("After Effects", 3), ("DaVinci Resolve", 3),
             ("CapCut", 4), ("Color grading", 4), ("Sound design", 3)]),
    ("Capture", [("Cinematic framing", 4), ("Composition", 4), ("Camera movement", 4),
                 ("B-roll", 4), ("Phone filming", 4)]),
]

FOOTER = "Thanks for stopping by"

# --------------------------------------------------------------- THEME --

W = 840  # the README column on desktop, so everything lands 1:1
ACCENT = "#c6ff3d"  # lime, the one color — same as the portfolio

THEMES = {
    "dark": dict(bg="#0a0a0a", card="#0f0f0f", raised="#161616", border="#262626", text="#fafafa",
                 muted="#a1a1a1", faint="#525252", grid="#1a1a1a", invert_bg="#fafafa", invert_fg="#0a0a0a",
                 glow=0.16, accent_ink=ACCENT, heat=["#161616", "#333333", "#6b6b6b", "#bdbdbd", ACCENT]),
    "light": dict(bg="#ffffff", card="#fafafa", raised="#ffffff", border="#e5e5e5", text="#0a0a0a",
                  muted="#525252", faint="#a3a3a3", grid="#efefef", invert_bg="#0a0a0a", invert_fg="#fafafa",
                  glow=0.32, accent_ink="#4d7c0f", heat=["#efefef", "#d4d4d4", "#8a8a8a", "#3a3a3a", "#9fd420"]),
}

FONT_B64 = base64.b64encode((ROOT / "scripts" / "fonts" / "Geist.woff2").read_bytes()).decode()
STYLE = (
    "<style>"
    f'@font-face{{font-family:Geist;src:url(data:font/woff2;base64,{FONT_B64}) format("woff2");font-weight:100 900}}'
    '.s{font-family:Geist,Inter,"Segoe UI",Helvetica,Arial,sans-serif}'
    ".m{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}"
    "</style>"
)

# ------------------------------------------------------------- HELPERS --


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def t(x, y, s, size, fill, weight=400, cls="s", anchor="start", ls=0.0, extra=""):
    spacing = f' letter-spacing="{ls}"' if ls else ""
    return (f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" font-weight="{weight}" fill="{fill}"'
            f' text-anchor="{anchor}"{spacing}{extra}>{esc(s)}</text>')


def width(s, size, mono=False):
    """Rough advance width — good enough for laying out pills."""
    return len(s) * size * (0.6 if mono else 0.515)


def label(x, y, s, th):
    return t(x, y, s.upper(), 11, th["muted"], 500, "m", ls=1.4)


def card(x, y, w, h, th, r=18, fill=None):
    return (f'<rect x="{x + 0.5}" y="{y + 0.5}" width="{w - 1}" height="{h - 1}" rx="{r}" '
            f'fill="{fill or th["card"]}" stroke="{th["border"]}"/>')


def pill(x, y, s, th, size=13, h=28, inverted=False, mono=False):
    w = width(s, size, mono) + 24
    bg, fg = (th["invert_bg"], th["invert_fg"]) if inverted else (th["raised"], th["text"])
    return (f'<rect x="{x + 0.5}" y="{y + 0.5}" width="{w:.0f}" height="{h - 1}" rx="{h / 2}" fill="{bg}" stroke="{th["border"]}"/>'
            + t(x + 12, y + h / 2 + size * 0.36, s, size, fg, 500, "m" if mono else "s")), w


def svg(w, h, body, label_text, th, defs=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{esc(label_text)}"><defs>{STYLE}{defs}</defs>{body}</svg>'
    )


def icon(kind, cx, cy, color, s=1.0):
    """Tiny line icons for the three crafts, centered on (cx, cy)."""
    sw = 2.2 * s
    if kind == "Code":
        return (f'<path d="M{cx - 8 * s} {cy - 9 * s}l-9 {9 * s} 9 {9 * s}M{cx + 8 * s} {cy - 9 * s}l9 {9 * s}-9 {9 * s}'
                f'M{cx + 3 * s} {cy - 12 * s}l-6 {24 * s}" stroke="{color}" stroke-width="{sw}" fill="none" '
                f'stroke-linecap="round" stroke-linejoin="round"/>')
    if kind == "Cut":  # an edit timeline: clips and a playhead
        return (f'<g fill="{color}"><rect x="{cx - 17 * s}" y="{cy - 9 * s}" width="{14 * s}" height="{6 * s}" rx="{2 * s}"/>'
                f'<rect x="{cx - 1 * s}" y="{cy - 9 * s}" width="{18 * s}" height="{6 * s}" rx="{2 * s}"/>'
                f'<rect x="{cx - 17 * s}" y="{cy + 2 * s}" width="{22 * s}" height="{6 * s}" rx="{2 * s}" opacity=".55"/></g>'
                f'<path d="M{cx + 4 * s} {cy - 14 * s}v{27 * s}" stroke="{color}" stroke-width="{sw}" stroke-linecap="round"/>')
    return (f'<rect x="{cx - 17 * s}" y="{cy - 10 * s}" width="{34 * s}" height="{22 * s}" rx="{5 * s}" stroke="{color}" '
            f'stroke-width="{sw}" fill="none"/><circle cx="{cx}" cy="{cy + 1 * s}" r="{6 * s}" stroke="{color}" '
            f'stroke-width="{sw}" fill="none"/><path d="M{cx - 7 * s} {cy - 10 * s}l3 {-4 * s}h{8 * s}l3 {4 * s}" '
            f'stroke="{color}" stroke-width="{sw}" fill="none" stroke-linejoin="round"/>')


# ------------------------------------------------------------- SCENES --

def hero(th):
    h = 360
    defs = (
        f'<pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse">'
        f'<path d="M28 0H0V28" fill="none" stroke="{th["grid"]}"/></pattern>'
        f'<radialGradient id="fade" cx="35%" cy="40%" r="75%"><stop offset="0" stop-color="#fff"/>'
        f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
        f'<mask id="gm"><rect width="{W}" height="{h}" fill="url(#fade)"/></mask>'
        f'<radialGradient id="glow" cx="80%" cy="18%" r="55%"><stop offset="0" stop-color="{ACCENT}" stop-opacity="{th["glow"]}"/>'
        f'<stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/></radialGradient>'
        f'<linearGradient id="ink" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{th["text"]}"/>'
        f'<stop offset="1" stop-color="{th["muted"]}"/></linearGradient>'
        f'<clipPath id="round"><rect width="{W}" height="{h}" rx="22"/></clipPath>'
    )
    body = [f'<g clip-path="url(#round)"><rect width="{W}" height="{h}" fill="{th["bg"]}"/>'
            f'<rect width="{W}" height="{h}" fill="url(#grid)" mask="url(#gm)"/>'
            f'<rect width="{W}" height="{h}" fill="url(#glow)"/></g>'
            f'<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="22" fill="none" stroke="{th["border"]}"/>']

    # Status pill with a pulsing dot
    sw = width(STATUS, 12.5) + 40
    body.append(f'<rect x="36.5" y="36.5" width="{sw:.0f}" height="29" rx="14.5" fill="{th["raised"]}" stroke="{th["border"]}"/>')
    body.append(f'<circle cx="52" cy="51" r="4" fill="{ACCENT}"/><circle cx="52" cy="51" r="4" fill="none" stroke="{ACCENT}">'
                f'<animate attributeName="r" values="4;10" dur="2s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="0.8;0" dur="2s" repeatCount="indefinite"/></circle>')
    body.append(t(64, 55.5, STATUS, 12.5, th["text"], 500))

    # Name, tagline, craft pills
    body.append(t(34, 140, NAME[0], 62, "url(#ink)", 600, ls=-2.6))
    body.append(t(34, 204, NAME[1], 62, "url(#ink)", 600, ls=-2.6))
    body.append(t(36, 246, TAGLINE[0], 18, th["muted"], 400))
    body.append(t(36, 270, TAGLINE[1], 18, th["muted"], 400))
    x = 36
    for i, (craft, _) in enumerate(CRAFTS):
        p, w = pill(x, 296, f"0{i + 1}  {craft}", th, size=13)
        body.append(p)
        x += w + 8

    # Three tilted cards, like the portfolio's hero covers, gently floating
    covers = [
        ("Code", -12, (-78, 18), th["raised"], th["text"], th["border"]),
        ("Cut", 5, (8, -10), th["invert_bg"], th["invert_fg"], th["invert_bg"]),
        ("Capture", 15, (88, 26), ACCENT, "#0a0a0a", ACCENT),
    ]
    cx0, cy0 = 660, 186
    for i, (craft, rot, (dx, dy), fill, ink, stroke) in enumerate(covers):
        cx, cy = cx0 + dx, cy0 + dy
        body.append(
            f'<g transform="rotate({rot} {cx} {cy})"><g>'
            f'<animateTransform attributeName="transform" type="translate" values="0 0;0 -7;0 0" dur="{6 + i}s" '
            f'begin="{i * 0.8}s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>'
            f'<rect x="{cx - 62}" y="{cy - 80}" width="124" height="160" rx="16" fill="#000" opacity=".18" transform="translate(4 8)"/>'
            f'<rect x="{cx - 62 + 0.5}" y="{cy - 80 + 0.5}" width="123" height="159" rx="16" fill="{fill}" stroke="{stroke}"/>'
            + t(cx - 48, cy - 56, f"0{i + 1}", 11, ink, 500, "m", ls=1)
            + icon(craft, cx, cy - 6, ink, 1.15)
            + t(cx - 48, cy + 62, craft.upper(), 12, ink, 600, "m", ls=1.6)
            + "</g></g>"
        )
    return svg(W, h, "".join(body), "Glyka Marie Amahan — developer, editor and videographer based in Cebu, Philippines", th, defs)


def about(th):
    gap = 12
    top_h, row_h = 222, 118
    h = top_h + gap + row_h
    rw = 300
    lw = W - rw - gap
    body = []

    # About paragraph — first line full ink, the rest muted
    body.append(card(0, 0, lw, top_h, th))
    body.append(label(26, 38, "About", th))
    for i, line in enumerate(ABOUT):
        body.append(t(26, 82 + i * 30, line, 22, th["text"] if i < 2 else th["muted"], 500, ls=-0.4))

    # Based in
    ch = (top_h - gap) / 2
    body.append(card(lw + gap, 0, rw, ch, th))
    body.append(label(lw + gap + 22, 32, "Based in", th))
    body.append(t(lw + gap + 22, 62, BASED_IN[0], 19, th["text"], 600, ls=-0.3))
    body.append(t(lw + gap + 22, 83, BASED_IN[1], 12.5, th["muted"]))

    # Currently learning, as pills
    y2 = ch + gap
    body.append(card(lw + gap, y2, rw, ch, th))
    body.append(label(lw + gap + 22, y2 + 32, "Currently learning", th))
    x, py = lw + gap + 22, y2 + 46
    for item in LEARNING:
        p, w = pill(x, py, item, th, size=12, h=24)
        if x + w > lw + gap + rw - 18:
            x, py = lw + gap + 22, py + 30
            p, w = pill(x, py, item, th, size=12, h=24)
        body.append(p)
        x += w + 6

    # Three craft cards
    cw = (W - gap * 2) / 3
    y = top_h + gap
    for i, (craft, line) in enumerate(CRAFTS):
        x = i * (cw + gap)
        body.append(card(x, y, cw, row_h, th))
        body.append(t(x + 22, y + 32, f"0{i + 1}", 11, th["faint"], 500, "m", ls=1))
        body.append(icon(craft, x + cw - 40, y + 34, th["accent_ink"] if i == 2 else th["text"], 0.9))
        body.append(t(x + 22, y + 72, craft, 22, th["text"], 600, ls=-0.5))
        body.append(t(x + 22, y + 96, line, 13.5, th["muted"]))
    return svg(W, h, "".join(body), "About: " + " ".join(ABOUT), th)


def stack(th):
    gap, pad = 12, 22
    cw = (W - gap * 2) / 3
    # Lay out pills first to know each card's height
    layouts, tallest = [], 0
    for craft, tools in STACK:
        x, y, items = pad, 104, []
        for tool, level in tools:
            w = width(tool, 13) + 24
            if x + w > cw - pad:
                x, y = pad, y + 36
            items.append((x, y, tool, level))
            x += w + 6
        layouts.append(items)
        tallest = max(tallest, y + 10 + pad)  # last pill row spans y-18 .. y+10
    head = 64
    h = head + tallest + 2

    body = [t(2, 28, "Tech stack", 24, th["text"], 600, ls=-0.6),
            t(2, 50, "What I build, cut and shoot with.", 14, th["muted"])]
    if any(level == 5 for _, tools in STACK for _, level in tools):  # legend only when something is highlighted
        lx = W - 2
        legend = "Daily driver"
        body.append(t(lx, 46, legend, 12, th["muted"], anchor="end"))
        body.append(f'<rect x="{lx - width(legend, 12) - 22}" y="35" width="14" height="14" rx="7" fill="{th["invert_bg"]}"/>')

    for i, ((craft, _), items) in enumerate(zip(STACK, layouts)):
        x0 = i * (cw + gap)
        body.append(card(x0, head, cw, tallest, th))
        body.append(t(x0 + pad, head + 32, f"0{i + 1}", 11, th["faint"], 500, "m", ls=1))
        body.append(icon(craft, x0 + cw - 40, head + 32, th["accent_ink"] if i == 2 else th["text"], 0.8))
        body.append(t(x0 + pad, head + 66, craft, 22, th["text"], 600, ls=-0.5))
        for j, (px, py, tool, level) in enumerate(items):
            p, _ = pill(x0 + px, head + py - 18, tool, th, size=13, inverted=level == 5)
            body.append(f'<g opacity="0"><set attributeName="opacity" to="1" begin="{0.15 + i * 0.2 + j * 0.06:.2f}s" fill="freeze"/>{p}</g>')
    return svg(W, h, "".join(body), "Tech stack: " + "; ".join(f"{c}: " + ", ".join(n for n, _ in tl) for c, tl in STACK), th)


def footer(th):
    h = 64
    defs = (f'<linearGradient id="line" x1="0" x2="1"><stop offset="0" stop-color="{th["border"]}" stop-opacity="0"/>'
            f'<stop offset=".5" stop-color="{th["faint"]}"/><stop offset="1" stop-color="{th["border"]}" stop-opacity="0"/></linearGradient>')
    body = (f'<rect x="0" y="12" width="{W}" height="1" fill="url(#line)"/>'
            f'<circle cx="{W / 2 - width(FOOTER, 13) / 2 - 12}" cy="43" r="3.5" fill="{ACCENT}"/>'
            + t(W / 2 + 6, 47, FOOTER, 13, th["muted"], 500, anchor="middle"))
    return svg(W, h, body, FOOTER, th, defs)


def main():
    out = ROOT / "assets"
    out.mkdir(exist_ok=True)
    for name, fn in {"hero": hero, "about": about, "stack": stack, "footer": footer}.items():
        for theme, th in THEMES.items():
            content = fn(th)
            (out / f"{name}-{theme}.svg").write_text(content, encoding="utf-8")
            print(f"{name}-{theme}.svg".ljust(24), f"{len(content) / 1024:6.1f} KB")


if __name__ == "__main__":
    main()
