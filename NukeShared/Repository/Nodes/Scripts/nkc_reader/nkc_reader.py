#====================================================
# NKC Reader for Nuke v0.1
#====================================================
#
# This tool lets you visualize the nuke .nkc cache files, 
#  located in Nuke's temp dir.
# It is intended for debugging only.
#
#----------------------------------------------------

#If you want to run this as a "standalone" thing.
#TEMP_DIR_OVERWRITE="/private/var/tmp/nuke-xxxx/ViewerCache" #linux
#TEMP_DIR_OVERWRITE="/var/tmp/nuke-xxxx" #mac
TEMP_DIR_OVERWRITE="C:/Users/madsh/AppData/Local/Temp/nuke/" #windows   

#====================================================
# Requirements
#====================================================
#
# NUKE:
# It will run natively inside nuke (python3, PySide2), 
#  ...but if you have numpy installed it will run significantly faster. 
# Also, as it does not do multithreading it can lock the main thread while processing.
#
# STANDALONE:
# Python3
# PySide2 or PyQt5
# Numpy (recommended)
# If running in standalone you must set the TEMP_DIR_OVERWRITE parameter!
#
#----------------------------------------------------


#====================================================
# How to use?
#====================================================
#
# It is recommended that you clear the cashe before you run it as it can take a while to load all of your cache if you have a ton of cache files.
# If running inside of Nuke just paste the code into the script editor and run.
# 
# If running running as a standalone application make sure to set the "TEMP_DIR_OVERWRITE" parameter
#
#----------------------------------------------------

#====================================================
# Known Bugs
#====================================================
#
# * No support for Half and Floating Point viewer caches yet. (Should be easy to implement)
# * Some aspects of this NKC format have not been reverse engineerd and as might in some cases not display the output properly.
#
#----------------------------------------------------

#====================================================
# Notes
#====================================================
#
# This code will run significantly faster if your viewer height is 640 or smaller as the parser code won't need to run.
# 
#----------------------------------------------------



import os
import sys,struct
from math import ceil
import time

try:
    from PyQt5.QtWidgets import *
    from PyQt5 import QtGui
    from PyQt5.QtGui import QImage, QPixmap,QPalette,QColor
    from PyQt5.QtCore import Qt, QTimer,QSize
except ImportError:
    from PySide2.QtWidgets import *
    from PySide2 import QtGui
    from PySide2.QtGui import QImage, QPixmap,QPalette,QColor
    from PySide2.QtCore import Qt, QTimer,QSize

GOTNUMPY = False
try:
    import numpy as np
    GOTNUMPY = True
except:
    GOTNUMPY = False

GOTNUKE = False
try:
    import nuke
    GOTNUKE = True
except:
    GOTNUKE = False


def read_image_data(file_path):

    #Read the file. This is maybe not the best way to do it as it could be accessed while we read it.
    try:
        with open(file_path, "rb") as f:
            data = f.read()
    except:
        return 0, 0, 0
    #Retrive metadata...
    width = int.from_bytes(data[8:12], byteorder='little')
    height = int.from_bytes(data[12:16], byteorder='little')
    offset = int.from_bytes(data[21:22], byteorder='big') * 16 * 16 #This is a pointer to the image data struct

    #Check if the data matches with what we expect...
    required_length = (width * height * 4) + offset
    if len(data) < required_length:
        print("Warning: This file is incomplete, trying to recover by padding with emptry bytes. %s" %(file_path[-22:]))
        try:
            data = data.ljust(required_length, b'\x00')
        except:
            return 0,0,0

    #Crop meta data so we can focus os the image.
    data = data[offset:]

    #If the height is smaller (in height) than 641 the file is contained in a single piece.
    #If not it will be split up into 5 pices and we need to take some extra steps to aseble it.
    #You can skip this part but that will make the image repeat 5 times.
    if height<=640:
        pass
    else:
        if GOTNUMPY:
            data=parse_numpy(data,width,height)
            pass
        else: #As nuke does not have numpy it would make sense to make a non-numpy version..but im too lazy for that for now.
            data=parse_no_numpy(data,width,height)
            pass

    #Turn the data back into byte data
    img_data = bytes(data)

    return img_data, width, height


