import os, sys, shutil, yaml

from glob import glob
from zipfile import ZipFile
from roboflow import Roboflow
from ultralytics import YOLO
import pandas as pd

import PIL, cv2
from PIL import Image
from IPython.display import Image, clear_output  # to display images
import matplotlib.pyplot as plt

# track video(mp4)
# Load an official or custom model
best_weights= '/Users/GitHub/Projects/AI_Project/yolov8-robot-cleaner/data/weights/mosaic4(best).pt' # pretrained model weight
track_mp4 = '/content/drive/MyDrive/Colab Notebooks/projects_bootcamp/robot_cleaner/MSW_twine_L_1_0.mp4' # target video to track


if __name__ == '__main__':

    # Perform tracking with the model
    model = YOLO(best_weights)  # Load a custom trained model
    results = model.track(source=track_mp4, save=True)  # Tracking with default tracker