"""Generate Cairn's honeycomb logo and wordmark SVGs.

Usage: python3 make_logo.py <Outfit variable TTF> <output dir>
"""
import math, sys, os, io
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
import uharfbuzz as hb

FONT, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)

PALETTES = {
    # for dark backgrounds (the default look)
    "dark":  {"a": "#5E646D", "b": "#9AA0A8", "h": "#F4A62A", "text": "#ECEDEF"},
    # for light backgrounds
    "light": {"a": "#4A4F57", "b": "#80868F", "h": "#D08200", "text": "#18191C"},
}

R, RC = 17.2, 3.0                      # cell circumradius, corner radius
SX = 32.08                             # centre spacing (equal on all six neighbours)
SY = SX * math.sqrt(3) / 2
CELLS = [  # (x, y, colour key): bottom row of 3, middle 2, honey on top
    (60 - SX, 60 + SY, "a"), (60, 60 + SY, "a"), (60 + SX, 60 + SY, "a"),
    (60 - SX / 2, 60, "b"), (60 + SX / 2, 60, "b"),
    (60, 60 - SY, "h"),
]


def f(v):
    return f"{v:.2f}".rstrip("0").rstrip(".")


def rounded_hex(cx, cy, r=R, rc=RC):
    """Pointy-top hexagon with arc-rounded corners, as SVG path data."""
    vs = [(cx + r * math.cos(math.radians(-90 + 60 * k)), cy + r * math.sin(math.radians(-90 + 60 * k))) for k in range(6)]
    t = rc / math.tan(math.radians(60))  # tangent length for a 120 degree corner
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


def mark_paths(pal, dx=0.0, dy=0.0, s=1.0):
    out = []
    for x, y, key in CELLS:
        out.append(f'<path fill="{pal[key]}" d="{rounded_hex(dx + x * s, dy + y * s, R * s, RC * s)}"/>')
    return "\n  ".join(out)


def write(name, body, vb, w=None, h=None):
    size = f' width="{w}" height="{h}"' if w else ""
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}"{size}>\n  {body}\n</svg>\n'
    with open(os.path.join(OUT, name), "w") as fh:
        fh.write(svg)


# --- logo mark (content spans x 13..107, y 15..105) ---
for key, pal in PALETTES.items():
    name = "cairn-logo.svg" if key == "dark" else "cairn-logo-light.svg"
    write(name, f"<title>Cairn</title>\n  " + mark_paths(pal), "10 10 100 100", 256, 256)

# --- wordmark: logo + "cairn" set in Outfit SemiBold, outlined to paths ---
tt = TTFont(FONT)
inst = instancer.instantiateVariableFont(tt, {"wght": 600})
buf = io.BytesIO(); inst.save(buf); data = buf.getvalue()
font600 = TTFont(io.BytesIO(data))
upem = font600["head"].unitsPerEm
xh = font600["OS/2"].sxHeight
gs = font600.getGlyphSet()

hbface = hb.Face(data); hbfont = hb.Font(hbface)
hbbuf = hb.Buffer(); hbbuf.add_str("cairn"); hbbuf.guess_segment_properties()
hb.shape(hbfont, hbbuf, {"kern": True, "liga": True})

LOGO = 100.0                     # logo box height (viewBox 10..110)
SIZE = LOGO * 0.91               # font size, matching the design preview proportions
GAP = LOGO * 0.27
scale = SIZE / upem
track = -0.015 * SIZE            # slight negative tracking, as in the preview
x0 = 10 + LOGO + GAP
cy = 60.0
baseline = cy + (xh * scale) / 2

glyph_paths = []
pen_x = 0.0
order = font600.getGlyphOrder()
for info, pos in zip(hbbuf.glyph_infos, hbbuf.glyph_positions):
    gname = order[info.codepoint]
    sp = SVGPathPen(gs)
    tp = TransformPen(sp, (scale, 0, 0, -scale, x0 + (pen_x + pos.x_offset) * scale, baseline))
    gs[gname].draw(tp)
    glyph_paths.append(sp.getCommands())
    pen_x += pos.x_advance + track / scale
text_right = x0 + pen_x * scale - track
W = text_right + 10
for key, pal in PALETTES.items():
    name = "cairn-wordmark.svg" if key == "dark" else "cairn-wordmark-light.svg"
    text = f'<path fill="{pal["text"]}" d="{" ".join(glyph_paths)}"/>'
    write(name, "<title>Cairn</title>\n  " + mark_paths(pal) + "\n  " + text, f"0 0 {f(W)} 120", round(W * 2), 240)

print("wordmark width", round(W, 1), "x-height", xh, "upem", upem)
