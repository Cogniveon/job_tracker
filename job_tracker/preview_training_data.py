import os

import cv2

image_dir = "dataset/val/images"
label_dir = "dataset/val/labels"

image_files = sorted(os.listdir(image_dir))


for image_file in image_files:
    # Load the image
    image_path = os.path.join(image_dir, image_file)
    image = cv2.imread(image_path)

    # Load corresponding label file
    label_file = "frame_" + image_file.split("_")[1].split(".")[0] + ".txt"
    label_path = os.path.join(label_dir, label_file)

    # Read label information from the file
    with open(label_path, "r") as file:
        lines = file.readlines()

    # Draw rectangles on the image based on the label information
    for line in lines:
        label_info = line.split()
        class_id, cx, cy, width, height = map(float, label_info)
        x = cx - (width / 2)
        y = cy - (height / 2)
        x, y, width, height = (
            int(x * image.shape[1]),
            int(y * image.shape[0]),
            int(width * image.shape[1]),
            int(height * image.shape[0]),
        )

        # Draw rectangle on the image
        cv2.rectangle(image, (x, y), (x + width, y + height), (0, 255, 0), 2)

    # Display the image with rectangles
    cv2.imshow("Image with Labels", image)

    # Set a delay between frames (milliseconds)
    cv2.waitKey(100)

    # Close the window when the user presses any key
    if cv2.waitKey(0) & 0xFF == 27:  # Press 'Esc' to exit
        break

# Release the window and close it
cv2.destroyAllWindows()
