import base64
from io import BytesIO

import numpy as np
from PIL import Image
from ultralytics import YOLO


def run_inference(model_path, image_path):
    # Runs
    model = YOLO(model_path)

    inference = model(image_path, conf=0.6)

    results = []

    for r in inference:
        r = r.cpu()

        buffer = BytesIO()
        result_plot = r.plot(conf=False, probs=False, labels=False)
        im = Image.fromarray(result_plot[..., ::-1])
        im.save(buffer, format="JPEG")

        results.append(
            {
                "rects": [np.floor(box.xywh.numpy()[0]).astype(int) for box in r.boxes],
                "preview": base64.b64encode(buffer.getvalue()),
            }
        )

    return results

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
