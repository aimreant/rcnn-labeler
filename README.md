# rcnn-labeler

## 简介
该程序用于标记图片、生成RCNN训练所需的XML与TXT文件，同时提供一定的预处理方法，用于生成不同于原图的副本。

## 运行环境
 - Python 2.7.13
 - 库cv2

```shell
pip install numpy Matplotlib
pip install opencv-python
sudo pip install -r requirements.txt
```
 
## 切换语言
 - 于config.py中修改LANGUAGE的值。
 - Change the value of LANGUAGE in config.py.
 
## 使用说明
### 文件目录说明
#### 目录
 - docs: 可忽略，仅用于存放README的图片
 - origin_images: 原图片存放于此，支持JPG/JPEG、BMP、PNG）
 - labels: 用于存放用户在图片上标注的标签信息
 - output_images: 用于存放该程序生成的图片，包括转换为JPG以及各可选功能转换出来的副本
 - xmls: 该程序生成的XML文件
 - sets: 该程序生成的训练集等txt文件
#### 文件
 - app.py: 程序主文件
 - tools.py: 工具类文件
 - config.py: 配置文件
 - lang.py: 语言配置文件
 - label_pydb: 存储标签信息
 
### 界面演示
#### 界面
通过`python app.py`打开程序，进入程序界面

![程序界面](https://raw.githubusercontent.com/aimreant/rcnn-labeler/master/docs/pic_1.png)

#### 原图目录 
程序左上角为原图目录，即origin_images目录下的图片文件
 - 约定规则为“不允许不同格式的同名字图片”，以免在后续处理产生不可预测的结果。

![原图目录](https://raw.githubusercontent.com/aimreant/rcnn-labeler/master/docs/pic_3.png)

点击选择图片，程序中间即出现标签原图片
![程序界面](https://raw.githubusercontent.com/aimreant/rcnn-labeler/master/docs/pic_2.png)


#### 标签
程序左下角为标签处理，可添加、删除标签
 - 需要在此处添加了所需名字的标签，才能使用该标签标记图片
 
![标签处理](https://raw.githubusercontent.com/aimreant/rcnn-labeler/master/docs/pic_4.png)

#### 操作
程序右上角有放大缩小图片的基本操作，以及当前图片的缩放比例

![操作](https://raw.githubusercontent.com/aimreant/rcnn-labeler/master/docs/pic_5.png)

#### 模式切换
程序右下角为模式切换
 - 观察模式（默认）
 - 标签模式，能在图片上进行标记
 - 删除模式，能删除图片上已经标记了的标签
 
![模式切换](https://raw.githubusercontent.com/aimreant/rcnn-labeler/master/docs/pic_6.png)

#### 可选功能
程序下方有多个可选功能，用于基于原图生成不同的副本，在【生成XML文件以及训练集TXT文件】前，选择所需功能即可

![可选功能](https://raw.githubusercontent.com/aimreant/rcnn-labeler/master/docs/pic_7.png)

