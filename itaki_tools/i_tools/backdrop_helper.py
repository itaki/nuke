#UIChanged and added more fuctionality v1.2.0


# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mdBackdrop_v2mGnvRH.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################
import nuke, random
import nukescripts
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import sys






class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(370, 499)
        Form.setMinimumSize(QSize(370, 499))
        Form.setMaximumSize(QSize(370, 499))
        self.actionEnter = QAction(Form)
        self.actionEnter.setObjectName(u"actionEnter")
        self.layoutWidget = QWidget(Form)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(10, 40, 351, 73))
        self.horizontalLayout = QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.lineEdit = QLineEdit(self.layoutWidget)
        self.lineEdit.setObjectName(u"lineEdit")
        self.lineEdit.setMinimumSize(QSize(0, 40))

        self.horizontalLayout.addWidget(self.lineEdit)

        self.pushButton_Plate_17 = QPushButton(self.layoutWidget)
        self.pushButton_Plate_17.setObjectName(u"pushButton_Plate_17")
        self.pushButton_Plate_17.setMinimumSize(QSize(0, 40))
        self.pushButton_Plate_17.setSizeIncrement(QSize(0, 0))
        self.pushButton_Plate_17.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.pushButton_Plate_17.setStyleSheet(u"font: 75 15pt \"Roboto\";\n"
"")

        self.horizontalLayout.addWidget(self.pushButton_Plate_17)

        self.gridLayoutWidget = QWidget(Form)
        self.gridLayoutWidget.setObjectName(u"gridLayoutWidget")
        self.gridLayoutWidget.setGeometry(QRect(10, 110, 351, 370))
        self.gridLayout = QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.pushButton_Plate_4 = QPushButton(self.gridLayoutWidget)
        self.pushButton_Plate_4.setObjectName(u"pushButton_Plate_4")
        self.pushButton_Plate_4.setMinimumSize(QSize(0, 40))
        self.pushButton_Plate_4.setSizeIncrement(QSize(0, 0))
        self.pushButton_Plate_4.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.pushButton_Plate_4.setStyleSheet(u"font: 75 15pt \"Roboto\";\n"
"")

        self.gridLayout.addWidget(self.pushButton_Plate_4, 1, 1, 1, 1)

        self.pushButton_Plate_13 = QPushButton(self.gridLayoutWidget)
        self.pushButton_Plate_13.setObjectName(u"pushButton_Plate_13")
        self.pushButton_Plate_13.setMinimumSize(QSize(0, 40))
        self.pushButton_Plate_13.setSizeIncrement(QSize(0, 0))
        self.pushButton_Plate_13.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.pushButton_Plate_13.setStyleSheet(u"font: 75 15pt \"Roboto\";\n"
"")

        self.gridLayout.addWidget(self.pushButton_Plate_13, 6, 0, 1, 1)

        self.pushButton_Plate_9 = QPushButton(self.gridLayoutWidget)
        self.pushButton_Plate_9.setObjectName(u"pushButton_Plate_9")
        self.pushButton_Plate_9.setMinimumSize(QSize(0, 40))
        self.pushButton_Plate_9.setSizeIncrement(QSize(0, 0))
        self.pushButton_Plate_9.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.pushButton_Plate_9.setStyleSheet(u"font: 75 15pt \"Roboto\";\n"
"")

        self.gridLayout.addWidget(self.pushButton_Plate_9, 4, 0, 1, 1)

        self.pushButton_Plate_10 = QPushButton(self.gridLayoutWidget)
        self.pushButton_Plate_10.setObjectName(u"pushButton_Plate_10")
        self.pushButton_Plate_10.setMinimumSize(QSize(0, 40))
        self.pushButton_Plate_10.setSizeIncrement(QSize(0, 0))
        self.pushButton_Plate_10.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.pushButton_Plate_10.setStyleSheet(u"font: 75 15pt \"Roboto\";\n"
"")

        self.gridLayout.addWidget(self.pushButton_Plate_10, 4, 1, 1, 1)

        self.pushButton_Plate_14 = QPushButton(self.gridLayoutWidget)
        self.pushButton_Plate_14.setObjectName(u"pushButton_Plate_14")
        self.pushButton_Plate_14.setMinimumSize(QSize(0, 40))
        self.pushButton_Plate_14.setSizeIncrement(QSize(0, 0))
        self.pushButton_Plate_14.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.pushButton_Plate_14.setStyleSheet(u"font: 75 15pt \"Roboto\";\n"
"")

        self.gridLayout.addWidget(self.pushButton_Plate_14, 6, 1, 1, 1)

        self.pushButton_Plate_8 = QPushButton(self.gridLayoutWidget)
        self.pushButton_Plate_8.setObjectName(u"pushButton_Plate_8")
        self.pushButton_Plate_8.setMinimumSize(QSize(0, 40))
        self.pushButton_Plate_8.setSizeIncrement(QSize(0, 0))
        self.pushButton_Plate_8.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.pushButton_Plate_8.setStyleSheet(u"font: 75 15pt \"Roboto\";\n"
"")

        self.gridLayout.addWidget(self.pushButton_Plate_8, 3, 1, 1, 1)

        self.pushButton_Plate_2 = QPushButton(self.gridLayoutWidget)
        self.pushButton_Plate_2.setObjectName(u"pushButton_Plate_2")
        self.pushButton_Plate_2.setMinimumSize(QSize(0, 40))
        self.pushButton_Plate_2.setSizeIncrement(QSize(0, 0))
        self.pushButton_Plate_2.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.pushButton_Plate_2.setStyleSheet(u"font: 75 15pt \"Roboto\";\n"
"")

        self.gridLayout.addWidget(self.pushButton_Plate_2, 0, 1, 1, 1)

        self.pushButton_Plate_7 = QPushButton(self.gridLayoutWidget)
        self.pushButton_Plate_7.setObjectName(u"pushButton_Plate_7")
        self.pushButton_Plate_7.setMinimumSize(QSize(0, 40))
        self.pushButton_Plate_7.setSizeIncrement(QSize(0, 0))
        self.pushButton_Plate_7.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.pushButton_Plate_7.setStyleSheet(u"font: 75 15pt \"Roboto\";\n"
"")

        self.gridLayout.addWidget(self.pushButton_Plate_7, 3, 0, 1, 1)

        self.pushButton_Plate_12 = QPushButton(self.gridLayoutWidget)
        self.pushButton_Plate_12.setObjectName(u"pushButton_Plate_12")
        self.pushButton_Plate_12.setMinimumSize(QSize(0, 40))
        self.pushButton_Plate_12.setSizeIncrement(QSize(0, 0))
        self.pushButton_Plate_12.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.pushButton_Plate_12.setStyleSheet(u"font: 75 15pt \"Roboto\";\n"
"")

        self.gridLayout.addWidget(self.pushButton_Plate_12, 5, 1, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 8, 0, 1, 1)

        self.pushButton_Plate_6 = QPushButton(self.gridLayoutWidget)
        self.pushButton_Plate_6.setObjectName(u"pushButton_Plate_6")
        self.pushButton_Plate_6.setMinimumSize(QSize(0, 40))
        self.pushButton_Plate_6.setSizeIncrement(QSize(0, 0))
        self.pushButton_Plate_6.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.pushButton_Plate_6.setStyleSheet(u"font: 75 15pt \"Roboto\";\n"
"")

        self.gridLayout.addWidget(self.pushButton_Plate_6, 2, 1, 1, 1)

        self.pushButton_Plate_15 = QPushButton(self.gridLayoutWidget)
        self.pushButton_Plate_15.setObjectName(u"pushButton_Plate_15")
        self.pushButton_Plate_15.setMinimumSize(QSize(0, 40))
        self.pushButton_Plate_15.setSizeIncrement(QSize(0, 0))
        self.pushButton_Plate_15.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.pushButton_Plate_15.setStyleSheet(u"font: 75 15pt \"Roboto\";\n"
"")

        self.gridLayout.addWidget(self.pushButton_Plate_15, 7, 0, 1, 1)

        self.pushButton_Plate_16 = QPushButton(self.gridLayoutWidget)
        self.pushButton_Plate_16.setObjectName(u"pushButton_Plate_16")
        self.pushButton_Plate_16.setMinimumSize(QSize(0, 40))
        self.pushButton_Plate_16.setSizeIncrement(QSize(0, 0))
        self.pushButton_Plate_16.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.pushButton_Plate_16.setStyleSheet(u"font: 75 15pt \"Roboto\";\n"
"")

        self.gridLayout.addWidget(self.pushButton_Plate_16, 7, 1, 1, 1)

        self.pushButton_Plate_3 = QPushButton(self.gridLayoutWidget)
        self.pushButton_Plate_3.setObjectName(u"pushButton_Plate_3")
        self.pushButton_Plate_3.setMinimumSize(QSize(0, 40))
        self.pushButton_Plate_3.setSizeIncrement(QSize(0, 0))
        self.pushButton_Plate_3.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.pushButton_Plate_3.setStyleSheet(u"font: 75 15pt \"Roboto\";\n"
"")

        self.gridLayout.addWidget(self.pushButton_Plate_3, 1, 0, 1, 1)

        self.pushButton_Plate = QPushButton(self.gridLayoutWidget)
        self.pushButton_Plate.setObjectName(u"pushButton_Plate")
        self.pushButton_Plate.setMinimumSize(QSize(0, 40))
        self.pushButton_Plate.setSizeIncrement(QSize(0, 0))
        self.pushButton_Plate.setMouseTracking(False)
        self.pushButton_Plate.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.pushButton_Plate.setStyleSheet(u"font: 75 15pt \"Roboto\";\n"
"\n"
"")

        self.gridLayout.addWidget(self.pushButton_Plate, 0, 0, 1, 1)

        self.pushButton_Plate_5 = QPushButton(self.gridLayoutWidget)
        self.pushButton_Plate_5.setObjectName(u"pushButton_Plate_5")
        self.pushButton_Plate_5.setMinimumSize(QSize(0, 40))
        self.pushButton_Plate_5.setSizeIncrement(QSize(0, 0))
        self.pushButton_Plate_5.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.pushButton_Plate_5.setStyleSheet(u"font: 75 15pt \"Roboto\";\n"
"")

        self.gridLayout.addWidget(self.pushButton_Plate_5, 2, 0, 1, 1)

        self.pushButton_Plate_11 = QPushButton(self.gridLayoutWidget)
        self.pushButton_Plate_11.setObjectName(u"pushButton_Plate_11")
        self.pushButton_Plate_11.setMinimumSize(QSize(0, 40))
        self.pushButton_Plate_11.setSizeIncrement(QSize(0, 0))
        self.pushButton_Plate_11.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.pushButton_Plate_11.setStyleSheet(u"font: 75 15pt \"Roboto\";\n"
"")

        self.gridLayout.addWidget(self.pushButton_Plate_11, 5, 0, 1, 1)

        self.label = QLabel(Form)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 0, 181, 39))
        font = QFont()
        font.setFamily(u"Roboto")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)

        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.actionEnter.setText(QCoreApplication.translate("Form", u"Enter", None))
