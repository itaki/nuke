import nuke
from PySide2.QtWidgets import *
from PySide2.QtGui import *
import os

class StockIcons():
    def __init__(self):
        self.html_icon_list = []
        # the first path nuke loads is the stock plugin repository which is last in the list
        self.stock_icons_path = os.path.join(nuke.pluginPath()[-1], 'icons') 
        # add the icons directory to the path
        self.stock_icons = os.listdir(self.stock_icons_path)
        self.stock_icons.sort()
        self.html_icon_list = self.make_html_icon_list()
        self.html_icon_dict = self.make_html_icon_dict()
    
    def make_html_icon_list(self):
        html_icon_list = []
        for icon in self.stock_icons:
            html_icon_list.append(f"<img src='{self.stock_icons_path}/{icon}'> {icon}")
        return html_icon_list

    def make_html_icon_dict(self):
        html_icon_dict = {}
        for icon in self.stock_icons:
            html_icon_dict[f"<img src='{self.stock_icons_path}/{icon}'> {icon}"] = icon
        return html_icon_dict
    
    def make_icon_list_just_images(self):
        icon_list = []
        for icon in self.stock_icons:
            icon_list.append(os.path.join(self.stock_icons_path,icon))
        return icon_list


class ImageMenu(QWidget):

    def __init__(self, parent=None):
        super(ImageMenu, self).__init__(parent)

        # Create the layout for the widget
        layout = QVBoxLayout()

        # Create the dropdown menu
        self.menu = QComboBox()

        # Add the images to the menu
        for i in range(5):
            item = QIcon('/Volumes/panda/images/image{}.png'.format(i+1))
            self.menu.addItem(item, 'Image {}'.format(i+1))

        # Connect the menu to a function that shows the selected image
        self.menu.currentIndexChanged.connect(self.showImage)

        # Add the menu to the layout
        layout.addWidget(self.menu)

        # Set the layout for the widget
        self.setLayout(layout)

    def showImage(self):
        # Get the selected image index from the menu
        index = self.menu.currentIndex()

        # Get the path to the selected image
        path = '/Volumes/panda/images/image{}.png'.format(index+1)

        # Create a QLabel widget to show the image
        image_widget = QLabel()
        pixmap = QPixmap(path)
        image_widget.setPixmap(pixmap)

        # Create a QDialog to show the image widget
        dialog = QDialog()
        dialog.setWindowTitle('Image {}'.format(index+1))
        dialog.setLayout(QVBoxLayout())
        dialog.layout().addWidget(image_widget)
        dialog.exec_()

# Create a Nuke panel for the ImageMenu widget
panel = nuke.Panel('Image Menu')

# Create an instance of the ImageMenu widget
menu_widget = ImageMenu()

# Add the widget to the Nuke panel
menu_widget.addToPane(panel)

# Show the Nuke panel
panel.show()

