"""Write Cairn's KDE colour schemes (CairnDark.colors, CairnLight.colors).

    python3 brand/tools/make_color_schemes.py brand/plasma/color-schemes

The values come from the palette in docs/brand.md. KDE colour schemes use
"r,g,b" triplets grouped by role (Window, View, Button, Selection, ...).
"""
import os
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "brand/plasma/color-schemes"


def rgb(h):
    h = h.lstrip("#")
    return ",".join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))


# Foreground sets shared by most groups, per mode.
DARK_FG = dict(normal="#ECEDEF", inactive="#A3A7AF", active="#F4A62A", link="#F4A62A",
               visited="#D6AA6E", negative="#F0626A", neutral="#F2C14E", positive="#57C76E")
LIGHT_FG = dict(normal="#18191C", inactive="#5C6068", active="#A35F00", link="#A35F00",
                visited="#7A5220", negative="#C42832", neutral="#A85A00", positive="#1E823C")
# Text on a honey selection is always dark.
ON_HONEY = dict(normal="#18191C", inactive="#3D3420", active="#18191C", link="#18191C",
                visited="#3D2A0A", negative="#7A1016", neutral="#4A3000", positive="#0A4F1E")

SCHEMES = {
    "CairnDark": {
        "name": "Cairn Dark",
        "accent": "#F4A62A",
        "groups": {
            "Window": ("#1B1D21", "#202227", DARK_FG),
            "View": ("#16171B", "#1B1D21", DARK_FG),
            "Button": ("#24272C", "#33363D", DARK_FG),
            "Header": ("#24272C", "#1B1D21", DARK_FG),
            "Header][Inactive": ("#1B1D21", "#24272C", DARK_FG),
            "Tooltip": ("#24272C", "#1B1D21", DARK_FG),
            "Complementary": ("#121316", "#1B1D21", DARK_FG),
            "Selection": ("#F4A62A", "#D99020", ON_HONEY),
        },
        "wm": dict(activeBackground="#24272C", activeForeground="#ECEDEF", activeBlend="#ECEDEF",
                   inactiveBackground="#1B1D21", inactiveForeground="#A3A7AF", inactiveBlend="#A3A7AF"),
        "disabled": "#383A40",
    },
    "CairnLight": {
        "name": "Cairn Light",
        "accent": "#D08200",
        "groups": {
            "Window": ("#F4F4F5", "#ECEDEF", LIGHT_FG),
            "View": ("#FFFFFF", "#F7F7F8", LIGHT_FG),
            "Button": ("#FBFBFC", "#E9EAEC", LIGHT_FG),
            "Header": ("#E9EAEC", "#F4F4F5", LIGHT_FG),
            "Header][Inactive": ("#F4F4F5", "#E9EAEC", LIGHT_FG),
            "Tooltip": ("#FFFFFF", "#F4F4F5", LIGHT_FG),
            # Complementary areas (e.g. the lock screen) stay dark in light mode too.
            "Complementary": ("#1B1D21", "#24272C", DARK_FG),
            "Selection": ("#D08200", "#B87300", ON_HONEY),
        },
        "wm": dict(activeBackground="#E9EAEC", activeForeground="#18191C", activeBlend="#18191C",
                   inactiveBackground="#F4F4F5", inactiveForeground="#5C6068", inactiveBlend="#5C6068"),
        "disabled": "#C8CACE",
    },
}


def scheme_text(sid, s):
    lines = [
        "[ColorEffects:Disabled]",
        f"Color={rgb(s['disabled'])}", "ColorAmount=0", "ColorEffect=0",
        "ContrastAmount=0.65", "ContrastEffect=1", "IntensityAmount=0.1", "IntensityEffect=2", "",
        "[ColorEffects:Inactive]",
        "ChangeSelectionColor=true", f"Color={rgb(s['disabled'])}", "ColorAmount=0.025", "ColorEffect=2",
        "ContrastAmount=0.1", "ContrastEffect=2", "Enable=false", "IntensityAmount=0", "IntensityEffect=0", "",
    ]
    for group, (bg, alt, fg) in s["groups"].items():
        lines += [
            f"[Colors:{group}]",
            f"BackgroundAlternate={rgb(alt)}",
            f"BackgroundNormal={rgb(bg)}",
            f"DecorationFocus={rgb(s['accent'])}",
            f"DecorationHover={rgb(s['accent'])}",
            f"ForegroundActive={rgb(fg['active'])}",
            f"ForegroundInactive={rgb(fg['inactive'])}",
            f"ForegroundLink={rgb(fg['link'])}",
            f"ForegroundNegative={rgb(fg['negative'])}",
            f"ForegroundNeutral={rgb(fg['neutral'])}",
            f"ForegroundNormal={rgb(fg['normal'])}",
            f"ForegroundPositive={rgb(fg['positive'])}",
            f"ForegroundVisited={rgb(fg['visited'])}",
            "",
        ]
    lines += ["[General]", f"ColorScheme={sid}", f"Name={s['name']}", "shadeSortColumn=true", "",
              "[KDE]", "contrast=4", "", "[WM]"]
    lines += [f"{k}={rgb(v)}" for k, v in sorted(s["wm"].items())]
    return "\n".join(lines) + "\n"


os.makedirs(OUT, exist_ok=True)
for sid, s in SCHEMES.items():
    path = os.path.join(OUT, f"{sid}.colors")
    with open(path, "w") as fh:
        fh.write(scheme_text(sid, s))
    print(path)
