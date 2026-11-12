# How GitHub builds Cairn

Cairn is built by GitHub Actions, GitHub's free build machines. There are two workflows,
both in `.github/workflows/`.

## Build Cairn (`build.yml`)

| When | What happens |
|---|---|
| A pull request is opened or updated | Builds the image as a **test**. Nothing is published. A red ✗ on the pull request means the change broke the build. |
| A pull request is merged into `main` | Builds and **publishes** the image. |
| Every day at 04:23 UTC | Builds and publishes, so Fedora's security fixes reach you within a day. |
| By hand (Actions → Build Cairn → Run workflow) | Builds and publishes. |

The steps:

1. **Free disk space** on the build machine (a desktop image is big).
2. **Build** the `Containerfile` with Podman.
3. **Split into layers:** repacks the image into many small layers, so your computer only
   downloads the parts that changed.
4. **Publish** to `ghcr.io/<owner>/cairn` with three tags: `latest`, `45` and `45.<date>`.

## Build Cairn ISO (`build-iso.yml`)

Run it by hand when you need an installer: **Actions → Build Cairn ISO → Run workflow**.
It takes the latest published image and turns it into an installer ISO with
[bootc-image-builder](https://github.com/osbuild/bootc-image-builder), using the settings in
`disk_config/iso.toml`. Then it adds `images/product.img` to the ISO: Cairn's installer
stylesheet and sidebar artwork from `brand/installer/`, which the installer applies when it starts. The ISO is attached to the run as **cairn-iso** for 14 days.

You only need a new ISO for new installs. Installed systems update themselves.
