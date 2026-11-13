/*
    Cairn's startup splash: shown between logging in and the desktop appearing.
    Based on KDE Breeze's Splash.qml (SPDX-FileCopyrightText: 2014 Marco Martin <mart@kde.org>,
    SPDX-License-Identifier: GPL-2.0-or-later).

    The wordmark (images/cairn-wordmark.svg) is copied in from brand/logo/ by the image build.
    ksplashqml sets `stage` as login progresses; this splash doesn't depend on its values.
*/

import QtQuick
import org.kde.kirigami as Kirigami

Rectangle {
    id: root
    color: "#121316"

    property int stage

    Component.onCompleted: introAnimation.running = true

    Item {
        id: content
        anchors.fill: parent
        opacity: 0

        Image {
            id: wordmark
            anchors.centerIn: parent
            asynchronous: true
            source: "images/cairn-wordmark.svg"
            sourceSize.height: Kirigami.Units.gridUnit * 4
        }

        // Three honey cells that light up in turn while the desktop loads.
        Row {
            anchors.top: wordmark.bottom
            anchors.topMargin: Kirigami.Units.gridUnit * 2
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: Kirigami.Units.smallSpacing * 2

            Repeater {
                model: 3
                Image {
                    id: cell
                    required property int index
                    source: "images/hex.svg"
                    sourceSize.width: Kirigami.Units.gridUnit
                    sourceSize.height: Kirigami.Units.gridUnit
                    opacity: 0.25

                    SequentialAnimation on opacity {
                        loops: Animation.Infinite
                        // Don't animate if the user has turned animations off.
                        running: Kirigami.Units.longDuration > 1
                        PauseAnimation { duration: cell.index * 200 }
                        NumberAnimation { to: 1; duration: 400; easing.type: Easing.InOutQuad }
                        NumberAnimation { to: 0.25; duration: 400; easing.type: Easing.InOutQuad }
                        PauseAnimation { duration: (2 - cell.index) * 200 }
                    }
                }
            }
        }
    }

    OpacityAnimator {
        id: introAnimation
        running: false
        target: content
        from: 0
        to: 1
        duration: Kirigami.Units.veryLongDuration * 2
        easing.type: Easing.InOutQuad
    }
}
