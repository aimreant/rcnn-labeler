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
from PIL import Image, ImageFilter
import random
import string
from pathos import multiprocessing
from pathos.multiprocessing import ProcessingPool as Pool
from functools import partial
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

    def remove_exist_xml(self):
        xml_dir = os.path.join('.', XML_PATH)
        xml_list = glob.glob(os.path.join(xml_dir, '*.xml'))

        for xml in xml_list:
            os.remove(xml)

    def remove_output_images(self):
        output_images_dir = os.path.join('.', OUTPUT_IMAGES_PATH)
        output_images_list = glob.glob(os.path.join(output_images_dir, '*.jpg'))

        for image in output_images_list:
            os.remove(image)

    def create_xml(self, origin):

        self.remove_exist_xml()
        # self.remove_output_images()

        if origin:
            images_path = ORIGIN_IMAGES_PATH
        else:
            images_path = OUTPUT_IMAGES_PATH
        for walk in os.walk(LABELS_PATH):
            # Here, walk = (dir path, dir names, file names)
            for file_name in walk[2]:
                # Here, file_name: *.txt
                file_in = open(os.path.join(walk[0], file_name), 'r')
                index = 0
                for data in islice(file_in, 1, None):
                    index += 1
                    data = data.strip('\n')
                    label_data = data.split(' ')
                    if 5 != len(label_data):
                        print('bounding box information error')
                        continue

                    if origin:
                        image_name = ImageTools.get_image_name(file_name)
                    else:
                        image_name = ImageTools.get_converted_jpg_image_name(file_name)
                    image_path = os.path.join(images_path, image_name)
                    if not os.path.exists(image_path):
                        continue

                    image = cv2.imread(image_path)
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

    def create_set(self, origin):
        if origin:
            images_path = ORIGIN_IMAGES_PATH
        else:
            images_path = OUTPUT_IMAGES_PATH

        image_dir = os.path.join('.', images_path)
        image_list = []
        for sf in SUPPORT_FORMAT:
            image_list += glob.glob(os.path.join(image_dir, '*' + sf))
        image_set_dir = os.path.join('.', 'sets')
        main_dir = os.path.join(image_set_dir, 'Main')
        if len(image_list) != 0:
            if not os.path.exists(image_set_dir):
                os.mkdir(image_set_dir)
            if not os.path.exists(main_dir):
                os.mkdir(main_dir)
            f_test = open(os.path.join(main_dir, 'test.txt'), 'w')
            f_train = open(os.path.join(main_dir, 'train.txt'), 'w')
            f_val = open(os.path.join(main_dir, 'val.txt'), 'w')
            f_trainval = open(os.path.join(main_dir, 'trainval.txt'), 'w')
            i = 0
            j = 0
            len_split = len(image_list) / 2
            len_tv = len_split / 2
            for image in image_list:
                image_name = os.path.split(image)[-1].split('.')[0]
                if not ImageTools.image_has_label(image_name + '.jpg'):
                    continue
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
        name_without_suffix = '.'.join(names[:-1])

        for sf in SUPPORT_FORMAT:
            try_name = name_without_suffix + sf
            image_path = os.path.join(ORIGIN_IMAGES_PATH, try_name)
            if os.path.exists(image_path):
                return try_name

        return ''

    @staticmethod
    def get_name_without_suffix(name_with_suffix):
        names = name_with_suffix.split('.')
        return '.'.join(names[:-1])

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
        if ImageTools.image_has_label(image_name):
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

    @staticmethod
    def generate_random_name(origin_name):
        random_string = ''.join(random.choice(string.ascii_lowercase) for x in range(10))
        names = origin_name.split('.')
        names[-2] = names[-2] + '_' + random_string
        return '.'.join(names)

    @staticmethod
    def save_one_label(image_name, labeled_list):
        file_name = ImageTools.get_label_txt_name(image_name)
        origin_labels_dir = os.path.join('.', LABELS_PATH)
        label_file_path = os.path.join(origin_labels_dir, file_name)
        with open(label_file_path, 'w') as f:
            f.write('%d\n' % len(labeled_list))
            for label in labeled_list:
                f.write(' '.join(map(str, label[0:5])) + '\n')

    @staticmethod
    def load_one_label(image_name):
        file_name = ImageTools.get_label_txt_name(image_name)
        origin_labels_dir = os.path.join('.', LABELS_PATH)
        label_file_path = os.path.join(origin_labels_dir, file_name)

        label_list = []
        if os.path.exists(label_file_path):
            with open(label_file_path) as f:
                # index = 0
                for (i, line) in enumerate(f):
                    if i == 0:
                        int(line.strip())
                        continue
                    tmp = [t for t in line.split()]

                    tmp[1], tmp[2], tmp[3], tmp[4] = \
                        int(tmp[1]), int(tmp[2]), int(tmp[3]), int(tmp[4])

                    label_list.append(tmp)

        return label_list

    @staticmethod
    def calculate_labels(label_list):
        """
        Get min(x,y) and max(x,y) from label_list
        :param label_list:
        :return: (x_min, y_min, x_max, y_max)
        """
        if len(label_list) == 0:
            return 0, 0, 0, 0
        x_min, y_min, x_max, y_max = label_list[0][1], label_list[0][2], label_list[0][3], label_list[0][4]
        for label in label_list:
            if label[1] < x_min:
                x_min = label[1]
            if label[2] < y_min:
                y_min = label[2]
            if label[3] > x_max:
                x_max = label[3]
            if label[4] > y_max:
                y_max = label[4]

        return x_min, y_min, x_max, y_max

    @staticmethod
    def generate_copy_for_one_img(image_path, options_dict):
        def save(_image, _labels_list, _image_name):
            _image_name = ImageTools.get_converted_jpg_image_name(_image_name)
            new_image_name = ImageTools.generate_random_name(_image_name)
            ImageTools.save_one_label(new_image_name, _labels_list)
            image.save(os.path.join(OUTPUT_IMAGES_PATH, new_image_name))

        image = Image.open(image_path)
        origin_image = image.convert("RGB")
        image = origin_image
        image_name = image_path.split('/')[-1]
        labels_list = ImageTools.load_one_label(image_name)
        origin_labels_list = labels_list
        if 'generate_one' in options_dict and options_dict['generate_one'] == 1:
            if 'zoom' in options_dict and options_dict['zoom'] == 1:
                image, labels_list = ImageTools.generate_zoom_copy(image, labels_list)
            if 'rotate_1' in options_dict and options_dict['rotate_1'] == 1:
                image, labels_list = ImageTools.generate_rotate_copy(image, labels_list, 270)
            if 'rotate_2' in options_dict and options_dict['rotate_2'] == 1:
                image, labels_list = ImageTools.generate_rotate_copy(image, labels_list, 180)
            if 'blur' in options_dict and options_dict['blur'] == 1:
                image, labels_list = ImageTools.generate_blur_copy(image, labels_list)
            if 'impurity' in options_dict and options_dict['impurity'] == 1:
                image, labels_list = ImageTools.generate_impurity_copy(image, labels_list)
            if 'edge_enhance' in options_dict and options_dict['edge_enhance'] == 1:
                image, labels_list = ImageTools.generate_edge_enhance_copy(image, labels_list)
            if 'noise_reduction' in options_dict and options_dict['noise_reduction'] == 1:
                image, labels_list = ImageTools.generate_noise_reduction_copy(image, labels_list)
            save(image, labels_list, image_name)
        else:
            if 'zoom' in options_dict and options_dict['zoom'] == 1:
                image, labels_list = ImageTools.generate_zoom_copy(origin_image, origin_labels_list)
                save(image, labels_list, image_name)
            if 'rotate_1' in options_dict and options_dict['rotate_1'] == 1:
                image, labels_list = ImageTools.generate_rotate_copy(origin_image, origin_labels_list, 270)
                save(image, labels_list, image_name)
            if 'rotate_2' in options_dict and options_dict['rotate_2'] == 1:
                image, labels_list = ImageTools.generate_rotate_copy(origin_image, origin_labels_list, 180)
                save(image, labels_list, image_name)
            if 'blur' in options_dict and options_dict['blur'] == 1:
                image, labels_list = ImageTools.generate_blur_copy(origin_image, origin_labels_list)
                save(image, labels_list, image_name)
            if 'impurity' in options_dict and options_dict['impurity'] == 1:
                image, labels_list = ImageTools.generate_impurity_copy(origin_image, origin_labels_list)
                save(image, labels_list, image_name)
            if 'edge_enhance' in options_dict and options_dict['edge_enhance'] == 1:
                image, labels_list = ImageTools.generate_edge_enhance_copy(origin_image, origin_labels_list)
                save(image, labels_list, image_name)
            if 'noise_reduction' in options_dict and options_dict['noise_reduction'] == 1:
                image, labels_list = ImageTools.generate_noise_reduction_copy(origin_image, origin_labels_list)
                save(image, labels_list, image_name)

    @staticmethod
    def generate_copy(images_list, options_dict):
        pool = Pool(multiprocessing.cpu_count())
        generate_work = partial(ImageTools.generate_copy_for_one_img, options_dict=options_dict)
        pool.map(generate_work, images_list)

    @staticmethod
    def generate_zoom_copy(image, labels_list):
        width, height = image.size
        x_min, y_min, x_max, y_max = ImageTools.calculate_labels(labels_list)
        x1 = random.randint(0, x_min - 1)
        y1 = random.randint(0, y_min - 1)
        x2 = random.randint(x_max, width - 1)
        y2 = random.randint(y_max, height - 1)
        image = image.crop((x1, y1, x2, y2))

        for label in labels_list:
            label[1] = label[1] - x1
            label[2] = label[2] - y1
            label[3] = label[3] - x1
            label[4] = label[4] - y1

        # TODO only cut, need zoom

        return image, labels_list

    @staticmethod
    def generate_rotate_copy(image, labels_list, rotate_type):
        if rotate_type == 270 or rotate_type == 90:
            image = image.rotate(270, expand=True)
            width, height = image.size
            new_labels_list = []

            for label in labels_list:
                tmp = label[0], width - label[4], label[1], width - label[2], label[3]
                new_labels_list.append(tmp)

            return image, new_labels_list
        elif rotate_type == 180:
            image = image.rotate(180, expand=True)
            width, height = image.size
            new_labels_list = []

            for label in labels_list:
                tmp = label[0], width - label[3], height - label[4], width - label[1], height - label[2]
                new_labels_list.append(tmp)

            return image, new_labels_list
        else:
            return image, labels_list

    @staticmethod
    def generate_blur_copy(image, labels_list):
        image = image.filter(ImageFilter.BLUR).filter(ImageFilter.GaussianBlur)
        return image, labels_list

    @staticmethod
    def generate_impurity_copy(image, labels_list):
        width, height = image.size
        pixel_time = width * height / 8
        for i in xrange(pixel_time):
            position = (random.randint(0, width - 1), random.randint(0, height - 1))
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            image.putpixel(position, color)
        return image, labels_list

    @staticmethod
    def generate_edge_enhance_copy(image, labels_list):
        image = image.filter(ImageFilter.EDGE_ENHANCE_MORE).filter(ImageFilter.EDGE_ENHANCE_MORE)
        return image, labels_list

    @staticmethod
    def is_noise(img, x, y):
        """
        For RGB
        Judge whether the pixel(x, y) is noise
        """
        def get_distance(p1, p2):
            if len(p1) != 3 and len(p2) != 3:
                return 0
            return int(((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2 + (p1[2] - p2[2]) ** 2) ** 0.5)

        diff_pixel = 0
        distance_list = []
        for y_diff in AREA_DIFF_RANGE:
            for x_diff in AREA_DIFF_RANGE:
                current_distance = get_distance(img.getpixel((x, y)), img.getpixel((x + x_diff, y + y_diff)))
                distance_list.append((x + x_diff, y + y_diff, current_distance))
                if current_distance > NOISE_THRESHOLD:
                    diff_pixel += 1

        if diff_pixel > 4:
            distance_list = sorted(distance_list, key=lambda d: d[2])
            aim_point = distance_list[4]
            return True, img.getpixel((aim_point[0], aim_point[1]))
        else:
            return False, (0, 0, 0)

    @staticmethod
    def generate_noise_reduction_copy(image, labels_list):
        x_min, y_min, x_max, y_max = ImageTools.calculate_labels(labels_list)

        for t in xrange(0, NOISE_REDUCTION_TIME):
            for x in xrange(x_min, x_max):
                for y in xrange(y_min, y_max):
                    noise_res = ImageTools.is_noise(image, x, y)
                    if noise_res[0]:
                        image.putpixel((x, y), noise_res[1])

        image = image.filter(ImageFilter.MedianFilter(3)).filter(ImageFilter.SHARPEN)

        return image, labels_list

    @staticmethod
    def image_has_label(image_name):
        file_name = ImageTools.get_label_txt_name(image_name)
        label_file_path = os.path.join(os.path.join('.', LABELS_PATH), file_name)

        if not os.path.exists(label_file_path):
            return False

        if os.path.getsize(label_file_path) == 0:
            return False

        if int(open(label_file_path, "r").readline().strip()) == 0:
            return False

        return True

