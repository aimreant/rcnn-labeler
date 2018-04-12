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
from app import LabelTool


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
                    image_name = LabelTool.get_image_name(file_name)
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
        pass


class ImageTools:
    def __init__(self):
        pass

    def convert_to_jpg(self):
        pass

if __name__ == '__main__':
    pass
