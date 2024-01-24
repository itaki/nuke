import renderlist as rl_main
import renderlist_functions as rl_functions

from PySide2 import QtGui, QtCore, QtWidgets

class InfoWindow(QtWidgets.QWidget):
	#This window displays information about the selected item in the list
	def __init__(self, n):
		super(InfoWindow, self).__init__()

		self.n = n

		#Setup window sizing
		self.setMinimumWidth(300)
		self.setMinimumHeight(200)

		#Setup window title
		self.setWindowTitle("Script Info")

		#Setup custom text box style
		self.textBoxPalette = QtGui.QPalette()
		self.textBoxPalette.setColor(QtGui.QPalette.Base, QtGui.QColor('gray'))

		#Setup widgets
		self.nameLEdit = QtWidgets.QLabel(str(rl_main.renderList[self.n].name))
		self.nameLEdit.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
		self.nameLEdit.setStyleSheet("QLabel { background-color : rgb(60, 60, 60); }")

		self.statusLabel = QtWidgets.QLabel(rl_main.renderList[self.n].status)
		if rl_main.renderList[self.n].status == "Queued":
			self.statusLabel.setStyleSheet("QLabel { color: rgb(255, 255, 255); font-size: 11px; }") #WHITE - Queued
		if rl_main.renderList[self.n].status == "Rendering":
			self.statusLabel.setStyleSheet("QLabel { color: rgb(50, 255, 50); font-size: 11px; }") #GREEN - Rendering
		if rl_main.renderList[self.n].status == "Complete":
			self.statusLabel.setStyleSheet("QLabel { color: rgb(50, 150, 255); font-size: 11px; }") #BLUE - Complete
		if rl_main.renderList[self.n].status == "Failed":
			self.statusLabel.setStyleSheet("QLabel { color: rgb(255, 50, 50); font-size: 11px; }") #RED - Failed


		self.notesLEdit = QtWidgets.QLineEdit(str(rl_main.renderList[self.n].comment))
		self.notesLEdit.setStyleSheet("QLineEdit { border: none }")

		self.pathLEdit = QtWidgets.QLabel(str(rl_main.renderList[self.n].path))
		self.pathLEdit.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
		self.pathLEdit.setStyleSheet("QLabel { background-color : rgb(60, 60, 60); }")

		self.renderPathLEdit = QtWidgets.QLabel(str(rl_main.renderList[self.n].renderPath))
		self.renderPathLEdit.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
		self.renderPathLEdit.setStyleSheet("QLabel { background-color : rgb(60, 60, 60); }")

		self.errHeader = QtWidgets.QLabel("<b>Error:</b>")
		self.errHeader.setStyleSheet("QLabel { color: rgb(255, 50, 50); font-size: 11px; }") #RED - Failed

		self.errLEdit = QtWidgets.QLabel(str(rl_main.renderList[self.n].errmsg).strip())
		self.errLEdit.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
		self.errLEdit.setStyleSheet("QLabel { background-color : rgb(60, 60, 60); }")

		self.btnOk = QtWidgets.QPushButton("OK")
		self.btnOk.clicked.connect(self.done)

		self.HLine = QtWidgets.QFrame()
		self.HLine.setFrameShape(QtWidgets.QFrame.HLine)
		self.HLine.setFrameShadow(QtWidgets.QFrame.Sunken)
		self.HLine2 = QtWidgets.QFrame()
		self.HLine2.setFrameShape(QtWidgets.QFrame.HLine)
		self.HLine2.setFrameShadow(QtWidgets.QFrame.Sunken)

		#Setup form layout for all options
		self.formLayout = QtWidgets.QFormLayout()
		self.formLayout.addRow(self.tr("<b>#</b>"), QtWidgets.QLabel(str(self.n+1)+" of "+str(len(rl_main.renderList))))
		self.formLayout.addRow(self.tr("<b>Name</b>"), self.nameLEdit)
		self.formLayout.addRow(self.tr("<b>Status</b>"), self.statusLabel)
		self.formLayout.setWidget(3, QtWidgets.QFormLayout.SpanningRole, self.HLine)
		self.formLayout.addRow(self.tr("<b>Notes</b>"), self.notesLEdit)
		framerange = rl_main.renderList[self.n].frames.split("-")
		framerange = int(framerange[1])-int(framerange[0])+1
		self.formLayout.addRow(self.tr("<b>Frames</b>"), QtWidgets.QLabel("%s (%s frames)" % (str(rl_main.renderList[self.n].frames), framerange)))
		self.formLayout.addRow(self.tr("<b>Script Path</b>"), self.pathLEdit)
		self.formLayout.addRow(self.tr("<b>Render Path</b>"), self.renderPathLEdit)

		if rl_main.renderList[self.n].errmsg:
			self.formLayout.addRow(self.errHeader, self.errLEdit)

		self.btnLayout = QtWidgets.QHBoxLayout()
		self.btnLayout.setAlignment(QtCore.Qt.AlignRight)
		self.btnLayout.addWidget(self.btnOk)

		self.vbox = QtWidgets.QVBoxLayout()
		self.vbox.addLayout(self.formLayout)
		self.vbox.addWidget(self.HLine2)
		self.vbox.addLayout(self.btnLayout)

		self.setLayout(self.vbox)

	def done(self):
		rl_main.renderList[self.n].comment = self.notesLEdit.text()
		rl_functions.saveList()
		self.close()