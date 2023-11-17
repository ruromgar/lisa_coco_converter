import pandas as pd
import argparse
import json
import os
import re

parser = argparse.ArgumentParser()
parser.add_argument('folder_path', type=str, help='Dataset main folder RELATIVE path')
args = parser.parse_args()
DATASET_PATH = args.folder_path


def get_segmentation(upper_left_x, upper_left_y, lower_right_x, lower_right_y):
    # Vertices are: 
    # Upper left  -> both x y given
    # Upper right -> x is the same as lower right; y is the same as upper left
    # Lower left  -> x is the same as upper left;  y is the same as lower right
    # Lower right -> both x y given
    # Coordinates are counted from the upper left corner of the pic

    return [[
        upper_left_x, upper_left_y,
        lower_right_x, upper_left_y,
        upper_left_x, lower_right_y,
        lower_right_x, lower_right_y
    ]]


def get_area(upper_left_x, upper_left_y, lower_right_x, lower_right_y):
    # Area is width * height
    # Width is lower_right_x - upper_left_x (right X - left X)
    # Height is upper_left_y - lower_right_y (upper Y - lower Y)
    # Height is negative because of the coordinates!

    return (lower_right_x - upper_left_x)*(-(upper_left_y - lower_right_y))


def get_bbox(upper_left_x, upper_left_y, lower_right_x, lower_right_y):
    # The COCO bounding box format is [top left x position, top left y position, width, height]
    # Top left x position is upper_left_x
    # Top left y position is upper_left_y
    # Width is lower_right_x - upper_left_x (right X - left X)
    # Height is upper_left_y - lower_right_y (upper Y - lower Y)
    # Height is negative because of the coordinates!

    return [upper_left_x, upper_left_y, (lower_right_x - upper_left_x), (-(upper_left_y - lower_right_y))] 


def get_info():
    return {
        "description": "LISA Traffic Sign Dataset",
        "url": "http://cvrr.ucsd.edu/LISA/lisa-traffic-sign-dataset.html",
        "version": "2.0",
        "year": 2018
    }


def get_licenses():
    return [
        {
            "url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
            "id": 1,
            "name": "CC BY-NC-SA 4.0"
        }
    ]


def get_images(training=True):
    # Getting dataset root path
    dir_path = os.path.dirname(os.path.realpath(__file__))
    lisa_path = os.path.join(dir_path, DATASET_PATH)

    if training:
        folder = os.path.join(lisa_path, 'train2017')
    else:
        folder = os.path.join(lisa_path, 'val2017')

    images = []
    id = 0
    for f in os.listdir(folder):
        if f.endswith('.jpg'):
            images.append(
            {
                "license": 1,
                "file_name": f,
                "height": 960,
                "width": 1280,
                "id": id
            })
            id += 1

    return images


def get_categories(training=True):
    # Getting dataset root path
    dir_path = os.path.dirname(os.path.realpath(__file__))
    lisa_path = os.path.join(dir_path, DATASET_PATH)

    if training:
        df = pd.read_csv(os.path.join(lisa_path, 'training_data.csv'), 
            index_col=False)
    else:
        df = pd.read_csv(os.path.join(lisa_path, 'test_data.csv'), 
            index_col=False)
 
    tags = sorted(df['Annotation tag'].unique().tolist())
    print('Tags len is: ' + str(len(tags)))

    categories = []
    for i, t in enumerate(tags, 1):
        categories.append(
            {"supercategory": "", "id": i, "name": t}
        )
    
    return categories


def get_annotations(images, categories, training=True):
    # Getting dataset root path
    dir_path = os.path.dirname(os.path.realpath(__file__))
    lisa_path = os.path.join(dir_path, DATASET_PATH)

    if training:
        df = pd.read_csv(os.path.join(lisa_path, 'training_data.csv'), 
            index_col=False)
    else:
        df = pd.read_csv(os.path.join(lisa_path, 'test_data.csv'), 
            index_col=False)

    # Converting the dataframe into a list of lists
    data = df.values.tolist()

    # Each element in data is a 11-element list with the following fields:
    # 0. Filename
    # 1. Annotation tag
    # 2. Upper left corner X
    # 3. Upper left corner Y
    # 4. Lower right corner X 
    # 5. Lower right corner Y
    # 6. Origin file
    # 7. Origin frame number
    # 8. Origin track
    # 9. Origin track frame number

    annotations = []
    total = len(data)
    for i, d in enumerate(data, 1):

        # Getting image ID from images based on filename (d[0])
        # Since filename has the format dayTrain/dayClip1--00347.jpg we need to strip from the slash
        filename = d[0].rsplit('/')[1]
        image_id = [i["id"] for i in images if i["file_name"].endswith(filename)][0]

        # Getting category ID from categories based on name (d[1])
        category_id = [c["id"] for c in categories if c["name"] == d[1]][0]

        segmentation = get_segmentation(d[2], d[3], d[4], d[5])
        area         = get_area(d[2], d[3], d[4], d[5])
        bbox         = get_bbox(d[2], d[3], d[4], d[5])

        annotations.append({
            "segmentation": segmentation, 
            "area": area,
            "iscrowd": 0,
            "image_id": image_id,
            "bbox": bbox,
            "category_id": category_id,
            "id": i 
        })
        print(f'Processed {i} of {total}')
    return annotations


def main():
    info = get_info()
    licenses = get_licenses()

    training_images = get_images(training=True)
    test_images     = get_images(training=False)

    training_categories = get_categories(training=True)
    test_categories     = get_categories(training=False)

    training_annotations = get_annotations(training_images, 
        training_categories, training=True)
    test_annotations     = get_annotations(test_images, 
        test_categories, training=False)

    training_data = {
        "info": info,
        "licenses": licenses,
        "images": training_images,
        "annotations": training_annotations,
        "categories": training_categories
    }

    test_data = {
        "info": info,
        "licenses": licenses,
        "images": test_images,
        "annotations": test_annotations,
        "categories": test_categories
    }

    with open('instances_train2017.json', 'w', encoding='utf-8') as f:
        json.dump(training_data, f, ensure_ascii=False, indent=4)
    with open('instances_val2017.json', 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=4)

main()