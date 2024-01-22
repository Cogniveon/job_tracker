import base64

import config
import cv2
import numpy as np
from googleapiclient.discovery import build
from PIL import Image, ImageDraw, ImageFont
from ultralytics import YOLO


class SampleTracker:
    def __init__(self) -> None:
        self.model = YOLO(
            "sample_tracker.onnx", task="detect"
        )  # yolov8n.pt sample_tracker.pt
        self.gvision = build("vision", "v1", developerKey=config.GOOGLE_API_KEY)

    def annotate_labels(self, cv_image, labels):
        image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)

        draw = ImageDraw.Draw(image)

        overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
        overlay_draw = ImageDraw.Draw(overlay)

        # Font settings - using a default font
        font_size = 13  # Adjust as needed
        font = ImageFont.load_default(font_size)

        for i, label in enumerate(labels):
            rect = label["rect"]
            text = label["text"]

            # Calculate the position of the top left corner of the rectangle
            top_left_x = rect[0] - rect[2] // 2
            top_left_y = rect[1] - rect[3] // 2

            box_start_x = top_left_x
            box_start_y = top_left_y
            box_end_x = top_left_x + rect[2]
            box_end_y = top_left_y + rect[3]
            overlay_draw.rectangle(
                [box_start_x, box_start_y, box_end_x, box_end_y],
                outline="red",
                fill=(100, 0, 0, 200),
                width=1,
            )

            text_width, text_height = draw.textbbox(
                (top_left_x, top_left_y), text, font=font
            )[2:]

            # Since we want the text to be centered in the rectangle, calculate the starting position
            text_start_x = top_left_x
            text_start_y = top_left_y

            overlay_draw.text(
                (text_start_x, text_start_y), text, font=font, fill="white"
            )

        image = Image.alpha_composite(image.convert("RGBA"), overlay)
        image = np.array(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        return image

    def split_images_by_xywh(self, image, rects):
        labels = []
        rois = []
        for rect in rects:
            cx, cy, w, h = rect
            half_width = w / 2
            half_height = h / 2

            roi = image[
                int(cy - half_height) : int(cy + half_height),
                int(cx - half_width) : int(cx + half_width),
            ]
            labels.append({"text": "", "rect": rect.tolist()})
            rois.append(roi)

        return labels, rois

    def run_inference(self, image):
        results = self.model(image, imgsz=640)
        r = results[0].cpu()

        rects = [np.floor(box.xywh.numpy()[0]).astype(int) for box in r.boxes]
        labels, rois = self.split_images_by_xywh(image, rects)

        for i, label in enumerate(labels):
            _, roi_encoded = cv2.imencode(".jpg", rois[i])
            roi_base64 = (base64.b64encode(roi_encoded)).decode("utf-8")

            request = self.gvision.images().annotate(
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
                            "imageContext": {"languageHints": ["en-GB"]},
                        }
                    ],
                }
            )
            responses = request.execute(num_retries=3)["responses"]

            if len(responses) > 0 and "fullTextAnnotation" in responses[0]:
                label["text"] = str(responses[0]["fullTextAnnotation"]["text"]).replace(
                    "\n", " "
                )

            labels[i] = label

        # result_plot = r.plot(conf=False, probs=False, labels=True)
        # result_plot = cv2.cvtColor(result_plot, cv2.COLOR_RGB2BGR)

        # cv2.rectangle(cv_img, (50, 50), (200, 200), (0, 255, 0), 2)

        labels = [{"text": l["text"], "rect": l["rect"]} for l in labels]

        return labels
