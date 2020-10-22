from PIL import Image
import os
from os import listdir
from os.path import splitext
import shutil

target_directory = 'data'
target = '.jpg'


for (dirpath, dirfile, filenames) in os.walk("data"):
    for filename in filenames:
        if filename.endswith(".JPEG"):
            file_prefix = filename.split('.')[0]
            im = Image.open(os.path.join(dirpath, filename))
            im.save(file_prefix + target)
            os.remove(os.path.join(dirpath, filename))
            shutil.move(file_prefix + target, "data/{}".format(file_prefix + target))