#if QT_CONFIG(shortcut)
        self.actionEnter.setShortcut(QCoreApplication.translate("Form", u"Return", None))
#endif // QT_CONFIG(shortcut)
        self.pushButton_Plate_17.setText(QCoreApplication.translate("Form", u"Enter", None))
        self.pushButton_Plate_4.setText(QCoreApplication.translate("Form", u"Alpha", None))
        self.pushButton_Plate_13.setText(QCoreApplication.translate("Form", u"3D", None))
        self.pushButton_Plate_9.setText(QCoreApplication.translate("Form", u"Cleanup", None))
        self.pushButton_Plate_10.setText(QCoreApplication.translate("Form", u"Roto", None))
        self.pushButton_Plate_14.setText(QCoreApplication.translate("Form", u"Lens Effect", None))
        self.pushButton_Plate_8.setText(QCoreApplication.translate("Form", u"Color Correction", None))
        self.pushButton_Plate_2.setText(QCoreApplication.translate("Form", u"Denoise", None))
        self.pushButton_Plate_7.setText(QCoreApplication.translate("Form", u"Transfrom", None))
        self.pushButton_Plate_12.setText(QCoreApplication.translate("Form", u"DMP", None))
        self.pushButton_Plate_6.setText(QCoreApplication.translate("Form", u"Despill", None))
        self.pushButton_Plate_15.setText(QCoreApplication.translate("Form", u"Grain", None))
        self.pushButton_Plate_16.setText(QCoreApplication.translate("Form", u"Final Output", None))
        self.pushButton_Plate_3.setText(QCoreApplication.translate("Form", u"Precomp", None))
        self.pushButton_Plate.setText(QCoreApplication.translate("Form", u"Plate", None))
        self.pushButton_Plate_5.setText(QCoreApplication.translate("Form", u"Keying", None))
        self.pushButton_Plate_11.setText(QCoreApplication.translate("Form", u"Projections", None))
        self.label.setText(QCoreApplication.translate("Form", u"BACKDROP HELPER", None))
    # retranslateUi




























