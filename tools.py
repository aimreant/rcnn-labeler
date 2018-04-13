#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Providing tools
    Author: lujianyu
    Email:  iam@jianyujianyu.com
"""
from config import *
import os
import cv2
from itertools import islice
from xml.dom.minidom import Document
import glob
from PIL import Image


class XMLTools:

    def __init__(self):
        pass

    def insert_object(self, doc, label_data):
        obj = doc.createElement('object')
        name = doc.createElement('name')
        name.appendChild(doc.createTextNode(label_data[0]))
        obj.appendChild(name)
        pose = doc.createElement('pose')
        pose.appendChild(doc.createTextNode('Unspecified'))
        obj.appendChild(pose)
        truncated = doc.createElement('truncated')
        truncated.appendChild(doc.createTextNode(str(0)))
        obj.appendChild(truncated)
        difficult = doc.createElement('difficult')
        difficult.appendChild(doc.createTextNode(str(0)))
        obj.appendChild(difficult)
        bndbox = doc.createElement('bndbox')

        x_min = doc.createElement('xmin')
        x_min.appendChild(doc.createTextNode(str(label_data[1])))
        bndbox.appendChild(x_min)

        y_min = doc.createElement('ymin')
        y_min.appendChild(doc.createTextNode(str(label_data[2])))
        bndbox.appendChild(y_min)

        x_max = doc.createElement('xmax')
        x_max.appendChild(doc.createTextNode(str(label_data[3])))
        bndbox.appendChild(x_max)

        y_max = doc.createElement('ymax')
        if '\r' == str(label_data[4])[-1] or '\n' == str(label_data[4])[-1]:
            data = str(label_data[4])[0:-1]
        else:
            data = str(label_data[4])
        y_max.appendChild(doc.createTextNode(data))
        bndbox.appendChild(y_max)

        obj.appendChild(bndbox)
        return obj

    def create_xml(self):
        for walk in os.walk(LABELS_PATH):
            # walk = (dir path, dir names, file names)
            for file_name in walk[2]:
                file_in = open(os.path.join(walk[0], file_name), 'r')
                index = 0
                for data in islice(file_in, 1, None):
                    index += 1
                    data = data.strip('\n')
                    label_data = data.split(' ')
                    if 5 != len(label_data):
                        print('bounding box information error')
                        continue
                    image_name = ImageTools.get_image_name(file_name)
                    image_path = os.path.join(ORIGIN_IMAGES_PATH, image_name)
                    image = cv2.imread(image_path)
                    print(image_path)
                    image_size = image.shape
                    
                    if 1 == index:
                        xml_name = file_name.replace('.txt', '.xml')
                        f = open(os.path.join(XML_PATH, xml_name), "w")
                        doc = Document()
                        annotation = doc.createElement('annotation')
                        doc.appendChild(annotation)

                        folder = doc.createElement('folder')
                        folder.appendChild(doc.createTextNode(FOLDER_NAME))
                        annotation.appendChild(folder)

                        filename = doc.createElement('filename')
                        filename.appendChild(doc.createTextNode(image_name))
                        annotation.appendChild(filename)

                        source = doc.createElement('source')
                        database = doc.createElement('database')
                        database.appendChild(doc.createTextNode('My Database'))
                        source.appendChild(database)
                        source_annotation = doc.createElement('annotation')
                        source_annotation.appendChild(doc.createTextNode(FOLDER_NAME))
                        source.appendChild(source_annotation)
                        image = doc.createElement('image')
                        image.appendChild(doc.createTextNode('flickr'))
                        source.appendChild(image)
                        flickrid = doc.createElement('flickrid')
                        flickrid.appendChild(doc.createTextNode('NULL'))
                        source.appendChild(flickrid)
                        annotation.appendChild(source)

                        owner = doc.createElement('owner')
                        flickrid = doc.createElement('flickrid')
                        flickrid.appendChild(doc.createTextNode('NULL'))
                        owner.appendChild(flickrid)
                        name = doc.createElement('name')
                        name.appendChild(doc.createTextNode('idaneel'))
                        owner.appendChild(name)
                        annotation.appendChild(owner)

                        size = doc.createElement('size')
                        width = doc.createElement('width')
                        width.appendChild(doc.createTextNode(str(image_size[1])))
                        size.appendChild(width)
                        height = doc.createElement('height')
                        height.appendChild(doc.createTextNode(str(image_size[0])))
                        size.appendChild(height)
                        depth = doc.createElement('depth')
                        depth.appendChild(doc.createTextNode(str(image_size[2])))
                        size.appendChild(depth)
                        annotation.appendChild(size)

                        segmented = doc.createElement('segmented')
                        segmented.appendChild(doc.createTextNode(str(0)))
                        annotation.appendChild(segmented)
                        annotation.appendChild(self.insert_object(doc, label_data))
                    else:
                        annotation.appendChild(self.insert_object(doc, label_data))
                try:
                    f.write(doc.toprettyxml(indent='    '))
                    f.close()
                    file_in.close()
                except:
                    pass


class TrainTools:
    def __init__(self):
        pass

    def create_set(self):
        image_dir = os.path.join('.', ORIGIN_IMAGES_PATH)
        image_list = glob.glob(os.path.join(image_dir, '*.jpg'))  # maybe more formats
        image_set_dir = os.path.join('.', 'sets')
        MainDir = os.path.join(image_set_dir, 'Main')
        if len(image_list) != 0:
            if not os.path.exists(image_set_dir):
                os.mkdir(image_set_dir)
            if not os.path.exists(MainDir):
                os.mkdir(MainDir)
            f_test = open(os.path.join(MainDir, 'test.txt'), 'w')
            f_train = open(os.path.join(MainDir, 'train.txt'), 'w')
            f_val = open(os.path.join(MainDir, 'val.txt'), 'w')
            f_trainval = open(os.path.join(MainDir, 'trainval.txt'), 'w')
            i = 0
            j = 0
            len_split = len(image_list) / 2
            len_tv = len_split / 2
            for image in image_list:
                image_name = os.path.split(image)[-1].split('.')[0]
                if i < len_split:
                    f_test.write(image_name + '\n')
                    i += 1
                else:
                    if j < len_tv:
                        f_train.write(image_name + '\n')
                    else:
                        f_val.write(image_name + '\n')
                    f_trainval.write(image_name + '\n')
                    j += 1
                    # print imagename
            f_test.close()
            f_train.close()
            f_val.close()
            f_trainval.close()


class ImageTools:
    def __init__(self):
        pass

    @staticmethod
    def get_label_txt_name(image_file_name):
        names = image_file_name.split('.')
        names[-1] = 'txt'
        return '.'.join(names)

    @staticmethod
    def get_image_name(label_txt_name):
        names = label_txt_name.split('.')
        no_suffix_name = '.'.join(names[:-1])

        for sf in SUPPORT_FORMAT:
            try_name = no_suffix_name + sf
            image_path = os.path.join(ORIGIN_IMAGES_PATH, try_name)
            if os.path.exists(image_path):
                return try_name

        return ''

    @staticmethod
    def get_converted_jpg_image_name(not_jpg_image_name):
        names = not_jpg_image_name.split('.')
        names[-1] = 'jpg'
        return '.'.join(names)

    @staticmethod
    def convert_to_jpg_by_name(image_name):
        image_path = os.path.join(ORIGIN_IMAGES_PATH, image_name)
        if not os.path.exists(image_path):
            return
        image = Image.open(image_path)
        image = image.convert('RGB')
        new_image_name = ImageTools.get_converted_jpg_image_name(image_name)
        image.save(os.path.join(OUTPUT_IMAGES_PATH, new_image_name))

    @staticmethod
    def convert_to_jpg_by_path(image_path):
        if not os.path.exists(image_path):
            return
        image = Image.open(image_path)
        image_name = image_path.split('/')[-1]
        image = image.convert('RGB')
        new_image_name = ImageTools.get_converted_jpg_image_name(image_name)
        image.save(os.path.join(OUTPUT_IMAGES_PATH, new_image_name))

    @staticmethod
    def convert_all_images_to_jpg():
        origin_images_dir = os.path.join('.', ORIGIN_IMAGES_PATH)
        origin_images_list = []
        for sf in SUPPORT_FORMAT:
            origin_images_list += glob.glob(os.path.join(origin_images_dir, '*' + sf))

        for image_path in origin_images_list:
            ImageTools.convert_to_jpg_by_path(image_path)


if __name__ == '__main__':
    # train_tools = TrainTools()
    # train_tools.create_set()

    # testing converter
    # ImageTools.convert_to_jpg_by_name('png_format_test.png')
    # ImageTools.convert_to_jpg_by_name('bmp_format_test.bmp')

    ImageTools.convert_all_images_to_jpg()
