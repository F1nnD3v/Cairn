# Cairn — the plan

This is the plan we agreed on before writing any code. It records **what** Cairn is
and **why** each choice was made, so future changes can be checked against it.

## What Cairn is

Cairn is a desktop Linux distribution you can use every day and show off.
A cairn is a pile of stones hikers stack, one at a time, to mark a trail;
Cairn is built the same way: layer on layer, each resting on the one below.

- **For whom:** built for its author first; a public release comes later.
- **Who builds it:** all code is written by Claude; the author tests it and decides what goes in.
- **Later:** a server edition, *Cairn Server*, planned in its own round once the desktop is done.

## Decisions

| Area | Decision | Why |
|---|---|---|
| Kind of OS | A distribution built **on top of an existing one** (not from source) | Security updates come from upstream; one person can't patch thousands of packages forever |
| Base | **Fedora Kinoite** (Fedora Atomic + KDE Plasma), official Fedora image | Image-based updates with rollback; depends only on Fedora, which isn't going away |
| How it's defined | One `Containerfile` (the same format Docker uses) | Readable, and what you learn transfers to other projects |
| Desktop | **KDE Plasma** | The most themeable desktop, with official theming hooks that survive updates |
| Signature features | **Its own look** + **updates that can't break it** | The look makes it worth showing; safe updates make it practical daily |
| Style | **Clean, with hexagons** | Chosen by the author |
| Colours | Neutral greys + **amber/honey accent**; **dark mode by default**, light mode available | Amber nods to honeycomb hexagons and almost no distro uses it |
| Hexagons appear on | Logo, wallpapers, boot animation, login & lock screens, app-launcher button, **hexagonal window buttons** | Strong identity without redrawing hundreds of app icons |
| Logo | **Honeycomb**: six equal hexagons stacked 3-2-1, grey stones under one honey cell (picked in Step 0) | Ties the name and the shape together; also fits the honeycomb wallpaper |
| Wordmark | **"cairn"** in lowercase, set in **Outfit** SemiBold (picked in Step 0) | Round, geometric, very even |
| Palette | Graphite greys + honey; exact values in [brand.md](brand.md) (confirmed in Step 0) | |
| Apps | Firefox · VS Code · Git · Podman + Distrobox (per-project coding containers) · Steam · KDE Discover with Flathub · full media codecs · KDE basics (Dolphin, Konsole, Okular, Gwenview, Spectacle, Ark, Kate) | Matches daily use: browsing, coding, some gaming |
| Updates | GitHub builds a new image **daily** and on every merged change; machines download in the background and switch on next restart; previous version stays selectable at boot; Flatpak apps auto-update; follows each new Fedora release | Safe, hands-off updates with a way back |
| Version numbers | Follow Fedora's: built on Fedora 45 → **Cairn 45**. `v0.x` names are internal milestones only | Simple and honest about what's underneath |
| Technical ID | `os-release` keeps `ID=fedora`; the visible name, logo and variant say Cairn | The installer builder and Fedora tools look things up by `ID` and break on unknown ones |
| Testing | Installer **ISO** in **VirtualBox** or **VMware Workstation** on a Windows (x86) PC; guest tools for both come with Kinoite | Tests the same install path a real PC will use |
| Repository | Renamed to `cairn` and made **public** | Unlimited free build minutes; machines can pull updates without a login token |
| Workflow | `main` created once; after that every change arrives as a **pull request** the author merges; merging triggers the official build; PRs get a test build | Nothing reaches a machine without the author's click |
| Signing | **Postponed to v0.3** (before anyone else installs) | Unsigned is acceptable while testing in a VM; switching an installed machine to signed updates later takes one command |
| Docs | A short plain-language note in `docs/` for every part | The author wants to learn as we go |
| Installer | Fedora's installer, **rebranded** in Cairn's look (decided after the first install); a fully custom installer stays an idea for later | Same reliable install steps, low risk; a custom installer has to be very reliable because it erases disks |

## Roadmap

### Step 0 — Design preview ✅
A page with the colour palette (dark + light), 4 logo versions and a hexagon wallpaper sample.
Picked: logo D (Honeycomb), wordmark font Outfit, colours as shown. See [brand.md](brand.md).

### v0.1 — "It's Cairn"
- Fedora Kinoite + the agreed apps, media codecs, VirtualBox support
- Daily automatic builds on GitHub, automatic background updates
- Installer ISO
- The Cairn name in the boot menu, the About screen and `os-release`
- Logo, wallpaper, amber accent, dark mode by default
- Docs: what each part does, plus a step-by-step VirtualBox install guide

### v0.2 — "It looks like Cairn"
- Hexagonal window buttons
- Login screen, lock screen, boot animation, startup splash
- Panel as in the design preview: floating, centred, fits its contents, Cairn logo as the launcher button
- Polished light mode
- Installer in Cairn's look: graphite sidebar with the honeycomb and wordmark, honey accents (same steps as Fedora's installer)

### v0.3 — "Ready for others"
- Signed builds (and the one-command switch for already-installed machines)
- Welcome app on first start
- GitHub page with screenshots, release notes
- Optional test on a real PC
- Hardware video decoding for real PCs (RPM Fusion's `mesa-va-drivers-freeworld`). Left out of v0.1:
  it isn't needed in a VM, and it must match Fedora's Mesa version exactly, so it often breaks daily builds for a day or two

### Then — Cairn Server
Planned in its own question round: what it runs, how it is managed.

## Still open

- **Licence** for the repository — to decide before the public release.
- **UI font** — to decide with the v0.2 theme.
