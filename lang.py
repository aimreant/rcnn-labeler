#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Config for app
    Author: lujianyu
    Email:  iam@jianyujianyu.com
"""
from config import LANGUAGE


if LANGUAGE == 'ch':
    text_images_directory = '原图目录'
    text_label = '标签'
    text_label_name = '名称:'
    text_add_label = '创建'
    text_delete_label = '删除'
    text_operating = '操作'
    text_button_images_zoom_1 = '放大 +'
    text_button_images_zoom_2 = '缩小 -'
    text_scaling = '比例: 0%'
    text_scaling_prefix = '比例: '
    text_mode = '模式切换'
    text_view_mode = '观察模式'
    text_create_mode = '标记模式'
    text_delete_mode = '删除模式'
    text_rotate = '生成旋转副本'
    text_zoom = '生成缩放副本'
    text_impurity = '生成杂质副本'
    text_blur = '生成模糊副本'
    text_convert_jpg = '输出转换为JPG'
    text_generate_xml = '生成XML文件'
    text_generate_set = '生成训练集'
    text_add_label_error_title = '创建标签错误'
    text_delete_label_error_title = '删除标签错误'
    text_add_label_error_info = '请输入标签名。'
    text_delete_label_error_info = '请选择标签。'
    text_delete_confirm_title = '删除确认'
    text_delete_confirm_info = '要执行此删除操作吗?'
else:
    text_images_directory = 'Images directory'
    text_label = 'Labels'
    text_label_name = 'Name:'
    text_add_label = 'Add'
    text_delete_label = 'Delete'
    text_operating = 'Operating'
    text_button_images_zoom_1 = 'Zoom in +'
    text_button_images_zoom_2 = 'Zoom out -'
    text_scaling = 'Rate: 0%'
    text_scaling_prefix = 'Rate: '
    text_mode = 'Modes'
    text_view_mode = 'VIEW MODE'
    text_create_mode = 'CREATE MODE'
    text_delete_mode = 'DELETE MODE'
    text_rotate = 'Rotate copy'
    text_zoom = 'Zoom copy'
    text_impurity = 'Impurity copy'
    text_blur = 'Blur copy'
    text_convert_jpg = 'Convert jpg copy'
    text_generate_xml = 'Generate XML'
    text_generate_set = 'Generate set'
    text_add_label_error_title = 'Add label error'
    text_delete_label_error_title = 'Delete label error'
    text_add_label_error_info = 'Please write label name.'
    text_delete_label_error_info = 'No Selected label.'
    text_delete_confirm_title = 'Delete confirm'
    text_delete_confirm_info = 'Sure to delete?'