# Where Cairn's apps come from

Apps reach Cairn in three ways.

## 1. Built into the system image

These are part of Cairn itself and update with it:

- **Web:** Firefox
- **Files and everyday tools:** Dolphin (files), Konsole (terminal), Okular (PDFs),
  Gwenview (images), Spectacle (screenshots), Ark (archives), Kate (text editor)
- **Coding:** VS Code, Git, Podman, Distrobox
- **Software store:** Discover
- **Media:** full codecs, so every common video and music format plays

## 2. Installed from Flathub on first start

Some apps are better as Flatpaks: they come straight from the app's makers and run in a sandbox.
On first start, with internet, Cairn installs:

- **Steam**

The list is `system_files/usr/share/cairn/flatpaks.list`. The script that installs it is
`system_files/usr/libexec/cairn/cairn-flatpak-setup`, run by `cairn-flatpak-setup.timer`
every 30 minutes until it succeeds (so it also works if you were offline at first).
When the list changes in a future update, the new apps are installed automatically.

## 3. Whatever you install yourself

Open **Discover** and install anything from Flathub. It stays installed across system updates.

## Coding containers (Distrobox)

To keep the system clean, programming languages and their tools go into containers:

```sh
distrobox create --name dev --image fedora:45   # once
distrobox enter dev                              # every time
sudo dnf install python3 nodejs golang           # inside: install whatever you need
```

Inside the container you have your normal home folder, so VS Code and your files work as usual.
If you break a container, delete it (`distrobox rm dev`) and make a new one. The system is never affected.
