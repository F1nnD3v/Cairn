"""Generate Cairn's window decorations (KDE Aurorae SVG themes) with hexagonal buttons.

    python3 brand/tools/make_window_decoration.py brand/plasma/aurorae

Writes two themes, Cairn (dark) and CairnLight, each with:
  metadata.desktop, <Name>rc, decoration.svg, close.svg, minimize.svg, maximize.svg, restore.svg

How Aurorae (KWin's SVG decoration engine, plugin org.kde.kwin.aurorae.v2) reads them:
- decoration.svg is a 9-slice frame (decoration-topleft, -top, ..., -center; the same with
  decoration-inactive-*). Each element's size is the frame margin; the centre is stretched
  under the titlebar and window. The outer ring of PAD pixels is the shadow (Padding* in the rc).
- Each button SVG has one group per state (active-center, hover-center, ...), stretched to
  ButtonWidth x ButtonHeight.
"""
import math
import os
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "brand/plasma/aurorae"

PAD = 16        # shadow ring
R_TOP = 8       # top corner radius
R_BOTTOM = 4    # bottom corner radius
BTN = 24        # button box

THEMES = {
    "Cairn": dict(
        title="#24272C", title_inactive="#1B1D21",
        text="#ECEDEF", text_inactive="#A3A7AF",
        shadow=0.38, shadow_inactive=0.26,
        btn=dict(
            normal=("#33363D", "#ECEDEF"), hover=("#4A4F57", "#FFFFFF"), pressed=("#5E646D", "#FFFFFF"),
            inactive=("#2A2D33", "#6F747C"), deactivated=("#2A2D33", "#4A4F57"),
        ),
        close=dict(
            normal=("#F4A62A", "#18191C"), hover=("#FFBA4A", "#18191C"), pressed=("#D99020", "#18191C"),
            inactive=("#2A2D33", "#6F747C"), deactivated=("#2A2D33", "#4A4F57"),
        ),
        comment="Cairn window decoration (dark): hexagonal buttons, honey close button",
    ),
    "CairnLight": dict(
        title="#E9EAEC", title_inactive="#F4F4F5",
        text="#18191C", text_inactive="#5C6068",
        shadow=0.22, shadow_inactive=0.14,
        btn=dict(
            normal=("#D2D4D8", "#18191C"), hover=("#C2C5CA", "#18191C"), pressed=("#B0B4BA", "#18191C"),
            inactive=("#E1E2E5", "#80868F"), deactivated=("#E1E2E5", "#B0B4BA"),
        ),
        close=dict(
            normal=("#D08200", "#18191C"), hover=("#E0920F", "#18191C"), pressed=("#B87300", "#18191C"),
            inactive=("#E1E2E5", "#80868F"), deactivated=("#E1E2E5", "#B0B4BA"),
        ),
        comment="Cairn window decoration (light): hexagonal buttons, honey close button",
    ),
}


def f(v):
    return f"{v:.3f}".rstrip("0").rstrip(".")


# ---------------------------------------------------------------- decoration.svg

