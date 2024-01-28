import base64
import json
import os
from datetime import datetime

import cherrypy
import cv2
import paho.mqtt.client as mqtt
from sample_tracker import SampleTracker

# Set the path to store the images
IMAGE_FOLDER = "images"
JOB_TRACKER_MODEL_PATH = "job_tracker.pt"


# MQTT callbacks
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#")
    client.subscribe("room-cutup")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print("mqtt:" + msg.topic + " " + str(msg.payload))


# CherryPy Server
class CameraApp:
    def __init__(self) -> None:
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = on_connect
        self.mqtt_client.on_message = on_message

        # self.mqtt_client.username_pw_set(username="user_name", password="password") # uncomment if you use password auth
        self.mqtt_client.connect("mosquitto", 1883, 60)

        # Blocking call that processes network traffic, dispatches callbacks and
        # handles reconnecting.
        # Other loop*() functions are available that give a threaded interface and a
        # manual interface.
        self.mqtt_client.loop_start()

    @cherrypy.expose
    def index(self, room=None, name=None):
        rooms = ["cutup", "embedding", "microtomy"]
        names = ["anand", "zhengyang", "greg", "german", "nicola", "jorge"]

        if room not in rooms or name not in names:
            # Show dropdown lists to select room and name
            room_options = "\n".join(
                [f'<option value="{r}">{r}</option>' for r in rooms]
            )
            name_options = "\n".join(
                [f'<option value="{n}">{n}</option>' for n in names]
            )
            return f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Camera App</title>
                </head>
                <body>
                    <h1>Select Room and Name</h1>
                    <form action="/index" method="post">
                        <label for="room">Select Room:</label>
                        <select id="room" name="room">
                            {room_options}
                        </select>
                        <br>
                        <label for="name">Select Name:</label>
                        <select id="name" name="name">
                            {name_options}
                        </select>
                        <br>
                        <button type="submit">Start Camera</button>
                    </form>
                </body>
                </html>
            """
        else:
            # Redirect to the camera page with selected room and name as query parameters
            raise cherrypy.HTTPRedirect(f"/camera?room={room}&name={name}")

    @cherrypy.expose
    def camera(self, room, name):
        return (
            '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Camera App</title>
            </head>
            <body>
                <h1>Click a Picture</h1>
                <button id="capture-btn" onclick="capture()">Capture</button>
                <br>
                <canvas id="camera-view" width="1280" height="720" style="border: 2px solid black; display:block;"></canvas>
                <br>
                <img id="image-preview" src="" alt="Image Preview" style="display:none; max-width: 1280px; max-height: 720px;">
                <script>
                    var cameraView = document.getElementById("camera-view");
                    var context = cameraView.getContext("2d");
                    
                    function startCamera() {
                        navigator.getUserMedia = (navigator.mediaDevices.getUserMedia ||
                            navigator.mediaDevices.webkitGetUserMedia ||
                            navigator.mediaDevices.mozGetUserMedia ||
                            navigator.mediaDevices.msGetUserMedia);
                        if (typeof navigator.getUserMedia !== 'undefined') {
                            navigator.mediaDevices.getUserMedia({ video: true })
                                .then(function(stream) {
                                    cameraView.style.display = "block";
                                    var video = document.createElement("video");
                                    video.srcObject = stream;
                                    video.play();
                                    drawCameraFrame(video);
                                })
                                .catch(function(err) {
                                    console.error("Error accessing camera: ", err);
                                });
                        } else {
                            console.error("getUserMedia not supported on this browser.");
                        }
                    }
                    
                    function drawCameraFrame(video) {
                        context.drawImage(video, 0, 0, cameraView.width, cameraView.height);
                        requestAnimationFrame(function() {
                            drawCameraFrame(video);
                        });
                    }
                    
                    function capture() {
                        if (cameraView.style.display == 'none') {
                            cameraView.style.display = "block;
                            imagePreview.style.display = "none";
                            captureBtn.innerText = "Capture";
                            return;
                        }

                        var imageData = cameraView.toDataURL("image/jpeg", 0.9); // Use "image/jpeg" format with 0.9 quality
                        var imagePreview = document.getElementById("image-preview");
                        imagePreview.src = imageData;
                        imagePreview.style.display = "block";
                        captureBtn.innerText = "Resume";
                        cameraView.style.display = "none";
                        
                        // Send the image data to the server
                        var xhr = new XMLHttpRequest();
                        xhr.open("POST", "/save_image", true);
                        xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
                        xhr.send("image_data=" + encodeURIComponent(imageData) + "&room=" + encodeURIComponent("'''
            + room
            + '''") + "&name=" + encodeURIComponent("'''
            + name
            + """"));
                        xhr.addEventListener('load', function(event) {
                            imagePreview.src = xhr.response;
                            imagePreview.style.display = "block";
                        })
                    }
                    
                    // Start the camera on page load
                    startCamera();
                </script>
            </body>
            </html>
        """
        )

    @cherrypy.expose
    def save_image(self, image_data, room, name):
        image_data = image_data.replace("data:image/jpeg;base64,", "")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_name = f"{name}_{room}_{timestamp}.jpeg"
        image_path = os.path.join(IMAGE_FOLDER, image_name)

        with open(image_path, "wb") as f:
            f.write(base64.b64decode(image_data))

        image = cv2.imread(image_path)

        sample_tracker = SampleTracker()

        labels = sample_tracker.run_inference(image)

        for i, label in enumerate(labels):
            # print(label)
            self.mqtt_client.publish(
                f"room-{room}",
                json.dumps(
                    {
                        "user": name,
                        "text": label["text"],
                        "rect": label["rect"],
                        "timestamp": timestamp,
                    }
                ),
            )

        preview = sample_tracker.annotate_labels(image, labels)

        # from model_src.inference import generate_preview, get_label_text, run_inference
        # result = run_inference(JOB_TRACKER_MODEL_PATH, image_path)[0]
        # preview = result["preview"]
        # labels = get_label_text(result["labels"])
        # preview = generate_preview(image_path, labels)

        return f"data:image/jpeg;base64,{base64.b64encode(cv2.imencode('.jpg', preview)[1]).decode('utf-8')}"


if __name__ == "__main__":
    if not os.path.exists(IMAGE_FOLDER):
        os.makedirs(IMAGE_FOLDER)

    cherrypy.config.update({"server.socket_host": "0.0.0.0"})
    cherrypy.quickstart(CameraApp())