#######################################################################################
def nodeIsInside(node, backdropNode):
    # Implementation of nodeIsInside function is missing here
    pass

def autoBackdropmd():
    '''
    Automatically puts a backdrop behind the selected nodes.
    The backdrop will be just big enough to fit all the select nodes in, with room
    at the top for some text in a large font.
    '''
    selNodes = nuke.selectedNodes()
    if not selNodes:
        return nuke.nodes.BackdropNode()

    # Calculate bounds for the backdrop node.
    bdX = min([node.xpos() for node in selNodes])
    bdY = min([node.ypos() for node in selNodes])
    bdW = max([node.xpos() + node.screenWidth() for node in selNodes]) - bdX
    bdH = max([node.ypos() + node.screenHeight() for node in selNodes]) - bdY

    zOrder = 0
    selectedBackdropNodes = nuke.selectedNodes("BackdropNode")
    # If there are backdropNodes selected, put the new one immediately behind the farthest one.
    if len(selectedBackdropNodes):
        zOrder = min([node.knob("z_order").value() for node in selectedBackdropNodes]) - 1
    else:
        # Otherwise (no backdrop in selection), find the nearest backdrop if it exists and set the new one in front of it.
        nonSelectedBackdropNodes = nuke.allNodes("BackdropNode")
        for nonBackdrop in selNodes:
            for backdrop in nonSelectedBackdropNodes:
                if nodeIsInside(nonBackdrop, backdrop):
                    zOrder = max(zOrder, backdrop.knob("z_order").value() + 1)

    # Expand the bounds to leave a little border. Elements are offsets for left, top, right, and bottom edges respectively.
    left, top, right, bottom = (-100, -80, 100, 100)
    bdX += left
    bdY += top
    bdW += (right - left)
    bdH += (bottom - top)

    n = nuke.nodes.BackdropNode(xpos=bdX,
                                bdwidth=bdW,
                                ypos=bdY,
                                bdheight=bdH,
                                tile_color=int((random.random() * (16 - 10))) + 10,
                                note_font_size=42,
                                z_order=zOrder)

    # Revert to the previous selection
    n['selected'].setValue(False)
    for node in selNodes:
        node['selected'].setValue(True)

    return n