def frame(prefix, fill, alpha, x0, y0):
    """One 9-slice frame, laid out at (x0, y0) in the SVG canvas. Returns (svg, gradient defs)."""
    S = PAD + R_TOP        # left/right/top margin
    B = PAD + R_BOTTOM     # bottom margin
    sh = f"rgb(0,0,0)"
    g = []    # gradients
    e = []    # elements
    gid = prefix.replace("-", "_")

    def radial(name, cx, cy, r, inner):
        g.append(
            f'<radialGradient id="{name}" gradientUnits="userSpaceOnUse" cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}">'
            f'<stop offset="{f(inner)}" stop-color="{sh}" stop-opacity="{alpha}"/>'
            f'<stop offset="1" stop-color="{sh}" stop-opacity="0"/></radialGradient>')

    def linear(name, x1, y1, x2, y2):
        g.append(
            f'<linearGradient id="{name}" gradientUnits="userSpaceOnUse" x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}">'
            f'<stop offset="0" stop-color="{sh}" stop-opacity="{alpha}"/>'
            f'<stop offset="1" stop-color="{sh}" stop-opacity="0"/></linearGradient>')

    # Coordinates of each piece on the canvas (pieces are spaced apart so they don't touch).
    gap = 4
    cx0, cx1, cx2 = x0, x0 + S + gap, x0 + S + gap + 1 + gap        # columns: left, middle (1px), right
    cy0, cy1, cy2 = y0, y0 + S + gap, y0 + S + gap + 1 + gap        # rows: top, middle (1px), bottom

    # top-left corner (S x S): window corner at (PAD, PAD), arc centre at (S, S)
    x, y = cx0, cy0
    radial(f"{gid}_tl", x + S, y + S, S, R_TOP / S)
    e.append(f'<g id="{prefix}-topleft"><rect x="{x}" y="{y}" width="{S}" height="{S}" fill="url(#{gid}_tl)"/>'
             f'<path d="M{x+S} {y+PAD} A{R_TOP} {R_TOP} 0 0 0 {x+PAD} {y+S} L{x+S} {y+S}Z" fill="{fill}"/></g>')
    # top edge (1 x S)
    x, y = cx1, cy0
    linear(f"{gid}_t", x, y + PAD, x, y)
    e.append(f'<g id="{prefix}-top"><rect x="{x}" y="{y}" width="1" height="{PAD}" fill="url(#{gid}_t)"/>'
             f'<rect x="{x}" y="{y+PAD}" width="1" height="{R_TOP}" fill="{fill}"/></g>')
    # top-right corner
    x, y = cx2, cy0
    radial(f"{gid}_tr", x, y + S, S, R_TOP / S)
    e.append(f'<g id="{prefix}-topright"><rect x="{x}" y="{y}" width="{S}" height="{S}" fill="url(#{gid}_tr)"/>'
             f'<path d="M{x} {y+PAD} A{R_TOP} {R_TOP} 0 0 1 {x+R_TOP} {y+S} L{x} {y+S}Z" fill="{fill}"/></g>')
    # left edge (S x 1)
    x, y = cx0, cy1
    linear(f"{gid}_l", x + PAD, y, x, y)
    e.append(f'<g id="{prefix}-left"><rect x="{x}" y="{y}" width="{PAD}" height="1" fill="url(#{gid}_l)"/>'
             f'<rect x="{x+PAD}" y="{y}" width="{R_TOP}" height="1" fill="{fill}"/></g>')
    # centre (1 x 1)
    x, y = cx1, cy1
    e.append(f'<rect id="{prefix}-center" x="{x}" y="{y}" width="1" height="1" fill="{fill}"/>')
    # right edge
    x, y = cx2, cy1
    linear(f"{gid}_r", x + R_TOP, y, x + S, y)
    e.append(f'<g id="{prefix}-right"><rect x="{x}" y="{y}" width="{R_TOP}" height="1" fill="{fill}"/>'
             f'<rect x="{x+R_TOP}" y="{y}" width="{PAD}" height="1" fill="url(#{gid}_r)"/></g>')
    # bottom-left corner (S x B): window corner at (PAD, R_BOTTOM), arc centre at (PAD+R_BOTTOM, 0)
    x, y = cx0, cy2
    radial(f"{gid}_bl", x + PAD + R_BOTTOM, y, PAD + R_BOTTOM, R_BOTTOM / (PAD + R_BOTTOM))
    e.append(f'<g id="{prefix}-bottomleft"><rect x="{x}" y="{y}" width="{S}" height="{B}" fill="url(#{gid}_bl)"/>'
             f'<path d="M{x+PAD} {y} L{x+S} {y} L{x+S} {y+R_BOTTOM} L{x+PAD+R_BOTTOM} {y+R_BOTTOM} '
             f'A{R_BOTTOM} {R_BOTTOM} 0 0 1 {x+PAD} {y}Z" fill="{fill}"/></g>')
    # bottom edge (1 x B)
    x, y = cx1, cy2
    linear(f"{gid}_b", x, y + R_BOTTOM, x, y + B)
    e.append(f'<g id="{prefix}-bottom"><rect x="{x}" y="{y}" width="1" height="{R_BOTTOM}" fill="{fill}"/>'
             f'<rect x="{x}" y="{y+R_BOTTOM}" width="1" height="{PAD}" fill="url(#{gid}_b)"/></g>')
    # bottom-right corner
    x, y = cx2, cy2
    radial(f"{gid}_br", x + R_TOP - R_BOTTOM, y, PAD + R_BOTTOM, R_BOTTOM / (PAD + R_BOTTOM))
    e.append(f'<g id="{prefix}-bottomright"><rect x="{x}" y="{y}" width="{S}" height="{B}" fill="url(#{gid}_br)"/>'
             f'<path d="M{x} {y} L{x+R_TOP} {y} A{R_BOTTOM} {R_BOTTOM} 0 0 1 {x+R_TOP-R_BOTTOM} {y+R_BOTTOM} '
             f'L{x} {y+R_BOTTOM}Z" fill="{fill}"/></g>')
    width = cx2 + S - x0
    height = cy2 + B - y0
    return "\n  ".join(e), g, width, height


