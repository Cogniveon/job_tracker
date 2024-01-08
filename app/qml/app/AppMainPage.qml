/*
Copyright 2023

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/


import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import header
import pyobjects
// import video_backend
import camera_stream


Page {
    anchors.fill: parent
    header: AppHeader {}

    ColumnLayout {
        id: aboutTab
        spacing: 8
        width: parent.width

        Rectangle { color: "transparent"; height: 10; width: 10 }

        CameraStream {
            id: cameraStream
            Layout.preferredWidth: 640
            Layout.preferredHeight: 480
            Layout.alignment: Qt.AlignHCenter
        }

        RowLayout {
            spacing: 8
            width: parent.width

            property bool isStreamingCamera: true


            ComboBox {
                id: captureDeviceSelect
                Layout.alignment: Qt.AlignHCenter
                model: cameraStream.captureOptions

                onCurrentIndexChanged: cameraStream.onSelectionChanged(currentIndex)
            }
            
            Button {
                text: "Capture"
                Layout.alignment: Qt.AlignHCenter
                onClicked: {
                    if (parent.isStreamingCamera) {
                        parent.isStreamingCamera = false
                        cameraStream.startDetection()
                    }
                    else {
                        cameraStream.resume()
                        parent.isStreamingCamera = true
                    }
                }
            }
        }

        // VideoBackend {
        //     id: videoBackend
        // }
        
        // Image {
        //     id: videoOutput
        //     // source: "qrc:/data/app-icon.svg"
        //     // source: "image://videostream/frame?" + currentFrameNumber
        //     asynchronous: true
        //     Layout.preferredWidth: 640
        //     Layout.preferredHeight: 480
        //     Layout.alignment: Qt.AlignHCenter
        // }

        // Connections {
        //     target: videoBackend

        //     function newImage(newImage) {
        //         console.log("newImage", newImage.size);
        //         videoOutput.source = newImage;
        //     }
        // }

        // Rectangle { color: "transparent"; height: 45; width: 10 }

        // Label {
        //     text: Qt.application.name + ' (' +  Qt.application.version + ')'
        //     font.bold: true
        //     font.pixelSize: Qt.application.font.pixelSize * 1.5
        //     Layout.alignment: Qt.AlignHCenter
        // }

        // Label {
        //     text: 'Running on ' +  Qt.platform.os
        //     font.bold: true
        //     font.pixelSize: Qt.application.font.pixelSize * 1.5
        //     Layout.alignment: Qt.AlignHCenter
        // }

        // Rectangle { color: "transparent"; height: 45; width: 10 }

        // Label {
        //     text: qsTranslate("MainPage", "Have fun!")
        //     color: Material.accent
        //     font.bold: true
        //     font.pixelSize: Qt.application.font.pixelSize * 2
        //     Layout.alignment: Qt.AlignHCenter
        // }

        // Rectangle { color: "transparent"; height: 45; width: 10 }

        // Label {
        //     text: qsTranslate("MainPage", "Exposed from Python: '%1'").arg(SingletonPyObject.exposed_property)
        //     Layout.alignment: Qt.AlignHCenter
        // }
    }

}
