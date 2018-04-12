#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
Label makers for RCNN
    Author: lujianyu
    Email:  iam@jianyujianyu.com
"""
import pickle
from Tkinter import *
from PIL import Image, ImageTk
import os
import glob
from tkMessageBox import *
from config import *
from lang import *


class LabelTool:
    def __init__(self, master):
        # Object parameters
        self.labels = StringVar()
        self.images = StringVar()
        self.file_icon = None
        self.origin_images_dir = None
        self.origin_labels_dir = None
        self.origin_images_list = None
        self.cur_box_color_map = {}
        self.labels_dir = None
        self.cur = None
        self.total_images_size = None
        self.cur_image_size = None
        self.cur_image_origin = None
        self.box_total_index = 0  # for color
        self.cur_mode = MODE[0]

        # Set main parameters -----------------------------------------------
        self.parent = master
        self.parent.title('RCNN-LABELER')
        self.parent.geometry(str(WINDOW_SIZE[0]) + 'x' + str(WINDOW_SIZE[1]))
        self.parent.resizable(width=False, height=False)

        # Build frames ------------------------------------------------------
        self.frame = Frame(self.parent)
        self.frame.pack(fill=BOTH, expand=1)
        self.frame_file_list = Frame(self.frame)
        self.frame_file_list.place(x=0, y=0, width=200, height=300)
        self.frame_label_list = Frame(self.frame)
        self.frame_label_list.place(x=0, y=300, width=200, height=200)
        self.frame_label_button = Frame(self.frame)
        self.frame_label_button.place(x=0, y=455, width=180, height=45)
        self.frame_image_area = Frame(self.frame)
        self.frame_image_area.place(x=200, y=0, width=IMAGE_AREA_SIZE[0], height=IMAGE_AREA_SIZE[1])
        self.frame_console = Frame(self.frame, bg="red")
        self.frame_console.place(x=200, y=IMAGE_AREA_SIZE[1],
                                 width=IMAGE_AREA_SIZE[0], height=WINDOW_SIZE[1] - IMAGE_AREA_SIZE[1])
        self.frame_mode = Frame(self.frame)
        self.frame_mode.place(x=800, y=0, width=100, height=500)

        # Build file list ---------------------------------------------------
        self.file_list_label = Label(self.frame_file_list, text=text_images_directory, bg='gray', anchor='w')
        self.file_list_label.place(x=0, y=0, width=200, height=20)

        self.file_list = Listbox(self.frame_file_list, selectmode=BROWSE, borderwidth=0, listvariable=self.images)
        self.file_list.place(x=0, y=20, width=200, height=280)

        self.file_list.bind('<ButtonRelease-1>', self.select_image)
        self.scrollbar_file_list = Scrollbar(self.frame_file_list)
        self.scrollbar_file_list.pack(side=RIGHT, fill=Y)
        self.file_list.configure(yscrollcommand=self.scrollbar_file_list.set)
        self.scrollbar_file_list['command'] = self.file_list.yview

        # Build label list ---------------------------------------------------
        self.label_list_label = Label(self.frame_label_list, text=text_label, bg='gray', anchor='w')
        self.label_list_label.place(x=0, y=0, width=200, height=20)

        self.label_list = Listbox(self.frame_label_list, selectmode=BROWSE, borderwidth=0, listvariable=self.labels)
        self.label_list.place(x=0, y=20, width=200, height=135)

        self.label_list.bind('<ButtonRelease-1>', self.select_label)
        self.scrollbar_label_list = Scrollbar(self.frame_label_list)
        self.scrollbar_label_list.pack(side=RIGHT, fill=Y)
        self.label_list.configure(yscrollcommand=self.scrollbar_label_list.set)
        self.scrollbar_label_list['command'] = self.label_list.yview

        # Build label buttons
        self.label_name_label = Label(self.frame_label_button, text=text_label_name, anchor='w')
        self.label_name_label.place(x=0, y=0, width=65, height=20)
        self.label_name = Entry(self.frame_label_button)
        self.label_name.place(x=65, y=0, width=115, height=20)

        self.add_label_bottom = Button(self.frame_label_button, command=self.add_label, text=text_add_label)
        self.add_label_bottom.place(x=0, y=20, width=90, height=23)
        self.delete_label_bottom = Button(self.frame_label_button, command=self.delete_label, text=text_delete_label)
        self.delete_label_bottom.place(x=90, y=20, width=90, height=23)

        # Build canvas area --------------------------------------------------
        self.image_area = Canvas(self.frame_image_area, cursor='arrow',
                                 width=IMAGE_AREA_SIZE[0], height=IMAGE_AREA_SIZE[1],
                                 scrollregion=(0, 0, IMAGE_AREA_SIZE[0], IMAGE_AREA_SIZE[1]))
        self.image_area.place(width=IMAGE_AREA_SIZE[0], height=IMAGE_AREA_SIZE[1])

        self.scrollbar_y_image_area = Scrollbar(self.frame_image_area, orient=VERTICAL)
        self.scrollbar_y_image_area.pack(side=RIGHT, fill=Y)
        self.scrollbar_y_image_area.config(command=self.image_area.yview)
        self.scrollbar_x_image_area = Scrollbar(self.frame_image_area, orient=HORIZONTAL)
        self.scrollbar_x_image_area.pack(side=BOTTOM, fill=X)
        self.scrollbar_x_image_area.config(command=self.image_area.xview)
        self.image_area.config(width=IMAGE_AREA_SIZE[0], height=IMAGE_AREA_SIZE[1])
        self.image_area.config(xscrollcommand=self.scrollbar_x_image_area.set,
                               yscrollcommand=self.scrollbar_y_image_area.set)

        # TODO bind mousewheel to scrollbar on canvas
        # self.image_area.bind_all("<MouseWheel>", self._on_mousewheel)
        self.image_area.bind("<Button-1>", self.canvas_on_mouse_click)
        self.image_area.bind("<Motion>", self.canvas_on_mouse_move)

        # Build operating area -----------------------------------------------------
        self.operating_label = Label(self.frame_mode, text=text_operating, bg='gray', anchor='w')
        self.operating_label.place(x=0, y=0, width=100, height=20)

        self.button_images_zoom_1 = Button(self.frame_mode, text=text_button_images_zoom_1, command=self.zoom_in_image)
        self.button_images_zoom_1.place(x=0, y=20, width=100, height=23)
        self.button_images_zoom_2 = Button(self.frame_mode, text=text_button_images_zoom_2, command=self.zoom_out_image)
        self.button_images_zoom_2.place(x=0, y=45, width=100, height=23)
        self.label_cur_scaling = Label(self.frame_mode, text=text_scaling, anchor='w')
        self.label_cur_scaling.place(x=10, y=70, width=80, height=20)
        self.label_cur_cursor_1 = Label(self.frame_mode, text='x : 0', anchor='w')
        self.label_cur_cursor_1.place(x=20, y=95, width=60, height=20)
        self.label_cur_cursor_2 = Label(self.frame_mode, text='y : 0', anchor='w')
        self.label_cur_cursor_2.place(x=20, y=115, width=60, height=20)
        # self.label_tmp = Label(self.frame_mode, text='')
        # self.label_tmp.place(x=0, y=0, width=100, height=20)

        # Build mode frame -----------------------------------------------------
        self.mode_switch_label = Label(self.frame_mode, text=text_mode, bg='gray', anchor='w')
        self.mode_switch_label.place(x=0, y=140, width=100, height=20)

        self.button_view_mode = Button(self.frame_mode, text=text_view_mode, bitmap='hourglass',
                                       command=self.switch_view_mode)
        self.button_view_mode.place(x=10, y=170, width=80, height=80)
        self.label_view_mode = Label(self.frame_mode, text=text_view_mode)
        self.label_view_mode.place(x=0, y=250, width=100, height=20)

        self.button_create_mode = Button(self.frame_mode, text=text_create_mode, bitmap='info',
                                         command=self.switch_create_mode)
        self.button_create_mode.place(x=10, y=280, width=80, height=80)
        self.label_create_mode = Label(self.frame_mode, text=text_create_mode)
        self.label_create_mode.place(x=0, y=360, width=100, height=20)

        self.button_delete_mode = Button(self.frame_mode, text=text_delete_mode, bitmap='error',
                                         command=self.switch_delete_mode)
        self.button_delete_mode.place(x=10, y=390, width=80, height=80)
        self.label_delete_mode = Label(self.frame_mode, text=text_delete_mode)
        self.label_delete_mode.place(x=0, y=470, width=100, height=20)

        # Build checkbox -----------------------------------------------------
        self.check_var_rotate = IntVar()
        self.check_rotate = Checkbutton(self.frame_console, text=text_rotate, variable=self.check_var_rotate)
        self.check_rotate.deselect()
        self.check_rotate.grid(row=0, column=0, sticky=W)

        self.check_var_zoom = IntVar()
        self.check_zoom = Checkbutton(self.frame_console, text=text_zoom, variable=self.check_var_zoom)
        self.check_zoom.deselect()
        self.check_zoom.grid(row=1, column=0, sticky=W)

        self.check_var_impurity = IntVar()
        self.check_impurity = Checkbutton(self.frame_console, text=text_impurity, variable=self.check_var_impurity)
        self.check_impurity.deselect()
        self.check_impurity.grid(row=2, column=0, sticky=W)

        self.check_var_blur = IntVar()
        self.check_blur = Checkbutton(self.frame_console, text=text_blur, variable=self.check_var_blur)
        self.check_blur.deselect()
        self.check_blur.grid(row=3, column=0, sticky=W)

        self.check_var_convert_jpg = IntVar()
        self.check_convert_jpg = Checkbutton(self.frame_console, text=text_convert_jpg,
                                             variable=self.check_var_convert_jpg)
        self.check_convert_jpg.deselect()
        self.check_convert_jpg.grid(row=4, column=0, sticky=W)

        self.generate_xml_label_bottom = Button(self.frame_console, text=text_generate_xml)
        self.generate_xml_label_bottom.grid(row=0, column=1, rowspan=2)
        self.generate_set_label_bottom = Button(self.frame_console, text=text_generate_set)
        self.generate_set_label_bottom.grid(row=1, column=1, rowspan=2)

        # Initial mouse and others in canvas
        self.mouse_state = {
            'click': False,
            'x': 0,
            'y': 0
        }

        self.labeled_list = []
        self.labeled_list_origin = []
        self.cur_label = {
            'name': 'nolabel',
            'index': 0
        }
        self.x_line = None
        self.y_line = None
        self.cross_line_1 = None
        self.cross_line_2 = None
        self.box_id_list = []
        self.box_text_list = {}
        self.box_id = None

        self.cur_image = None
        self.tk_image = None

        self.cur_scaling = 0.0
        self.cur_file_name = ''

        try:
            self.load_labels_from_pydb()
        except EOFError:
            pass

        # Initial operation
        self.load_images()
        self.switch_view_mode()

    def load_images(self):
        self.parent.focus()

        # Get image list
        self.origin_images_dir = os.path.join('.', ORIGIN_IMAGES_PATH)
        self.origin_labels_dir = os.path.join('.', LABELS_PATH)
        self.origin_images_list = []
        for sf in SUPPORT_FORMAT:
            self.origin_images_list += glob.glob(os.path.join(self.origin_images_dir, '*' + sf))

        if len(self.origin_images_list) == 0:
            showerror(text_no_images_title, text_no_images_info)

        # Set label dir
        self.labels_dir = os.path.join('.', 'labels')  # label输出路径
        if not os.path.exists(self.labels_dir):
            os.mkdir(self.labels_dir)

        self.cur = 0
        self.total_images_size = len(self.origin_images_list)
        for image in self.origin_images_list:
            file_name = image.split('/')[-1]
            self.insert_to_file_list(file_name)

    def insert_to_file_list(self, file_name, handled=False):
        if handled:
            file_name_in_list_str = ' [v] ' + file_name
        else:
            file_name_in_list_str = ' [x] ' + file_name
        self.file_list.insert(END, file_name_in_list_str)

    def mark_file(self, index, handled=True):
        file_name = self.file_list.get(index)[5:]
        if handled:
            file_name_in_list_str = ' [v] ' + file_name
        else:
            file_name_in_list_str = ' [x] ' + file_name
        self.file_list.delete(index)
        self.file_list.insert(index, file_name_in_list_str)
        self.file_list.selection_set(index)

    def mark_label(self, index, handled=True, selection_set=True):
        label_name = self.label_list.get(index)[5:]
        if handled:
            label_name_in_list_str = ' [v] ' + label_name
        else:
            label_name_in_list_str = ' [x] ' + label_name
        self.label_list.delete(index)
        self.label_list.insert(index, label_name_in_list_str)
        if selection_set:
            self.label_list.selection_set(index)

    def mark_label_by_name(self, label_name):
        for i in range(0, self.label_list.size()):
            label_mark = self.label_list.get(i)[:5]
            label = self.label_list.get(i)[5:]
            if label_name == label and label_mark == ' [x] ':
                label_name_in_list_str = ' [v] ' + label_name

                self.label_list.delete(i)
                self.label_list.insert(i, label_name_in_list_str)
                break

    def flush_labels(self):
        for i in range(0, self.label_list.size()):
            self.mark_label(i, False, False)

    def flush_box(self):
        self.box_total_index = 0
        self.box_id_list = []
        self.box_text_list = {}
        # self.cur_box_color_map = {}

    def select_image(self, event):
        self.image_area.delete("all")

        file_list_cur_selection = self.file_list.curselection()
        if not file_list_cur_selection:
            showerror(text_loading_error_title, text_loading_error_info)
            file_list_cur_selection = 1
        file_name_with_mark = self.file_list.get(file_list_cur_selection)
        self.cur_file_name = file_name_with_mark[5:]
        file_path = os.path.join(self.origin_images_dir, self.cur_file_name)
        self.cur_image = Image.open(file_path)
        self.cur_image_size = self.cur_image.size
        self.cur_image_origin = self.cur_image

        (width, height) = self.cur_image_origin.size
        if float(width) / float(height) > float(IMAGE_AREA_SIZE[0]) / float(IMAGE_AREA_SIZE[1]):
            # is landscape
            height = height * IMAGE_AREA_SIZE[0] / width
            width = IMAGE_AREA_SIZE[0]
        else:
            # is not landscape
            width = width * IMAGE_AREA_SIZE[1] / height
            height = IMAGE_AREA_SIZE[1]
        self.cur_scaling = round(float(width) / float(self.cur_image_origin.size[0]), 2) * 100
        self.label_cur_scaling.config(text=text_scaling_prefix + str(self.cur_scaling) + '%')

        self.cur_image = self.cur_image.resize((width, height), Image.ANTIALIAS)
        self.tk_image = ImageTk.PhotoImage(self.cur_image)
        self.image_area.create_image(0, 0, image=self.tk_image, anchor=NW)
        self.image_area.configure(scrollregion=(0, 0, width, height))

        self.load_labels(self.cur_file_name)

    def zoom_in_image(self):
        self.zoom_image(True)

    def zoom_out_image(self):
        self.zoom_image(False)

    def zoom_image(self, bigger=True):
        if self.cur_image_origin:
            self.image_area.delete("all")

            if bigger:
                self.cur_scaling += 7
            else:
                self.cur_scaling -= 7
            if self.cur_scaling < 10:
                self.cur_scaling = 10
            scaling_percent = self.cur_scaling * 0.01
            (width, height) = self.cur_image_origin.size
            width = int(width * scaling_percent)
            height = int(height * scaling_percent)

            self.label_cur_scaling.config(text=text_scaling_prefix + str(self.cur_scaling) + '%')

            self.cur_image = self.cur_image.resize((width, height), Image.ANTIALIAS)
            self.tk_image = ImageTk.PhotoImage(self.cur_image)
            self.image_area.create_image(0, 0, image=self.tk_image, anchor=NW)
            self.image_area.configure(scrollregion=(0, 0, width, height))

            self.flush_labels()
            self.flush_box()
            # index = 0
            for label in self.labeled_list_origin:
                box_id = self.create_label_box(
                    label[1] * scaling_percent, label[2] * scaling_percent,
                    label[3] * scaling_percent, label[4] * scaling_percent,
                    label[0]
                )
                label = (label[0], label[1], label[2], label[3], label[4], box_id)
                self.mark_label_by_name(label[0])

    def canvas_on_mousewheel(self, event):
        self.image_area.yview_scroll(-1 * (event.delta / 20), "units")

    def canvas_on_mouse_click(self, event):
        cur_x, cur_y, cur_x_origin, cur_y_origin = self.get_current_xy_with_scrollbar(event.x, event.y)
        self.label_cur_cursor_1.config(text='x : ' + str(cur_x_origin))
        self.label_cur_cursor_2.config(text='y : ' + str(cur_y_origin))

        if self.cur_mode == CREATE_MODE:
            if not self.tk_image:
                # If the image not exists
                return

            if self.mouse_state['click']:
                # Click second time
                x1, x2 = min(self.mouse_state['x'], cur_x), max(self.mouse_state['x'], cur_x)
                y1, y2 = min(self.mouse_state['y'], cur_y), max(self.mouse_state['y'], cur_y)

                # Check if out of bound
                if x2 > self.cur_image.size[0]:
                    x2 = self.cur_image.size[0]
                if y2 > self.cur_image.size[1]:
                    y2 = self.cur_image.size[1]

                self.labeled_list.append((self.cur_label['name'], x1, y1, x2, y2))

                box_text_id = self.image_area.create_text(
                    x1,
                    y2,
                    text=self.cur_label['name'],
                )

                scaling_percent = self.cur_scaling * 0.01
                x1, y1 = int(x1 / scaling_percent), int(y1 / scaling_percent)
                x2, y2 = int(x2 / scaling_percent), int(y2 / scaling_percent)
                self.labeled_list_origin.append((self.cur_label['name'], x1, y1, x2, y2, self.box_id))

                self.cur_box_color_map[self.box_id] = COLORS[self.box_total_index % len(COLORS)]
                self.box_id_list.append(self.box_id)
                self.box_text_list[self.box_id] = box_text_id
                self.box_total_index += 1

                self.box_id = None
                self.mark_label(self.cur_label['index'], True)
                self.save_labels()

            else:
                # Click first time
                self.mouse_state['x'], self.mouse_state['y'] = cur_x, cur_y

            # Invert click boolean flag
            self.mouse_state['click'] = not self.mouse_state['click']

        elif self.cur_mode == DELETE_MODE:
            for label in self.labeled_list_origin:
                if label[1] < cur_x_origin < label[3] and label[2] < cur_y_origin < label[4]:
                    self.labeled_list_origin.remove(label)
                    self.delete_label_box(int(label[5]))

    def canvas_on_mouse_move(self, event):
        cur_x, cur_y, cur_x_origin, cur_y_origin = self.get_current_xy_with_scrollbar(event.x, event.y)
        self.label_cur_cursor_1.config(text='x : ' + str(cur_x_origin))
        self.label_cur_cursor_2.config(text='y : ' + str(cur_y_origin))

        if self.cur_mode == CREATE_MODE:
            if self.tk_image:
                if self.x_line:
                    self.image_area.delete(self.x_line)
                self.x_line = self.image_area.create_line(0, cur_y, self.tk_image.width(), cur_y, width=1)
                if self.y_line:
                    self.image_area.delete(self.y_line)
                self.y_line = self.image_area.create_line(cur_x, 0, cur_x, self.tk_image.height(), width=1)

            if self.mouse_state['click']:
                if self.box_id:
                    self.image_area.delete(self.box_id)
                self.box_id = self.image_area.create_rectangle(
                    self.mouse_state['x'], self.mouse_state['y'],
                    cur_x, cur_y,
                    width=1,
                    outline=COLORS[self.box_total_index % len(COLORS)]
                )
        elif self.cur_mode == DELETE_MODE:
            scaling_percent = self.cur_scaling * 0.01
            cur_in_label_flag = False
            for label in self.labeled_list_origin:
                if label[1] < cur_x_origin < label[3] and label[2] < cur_y_origin < label[4]:
                    cur_in_label_flag = True
                    # Create box cross
                    if self.tk_image:
                        if not self.cur_box_color_map.has_key(label[5]):
                            color = 'red'
                        else:
                            color = self.cur_box_color_map[label[5]]

                        if self.cross_line_1:
                            self.image_area.delete(self.cross_line_1)
                        self.cross_line_1 = self.image_area.create_line(
                            label[1] * scaling_percent, label[2] * scaling_percent,
                            label[3] * scaling_percent, label[4] * scaling_percent,
                            width=1,
                            fill=color
                        )
                        if self.cross_line_2:
                            self.image_area.delete(self.cross_line_2)
                        self.cross_line_2 = self.image_area.create_line(
                            label[1] * scaling_percent, label[4] * scaling_percent,
                            label[3] * scaling_percent, label[2] * scaling_percent,
                            width=1,
                            fill=color
                        )

            if not cur_in_label_flag:
                # Delete box cross if mouse out of box
                self.image_area.delete(self.cross_line_1)
                self.image_area.delete(self.cross_line_2)

    def select_label(self, event):
        label_list_cur_selection = self.label_list.curselection()
        label_name_with_mark = self.label_list.get(label_list_cur_selection)
        label_name = label_name_with_mark[5:]
        self.cur_label['name'] = label_name
        self.cur_label['index'] = label_list_cur_selection

    def add_label(self):
        if self.label_name.get() == '':
            showerror(text_add_label_error_title, text_add_label_error_info)
        else:
            self.label_list.insert(END, ' [x] ' + self.label_name.get())
            self.save_labels_to_pydb()

    def delete_label(self):
        if self.label_list.size() == 0:
            showerror(text_delete_label_error_title, text_delete_label_error_info)
        else:
            confirm_delete = askokcancel(text_delete_confirm_title, text_delete_confirm_info)
            if confirm_delete:
                self.label_list.delete(self.label_list.curselection())
                self.save_labels_to_pydb()

    def save_labels_to_pydb(self):
        labels = []
        for i in range(0, self.label_list.size()):
            labels.append(self.label_list.get(i))
        labels = tuple(labels)
        with open(PYDB, 'wb') as f:
            pickle.dump(labels, f)

    def load_labels_from_pydb(self):
        with open(PYDB, 'rb') as f:
            labels = pickle.load(f)
            self.labels.set(labels)
        self.label_list.selection_set(0)
            
    def save_labels(self):
        file_name = self.get_label_txt_name(self.cur_file_name)
        label_file_path = os.path.join(self.origin_labels_dir, file_name)
        with open(label_file_path, 'w') as f:
            f.write('%d\n' % len(self.labeled_list_origin))
            for label in self.labeled_list_origin:
                f.write(' '.join(map(str, label[:-1])) + '\n')

    def load_labels(self, file_name):
        # load label when select an image
        self.labeled_list_origin = []
        self.labeled_list = []

        file_name = self.get_label_txt_name(file_name)
        label_file_path = os.path.join(self.origin_labels_dir, file_name)
        scaling_percent = self.cur_scaling * 0.01

        self.flush_labels()
        self.flush_box()
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

                    box_id = self.create_label_box(
                        int(tmp[1]) * scaling_percent, int(tmp[2]) * scaling_percent,
                        int(tmp[3]) * scaling_percent, int(tmp[4]) * scaling_percent,
                        tmp[0],
                    )
                    tmp.append(box_id)
                    self.labeled_list_origin.append(tuple(tmp))

                    self.mark_label_by_name(tmp[0])

    @staticmethod
    def get_label_txt_name(image_file_name):
        return image_file_name + '.txt'

    @staticmethod
    def get_image_name(label_txt_name):
        return label_txt_name[:-4]

    def create_label_box(self, x1, y1, x2, y2, label_name):
        box_id = self.image_area.create_rectangle(
            int(x1), int(y1),
            int(x2), int(y2),
            width=1,
            outline=COLORS[self.box_total_index % len(COLORS)]
        )
        box_text_id = self.image_area.create_text(
            int(x1), int(y2),
            text=label_name,
        )
        self.box_id_list.append(box_id)
        self.box_text_list[box_id] = box_text_id
        self.cur_box_color_map[box_id] = COLORS[self.box_total_index % len(COLORS)]
        self.box_total_index += 1

        return box_id

    def delete_label_box(self, box_id):
        self.image_area.delete(box_id)
        self.box_id_list.remove(box_id)
        self.image_area.delete(self.box_text_list[box_id])
        self.box_text_list[box_id] = None

        # Delete box cross
        self.image_area.delete(self.cross_line_1)
        self.image_area.delete(self.cross_line_2)

        # Refresh label marks
        self.save_labels()
        self.load_labels(self.cur_file_name)

    def switch_view_mode(self):
        self.switch_mode(VIEW_MODE)

    def switch_create_mode(self):
        self.switch_mode(CREATE_MODE)

    def switch_delete_mode(self):
        self.switch_mode(DELETE_MODE)

    def switch_mode(self, mode):
        if mode in MODE:
            self.cur_mode = mode
            self.button_view_mode.configure(state='normal')
            self.button_create_mode.configure(state='normal')
            self.button_delete_mode.configure(state='normal')

            self.image_area.delete(self.x_line)
            self.image_area.delete(self.y_line)
            self.image_area.delete(self.cross_line_1)
            self.image_area.delete(self.cross_line_2)

            if mode == VIEW_MODE:
                self.image_area.configure(cursor='arrow')
                self.button_view_mode.configure(state='disabled')
            elif mode == CREATE_MODE:
                self.image_area.configure(cursor='tcross')
                self.button_create_mode.configure(state='disabled')
            elif mode == DELETE_MODE:
                self.image_area.configure(cursor='diamond_cross')
                self.button_delete_mode.configure(state='disabled')

    def get_current_xy_with_scrollbar(self, event_x, event_y):
        if not self.cur_image:
            return 0, 0, 0, 0
        cur_x = int(self.scrollbar_x_image_area.get()[0] * self.cur_image.size[0] + event_x)
        cur_y = int(self.scrollbar_y_image_area.get()[0] * self.cur_image.size[1] + event_y)
        scaling_percent = self.cur_scaling * 0.01
        cur_x_origin, cur_y_origin = int(cur_x / scaling_percent), int(cur_y / scaling_percent)

        return cur_x, cur_y, cur_x_origin, cur_y_origin

if __name__ == '__main__':
    root = Tk()
    tool = LabelTool(root)
    root.mainloop()
