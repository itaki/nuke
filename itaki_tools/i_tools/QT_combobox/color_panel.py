import os
import nuke
import webbrowser

#****************************************************************
#*********************** THIS IS DIFFERENT***********************
#****************************************************************
if nuke.NUKE_VERSION_MAJOR < 11:
	from PySide.QtGui import *
	from PySide.QtCore import *
	from PySide.QtUiTools import QUiLoader
	from PySide import QtCore, QtGui, QtUiTools, QtGui as QtWidgets
else:
	from PySide2.QtGui import *
	from PySide2.QtCore import *
	from PySide2.QtUiTools import QUiLoader
	from PySide2 import QtCore, QtGui, QtUiTools, QtGui, QtWidgets



thisFileDir = os.path.dirname(os.path.realpath(__file__))
file_interface = os.path.join(thisFileDir, "ColorPanel.ui")


global color_copied
color_copied = None

#****************************************************************
#*********************** THIS IS DIFFERENT***********************
#****************************************************************
class MyWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.main_widget = self.load_ui(file_interface)
        self.setCentralWidget(self.main_widget)
        self.setWindowTitle("ColorPanel")
        #windows always on top
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        
        #set Fixed Sizes
        self.setFixedWidth(361)
        self.setFixedHeight(628)

        self.load_ui_elements()


#****************************************************************
#*********************** THIS IS DIFFERENT***********************
#****************************************************************
    def load_ui(self, ui_file):
        loader = QUiLoader()
        file = QFile(ui_file)
        file.open(QFile.ReadOnly)
        myWidget = loader.load(file, None)
        file.close()
        return myWidget


    def load_ui_elements(self):
            self.button1 = self.main_widget.findChild(QtWidgets.QPushButton, 'button1')
            self.button1.clicked.connect(lambda: self.changeColorNode(self.button1.styleSheet()))

            self.button2 = self.main_widget.findChild(QtWidgets.QPushButton, 'button2')
            self.button2.clicked.connect(lambda: self.changeColorNode(self.button2.styleSheet()))

            self.button3 = self.main_widget.findChild(QtWidgets.QPushButton, 'button3')
            self.button3.clicked.connect(lambda: self.changeColorNode(self.button3.styleSheet()))

            self.button4 = self.main_widget.findChild(QtWidgets.QPushButton, 'button4')
            self.button4.clicked.connect(lambda: self.changeColorNode(self.button4.styleSheet()))

            self.button5 = self.main_widget.findChild(QtWidgets.QPushButton, 'button5')
            self.button5.clicked.connect(lambda: self.changeColorNode(self.button5.styleSheet()))

            self.button6 = self.main_widget.findChild(QtWidgets.QPushButton, 'button6')
            self.button6.clicked.connect(lambda: self.changeColorNode(self.button6.styleSheet()))  

            #.
            #.
            #.

            self.button56 = self.main_widget.findChild(QtWidgets.QPushButton, 'button56')
            self.button56.clicked.connect(lambda: self.changeColorNode(self.button56.styleSheet()))

            self.button57 = self.main_widget.findChild(QtWidgets.QPushButton, 'button57')
            self.button57.clicked.connect(lambda: self.changeColorNode(self.button57.styleSheet()))

            self.button58 = self.main_widget.findChild(QtWidgets.QPushButton, 'button58')
            self.button58.clicked.connect(lambda: self.changeColorNode(self.button58.styleSheet()))    

            self.button59 = self.main_widget.findChild(QtWidgets.QPushButton, 'button59')
            self.button59.clicked.connect(lambda: self.changeColorNode(self.button59.styleSheet()))

            self.button60 = self.main_widget.findChild(QtWidgets.QPushButton, 'button60')
            self.button60.clicked.connect(lambda: self.changeColorNode(self.button60.styleSheet()))


            self.customColor = self.main_widget.findChild(QtWidgets.QPushButton, 'customColor')
            self.customColor.clicked.connect(self.changeColorNodeCustom)
            
            self.restoreColor = self.main_widget.findChild(QtWidgets.QPushButton, 'restoreColor')
            self.restoreColor.clicked.connect(self.restoreOriginalColor)
            
            self.copyButton = self.main_widget.findChild(QtWidgets.QPushButton, 'copyButton')
            self.copyButton.clicked.connect(self.copy_color)

            self.pasteButton = self.main_widget.findChild(QtWidgets.QPushButton, 'pasteButton')
            self.pasteButton.clicked.connect(self.paste_color)
			
            self.infoButton = self.main_widget.findChild(QtWidgets.QPushButton, 'infoButton')
            self.infoButton.clicked.connect(self.website)
			
            self.checkboxClose = self.main_widget.findChild(QtWidgets.QCheckBox, 'checkboxClose')


    #if clicked button
    def changeColorNode(self, color):
        color = color.replace('background-color: rgb','').replace(';','').replace('(','').replace(')','').replace(' ','')
        r,g,b = color.split(',')
        #convert from RGB to Hex
        red = float(float(r)/255)
        green = float(float(g)/255)
        blue = float(float(b)/255)
        hexColour = '%02x' % (red*255) + '%02x' % (green*255) + '%02x' % (blue*255)
        weird = int('%02x%02x%02x%02x' % (red*255,green*255,blue*255,1),16)
        #weird = int(hexColour,16)
        print (weird)
        #print self.button.palette().color(QtGui.QPalette.Background).getRgb()

        for node in nuke.selectedNodes():
            node.knob('tile_color').setValue(weird)
        
        self.closeWindow()

#---------------------------------------------------------
    #if clicked custom color button
    def changeColorNodeCustom(self):
        col = nuke.getColor()

        if col:
            for n in nuke.selectedNodes():
                n['tile_color'].setValue(col)
                n['gl_color'].setValue(col)
        print ("COLOR: " + str(col))
        
        self.closeWindow()
#---------------------------------------------------------

    #COPY
    def copy_color(self):
        global color_copied
        if len(nuke.selectedNodes()) >= 1:
            n = nuke.selectedNode()
            if n['tile_color'].getValue()==0:
                color_copied = nuke.defaultNodeColor(n.Class())
            else:
                color_copied = int(n['tile_color'].getValue())
        else:
            nuke.message("select a node")
        if color_copied is None:
            color_copied = 0
        print ("COPIED COLOR: " + str(color_copied))


    #PASTE
    def paste_color(self):
        if color_copied is not None: 
            for n in nuke.selectedNodes(): 
                n['tile_color'].setValue(color_copied)
#---------------------------------------------------------         
	#www
    def website(self):
        webbrowser.open('http://www.andreageremia.it/tutorial_color_panel.html')  # Go to the website
#---------------------------------------------------------
    #close window
    def closeWindow(self):
        if self.checkboxClose.isChecked():
            self.close()
    
#GOOOOOOOOOOOOOOOOOO!
def colorPanel():
    my_window = MyWindow()
    my_window.show()