def parse_numpy(data,width,height):

    dataLen = width*height*4
    data = data[len(data)-dataLen:]

    data_array = np.frombuffer(data, dtype=np.uint8)

    #Calculate each section size, not super pretty...
    base = height/16
    temp1= ceil(base)
    temp2= ceil((base*2)-(ceil(base)))
    temp3= ceil((base*4)-(ceil(base*2)))
    temp4= ceil((base*8)-(ceil(base*4)))
    temp5= ceil((base*16)-(ceil(base*8)))
    split_idx1 = temp1
    split_idx2 = split_idx1+temp2
    split_idx3 = split_idx2+temp3
    split_idx4 = split_idx3+temp4
    split_idx5 = split_idx4+temp5

    # Reshape the data into a 2D array of shape (height, width*4)
    data_2d = data_array.reshape((height, width*4))

    # Split the data along the rows to get d1, d2, d3, d4, d5
    d1, d2, d3, d4, d5 = np.split(data_2d, [split_idx1, split_idx2, split_idx3, split_idx4], axis=0)

    #Remove the extra dimension from each split array
    d1, d2, d3, d4, d5 = d1.squeeze(), d2.squeeze(), d3.squeeze(), d4.squeeze(), d5.squeeze()

    #Interleave the d's
    d3a = d3[::2]   # Take every even-indexed element of d3
    d3b = d3[1::2]  # Take every odd-indexed element of d3

    d4a = d4[::4]   # Take every 4th element of d4
    d4b = d4[1::4]  # Take every 4th element starting from the 1st element of d4
    d4c = d4[2::4]  # Take every 4th element starting from the 2nd element of d4
    d4d = d4[3::4]  # Take every 4th element starting from the 3rd element of d4

    split_indices = np.arange(len(d5)) % 8  # Create indices for splitting d5
    d5_split = [d5[split_indices == i] for i in range(8)]  # Split d5 into 8 parts

    # Pad the arrays to have the same length
    section_length = max(len(d1), len(d2), len(d3a), len(d3b), len(d4a), len(d4b), len(d4c), len(d4d), *[len(split) for split in d5_split])
    d1 = np.pad(d1, ((0, section_length - len(d1)), (0, 0)), mode='constant')
    d2 = np.pad(d2, ((0, section_length - len(d2)), (0, 0)), mode='constant')
    d3a = np.pad(d3a, ((0, section_length - len(d3a)), (0, 0)), mode='constant')
    d3b = np.pad(d3b, ((0, section_length - len(d3b)), (0, 0)), mode='constant')
    d4a = np.pad(d4a, ((0, section_length - len(d4a)), (0, 0)), mode='constant')
    d4b = np.pad(d4b, ((0, section_length - len(d4b)), (0, 0)), mode='constant')
    d4c = np.pad(d4c, ((0, section_length - len(d4c)), (0, 0)), mode='constant')
    d4d = np.pad(d4d, ((0, section_length - len(d4d)), (0, 0)), mode='constant')
    d5_split = [np.pad(split, ((0, section_length - len(split)), (0, 0)), mode='constant') for split in d5_split]

    combined_data = np.column_stack((d1, d5_split[0], d4a, d5_split[1], d3a, d5_split[2], d4b, d5_split[3], d2, d5_split[4], d4c, d5_split[5], d3b, d5_split[6], d4d, d5_split[7]))
    combined_data = combined_data.flatten()


    # Convert the flattened array to bytes
    combined_data_bytes = combined_data.tobytes()

    return combined_data_bytes

