import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: loadingDialog
    visible: false
    anchors.fill: parent
    Rectangle {
        anchors.fill: parent
        color: "#80000000"  // Semi-transparent background

        ColumnLayout {
            anchors.centerIn: parent
            spacing: 20

            BusyIndicator {
                id: busyIndicator
                running: loadingDialog.visible
            }

            Label {
                id: messageLabel
                text: "Processing..."
                color: "#FFFFFF"
            }
        }
    }

    function showDialog() {
        loadingDialog.visible = true
    }

    function hideDialog() {
        loadingDialog.visible = false
    }
}