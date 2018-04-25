#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Config for app
    Author: lujianyu
    Email:  iam@jianyujianyu.com
"""

# Common config
ORIGIN_IMAGES_PATH = 'origin_images'
OUTPUT_IMAGES_PATH = 'output_images'
LABELS_PATH = 'labels'
XML_PATH = 'xmls'
FOLDER_NAME = 'VOC2007'
COLORS = ['red', 'blue', 'cyan', 'green', 'black']
SUPPORT_FORMAT = ['.jpg', '.jpeg', '.png', '.bmp']
WINDOW_SIZE = 900, 500
IMAGE_AREA_SIZE = 600, 350
PYDB = 'label_pydb'

# Mode config
VIEW_MODE = 0
CREATE_MODE = 1
DELETE_MODE = 2
MODE = [VIEW_MODE, CREATE_MODE, DELETE_MODE]

# Language config
LANGUAGE = 'ch'  # 'en', 'ch'

# Noise reduction config
NOISE_THRESHOLD = 50
AREA_DIFF_RANGE = [-1, 0, 1]
NOISE_REDUCTION_TIME = 1
