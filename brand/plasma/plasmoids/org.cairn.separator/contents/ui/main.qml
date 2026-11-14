/*
    Cairn's panel divider: a thin line, as in the design preview.
    Adapted from KDE's Margins Separator widget
    (SPDX-FileCopyrightText: 2020 Niccolò Venerandi <niccolo@venerandi.com>,
    SPDX-License-Identifier: GPL-2.0-only OR GPL-3.0-only OR LicenseRef-KDE-Accepted-GPL).
*/
pragma ComponentBehavior: Bound

import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore
import org.kde.kirigami as Kirigami
import org.kde.ksvg as KSvg

PlasmoidItem {
    id: root

    readonly property bool isVertical: Plasmoid.formFactor === PlasmaCore.Types.Vertical
    readonly property int thickness: Kirigami.Units.largeSpacing * 2

    Layout.minimumWidth: isVertical ? -1 : thickness
    Layout.preferredWidth: Layout.minimumWidth
    Layout.maximumWidth: Layout.minimumWidth

    Layout.minimumHeight: isVertical ? thickness : -1
    Layout.preferredHeight: Layout.minimumHeight
    Layout.maximumHeight: Layout.minimumHeight

    preferredRepresentation: fullRepresentation
    Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground

    KSvg.SvgItem {
        anchors.centerIn: parent
        height: root.isVertical ? 1 : Math.round(root.height * 0.5)
        width: root.isVertical ? Math.round(root.width * 0.5) : 1
        imagePath: "widgets/line"
        elementId: root.isVertical ? "horizontal-line" : "vertical-line"
    }
}
