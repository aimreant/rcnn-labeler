#!/usr/bin/python
# -*- coding: UTF-8 -*-
import pickle
from Tkinter import *
from PIL import Image, ImageTk
import os
import glob
from tkMessageBox import *


ORIGIN_IMAGES_PATH = 'origin_images'


class PreProcessingTool:
    def __init__(self, master):
        # Object parameters
        self.labels = StringVar()
        self.images = StringVar()
        try:
            self.load_labels_from_file()
        except EOFError:
            pass

        # Set main parameters -----------------------------------------------
        self.parent = master
        self.parent.title("PreProcessingTool")
        self.parent.geometry("800x500")
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
        self.frame_image_area.place(x=200, y=0, width=600, height=350)
        self.frame_console = Frame(self.frame, bg="red")
        self.frame_console.place(x=200, y=350, width=600, height=150)

        # Build file list ---------------------------------------------------
        self.file_list_label = Label(self.frame_file_list, text='Images directory', bg='gray', anchor='w')
        self.file_list_label.place(x=0, y=0, width=200, height=20)

        self.file_list = Listbox(self.frame_file_list, selectmode=BROWSE, borderwidth=0, listvariable=self.images)
        self.file_list.place(x=0, y=20, width=200, height=280)

        self.file_list.bind('<ButtonRelease-1>', self.select_image)
        self.scrollbar_file_list = Scrollbar(self.frame_file_list)
        self.scrollbar_file_list.pack(side=RIGHT, fill=Y)
        self.file_list.configure(yscrollcommand=self.scrollbar_file_list.set)
        self.scrollbar_file_list['command'] = self.file_list.yview

        # Build label list ---------------------------------------------------
        self.label_list_label = Label(self.frame_label_list, text='Labels', bg='gray', anchor='w')
        self.label_list_label.place(x=0, y=0, width=200, height=20)

        self.label_list = Listbox(self.frame_label_list, selectmode=BROWSE, borderwidth=0, listvariable=self.labels)
        self.label_list.place(x=0, y=20, width=200, height=135)

        # self.label_list.bind('<ButtonRelease-1>', self.print_test)
        self.scrollbar_label_list = Scrollbar(self.frame_label_list)
        self.scrollbar_label_list.pack(side=RIGHT, fill=Y)
        self.label_list.configure(yscrollcommand=self.scrollbar_label_list.set)
        self.scrollbar_label_list['command'] = self.label_list.yview

        # Build label buttons
        self.label_name_label = Label(self.frame_label_button, text='Name:', anchor='w')
        self.label_name_label.place(x=0, y=0, width=65, height=20)
        self.label_name = Entry(self.frame_label_button)
        self.label_name.place(x=65, y=0, width=115, height=20)

        self.add_label_bottom = Button(self.frame_label_button, command=self.add_label, text="Add")
        self.add_label_bottom.place(x=0, y=20, width=90, height=23)
        self.delete_label_bottom = Button(self.frame_label_button, command=self.delete_label, text="Delete")
        self.delete_label_bottom.place(x=90, y=20, width=90, height=23)

        # Build canvas area --------------------------------------------------
        self.image_area = Canvas(self.frame_image_area, cursor='tcross', width=600, height=350,
                                 scrollregion=(0, 0, 600, 350))
        self.image_area.place(width=600, height=350)

        self.scrollbar_y_image_area = Scrollbar(self.frame_image_area, orient=VERTICAL)
        self.scrollbar_y_image_area.pack(side=RIGHT, fill=Y)
        self.scrollbar_y_image_area.config(command=self.image_area.yview)
        self.scrollbar_x_image_area = Scrollbar(self.frame_image_area, orient=HORIZONTAL)
        self.scrollbar_x_image_area.pack(side=BOTTOM, fill=X)
        self.scrollbar_x_image_area.config(command=self.image_area.xview)
        self.image_area.config(width=300, height=300)
        self.image_area.config(xscrollcommand=self.scrollbar_x_image_area.set,
                               yscrollcommand=self.scrollbar_y_image_area.set)

        # TODO bind mousewheel to scrollbar on canvas
        # self.image_area.bind_all("<MouseWheel>", self._on_mousewheel)

        # Build checkbox -----------------------------------------------------
        self.check_var_rotate = IntVar()
        self.check_rotate = Checkbutton(self.frame_console, text="Rotate", variable=self.check_var_rotate)
        self.check_rotate.deselect()
        self.check_rotate.grid(row=0, column=0, sticky=W)

        self.check_var_zoom = IntVar()
        self.check_zoom = Checkbutton(self.frame_console, text="Zoom", variable=self.check_var_zoom)
        self.check_zoom.deselect()
        self.check_zoom.grid(row=1, column=0, sticky=W)

        self.check_var_impurity = IntVar()
        self.check_impurity = Checkbutton(self.frame_console, text="Impurity", variable=self.check_var_impurity)
        self.check_impurity.deselect()
        self.check_impurity.grid(row=2, column=0, sticky=W)

        self.check_var_blur = IntVar()
        self.check_blur = Checkbutton(self.frame_console, text="Blur", variable=self.check_var_blur)
        self.check_blur.deselect()
        self.check_blur.grid(row=3, column=0, sticky=W)

        self.generate_label_bottom = Button(self.frame_console, text="Generate")
        self.generate_label_bottom.grid(row=0, column=1, rowspan=4)

        self.button_images_zoom_1 = Button(self.frame_console, text='+', command=self.zoom_in_image)
        self.button_images_zoom_1.grid(row=0, column=2, rowspan=2)
        self.button_images_zoom_2 = Button(self.frame_console, text='-', command=self.zoom_out_image)
        self.button_images_zoom_2.grid(row=1, column=2, rowspan=2)
        self.label_cur_scaling = Label(self.frame_console, text='0%')
        self.label_cur_scaling.grid(row=2, column=2, rowspan=2)

        # Initial Operation
        self.load_icon()
        # self.load_file_list()
        self.load_images()

    def print_test(self, event):
        print(self.file_list.get(self.file_list.curselection()))
        self.mark_file(self.file_list.curselection(), True)

    def load_file_list(self):
        li = ['C', 'python', 'php', 'html', 'SQL', 'java']
        for i in range(0, 2):
            for item in li:
                self.file_list.insert(0, ' [x] ' + item)

    def load_icon(self):
        self.file_icon = PhotoImage(Image.open('icons/file.png'))

    def load_images(self):
        self.parent.focus()

        # Get image list
        self.origin_images_dir = os.path.join('.', ORIGIN_IMAGES_PATH)
        self.origin_images_list = glob.glob(os.path.join(self.origin_images_dir, '*.jpg'))

        if len(self.origin_images_list) == 0:
            showerror("No image", 'No ".jpg" images found in the specified dir  "' + ORIGIN_IMAGES_PATH + '"')

        # Set label dir
        self.labels_dir = os.path.join('.', 'labels')  # label输出路径
        if not os.path.exists(self.labels_dir):
            os.mkdir(self.labels_dir)

        self.cur = 0
        self.total_images_size = len(self.origin_images_list)
        # TODO load file list in origin_images
        for image in self.origin_images_list:
            file_name = image.split('/')[-1]
            self.insert_to_file_list(file_name)

        # TODO load file-label in labels


        # TODO load current image to canvas


        self.cur_image_path = self.origin_images_list[self.cur]

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

    def select_image(self, event):
        print('select image: ' + self.file_list.get(self.file_list.curselection()))

        file_list_cur_selection = self.file_list.curselection()
        if not file_list_cur_selection:
            showerror("Loading error", 'Please contact with developers.')
            file_list_cur_selection = 1
        file_name_with_mark = self.file_list.get(file_list_cur_selection)
        file_name = file_name_with_mark[5:]
        file_path = os.path.join(self.origin_images_dir, file_name)
        self.cur_image = Image.open(file_path)
        self.cur_imagr_size = self.cur_image.size
        self.cur_image_origin = self.cur_image

        (width, height) = self.cur_image_origin.size
        if width / height > 600 / 350:
            # is landscape
            height = height * 600 / width
            width = 600
        else:
            # is not landscape
            width = width * 350 / height
            height = 350
        self.cur_scaling = round(float(width) / float(self.cur_image_origin.size[0]), 2) * 100
        self.label_cur_scaling.config(text=str(self.cur_scaling) + '%')

        self.cur_image = self.cur_image.resize((width, height), Image.ANTIALIAS)
        self.tk_image = ImageTk.PhotoImage(self.cur_image)
        self.image_area.create_image(0, 0, image=self.tk_image, anchor=NW)

        self.image_area.configure(scrollregion=(0, 0, width, height))

    def zoom_in_image(self):
        self.zoom_image(True)

    def zoom_out_image(self):
        self.zoom_image(False)

    def zoom_image(self, bigger=True):
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

        self.label_cur_scaling.config(text=str(self.cur_scaling) + '%')

        self.cur_image = self.cur_image.resize((width, height), Image.ANTIALIAS)
        self.tk_image = ImageTk.PhotoImage(self.cur_image)
        self.image_area.create_image(0, 0, image=self.tk_image, anchor=NW)

        self.image_area.configure(scrollregion=(0, 0, width, height))

    def _on_mousewheel(self, event):
        self.image_area.yview_scroll(-1 * (event.delta / 20), "units")

    def add_label(self):
        if self.label_name.get() == '':
            showerror("Add label error", "Please write label name.")
        else:
            self.label_list.insert(END, ' [x] ' + self.label_name.get())
        self.save_labels_to_file()

    def delete_label(self):
        if self.label_list.size() == 0:
            showerror("Delete label error", "No label.")
        else:
            self.label_list.delete(self.label_list.curselection())
            self.save_labels_to_file()

    def save_labels_to_file(self):
        labels = []
        for i in range(0, self.label_list.size()):
            labels.append(self.label_list.get(i))
        labels = tuple(labels)
        with open('label_pydb', 'wb') as f:
            pickle.dump(labels, f)

    def load_labels_from_file(self):
        with open('label_pydb', 'rb') as f:
            labels = pickle.load(f)
            self.labels.set(labels)


if __name__ == '__main__':
    root = Tk()
    tool = PreProcessingTool(root)
    root.mainloop()
