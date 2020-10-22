import cv2
import os
import shutil

path = "data"
output = 'images/'
for (dirpath, dirfile, filenames) in os.walk(path):
    for filename in filenames:
        try:
            if filename.endswith('.jpg'):

                image = cv2.imread(os.path.join(dirpath, filename))
                image = cv2.resize(image, (416, 416))
                cv2.imwrite(filename, image)
                shutil.move(filename, output + filename)
        except FileNotFoundError:
            if filename.endswith('.JPEG'):

                image = cv2.imread(os.path.join(dirpath, filename))
                image = cv2.resize(image, (416, 416))
                cv2.imwrite(filename, image)
                shutil.move(filename, output + filename)
