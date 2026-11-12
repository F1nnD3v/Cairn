# Install Cairn in VirtualBox

This guide installs Cairn in a VirtualBox virtual machine on a Windows PC.
Your Windows system is not touched. It takes about 30 minutes, most of it waiting.

## What you need

- VirtualBox 7 or newer, from [virtualbox.org](https://www.virtualbox.org/wiki/Downloads) ("Windows hosts").
- About 50 GB of free disk space and at least 8 GB of RAM in your PC.
- The Cairn installer ISO (next section).

## 1. Download the installer ISO

The ISO is built by GitHub, on request, from the latest Cairn image.

1. Open the repository on GitHub and go to **Actions → Build Cairn ISO**.
2. If there is no recent successful run, click **Run workflow → Run workflow** and wait for it to finish (about 30 minutes).
3. Open the newest successful run and download **cairn-iso** under **Artifacts**.
4. Unzip it. Inside is `install.iso` (a few GB).

## 2. Create the virtual machine

In VirtualBox, click **New** and fill in:

| Setting | Value |
|---|---|
| Name | `Cairn` |
| ISO Image | the `install.iso` you downloaded |
| Type / Version | Linux / Fedora (64-bit) |
| Skip Unattended Installation | **ticked** (the Cairn installer asks its own questions) |
| Base Memory | 8192 MB (4096 MB is the minimum) |
| Processors | 4 (2 is the minimum) |
| Enable EFI | **ticked** (Cairn only boots in EFI mode) |
| Hard Disk | Create a virtual hard disk now, **64 GB** |

Click **Finish**. Then open the VM's **Settings → Display**:

- Graphics Controller: **VMSVGA**
- Video Memory: **128 MB**
- Enable 3D Acceleration: leave it **off** at first. It is faster when it works, but VirtualBox's 3D support is sometimes glitchy with KDE Plasma. Try turning it on later if the desktop feels slow.

## 3. Install

1. Select the VM and click **Start**. Choose **Install Cairn** in the boot menu if it asks.
2. The Fedora installer (called Anaconda) starts. Pick your language.
3. **Installation Destination**: select the 64 GB virtual disk and keep "Automatic". This only uses the virtual disk, never your real one.
4. **User Creation**: create your account, and tick **Make this user administrator**.
5. Click **Begin Installation** and wait until it finishes.
6. Click **Reboot System**. If the installer starts again, close the VM, open **Settings → Storage**, remove `install.iso` from the optical drive, and start the VM again.

## 4. First start

- Log in with the account you created. You should see the Cairn wallpaper and the dark graphite-and-honey look.
- Open the app launcher, search for **About this System**, and check that it says **Cairn**.
- **Give it a few minutes online.** In the background Cairn installs Steam from Flathub. It appears in the launcher when it's done.

## 5. Updates

You don't have to do anything.

- Every day Cairn checks for a new version, downloads it in the background, and switches to it the next time you restart.
- Apps from Flathub update themselves daily.
- To see what's installed and what's waiting for the next restart, open a terminal (Konsole) and run `rpm-ostree status`.

### If an update breaks something

The previous version is always kept.

- **At startup:** in the boot menu, pick the second entry (the older version).
- **From a terminal:** run `rpm-ostree rollback`, then restart.

Then tell me what broke.

## What to report

When something doesn't work, send:

1. What you did and what happened instead.
2. A screenshot or phone photo.
3. If you can open a terminal, the output of `rpm-ostree status`.
