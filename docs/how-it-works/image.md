# How Cairn is built

**In one sentence:** Cairn is Fedora Kinoite with a recipe of changes on top, packaged
as a single image, the same kind of image Docker uses.

## The idea

Most Linux systems update package by package: hundreds of small changes on your
disk, and if one goes wrong mid-way you can end up with a half-updated system.

Cairn updates **as one piece**. GitHub builds a complete, finished system image.
Your computer downloads it, keeps it next to the one you're running, and switches
at the next restart. The old one stays, so you can always go back.

This is called an *image-based* or *atomic* system. Fedora calls its version
**Fedora Atomic**; the KDE edition is **Kinoite**.

## The files

| File | What it does |
|---|---|
| `Containerfile` | The recipe. Starts from Fedora's Kinoite image and runs `build.sh` on it. |
| `build_files/build.sh` | The changes, in order: add software sources, codecs, apps, Cairn's look, settings, and the Cairn name. |
| `brand/` | Logo, wallpaper, colour schemes and global theme (see [brand.md](../brand.md)). |
| `system_files/` | Files copied as-is into the system, e.g. services and default settings. Their path inside the folder is their path on the installed system. |

## What `build.sh` does

1. **Adds software sources:** RPM Fusion (for codecs) and Microsoft's VS Code repository.
2. **Codecs:** swaps Fedora's limited FFmpeg for the full one, adds the GStreamer codec plugins.
3. **Apps:** Okular, Gwenview, Kate, Git, VS Code and Distrobox.
   Firefox, Dolphin, Konsole, Spectacle, Ark, Podman, Discover and the guest tools for
   VirtualBox, VMware and QEMU/KVM are already in Kinoite.
   **First start:** switches off KDE's first-start wizard (the installer already asked for language
   and account) and removes Fedora's page from the Welcome Center.
4. **Look:** installs the logo, wallpaper, colour schemes and the Cairn global theme.
5. **System files:** copies everything in `system_files/`.
6. **Name:** edits `/usr/lib/os-release` so the system calls itself Cairn.
7. **Services:** turns on automatic updates and the first-start app install.
8. **Tidy up:** switches the extra software sources off again. You don't need them on the
   installed system, because updates come as whole images.

## Why `ID` stays `fedora`

`/usr/lib/os-release` has a technical `ID` field. Cairn sets the visible fields
(`NAME`, `PRETTY_NAME`, `VARIANT`, `LOGO`) to Cairn but keeps `ID=fedora`.
The installer builder and some Fedora tools look Fedora-specific things up by `ID`,
and they break with an unknown one.

## Build it yourself

You don't need to, because GitHub builds it. But on any Linux machine with Podman:

```sh
podman build -t cairn .
```

It takes 10–20 minutes and about 20 GB of disk space.
