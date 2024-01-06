import argparse
import math
import os
import random
import shutil

import cv2


def train_val_split(input_folder, output_folder, ratio=0.8):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    train_folder = os.path.join(output_folder, "train")
    os.makedirs(train_folder)

    val_folder = os.path.join(output_folder, "val")
    os.makedirs(val_folder)

    os.makedirs(os.path.join(train_folder, "images"))
    os.makedirs(os.path.join(train_folder, "labels"))
    os.makedirs(os.path.join(val_folder, "images"))
    os.makedirs(os.path.join(val_folder, "labels"))

    all_images = os.listdir(os.path.join(input_folder, "images"))
    random.shuffle(all_images)
    # all_images.sort()

    no_training_images = math.ceil(len(all_images) * ratio)
    train_images = all_images[:no_training_images]
    val_images = all_images[no_training_images:]

    for x in train_images:
        shutil.copy(
            os.path.join(input_folder, "images", x),
            os.path.join(train_folder, "images"),
        )
        shutil.copy(
            os.path.join(input_folder, "labels", x.replace(".jpg", ".txt")),
            os.path.join(train_folder, "labels"),
        )

    for x in val_images:
        shutil.copy(
            os.path.join(input_folder, "images", x), os.path.join(val_folder, "images")
        )
        shutil.copy(
            os.path.join(input_folder, "labels", x.replace(".jpg", ".txt")),
            os.path.join(val_folder, "labels"),
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Split training and validation data from a given folder"
    )
    parser.add_argument(
        "input_folder",
        help="Path to the input folder that contains an images and labels folder to be split.",
    )
    parser.add_argument(
        "output_folder",
        help="Path to the output folder where a train & val folders will be made.",
    )
    parser.add_argument("ratio", type=float, help="Ratio of the training data")
    args = parser.parse_args()

    train_val_split(args.input_folder, args.output_folder, args.ratio)