def parse_no_numpy(data, width, height):

    dataLen = width * height * 4
    data = data[len(data) - dataLen:]

    # Calculate each section size, not super pretty...
    base = height / 16
    temp1 = ceil(base)
    temp2 = ceil((base * 2) - (ceil(base)))
    temp3 = ceil((base * 4) - (ceil(base * 2)))
    temp4 = ceil((base * 8) - (ceil(base * 4)))
    temp5 = ceil((base * 16) - (ceil(base * 8)))
    split_idx1 = temp1
    split_idx2 = split_idx1 + temp2
    split_idx3 = split_idx2 + temp3
    split_idx4 = split_idx3 + temp4
    split_idx5 = split_idx4 + temp5

    # Split the data manually
    data_2d = []
    for i in range(height):
        start_idx = i * width * 4
        end_idx = start_idx + width * 4
        data_2d.append(list(data[start_idx:end_idx]))

    # Split the data along the rows to get d1, d2, d3, d4, d5
    d1 = data_2d[:split_idx1]
    d2 = data_2d[split_idx1:split_idx2]
    d3 = data_2d[split_idx2:split_idx3]
    d4 = data_2d[split_idx3:split_idx4]
    d5 = data_2d[split_idx4:split_idx5]

    # Remove the extra dimension from each split array
    d1 = [row for row in d1]
    d2 = [row for row in d2]
    d3 = [row for row in d3]
    d4 = [row for row in d4]
    d5 = [row for row in d5]

    combined_data = []
    section_length = len(d1)

    for i in range(section_length):  
        combined_row = []
        try:
            combined_row.extend(d1.pop(0))
            combined_row.extend(d5.pop(0))
            combined_row.extend(d4.pop(0))
            combined_row.extend(d5.pop(0))
            combined_row.extend(d3.pop(0))
            combined_row.extend(d5.pop(0))
            combined_row.extend(d4.pop(0))
            combined_row.extend(d5.pop(0))
            combined_row.extend(d2.pop(0))
            combined_row.extend(d5.pop(0))
            combined_row.extend(d4.pop(0))
            combined_row.extend(d5.pop(0))
            combined_row.extend(d3.pop(0))
            combined_row.extend(d5.pop(0))
            combined_row.extend(d4.pop(0))
            combined_row.extend(d5.pop(0))
        except:
            pass
        combined_data.extend(combined_row)
    # Convert the flattened list to bytes
    combined_data_bytes = bytes(combined_data)
    return combined_data_bytes



def load_stylesheet():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    qss_path = os.path.join(dir_path, 'style.qss')
    with open(qss_path, "r") as f:
        return f.read()

