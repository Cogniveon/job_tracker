import cv2
import os, argparse

def split_images(annotations, output_folder):
  with open(annotations, 'r') as file:
    image_entries = file.readlines()

    for image_entry in image_entries:
      values = image_entry.split()

      image_path = values[0]
      filename = os.path.basename(image_path).split('.')[0]
      ext = os.path.basename(image_path).split('.')[1]

      img = cv2.imread(image_path);

      num_of_objs = int(values[1])

      rects = values[2:]

      for i in range(num_of_objs):
        rect = rects[(i * 4): (i * 4) + 4]

        [x, y, w, h] = [int(x) for x in rect]

        cropped_image = img[y:y + h, x:x + w]

        cv2.imwrite(os.path.join(output_folder, filename + '_' + str(i) + '.' + ext), cropped_image)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="Crop images from annotations.txt file.")
  parser.add_argument("annotations", help="Path to the annotations.txt file.")
  parser.add_argument("output_folder", help="Path to the output folder.")
  args = parser.parse_args()

  split_images(args.annotations, args.output_folder)
