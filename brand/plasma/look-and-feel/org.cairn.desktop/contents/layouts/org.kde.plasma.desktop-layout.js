// Cairn's desktop layout: one floating panel at the bottom, centred and only as wide as
// its contents, like a dock. The Cairn logo is the app-launcher button.
//
// Plasma runs this on a user's first login, and again when the Cairn global theme is
// applied with "Desktop and window layout" ticked (System Settings → Colours & Themes →
// Global Theme). Scripting reference: https://develop.kde.org/docs/plasma/scripting/

var panel = new Panel
panel.location = "bottom"
// Same height rule as KDE's default panel (an even number of pixels).
panel.height = 2 * Math.ceil(gridUnit * 2.5 / 2)
panel.floating = true
panel.alignment = "center"
panel.lengthMode = "fit"

var launcher = panel.addWidget("org.kde.plasma.kickoff")
launcher.currentConfigGroup = ["General"]
launcher.writeConfig("icon", "cairn-logo")

// Pinned apps: web browser, files, terminal, VS Code, app store.
var tasks = panel.addWidget("org.kde.plasma.icontasks")
tasks.currentConfigGroup = ["General"]
tasks.writeConfig("launchers", [
    "preferred://browser",
    "preferred://filemanager",
    "applications:org.kde.konsole.desktop",
    "applications:com.microsoft.VSCode.desktop",
    "applications:org.kde.discover.desktop"
].join(","))

panel.addWidget("org.kde.plasma.marginsseparator")

// Languages that usually need an input method get KDE's input method widget,
// the same rule as KDE's default panel.
var inputMethodLanguages = ["as", "bn", "bo", "brx", "doi", "gu", "hi", "ja", "kn", "ko", "kok",
    "ks", "lep", "mai", "ml", "mni", "mr", "ne", "or", "pa", "sa", "sat", "sd", "si", "ta", "te",
    "th", "ur", "vi", "zh_CN", "zh_TW"]
if (inputMethodLanguages.indexOf(languageId) != -1) {
    panel.addWidget("org.kde.plasma.kimpanel")
}

// System tray: only volume, network, battery and notifications stay visible; the rest
// (clipboard, brightness, display settings) live behind the tray's arrow.
var trayHidden = [
    "org.kde.plasma.clipboard",
    "org.kde.plasma.brightness",
    "org.kde.plasma.nightcolorcontrol",
    "org.kde.kscreen"
].join(",")
var tray = panel.addWidget("org.kde.plasma.systemtray")
// Older Plasma versions keep the tray's settings in a separate inner containment.
var trayInnerId = tray.readConfig("SystrayContainmentId")
tray.currentConfigGroup = ["General"]
tray.writeConfig("hiddenItems", trayHidden)
try {
    if (trayInnerId) {
        var trayInner = desktopById(trayInnerId)
        trayInner.currentConfigGroup = ["General"]
        trayInner.writeConfig("hiddenItems", trayHidden)
    }
} catch (e) {
    print("Cairn layout: could not configure the inner system tray: " + e)
}

// Clock: time only, as in the design.
var clock = panel.addWidget("org.kde.plasma.digitalclock")
clock.currentConfigGroup = ["Appearance"]
clock.writeConfig("showDate", false)

// The desktop itself shows a wallpaper image (Cairn's, from this theme's defaults).
var desktopsArray = desktopsForActivity(currentActivity())
for (var j = 0; j < desktopsArray.length; j++) {
    desktopsArray[j].wallpaperPlugin = "org.kde.image"
}
