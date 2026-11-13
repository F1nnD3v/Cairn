#!/usr/bin/bash
# Turns Fedora Kinoite into Cairn. Runs once, inside the image build (see Containerfile).
# /ctx holds this repository's build_files/, brand/ and system_files/, read-only.
set -euxo pipefail

FEDORA_VERSION="$(rpm -E %fedora)"
CAIRN_VERSION="${CAIRN_VERSION:-${FEDORA_VERSION}}"

### 1. Extra software sources ##################################################

# RPM Fusion (free): full media codecs that Fedora can't ship.
dnf5 install -y \
    "https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-${FEDORA_VERSION}.noarch.rpm"

# Microsoft's repository for VS Code.
rpm --import https://packages.microsoft.com/keys/microsoft.asc
cat > /etc/yum.repos.d/vscode.repo <<'EOF'
[code]
name=Visual Studio Code
baseurl=https://packages.microsoft.com/yumrepos/vscode
enabled=1
gpgcheck=1
gpgkey=https://packages.microsoft.com/keys/microsoft.asc
EOF

### 2. Media codecs ############################################################

# Replace Fedora's codec-limited FFmpeg libraries with the full ones.
# (RPM Fusion's ffmpeg-libs conflicts with the *-free libraries, so --allowerasing swaps them.)
dnf5 install -y --allowerasing ffmpeg ffmpeg-libs libavdevice
dnf5 install -y \
    gstreamer1-plugins-bad-freeworld \
    gstreamer1-plugins-ugly

### 3. Apps and tools ##########################################################

# Kinoite already has Firefox, Dolphin, Konsole, Spectacle, Ark, Podman, Discover and the
# guest tools for VirtualBox, VMware and QEMU/KVM.
# Added here: the KDE apps it leaves out, full Git, VS Code and Distrobox.
dnf5 install -y \
    okular \
    gwenview \
    kate \
    git \
    code \
    distrobox

### 3b. First start ############################################################

# The installer already asks for language and account, so KDE's first-start wizard
# (plasma-setup) is skipped: it only runs while /etc/plasma-setup-done is missing, and
# system_files/ ships that file. Its dark/light switch would also replace Cairn's theme
# with Fedora's.
# Fedora's page in the Welcome Center goes too; KDE's own Plasma tour stays until
# Cairn's welcome app (v0.3).
if rpm -q plasma-welcome-fedora; then
    if rpm -q --whatrequires plasma-welcome-fedora; then
        echo "Something still needs plasma-welcome-fedora; not removing it." >&2
        exit 1
    fi
    dnf5 remove -y --no-autoremove plasma-welcome-fedora
fi

### 4. Cairn's look ############################################################

