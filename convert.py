################### ANNOTATIONS YOLO #######################
#### CLASS_ID, X_center/widht, Y_center/HEIGHT, WIDTH_LABEL, HEIGHT_LABEL

import os
import math
import json
import shutil
import datetime
import numpy as np
from PIL import Image

ANNOTATIONS_DIR_PREFIX = "data"

supercategory = "drone" # Name of classes what do you want to save
create_dir = ['train', 'test', 'val']

WIDTH = 0 #### chieu rong cua image
HEIGHT = 0 #### chieu cao cua image

CLASS_MAPPING_TEMP = ['0', '1']
CLASS_MAPPING = {
    '0': '1', #### 1 : class_name dau`
    '1': '2' #### 2: class_name 2nd
    # Add your remaining classes here.
}


now = datetime.datetime.now() # ngay gio  hien tai
#---------------------------- split data =---------------------------- #####
def split_dataset():

    root_dir = "D:\PracticePY\Project\DeTai\\tool\\txt-to-json\\"
    
    val_ratio = 0.2
    test_ratio = 0.1

    create_dir = ["train", "val", "test", "images"]
    for folder in create_dir: 
        if os.path.exists(folder) == True:
            for(dirpath, dirfile, filenames) in os.walk(folder):
                for f in filenames:
                    os.remove(os.path.join(dirpath, f))
            os.removedirs(folder)
        os.makedirs(root_dir + folder)

    ############### copy images jpg to folder images
    for(dirpath, dirfile, filenames) in os.walk(ANNOTATIONS_DIR_PREFIX):
        for filename in filenames:
            if filename.endswith(".jpg"):
                shutil.copy("data\\" + filename, "images")

    src = root_dir + "images"

    allFileNames = os.listdir(src)
    np.random.shuffle(allFileNames)
    train_FileNames, val_FileNames, test_FileNames = np.split(np.array(allFileNames),
                                                            [int(len(allFileNames)* (1 - (val_ratio + test_ratio))), 
                                                            int(len(allFileNames)* (1 - test_ratio))])

    print('Total images: ', len(allFileNames))
    print('Training: ', len(train_FileNames))
    print('Validation: ', len(val_FileNames))
    print('Testing: ', len(test_FileNames))

    for name in train_FileNames:
        filename_prefix = name.split(".")[0]
        print(filename_prefix)
        shutil.copy('images\\' + name, root_dir + 'train')
        file_txt = filename_prefix + ".txt"
        print(file_txt)
        shutil.copy('data\\' + file_txt, root_dir + 'train')
    for name in val_FileNames:
        filename_prefix = name.split(".")[0]
        shutil.copy('images\\' + name, root_dir + 'val')
        file_txt = filename_prefix + ".txt"
        shutil.copy('data\\' + file_txt, root_dir + 'val')
    for name in test_FileNames:
        filename_prefix = name.split(".")[0]
        shutil.copy('images\\' + name, root_dir + 'test')
        file_txt = filename_prefix + ".txt"
        shutil.copy('data\\' + file_txt, root_dir + 'test')

################## convert bounding box ####################
def solve(x_center_scale, y_center_scale, width_scale, height_scale, height_image, width_image): 
    # x_center = x_center_scale * 2 * WIDTH
    # y_center = y_center_scale * 2 * HEIGHT
    width_bb = width_scale * width_image
    height_bb = height_scale * height_image
    x_left = (width_image / 2) * (2*x_center_scale - width_scale)
    # x_right = WIDTH * width_scale + x_left
    y_left = (height_image / 2) * (2*y_center_scale - height_scale)
    # y_right = HEIGHT * height_scale + y_left
    return [x_left, y_left, width_bb, height_bb]

def create_root(data):
    data["info"] = {"date_created": now.strftime("%d-%m-%Y %H:%M:%S"),
                    "create_by": "Long"}

    dict_licenses = {"id": 1,
                    "url": "",
                    "name": "Unknown"}

    data["licenses"].append(dict_licenses)

    with open("classes.txt", "r") as f:

        read = f.readlines()

        for j in range(len(read) + 1):
            if j == 0:
                categories = {
                        "id": j,
                        "name": "0",
                        "supercategory": "none"
                    }  
            else:
                read[j-1] = read[j-1].strip() # xoa khoang trang
                class_name = read[j-1]
                categories = {
                        "id": j,
                        "name": class_name,
                        "supercategory": supercategory
                    }   
            data["categories"].append(categories)


