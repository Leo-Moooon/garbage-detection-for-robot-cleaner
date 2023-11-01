import os, sys, shutil, yaml

from tqdm import tqdm
from glob import glob
from zipfile import ZipFile
from roboflow import Roboflow
from ultralytics import YOLO
import pandas as pd

import PIL, cv2
from PIL import Image
from IPython.display import Image, clear_output  # to display images
import matplotlib.pyplot as plt

project_dir = '/Users/GitHub/Projects/AI_Project/yolov8-robot-cleaner'

img_pred_dir = os.path.join(project_dir, '/predict/mosaic3/')
if not os.path.exists(img_pred_dir): os.mkdir(img_pred_dir)


os.chdir(img_pred_dir)

# weights
mosaic3_weight = os.path.join(project_dir, '/data/weights/mosaic3(best).pt')

# img list
valid_img_list = glob(f'{project_dir}/data/dataset4/valid/images/*.jpg')
img_pred_dir = os.path.join(project_dir, '/predict/mosaic3/')

os.chdir(img_pred_dir)


if __name__ == '__main__':
    model = YOLO(mosaic3_weight)

    for idx, img in tqdm(enumerate(valid_img_list)):
        results = model.predict(img, save=True)