install -Dm0644 /ctx/brand/logo/cairn-logo.svg /usr/share/icons/hicolor/scalable/apps/cairn-logo.svg
install -Dm0644 /ctx/brand/logo/cairn-logo.svg /usr/share/pixmaps/cairn-logo.svg
install -Dm0644 /ctx/brand/logo/cairn-logo-light.svg /usr/share/pixmaps/cairn-logo-light.svg
install -Dm0644 -t /usr/share/color-schemes /ctx/brand/plasma/color-schemes/*.colors
mkdir -p /usr/share/wallpapers /usr/share/plasma/look-and-feel
cp -r /ctx/brand/wallpaper/Cairn /usr/share/wallpapers/Cairn
cp -r /ctx/brand/plasma/look-and-feel/org.cairn.desktop /usr/share/plasma/look-and-feel/org.cairn.desktop
# Cairn Light shares the dark theme's panel layout.
cp -r /ctx/brand/plasma/look-and-feel/org.cairn.desktop.light /usr/share/plasma/look-and-feel/org.cairn.desktop.light
cp -r /ctx/brand/plasma/look-and-feel/org.cairn.desktop/contents/layouts \
    /usr/share/plasma/look-and-feel/org.cairn.desktop.light/contents/layouts

# Fedora's lock screen and login screen show /usr/share/wallpapers/Fedora; point it at Cairn's.
rm -rf /usr/share/wallpapers/Fedora
ln -s Cairn /usr/share/wallpapers/Fedora

# Startup splash after login: the wordmark comes from brand/logo/.
install -Dm0644 /ctx/brand/logo/cairn-wordmark.svg \
    /usr/share/plasma/look-and-feel/org.cairn.desktop/contents/splash/images/cairn-wordmark.svg

# Window decorations with hexagonal buttons (KDE Aurorae themes), dark and light.
mkdir -p /usr/share/aurorae/themes
cp -r /ctx/brand/plasma/aurorae/Cairn /ctx/brand/plasma/aurorae/CairnLight /usr/share/aurorae/themes/

# Boot animation (Plymouth): Cairn's artwork plus the password-prompt images from
# Fedora's spinner theme, which every two-step theme needs.
install -d /usr/share/plymouth/themes/cairn
cp /ctx/brand/plymouth/cairn/* /usr/share/plymouth/themes/cairn/
for img in lock entry bullet; do
    cp /usr/share/plymouth/themes/spinner/${img}.png /usr/share/plymouth/themes/cairn/
done
for img in capslock keyboard keymap-render; do
    if [ -f /usr/share/plymouth/themes/spinner/${img}.png ]; then
        cp /usr/share/plymouth/themes/spinner/${img}.png /usr/share/plymouth/themes/cairn/
    fi
done
if command -v plymouth-set-default-theme >/dev/null; then
    plymouth-set-default-theme cairn
else
    mkdir -p /etc/plymouth
    printf '[Daemon]\nTheme=cairn\n' > /etc/plymouth/plymouthd.conf
fi

### 5. System files: defaults, services, installer settings ###################

# Includes /etc/xdg/kdeglobals, which makes Cairn's global theme the default for new users.
cp -rv /ctx/system_files/. /

### 6. Name the system Cairn ###################################################

# os-release is what every program reads to learn the system's name.
# ID stays "fedora" so Fedora's tools and the installer builder keep working.
osr=/usr/lib/os-release
set_osr() {
    if grep -q "^$1=" "$osr"; then
        sed -i "s|^$1=.*|$1=$2|" "$osr"
    else
        echo "$1=$2" >> "$osr"
    fi
}
set_osr NAME '"Cairn"'
set_osr VERSION "\"${CAIRN_VERSION} (Kinoite)\""
set_osr PRETTY_NAME "\"Cairn ${FEDORA_VERSION}\""
set_osr VARIANT '"Cairn Desktop"'
set_osr VARIANT_ID cairn
set_osr LOGO cairn-logo
set_osr ANSI_COLOR '"38;2;244;166;42"'
set_osr DEFAULT_HOSTNAME cairn
set_osr IMAGE_ID cairn
set_osr IMAGE_VERSION "${CAIRN_VERSION}"
sed -i '/^HOME_URL=/d;/^DOCUMENTATION_URL=/d;/^SUPPORT_URL=/d;/^BUG_REPORT_URL=/d;/^REDHAT_/d' "$osr"
cat "$osr"

### 7. Services ################################################################

# Download system updates in the background; they apply at the next restart
# (policy set in /etc/rpm-ostreed.conf).
systemctl enable rpm-ostreed-automatic.timer
systemctl enable cairn-flatpak-setup.timer
systemctl enable cairn-flatpak-update.timer

### 8. Tidy up #################################################################

# Leave third-party repos off: the system updates as a whole image, not package by package.
# (Repo files can live in /etc/yum.repos.d or, for packaged repos, /usr/share/dnf5/repos.d.)
shopt -s nullglob
for repo in /etc/yum.repos.d/vscode.repo \
            /etc/yum.repos.d/rpmfusion-*.repo \
            /usr/share/dnf5/repos.d/rpmfusion-*.repo; do
    sed -i 's/^enabled=1/enabled=0/' "$repo"
    echo "Turned off the repos in ${repo}"
done
shopt -u nullglob
dnf5 repolist --enabled
dnf5 clean all
# dnf leaves runtime state behind that doesn't belong in an image (flagged by `bootc container lint`).
rm -rf /run/dnf /var/lib/dnf/repos

### 9. Rebuild the startup image (initramfs) ####################################

# The boot animation lives in the initramfs, so it has to be rebuilt after the theme
# changed. Same command as Universal Blue's images. Runs last: os-release goes in too.
KVER="$(rpm -q --queryformat='%{VERSION}-%{RELEASE}.%{ARCH}' kernel-core)"
IMG="/usr/lib/modules/${KVER}/initramfs.img"
stock_modules="$(lsinitrd -m "$IMG" | sed -n '/^dracut modules:/,/^=/p' | grep -v -E '^(dracut modules:|=+)$' || true)"

# Leave the daily version out of the initramfs, so it only changes when its contents do
# (smaller updates).
cp /usr/lib/os-release /tmp/os-release.full
sed -i '/^VERSION=/d;/^IMAGE_VERSION=/d;/^OSTREE_VERSION=/d;/^BUILD_ID=/d' /usr/lib/os-release
DRACUT_NO_XATTR=1 dracut --no-hostonly --kver "$KVER" --reproducible --add ostree -f "$IMG"
cp /tmp/os-release.full /usr/lib/os-release
chmod 0600 "$IMG"

# Check the result: Cairn's boot animation and the ostree boot step are in, and no module
# that Fedora's own initramfs had has gone missing.
listing="$(lsinitrd "$IMG")"
grep -q 'usr/share/plymouth/themes/cairn/cairn.plymouth' <<<"$listing"
grep -q 'ostree-prepare-root' <<<"$listing"
new_modules="$(lsinitrd -m "$IMG" | sed -n '/^dracut modules:/,/^=/p' | grep -v -E '^(dracut modules:|=+)$' || true)"
missing="$(comm -23 <(sort <<<"$stock_modules") <(sort <<<"$new_modules"))"
if [ -n "$missing" ]; then
    echo "The rebuilt initramfs lost these dracut modules:" >&2
    echo "$missing" >&2
    exit 1
fi
lsinitrd -f etc/plymouth/plymouthd.conf "$IMG" || true