def read_file():
    for folder in create_dir:
        id_anno = 0
        num_image = 0
        data = {
                "info": {},
                "licenses": [],
                "categories": [],
                "images": [],
                "annotations": []
            }
        create_root(data)
        for (dirpath, dirnames, filenames) in os.walk(folder):          
            for filename in filenames:
                if filename.endswith('.txt'):
                    print(os.path.join(dirpath, filename))                
                    image_path_txt = os.path.join(dirpath, filename)
                    
                    ############################### IMAGES ###############################
                    
                    file = image_path_txt.split("\\")
                    file_prefix = file[1].split(".txt")[0]
                    try:
                        image_file_name = "{}.jpg".format(file_prefix)
                        img = Image.open("{}/{}".format("images", image_file_name))
                    except FileNotFoundError:
                        print("Error")
                        image_file_name = "{}.JPEG".format(file_prefix)
                        img = Image.open("{}/{}".format("images", image_file_name))                
                    WIDTH, HEIGHT = img.size

                    image_license = data["licenses"][0].get("id")
                    data_captured = now.strftime("%d-%m-%Y %H:%M:%S")
                    image_data = {
                            "id": num_image,
                            "license": image_license,
                            "file_name": image_file_name,
                            "height": WIDTH,
                            "width": HEIGHT,
                            "date_captured": data_captured
                            }
                    data["images"].append(image_data)
                    

                    ############################### ANNOTATIONS ###############################
                    with open(image_path_txt, "r") as f: # mo file txt
                        lines = f.readlines()
                        for line in lines:
                            
                            line = line.strip()
                            Data = line.split()
                            for i in range(len(CLASS_MAPPING_TEMP)):
                                if Data[0] == CLASS_MAPPING_TEMP[i]: #### Truong hop: 1 classes
                                    category_id = CLASS_MAPPING.get(CLASS_MAPPING_TEMP[i]) # string                             
                                    result = solve(float(Data[1]), float(Data[2]), float(Data[3]), float(Data[4]), height_image=416, width_image=416)
                                    
                                    for m in range(len(result)):
                                        result[m] = round(result[m], 1) ## lam tron 2 chu so
                                        result_temp = (str(result[m]).split("."))
                                        if result_temp[1] <= '2':
                                            result[m] = math.floor(result[m])
                                        elif (result_temp[1] > '2') and (result_temp[1] < '8'):
                                            result_temp[1] = '5'
                                            result[m] = float(result_temp[0] + '.' + result_temp[1])
                                        elif result_temp[1] >= '8':
                                            result[m] = math.ceil(result[m])

                                    area = result[2] * result[3]
                                    anno_data = {
                                        "id": id_anno,
                                        "image_id": num_image,
                                        "category_id": int(category_id),
                                        "bbox": result,
                                        "area": area,
                                        "segmentation": [],
                                        "iscrowd": 0
                                    }

                                    data["annotations"].append(anno_data)                           
                            id_anno += 1 ### tang id annotation
                    num_image += 1 # so luong anh    
                            
                else:
                    print("Skipping file: {}".format(filename))

        ########### save result ##############
        with open("_annotations_{}.coco.json".format(folder), "w") as fout:
            json.dump(data, fout, indent=4)
    
# ------------------------------ remove txt and move anno.json to folder(train, test, val) after finishing convert ----------------- ###
def remove_txt():
    for folder in create_dir:
        if folder == "images":
            continue
        shutil.copy("_annotations_{}.coco.json".format(folder), folder)
        os.remove("_annotations_{}.coco.json".format(folder))
        for (dirpath, dirfile, filenames) in os.walk(folder):
            for filename in filenames:
                if filename.endswith(".txt"):
                    print("Removing %s" % filename)
                    os.remove(os.path.join(dirpath, filename))
    print("Done removing")

def start():
    split_dataset()
    read_file()
    remove_txt()

if __name__ == "__main__":
    start()