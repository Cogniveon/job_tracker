import base64
import os
from io import BytesIO

import cv2
import numpy as np
from googleapiclient.discovery import build
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO


def split_images_by_xywh(image, rects):
    labels = []
    for rect in rects:
        cx, cy, w, h = rect
        half_width = w / 2
        half_height = h / 2

        roi = image[
            int(cy - half_height) : int(cy + half_height),
            int(cx - half_width) : int(cx + half_width),
        ]
        labels.append({"label_text": "", "rect": rect, "image": roi})

    return labels


def run_inference(model_path, image_path):
    image = cv2.imread(image_path)
    model = YOLO(model_path)

    inference = model(image_path, conf=0.6)

    results = []

    for r in inference:
        r = r.cpu()

        result_plot = r.plot(conf=False, probs=False, labels=False)
        im = Image.fromarray(result_plot[..., ::-1])

        buffer = BytesIO()
        im.save(buffer, format="JPEG")

        rects = [np.floor(box.xywh.numpy()[0]).astype(int) for box in r.boxes]
        labels = split_images_by_xywh(image, rects)
        results.append(
            {
                "labels": labels,
                "preview": base64.b64encode(buffer.getvalue()),
            }
        )

    return results


def get_label_text(labels: list[dict]):
    # print(f"Google API KEY={os.environ.get('GOOGLE_API_KEY')}")
    vservice = build("vision", "v1", developerKey=os.environ.get("GOOGLE_API_KEY"))

    for i, label in enumerate(labels):
        roi = label["image"]

        _, roi_encoded = cv2.imencode(".jpg", roi)
        roi_base64 = (base64.b64encode(roi_encoded)).decode("utf-8")

        request = vservice.images().annotate(
            body={
                "requests": [
                    {
                        "image": {
                            "content": roi_base64,
                            # 'source': {
                            #     'gcs_image_uri': IMAGE
                            # }
                        },
                        "features": [
                            {
                                "type": "TEXT_DETECTION",
                                "maxResults": 3,
                            }
                        ],
                    }
                ],
            }
        )
        responses = request.execute(num_retries=3)

        label["label_text"] = str(
            responses["responses"][0]["textAnnotations"][0]["description"]
        ).replace("\n", " ")

        labels[i] = label

    return labels


def generate_preview(image_path, labels):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    for label in labels:
        label_text = label["label_text"]
        cx, cy, w, h = label["rect"]
        half_width = w / 2
        half_height = h / 2

        rect_outline = [
            cx - half_width,
            cy - half_height,
            cx + half_width,
            cy + half_height,
        ]
        draw.rectangle(rect_outline, outline=(255, 0, 0))

        text_position = (cx - half_width, cy - half_height - 20)
        print(f"Drawing {label_text} at {text_position}")
        draw.text(text_position, label_text, fill=(255, 0, 0), font=font)

    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode()

    # # Load a model
    # model = YOLO("job_tracker.pt")

    # results = model("/home/alqaholic/Downloads/test.jpeg")

    # # Show the results
    # for r in results:
    #     im_array = r.plot()  # plot a BGR numpy array of predictions
    # OpenCV uses BGR format, so no need to reverse channels
    # im = Image.fromarray(im_array)


#     # Convert the PIL image to a NumPy array
#     im_np = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)

#     # Display the image using OpenCV
#     cv2.imshow("YOLO Results", im_np)
#     cv2.waitKey(0)

# # Close the OpenCV window
# cv2.destroyAllWindows()
