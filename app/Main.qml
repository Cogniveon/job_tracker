import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 2.15

import camera_preview
import "."

ApplicationWindow {
    id: window
    title: "Sample Tracker"
    width: 800
    height: 480
    visible: true
    flags: Qt.FramelessWindowHint | Qt.Window

    required property var users
    required property var rooms

    function startDetection(user, room) {
      cameraPreview.pause()
      backend.startDetection(user, room)
    }

    Shortcut {
        sequences: ["Esc", "Back"]
        // enabled: stackView.depth > 1
        onActivated: window.close()
    }

    Shortcut {
        sequences: ["Space"]
        onActivated: {
          startDetection(userSelect.currentIndex, roomSelect.currentIndex)
        }
    }

    LoadingDialog {
        id: loadingDialog


        Component.onCompleted: {
            backend.showLoading.connect(loadingDialog.showDialog)
            backend.hideLoading.connect(loadingDialog.hideDialog)
        }
    }

    RowLayout {
      spacing: 6

      RowLayout {
        spacing: 6

        CameraPreview {
            id: cameraPreview
            Layout.fillWidth: true
            Layout.minimumWidth: 640
            Layout.maximumWidth: 640
            Layout.minimumHeight: 480
        }

        // Rectangle {
        //     color: 'teal'
        //     Layout.fillWidth: true
        //     Layout.minimumWidth: 640
        //     Layout.maximumWidth: 640
        //     Layout.minimumHeight: 480
        //     Text {
        //         anchors.centerIn: parent
        //         text: parent.width + 'x' + parent.height
        //     }
        // }

        ColumnLayout {
          Layout.fillWidth: true
          Layout.fillHeight: true
          Layout.minimumWidth: 150


          Label {
              text: "User:"
          }

          ComboBox {
              id: userSelect
              model: window.users
              // Component.onCompleted: {
              //     console.log('Selection: ' + currentIndex)
              // }
              Layout.fillWidth: true
          }


          Label {
              text: "Room:"
          }

          ComboBox {
              id: roomSelect
              model: window.rooms
              // Component.onCompleted: {
              //     console.log('Selection: ' + currentIndex)
              // }
              Layout.fillWidth: true
          }

          Button {
            id: captureButton
            text: "Detect"
            // Signal to handle button click will be connected to Python
            onClicked: startDetection(userSelect.currentIndex, roomSelect.currentIndex)
          }

          Button {
            id: resumeButton
            text: "Resume"
            visible: false
            // Signal to handle button click will be connected to Python
            onClicked: cameraPreview.resume()
          }
        }
        // Rectangle {
        //     color: 'plum'
        //     Layout.fillWidth: true
        //     Layout.fillHeight: true
        //     Layout.minimumWidth: 100
        //     Layout.preferredWidth: 200
        //     Layout.preferredHeight: 100
        //     Text {
        //         anchors.centerIn: parent
        //         text: parent.width + 'x' + parent.height
        //     }
        // }
      }
    }




  Connections {
    target: cameraPreview

    function onNewImage(newImage) {
      backend.updateImage(newImage)
    }

    function onIsPlaying(isPlaying) {
      if (isPlaying) {
        captureButton.visible = true
        resumeButton.visible = false
      }
      else {
        resumeButton.visible = true
        captureButton.visible = false
      }
    }
  }

  Connections {
    target: backend

    function onNewPreview(preview) {
      cameraPreview.updatePreview(preview)
    }
  }

}