def decoration_svg(t):
    a, ga, w, h = frame("decoration", t["title"], t["shadow"], 0, 0)
    b, gb, _, _ = frame("decoration-inactive", t["title_inactive"], t["shadow_inactive"], w + 10, 0)
    # Maximized windows: no shadow or rounded corners, only the centre is used.
    c = (f'<rect id="decoration-maximized-center" x="{2*w+20}" y="0" width="1" height="1" fill="{t["title"]}"/>\n  '
         f'<rect id="decoration-maximized-inactive-center" x="{2*w+24}" y="0" width="1" height="1" fill="{t["title_inactive"]}"/>')
    defs = "\n    ".join(ga + gb)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{2*w+30}" height="{h}" viewBox="0 0 {2*w+30} {h}">\n'
            f'  <defs>\n    {defs}\n  </defs>\n  {a}\n  {b}\n  {c}\n</svg>\n')


# ---------------------------------------------------------------- buttons

def rounded_flat_hex(cx, cy, r, rc):
    """Flat-top hexagon (as in the design preview's window buttons) with rounded corners."""
    vs = [(cx + r * math.cos(math.radians(60 * k)), cy + r * math.sin(math.radians(60 * k))) for k in range(6)]
    t = rc / math.tan(math.radians(60))
    pts = []
    for k in range(6):
        v, p, n = vs[k], vs[k - 1], vs[(k + 1) % 6]

        def towards(a, b):
            d = math.hypot(b[0] - a[0], b[1] - a[1])
            return (a[0] + (b[0] - a[0]) * t / d, a[1] + (b[1] - a[1]) * t / d)
        pts.append((towards(v, p), towards(v, n)))
    d = f"M{f(pts[0][1][0])} {f(pts[0][1][1])}"
    for k in list(range(1, 6)) + [0]:
        a, b = pts[k]
        d += f"L{f(a[0])} {f(a[1])}A{f(rc)} {f(rc)} 0 0 1 {f(b[0])} {f(b[1])}"
    return d + "Z"


def hex_outline(cx, cy, r):
    vs = [(cx + r * math.cos(math.radians(60 * k)), cy + r * math.sin(math.radians(60 * k))) for k in range(6)]
    return "M" + "L".join(f"{f(x)} {f(y)}" for x, y in vs) + "Z"


