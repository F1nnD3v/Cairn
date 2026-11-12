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

# Kinoite already has Firefox, Dolphin, Konsole, Spectacle, Ark, Podman and Discover.
# Added here: the KDE apps it leaves out, full Git, VS Code, Distrobox and VirtualBox support.
dnf5 install -y \
    okular \
    gwenview \
    kate \
    git \
    code \
    distrobox \
    virtualbox-guest-additions

### 4. Cairn's look ############################################################

install -Dm0644 /ctx/brand/logo/cairn-logo.svg /usr/share/icons/hicolor/scalable/apps/cairn-logo.svg
install -Dm0644 /ctx/brand/logo/cairn-logo.svg /usr/share/pixmaps/cairn-logo.svg
install -Dm0644 /ctx/brand/logo/cairn-logo-light.svg /usr/share/pixmaps/cairn-logo-light.svg
install -Dm0644 -t /usr/share/color-schemes /ctx/brand/plasma/color-schemes/*.colors
mkdir -p /usr/share/wallpapers /usr/share/plasma/look-and-feel
cp -r /ctx/brand/wallpaper/Cairn /usr/share/wallpapers/Cairn
cp -r /ctx/brand/plasma/look-and-feel/org.cairn.desktop /usr/share/plasma/look-and-feel/org.cairn.desktop

# Fedora's lock screen and login screen show /usr/share/wallpapers/Fedora; point it at Cairn's.
rm -rf /usr/share/wallpapers/Fedora
ln -s Cairn /usr/share/wallpapers/Fedora

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