def hex_color_to_rgb(red, green, blue):
    return int('%02x%02x%02x%02x' % (int(red*255),int(green*255),int(blue*255),255),16)

#MainCode

class md_backdrop(QWidget, Ui_Form):
    def __init__(self):
        super(md_backdrop, self).__init__()
        self.setupUi(self)
        self.pushButton_Plate_4.clicked.connect(self.Alpha)
        self.pushButton_Plate_4.clicked.connect(self.close)

        self.pushButton_Plate.clicked.connect(self.Plate)
        self.pushButton_Plate.clicked.connect(self.close)

        self.pushButton_Plate_5.clicked.connect(self.Keying)
        self.pushButton_Plate_5.clicked.connect(self.close)

        self.pushButton_Plate_2.clicked.connect(self.Denoise)
        self.pushButton_Plate_2.clicked.connect(self.close)

        self.pushButton_Plate_6.clicked.connect(self.Desipill)
        self.pushButton_Plate_6.clicked.connect(self.close)

        self.pushButton_Plate_8.clicked.connect(self.CC)
        self.pushButton_Plate_8.clicked.connect(self.close)

        self.pushButton_Plate_7.clicked.connect(self.Transfrom)
        self.pushButton_Plate_7.clicked.connect(self.close)

        self.pushButton_Plate_13.clicked.connect(self.ThreeD)
        self.pushButton_Plate_13.clicked.connect(self.close)

        self.pushButton_Plate_12.clicked.connect(self.DMP)
        self.pushButton_Plate_12.clicked.connect(self.close)

        self.pushButton_Plate_3.clicked.connect(self.Precomp)
        self.pushButton_Plate_3.clicked.connect(self.close)

        self.pushButton_Plate_16.clicked.connect(self.Render)
        self.pushButton_Plate_16.clicked.connect(self.close)

        self.pushButton_Plate_15.clicked.connect(self.Grain)
        self.pushButton_Plate_15.clicked.connect(self.close)

        self.pushButton_Plate_14.clicked.connect(self.LensFX)
        self.pushButton_Plate_14.clicked.connect(self.close)

        self.pushButton_Plate_9.clicked.connect(self.Cleanup)
        self.pushButton_Plate_9.clicked.connect(self.close)

        self.pushButton_Plate_10.clicked.connect(self.roto)
        self.pushButton_Plate_10.clicked.connect(self.close)

        self.pushButton_Plate_11.clicked.connect(self.projection)
        self.pushButton_Plate_11.clicked.connect(self.close)


        self.pushButton_Plate_17.clicked.connect(self.copy_from_user)

        self.pushButton_Plate_17.setShortcut('Return')
        

        self.pushButton_Plate_17.clicked.connect(self.close)
        







        
    def copy_from_user(self):
        self.textEdit.toPlainText()

        







 #Custom  
    def copy_from_user(self):


       bd_node = autoBackdropmd()
       bd_node['label'].setValue(self.lineEdit.text())
       bd_node['note_font'].setValue('bold')
       bd_node['note_font_size'].setValue(50)



 #Custom  
    def Cleanup(self):


       bd_node = autoBackdropmd()
       bd_node['label'].setValue('Cleanup')
       bd_node['note_font'].setValue('bold')
       bd_node['note_font_size'].setValue(50)




 #Custom  
    def roto(self):


       bd_node = autoBackdropmd()
       bd_node['label'].setValue('roto')
       bd_node['note_font'].setValue('bold')
       bd_node['note_font_size'].setValue(50)


 #Custom  
    def projection(self):


       bd_node = autoBackdropmd()
       bd_node['label'].setValue('roto')
       bd_node['note_font'].setValue('bold')
       bd_node['note_font_size'].setValue(50)



 #ForPlate   
    def Plate(self):


       bd_node = autoBackdropmd()
       bd_node['label'].setValue('Plate')
       bd_node['note_font'].setValue('bold')
       bd_node['note_font_size'].setValue(50)
       bd_node['tile_color'].setValue(hex_color_to_rgb(.24,.24,.24))