C = BTN / 2
HEX = rounded_flat_hex(C, C, 10.6, 2.2)
GLYPHS = {
    "minimize": lambda col, bg: f'<path d="M8.4 12H15.6" stroke="{col}" stroke-width="1.9" stroke-linecap="round" fill="none"/>',
    "maximize": lambda col, bg: f'<path d="{hex_outline(C, C, 4.4)}" stroke="{col}" stroke-width="1.7" stroke-linejoin="round" fill="none"/>',
    "restore": lambda col, bg: (
        f'<path d="{hex_outline(C + 1.6, C - 1.4, 3.4)}" stroke="{col}" stroke-width="1.5" stroke-linejoin="round" fill="none"/>'
        f'<path d="{hex_outline(C - 1.6, C + 1.4, 3.4)}" stroke="{col}" stroke-width="1.5" stroke-linejoin="round" fill="{bg}"/>'),
    "close": lambda col, bg: f'<path d="M9.2 9.2 14.8 14.8M14.8 9.2 9.2 14.8" stroke="{col}" stroke-width="2" stroke-linecap="round" fill="none"/>',
}
# state element -> palette key
STATES = [
    ("active-center", "normal"), ("hover-center", "hover"), ("pressed-center", "pressed"),
    ("deactivated-center", "deactivated"), ("inactive-center", "inactive"),
    ("hover-inactive-center", "hover"), ("pressed-inactive-center", "pressed"),
    ("deactivated-inactive-center", "deactivated"),
]


def button_svg(kind, t):
    palette = t["close"] if kind == "close" else t["btn"]
    groups = []
    for i, (state, key) in enumerate(STATES):
        bg, fg = palette[key]
        dx = i * (BTN + 4)
        groups.append(
            f'<g id="{state}" transform="translate({dx} 0)">'
            f'<rect width="{BTN}" height="{BTN}" opacity="0"/>'
            f'<path d="{HEX}" fill="{bg}"/>{GLYPHS[kind](fg, bg)}</g>')
    width = len(STATES) * (BTN + 4)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{BTN}" viewBox="0 0 {width} {BTN}">\n  '
            + "\n  ".join(groups) + "\n</svg>\n")


def rc(t):
    return f"""[General]
ActiveTextColor={t["text"]}
InactiveTextColor={t["text_inactive"]}
TitleAlignment=Left
TitleVerticalAlignment=Center

[Layout]
BorderLeft=4
BorderRight=4
BorderBottom=4
BorderTop=0
TitleHeight={BTN}
TitleEdgeTop=5
TitleEdgeBottom=5
TitleEdgeLeft=10
TitleEdgeRight=8
TitleEdgeTopMaximized=5
TitleEdgeBottomMaximized=5
TitleEdgeLeftMaximized=10
TitleEdgeRightMaximized=8
TitleBorderLeft=6
TitleBorderRight=8
ButtonWidth={BTN}
ButtonHeight={BTN}
ButtonSpacing=6
ButtonMarginTop=0
ButtonMarginTopMaximized=0
ExplicitButtonSpacer=10
PaddingLeft={PAD}
PaddingRight={PAD}
PaddingTop={PAD}
PaddingBottom={PAD}
"""


for name, t in THEMES.items():
    d = os.path.join(OUT, name)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "metadata.desktop"), "w") as fh:
        fh.write(f"[Desktop Entry]\nName={'Cairn' if name == 'Cairn' else 'Cairn Light'}\n"
                 f"Comment={t['comment']}\nX-KDE-PluginInfo-Name={name}\n")
    with open(os.path.join(d, f"{name}rc"), "w") as fh:
        fh.write(rc(t))
    with open(os.path.join(d, "decoration.svg"), "w") as fh:
        fh.write(decoration_svg(t))
    for kind in GLYPHS:
        with open(os.path.join(d, f"{kind}.svg"), "w") as fh:
            fh.write(button_svg(kind, t))
    print("wrote", d, sorted(os.listdir(d)))
