from PySide2 import QtCore, QtGui, QtWidgets
import os

class AllIcons(QtWidgets.QWidget):
    def __init__(self, resource):
        super(AllIcons, self).__init__()
        self.setLayout(QtWidgets.QVBoxLayout())
        # put a scrollbar first
        body_container = QtWidgets.QWidget()
        self.body = QtWidgets.QVBoxLayout()
        # self.body.addStretch(1)
        body_container.setLayout(self.body)

        # Scroll Area Properties
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(body_container)
        for icon in QtCore.QDir(resource).entryList():
            image_label = QtWidgets.QLabel()
            image_label.setPixmap(QtGui.QPixmap("{}/{}".format(resource, icon)))
            text_label = QtWidgets.QLabel(icon)
            self.body.addWidget(image_label)
            self.body.addWidget(text_label)
            
        self.layout().addWidget(scroll)

def runme():
    w = AllIcons(u':/qrc/images')
    w.show()

def get_icons():
    icons = QtCore.QResource(':qrc/images').children()
    for icon in icons:
        name = os.path.splitext(icon.split('/')[-1] )[0]
        iconString = '%s <img src=":qrc/images/%s">' % (name, icon)
        print(iconString)