#!/usr/bin/bash
# Turns Fedora Kinoite into Cairn. Runs once, inside the image build (see Containerfile).
# /ctx is this repository's build_files/, brand/ and system_files/, mounted read-only.
set -euxo pipefail

FEDORA_VERSION="$(rpm -E %fedora)"
CAIRN_VERSION="${CAIRN_VERSION:-${FEDORA_VERSION}}"

### 1. Extra software sources ##################################################

# RPM Fusion (free) for full media codecs.
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

# Fedora ships codec-limited builds; swap in the full ones from RPM Fusion.
dnf5 swap -y ffmpeg-free ffmpeg --allowerasing
dnf5 install -y \
    gstreamer1-plugins-bad-freeworld \
    gstreamer1-plugins-ugly \
    gstreamer1-plugin-libav \
    mesa-va-drivers-freeworld

### 3. Apps and tools ##########################################################

# Already in Kinoite are kept; listing them here guarantees they're present.
dnf5 install -y \
    firefox \
    dolphin konsole okular gwenview spectacle ark kate \
    git \
    code \
    distrobox \
    podman \
    virtualbox-guest-additions

### 4. Cairn's look ############################################################

install -Dm0644 /ctx/brand/logo/cairn-logo.svg /usr/share/icons/hicolor/scalable/apps/cairn-logo.svg
install -Dm0644 /ctx/brand/logo/cairn-logo.svg /usr/share/pixmaps/cairn-logo.svg
install -Dm0644 /ctx/brand/logo/cairn-logo-light.svg /usr/share/pixmaps/cairn-logo-light.svg
install -Dm0644 -t /usr/share/color-schemes /ctx/brand/plasma/color-schemes/*.colors
mkdir -p /usr/share/wallpapers /usr/share/plasma/look-and-feel
cp -r /ctx/brand/wallpaper/Cairn /usr/share/wallpapers/Cairn
cp -r /ctx/brand/plasma/look-and-feel/org.cairn.desktop /usr/share/plasma/look-and-feel/org.cairn.desktop

### 5. System files (services, defaults) #######################################

cp -r /ctx/system_files/. /

### 6. Name the system Cairn ###################################################

# os-release is what every program reads to learn the system's name.
# ID stays "fedora" so Fedora's own tools (toolbox, installer, update checks) keep working.
osr="$(readlink -f /usr/lib/os-release)"
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
sed -i '/^HOME_URL=/d;/^DOCUMENTATION_URL=/d;/^SUPPORT_URL=/d;/^BUG_REPORT_URL=/d' "$osr"

### 7. Services ################################################################

systemctl enable rpm-ostreed-automatic.timer
systemctl enable cairn-flatpak-setup.timer
systemctl enable cairn-flatpak-update.timer

### 8. Tidy up #################################################################

# Leave third-party repos off: the system updates as a whole image, not package by package.
sed -i 's/^enabled=1/enabled=0/' /etc/yum.repos.d/vscode.repo
for repo in /etc/yum.repos.d/rpmfusion-*.repo; do
    sed -i 's/^enabled=1/enabled=0/' "$repo"
done
dnf5 clean all
