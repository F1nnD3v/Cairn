# How updates work

You never have to do anything. Updates come from two places, and both are automatic.

## The system (once a day)

1. GitHub builds a fresh Cairn image every day at 04:23 UTC, and every time a change is merged.
   It's published to `ghcr.io/<owner>/cairn:latest`.
2. On your computer, `rpm-ostreed-automatic.timer` checks for a new image about once a day.
3. If there is one, it downloads it **in the background** and prepares it next to the running system.
   This is the `AutomaticUpdatePolicy=stage` setting in `/etc/rpm-ostreed.conf`.
4. The next time you restart, you're on the new version. **Nothing restarts the computer by itself.**

Discover may also tell you an update is ready and offer to restart. That's the same update.

## Apps from Flathub (once a day)

`cairn-flatpak-update.timer` runs `flatpak update` daily.

## Going back

Every update keeps the previous version.

- **At startup:** the boot menu lists both. Pick the older one.
- **From a terminal:** `rpm-ostree rollback`, then restart.

## Checking what you're running

```sh
rpm-ostree status
```

This shows the version you're on, any update waiting for the next restart, and the previous version.

## New Fedora releases

Cairn's version number is the Fedora version it's built on (Cairn 45 = Fedora 45).
When a new Fedora comes out, the `FEDORA_VERSION` value in `.github/workflows/build.yml`
and `Containerfile` is raised, and the next daily update moves every machine to it.
The old version stays in the boot menu, as always.

## Why the image must be public

Computers download updates from GitHub's container registry without logging in.
So the `cairn` package on GitHub must be **public**. If updates fail with
"unauthorized" or "denied", check the package's visibility.
