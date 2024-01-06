import gc

import torch
from ultralytics import YOLO

device = "cuda:0" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")


def train():
    # Load a model
    model = YOLO("yolov8n.pt")  # load a pretrained model (recommended for training)

    # Use the model
    model.train(
        data="config.yaml",
        epochs=20,
        val=True,
        device=device,
    )  # train the model

    # metrics = model.val()  # evaluate model performance on the validation set
    # print(f"MAP: {metrics.box.map}")

    path = model.export(format="onnx")  # export the model to ONNX format

    print(f"Saved to {path}")

    torch.cuda.empty_cache()
    gc.collect()


if __name__ == "__main__":
    train()