#For Key
    def Keying(self):


       bd_node = autoBackdropmd()
       bd_node['label'].setValue('Key')
       bd_node['note_font'].setValue('bold')
       bd_node['note_font_size'].setValue(50)
       bd_node['tile_color'].setValue(hex_color_to_rgb(.15,.25,.15))


#For Denoise
    def Denoise(self):


       bd_node = autoBackdropmd()
       bd_node['label'].setValue('Denoise')
       bd_node['note_font'].setValue('bold')
       bd_node['note_font_size'].setValue(50)
       bd_node['tile_color'].setValue(hex_color_to_rgb(.30,.30,.30))


#For Despill

    def Desipill(self):


       bd_node = autoBackdropmd()
       bd_node['label'].setValue('Desipill')
       bd_node['note_font'].setValue('bold')
       bd_node['note_font_size'].setValue(50)
       bd_node['tile_color'].setValue(hex_color_to_rgb(.3,.1,0))
            



#For CC

    def CC(self):


       bd_node = autoBackdropmd()
       bd_node['label'].setValue('Color Correction')
       bd_node['note_font'].setValue('bold')
       bd_node['note_font_size'].setValue(50)
       bd_node['tile_color'].setValue(hex_color_to_rgb(.15,.20,.25))


#For Transform

    def Transfrom(self):


       bd_node = autoBackdropmd()
       bd_node['label'].setValue('Transfrom')
       bd_node['note_font'].setValue('bold')
       bd_node['note_font_size'].setValue(50)
       bd_node['tile_color'].setValue(hex_color_to_rgb(.3,0,.3))



