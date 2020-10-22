################### ANNOTATIONS YOLO #######################
#### CLASS_ID, X_center/widht, Y_center/HEIGHT, WIDTH_LABEL, HEIGHT_LABEL

import os
import math
import json
import datetime
from PIL import Image

ANNOTATIONS_DIR_PREFIX = "data"

supercategory = "drone" # Name of classes what do you want to save

WIDTH = 0 #### chieu rong cua image
HEIGHT = 0 #### chieu cao cua image

CLASS_MAPPING_TEMP = ['0', '1']
CLASS_MAPPING = {
    '0': '1', #### 1 : class_name dau`
    '1': '2' #### 2: class_name 2nd
    # Add your remaining classes here.
}
data = {
            "info": {},
            "licenses": [],
            "categories": [],
            "images": [],
            "annotations": []
        }

now = datetime.datetime.now() # ngay gio  hien tai

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

def create_root():
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
    num_image = 0
    id_anno = 0
    for (dirpath, dirnames, filenames) in os.walk(ANNOTATIONS_DIR_PREFIX):
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
    with open("_annotations.coco.json", "w") as fout:
        json.dump(data, fout, indent=4)
    

def start():
    create_root()
    read_file()


if __name__ == "__main__":
    start()
    

