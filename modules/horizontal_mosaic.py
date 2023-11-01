"""
Reference

This Mosaic class is a modification of 
https://github.com/ultralytics/ultralytics/blob/main/ultralytics/data/augment.py
"""

# Ultralytics YOLO 🚀, AGPL-3.0 license

import math
import random
from copy import deepcopy

import cv2
import numpy as np
import torch
import torchvision.transforms as T

from ultralytics.utils import LOGGER, colorstr
from ultralytics.utils.checks import check_version
from ultralytics.utils.instance import Instances
from ultralytics.utils.metrics import bbox_ioa
from ultralytics.utils.ops import segment2box

from .utils import polygons2masks, polygons2masks_overlap

POSE_FLIPLR_INDEX = [0, 2, 1, 4, 3, 6, 5, 8, 7, 10, 9, 12, 11, 14, 13, 16, 15]

class Mosaic(BaseMixTransform):
    """
    Mosaic augmentation.

    This class performs mosaic augmentation by combining multiple (4 or 9) images into a single mosaic image.
    The augmentation is applied to a dataset with a given probability.

    Attributes:
        dataset: The dataset on which the mosaic augmentation is applied.
        imgsz (int, optional): Image size (height and width) after mosaic pipeline of a single image. Default to 640.
        p (float, optional): Probability of applying the mosaic augmentation. Must be in the range 0-1. Default to 1.0.
        n (int, optional): The grid size, either 4 (for 2x2) or 9 (for 3x3).
    """

    def __init__(self, dataset, imgsz=640, p=1.0, n=3):
        """Initializes the object with a dataset, image size, probability, and border."""
        assert 0 <= p <= 1.0, f'The probability should be in range [0, 1], but got {p}.'
        assert n in (3, 4, 9), 'grid must be equal to 3, 4 or 9.'
        super().__init__(dataset=dataset, p=p)
        self.dataset = dataset
        self.imgsz = imgsz
        self.border = (-imgsz // 2, -imgsz // 2)  # width, height
        self.n = n

    def get_indexes(self, buffer=True):
        """Return a list of random indexes from the dataset."""
        if buffer:  # select images from buffer
            return random.choices(list(self.dataset.buffer), k=self.n - 1)
        else:  # select any images
            return [random.randint(0, len(self.dataset) - 1) for _ in range(self.n - 1)]

    def _mix_transform(self, labels):
        """Apply mixup transformation to the input image and labels."""
        assert labels.get('rect_shape', None) is None, 'rect and mosaic are mutually exclusive.'
        assert len(labels.get('mix_labels', [])), 'There are no other images for mosaic augment.'
        return self._mosaic3(labels) if self.n == 3 else self._mosaic4(labels) if self.n == 4 else self._mosaic9(labels)


    def _mosaic3(self, labels):
        """Create a 1x3 image mosaic."""
        mosaic_labels = []
        s = self.imgsz
        hp, wp = -1, -1  # height, width previous
        for i in range(3):
            labels_patch = labels if i == 0 else labels['mix_labels'][i - 1]
            # Load image
            img = labels_patch['img']
            h, w = labels_patch.pop('resized_shape')

            # Place img in img3
            if i == 0:  # center
                img3 = np.full((s * 3, s * 3, img.shape[2]), 114, dtype=np.uint8)  # base image with 3 tiles
                h0, w0 = h, w
                c = s, s, s + w, s + h  # xmin, ymin, xmax, ymax (base) coordinates
            elif i == 1:  # right
                c = s + w0, s, s + w0 + w, s + h
            elif i == 2:  # left
                c = s - w, s + h0 - h, s, s + h0

            padw, padh = c[:2]
            x1, y1, x2, y2 = (max(x, 0) for x in c)  # allocate coords


            img3[y1:y2, x1:x2] = img[y1 - padh:, x1 - padw:]  # img3[ymin:ymax, xmin:xmax]
            hp, wp = h, w  # height, width previous for next iteration

            # Labels assuming imgsz*2 mosaic size
            labels_patch = self._update_labels(labels_patch, padw + self.border[0], padh + self.border[1])
            mosaic_labels.append(labels_patch)
        final_labels = self._cat_labels(mosaic_labels)

        final_labels['img'] = img3[-self.border[0]:self.border[0], -self.border[1]:self.border[1]]
        return final_labels