class BigImageDisplay(QWidget):
    def __init__(self, pixmap, image_scroll_widget, current_file_path):
        super().__init__()
        self.image_scroll_widget = image_scroll_widget
        self.current_file_path = current_file_path
        self.setWindowTitle('Big Image Display')

        # Get the size of the screen
        self.screen_size = QApplication.desktop().screenGeometry().size()

        # Calculate the desired size
        ratio = pixmap.width() / pixmap.height()
        new_width = self.screen_size.width() * 0.9 
        new_height = new_width / ratio

        # If the new height is too big, adjust the width and height
        if new_height > self.screen_size.height() * 0.9: 
            new_height = self.screen_size.height() * 0.9
            new_width = new_height * ratio

        max_size = QSize(int(new_width), int(new_height))
        pixmap = pixmap.scaled(max_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.setFixedSize(pixmap.size())
        self.lbl_image = QLabel()
        self.lbl_image.setPixmap(pixmap)

        vbox = QVBoxLayout()
        vbox.addWidget(self.lbl_image)

        self.setLayout(vbox)

        # Set the window flags
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # Frame playing variables
        self.timer = QTimer()
        self.timer.setInterval(1000 // 24) 
        self.timer.timeout.connect(self.play_frame)
        self.playing = False
        self.end_of_file = False

    def update_image(self, pixmap, file_name):
        self.lbl_image.setPixmap(pixmap)
        self.setWindowTitle(file_name)

        # Calculate the desired size
        ratio = pixmap.width() / pixmap.height()
        new_width = self.screen_size.width() * 0.9 
        new_height = new_width / ratio

        # If the new height is too big, adjust the width and height
        if new_height > self.screen_size.height() * 0.9: 
            new_height = self.screen_size.height() * 0.9
            new_width = new_height * ratio

        max_size = QSize(int(new_width), int(new_height))
        pixmap = pixmap.scaled(max_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.setFixedSize(pixmap.size())
        self.lbl_image.setPixmap(pixmap)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.close()

    def showEvent(self, event):
        screen_geometry = QDesktopWidget().availableGeometry()
        x = (screen_geometry.width() - self.width()) / 2
        y = (screen_geometry.height() - self.height()) / 2
        self.move(int(x), int(y))

    def keyPressEvent(self, event):
        image_display_widgets = list(self.image_scroll_widget.widgets.values())
        if event.key() == Qt.Key_Right:
            if self.image_scroll_widget.current_index < len(image_display_widgets) - 1:
                self.image_scroll_widget.current_index += 1
                next_widget = image_display_widgets[self.image_scroll_widget.current_index]
                self.update_image(next_widget.lbl_image.pixmap, next_widget.file_name)
        elif event.key() == Qt.Key_Left:
            if self.image_scroll_widget.current_index > 0:
                self.image_scroll_widget.current_index -= 1
                prev_widget = image_display_widgets[self.image_scroll_widget.current_index]
                self.update_image(prev_widget.lbl_image.pixmap, prev_widget.file_name)
        elif event.key() == Qt.Key_Space:
            if self.playing:
                self.stop_frame_playback()
            else:
                self.start_frame_playback()
        else:
            super().keyPressEvent(event)

    def update_pixmap(self, pixmap):
        # Calculate the desired size
        ratio = pixmap.width() / pixmap.height()
        new_width = self.screen_size.width() * 0.9 
        new_height = new_width / ratio

        # If the new height is too big, adjust the width and height
        if new_height > self.screen_size.height() * 0.9: 
            new_height = self.screen_size.height() * 0.9
            new_width = new_height * ratio

        max_size = QSize(int(new_width), int(new_height))
        pixmap = pixmap.scaled(max_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.setFixedSize(pixmap.size())
        self.lbl_image.setPixmap(pixmap)

    def start_frame_playback(self):
        self.playing = True
        self.timer.start()

    def stop_frame_playback(self):
        self.playing = False
        self.timer.stop()

    def play_frame(self):
        image_display_widgets = list(self.image_scroll_widget.widgets.values())
        if self.image_scroll_widget.current_index < len(image_display_widgets) - 1:
            self.image_scroll_widget.current_index += 1
            next_widget = image_display_widgets[self.image_scroll_widget.current_index]
            self.update_image(next_widget.lbl_image.pixmap, next_widget.file_name)
        else:
            if self.end_of_file == True:
                self.image_scroll_widget.current_index = 0  # Move back to the first frame
                first_widget = image_display_widgets[0]
                self.update_image(first_widget.lbl_image.pixmap, first_widget.file_name)
                self.end_of_file = False
            else:
                self.end_of_file = True
                self.playing = False
                self.timer.stop()                




class ImageLabel(QLabel):
    def __init__(self, pixmap, file_name):
        super().__init__()
        self.pixmap = pixmap
        self.file_name = file_name
        #self.setPixmap(pixmap.scaledToWidth(self.width(), Qt.SmoothTransformation))        

    def resizeEvent(self, event):
        scaled_pixmap = self.pixmap.scaledToWidth(self.width(), Qt.SmoothTransformation)
        self.setPixmap(scaled_pixmap)

class ImageDisplay(QWidget):
    def __init__(self, image_data, width, height, file_name):
        super().__init__()
        image = QImage(image_data, width, height, QImage.Format_RGBA8888)
        if image.isNull():
            print ("ERROR, image is null")
        image = image.mirrored(False, True)
        pixmap = QPixmap.fromImage(image.convertToFormat(QImage.Format_RGB888))  # Convert to RGB888 format
        #pixmap = QPixmap.fromImage(image)
        if pixmap.isNull():
            print ("ERROR, pixmap is null")
        self.lbl_image = ImageLabel(pixmap, file_name)
        vbox = QVBoxLayout()
        vbox.addWidget(self.lbl_image)

        self.file_name = file_name

        self.big_display = None  # add this line
        # Add file name label
        lbl_file_name = QLabel(file_name)
        lbl_file_name.setStyleSheet("QLabel { color : white; }")
        lbl_file_name.setAlignment(Qt.AlignCenter)
        vbox.addWidget(lbl_file_name)

        self.setLayout(vbox)
        self.setMinimumWidth(100)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent().current_index = list(self.parent().widgets.values()).index(self)
            self.big_display = BigImageDisplay(self.lbl_image.pixmap, self.parent(), self.file_name)
            self.big_display.show()

class ImageScrollWidget(QWidget):
    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path
        self.file_paths = []
        self.last_modification_times = {}
        self.scroll_area = None
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_for_new_files)
        self.timer.timeout.connect(self.check_for_removed_files)
        self.timer.timeout.connect(self.update_file_count)
        self.timer.start(100)  # 100ms interval
        self.current_index = 0
        self.main_widget = None
        self.widgets = {}  # This is used to track the widgets

        palette = QPalette()
        palette.setColor(QPalette.Background, QColor(53, 53, 53))
        self.setPalette(palette)

    def check_for_new_files(self):
        new_file_paths = []
        updated_file_paths = []
        for root, dirs, files in os.walk(self.folder_path):
            for file in files:
                if file.endswith(".nkc"):
                    file_path = os.path.join(root, file)
                    last_modification_time = os.path.getmtime(file_path)
                    if file_path not in self.file_paths:
                        new_file_paths.append(file_path)
                        self.last_modification_times[file_path] = last_modification_time
                    elif last_modification_time > self.last_modification_times.get(file_path, 0):
                        updated_file_paths.append(file_path)
                        self.last_modification_times[file_path] = last_modification_time

        if new_file_paths:
            self.handle_new_files(new_file_paths)
        if updated_file_paths:
            self.handle_updated_files(updated_file_paths)

        self.adjustSize()

    def handle_new_files(self, new_file_paths):
        new_file_paths.sort(key=os.path.getmtime, reverse=False)
        self.file_paths.extend(new_file_paths)

        main_widget.progress_bar.setMaximum(len(new_file_paths))  # Initial maximum value
     
        for x,file_path in enumerate(new_file_paths):
            self.add_image_widget(file_path)
            main_widget.progress_bar.setValue(x)               
            #QApplication.processEvents()
        main_widget.progress_bar.hide()

    def handle_updated_files(self, updated_file_paths):
        for file_path in updated_file_paths:
            # Remove the old widget first
            widget_to_remove = self.widgets.get(file_path)
            if widget_to_remove is not None:
                self.layout.removeWidget(widget_to_remove)
                widget_to_remove.setParent(None)
                widget_to_remove.deleteLater()
            # Then add the updated one
            self.add_image_widget(file_path)
            #QApplication.processEvents()

    def add_image_widget(self, file_path):
        image_data, width, height = read_image_data(file_path)
        if not image_data==0:
            file_name = os.path.basename(file_path)
            display = ImageDisplay(image_data, width, height, file_name)
            self.layout.insertWidget(0, display)  # Insert at the top
            self.widgets[file_path] = display
            if self.scroll_area is not None:
                self.scroll_area.ensureWidgetVisible(display)

    def check_for_removed_files(self):
        removed_files = [file_path for file_path in self.file_paths if not os.path.isfile(file_path)]
        if removed_files:
            for file_path in removed_files:
                self.file_paths.remove(file_path)
                widget = self.widgets.get(file_path)
                if widget is not None:
                    self.layout.removeWidget(widget)
                    widget.setParent(None)
                    widget.deleteLater()
                    
                    # remove this widget from widgets dictionary
                    self.widgets.pop(file_path, None)



    def update_file_count(self):
        file_count = len(self.file_paths)
        if self.main_widget is not None:
            self.file_count_label.setText(f"File Count: {file_count}")


class MainWidget(QWidget):
    global TEMP_DIR_OVERWRITE
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        temp_dir = os.environ.get('NUKE_TEMP_DIR')
        if not temp_dir:
            temp_dir = TEMP_DIR_OVERWRITE
         
        folder_path = os.path.join(temp_dir, "ViewerCache")


        scroll_widget = ImageScrollWidget(folder_path)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn) 

        #We only show this the first time you run the app as if you have a ton of cache files you might want to see how long time is left...
        self.progress_bar = QProgressBar() 
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(1)  # Initial maximum value
        self.progress_bar.setValue(0)

        self.resize(720, 1280)


        scroll_widget.file_count_label = QLabel()
        scroll_widget.file_count_label.setAlignment(Qt.AlignCenter)

        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll_area)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(scroll_widget.file_count_label)

        self.setLayout(main_layout)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint) 

        scroll_widget.main_widget = self
        self.setWindowTitle(".nkc Reader")


if __name__ == "__main__":
    if GOTNUKE:
        main_widget = MainWidget()
        main_widget.show()
    else:
        app = QApplication(sys.argv)
        app.setStyleSheet(load_stylesheet())
        main_widget = MainWidget()
        main_widget.show()
        sys.exit(app.exec_())
