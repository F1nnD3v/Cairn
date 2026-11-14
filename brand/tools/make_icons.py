"""Write Cairn's icon themes: monochrome line icons for the apps pinned on the panel,
drawn like the design preview, on top of KDE's Breeze icons.

    python3 brand/tools/make_icons.py brand/icons

Writes brand/icons/Cairn (dark, inherits breeze-dark) and brand/icons/Cairn-Light
(light, inherits breeze). The icons use KDE's colour-scheme stylesheet
(class="ColorScheme-Text"), so Plasma draws them in the current text colour; the
colour written in the file is only the fallback for non-KDE apps.
"""
import os
import sys

OUT = sys.argv[1] if len(sys.argv) > 1 else "brand/icons"

# icon name (as the apps' .desktop files use it) -> line drawing on a 24x24 grid
GLYPHS = {
    # Firefox: a globe
    "firefox": '<circle cx="12" cy="12" r="8.5"/>'
               '<path d="M3.5 12h17M12 3.5c2.6 2.4 3.9 5.2 3.9 8.5s-1.3 6.1-3.9 8.5c-2.6-2.4-3.9-5.2-3.9-8.5S9.4 5.9 12 3.5z"/>',
    # Dolphin (files): a folder
    "org.kde.dolphin": '<path d="M3.5 7.5a2 2 0 0 1 2-2h4l2 2.2h7a2 2 0 0 1 2 2V17a2 2 0 0 1-2 2h-13a2 2 0 0 1-2-2z"/>',
    # Konsole (terminal): a window with a prompt
    "utilities-terminal": '<rect x="3.5" y="4.5" width="17" height="15" rx="2.5"/>'
                          '<path d="M7.5 9.5l3 2.5-3 2.5M12.5 15h4"/>',
    # VS Code: </>
    "vscode": '<path d="M9 7l-5 5 5 5M15 7l5 5-5 5"/>',
    # Steam: a gamepad
    "com.valvesoftware.Steam": '<path d="M7 8.5h10a4 4 0 0 1 4 4v.5a3.5 3.5 0 0 1-6.3 2.1L14 14h-4l-.7 1.1A3.5 3.5 0 0 1 3 13v-.5a4 4 0 0 1 4-4z"/>'
                               '<path d="M7.5 10.5v3M6 12h3M16 11.2h.01M18 12.8h.01" stroke-width="1.9"/>',
}

THEMES = {
    "Cairn": dict(inherits="breeze-dark,breeze,hicolor", colour="#ECEDEF",
                  comment="Cairn's line icons for the panel apps, on top of Breeze Dark"),
    "Cairn-Light": dict(inherits="breeze,hicolor", colour="#18191C",
                        comment="Cairn's line icons for the panel apps, on top of Breeze"),
}

INDEX = """[Icon Theme]
Name={name}
Comment={comment}
Inherits={inherits}
FollowsColorScheme=true
Directories=scalable/apps

[scalable/apps]
Size=32
MinSize=16
MaxSize=512
Type=Scalable
Context=Applications
"""

for name, t in THEMES.items():
    apps = os.path.join(OUT, name, "scalable", "apps")
    os.makedirs(apps, exist_ok=True)
    with open(os.path.join(OUT, name, "index.theme"), "w") as fh:
        fh.write(INDEX.format(name=name.replace("-", " "), **t))
    for icon, body in GLYPHS.items():
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">\n'
            f'  <style type="text/css" id="current-color-scheme">.ColorScheme-Text {{ color:{t["colour"]}; }}</style>\n'
            '  <g class="ColorScheme-Text" fill="none" stroke="currentColor" stroke-width="1.6" '
            'stroke-linecap="round" stroke-linejoin="round">\n'
            f'    {body}\n'
            '  </g>\n</svg>\n'
        )
        with open(os.path.join(apps, f"{icon}.svg"), "w") as fh:
            fh.write(svg)
    print("wrote", os.path.join(OUT, name), sorted(os.listdir(apps)))