#For 3d

    def ThreeD(self):


       bd_node = autoBackdropmd()
       bd_node['label'].setValue('3d')
       bd_node['note_font'].setValue('bold')
       bd_node['note_font_size'].setValue(50)
       bd_node['tile_color'].setValue(hex_color_to_rgb(.05,0.01,.03))



#For DMP

    def DMP(self):


       bd_node = autoBackdropmd()
       bd_node['label'].setValue('DMP')
       bd_node['note_font'].setValue('bold')
       bd_node['note_font_size'].setValue(50)
       bd_node['tile_color'].setValue(hex_color_to_rgb(0.1,.1,0.3))




#For Precomp

    def Precomp(self):


       bd_node = autoBackdropmd()
       bd_node['label'].setValue('Precomp')
       bd_node['note_font'].setValue('bold')
       bd_node['note_font_size'].setValue(50)
       bd_node['tile_color'].setValue(hex_color_to_rgb(.4,.4,0.4))





#For Grain

    def Grain(self):


       bd_node = autoBackdropmd()
       bd_node['label'].setValue('Grain')
       bd_node['note_font'].setValue('bold')
       bd_node['note_font_size'].setValue(50)
       bd_node['tile_color'].setValue(hex_color_to_rgb(.7,.7,.7))



#For Render

    def Render(self):


       bd_node = autoBackdropmd()
       bd_node['label'].setValue('Render')
       bd_node['note_font'].setValue('bold')
       bd_node['note_font_size'].setValue(50)
       bd_node['tile_color'].setValue(hex_color_to_rgb(.5,0,0))


#For LensFX

    def LensFX(self):


       bd_node = autoBackdropmd()
       bd_node['label'].setValue('LensFX/Filter')
       bd_node['note_font'].setValue('bold')
       bd_node['note_font_size'].setValue(50)
       bd_node['tile_color'].setValue(hex_color_to_rgb(.4,.2,.1))


#For Alpha

    def Alpha(self):


       bd_node = autoBackdropmd()
       bd_node['label'].setValue('Alpha')
       bd_node['note_font'].setValue('bold')
       bd_node['note_font_size'].setValue(50)
       bd_node['tile_color'].setValue(hex_color_to_rgb(.8,.8,.8))




def backdrop_helper():
    backdrop_helper.md_backdrop = md_backdrop()
    backdrop_helper.md_backdrop.show()

