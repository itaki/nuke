import nuke
import re

import renderlist as rl_main
import renderlist_functions as rl_functions
import renderlist_ui_main as ui_main

from PySide2 import QtGui, QtCore, QtWidgets

"""
This is the "add script" popup, which handles adding a new Nuke script to the list and sanitizing inputs
"""

class AddScriptWindow(QtWidgets.QWidget):
	#This window shows options for adding a script to the RenderList
	parentWindow = 0
	def __init__(self, parentWindow):
		super(AddScriptWindow, self).__init__()

		#Keep track of the instance that called this, as we need it for calling the function back in RenderListWindow
		self.parentWindow = parentWindow

		#Setup window sizing
		self.setMinimumWidth(250)

		#Setup window title
		self.setWindowTitle("Add Script")

		#Setup widgets
		self.scriptLEdit = QtWidgets.QLineEdit("")
		self.commentsLEdit = QtWidgets.QLineEdit("")
		self.framesLEdit = QtWidgets.QLineEdit("")
		self.framesLEdit.textChanged.connect(self.textChanged)
		self.framesCombo = QtWidgets.QComboBox()
		self.framesCombo.addItems(["Global", "Custom"])
		self.framesCombo.currentIndexChanged.connect(self.comboChanged)
		self.selectedWritesRadioBtn = QtWidgets.QRadioButton("Selected write node only")
		self.btnOk = QtWidgets.QPushButton("OK")
		self.btnOk.clicked.connect(self.submitToList)
		self.btnCancel = QtWidgets.QPushButton("Cancel")
		self.btnCancel.clicked.connect(self.close)
		self.HLine = QtWidgets.QFrame()
		self.HLine.setFrameShape(QtWidgets.QFrame.HLine)
		self.HLine.setFrameShadow(QtWidgets.QFrame.Sunken)

		#Setup frame range select layout (combo box + line edit)
		self.frameRangeLayout = QtWidgets.QHBoxLayout()
		self.frameRangeLayout.addWidget(self.framesCombo)
		self.frameRangeLayout.addWidget(self.framesLEdit)

		#Setup form layout for all options
		self.formLayout = QtWidgets.QFormLayout()
		self.formLayout.addRow(self.tr("Name"), self.scriptLEdit)
		self.formLayout.addRow(self.tr("Notes"), self.commentsLEdit)
		self.formLayout.addRow(self.tr("Frames"), self.frameRangeLayout)
		self.formLayout.addRow(self.tr(""), self.selectedWritesRadioBtn)

		self.btnLayout = QtWidgets.QHBoxLayout()
		self.btnLayout.setAlignment(QtCore.Qt.AlignRight)
		self.btnLayout.addWidget(self.btnOk)
		self.btnLayout.addWidget(self.btnCancel)

		self.vbox = QtWidgets.QVBoxLayout()
		self.vbox.setAlignment(QtCore.Qt.AlignTop)
		self.vbox.addLayout(self.formLayout)
		self.vbox.addWidget(self.HLine)
		self.vbox.addLayout(self.btnLayout)

		self.setLayout(self.vbox)

	def reset(self):
		#This will run whenever the submit window is opened
		self.scriptLEdit.setText(rl_functions.getNukeScriptName()) #Reset the script name
		self.framesLEdit.setText(rl_functions.getNukeFrameRange()) #Reset the global frame range

	def comboChanged(self):
		#Fill in the Nuke script global frame range if "Global" was selected in the combobox
		if (self.framesCombo.currentText() == "Global"):
			self.framesLEdit.setText(rl_functions.getNukeFrameRange())

	def textChanged(self):
		#If the user types in a different frame range, set the combo box to "Custom"
		if(self.framesLEdit.text() != rl_functions.getNukeFrameRange()):
			self.framesCombo.setCurrentIndex(1)

	def submitToList(self):
		#Check validity of frame range: The user should enter 2 integers separated by a -, or 1 integer.
		self.framesInput = self.framesLEdit.text()

		if re.match("^\d*-\d*$", self.framesInput):
			self.startFrame = self.framesInput.split("-")[0]
			
			try:
				self.endFrame = self.framesInput.split("-")[1]
			except:
				self.endFrame = self.startFrame

			# If the frame range is valid, let's check to see if the user wants to render a specific write node
			self.selectedWriteNode = ""
			self.selectedWriteNodePath = ""

			if self.selectedWritesRadioBtn.isChecked():
				if nuke.selectedNodes():
					for node in nuke.selectedNodes():
						if node.Class() == "Write":
							self.selectedWriteNode = str(node['name'].getValue())
							self.selectedWriteNodePath = str(node['file'].getValue())
							rl_functions.debugMsg("Found a selected write node: %s" % self.selectedWriteNode)
							rl_functions.debugMsg("Selected write path: %s" % self.selectedWriteNodePath)
						else:
							nuke.message("Please select a write node!")
							return
				else:
					nuke.message("Please select a write node!")
					return
			else:
				for node in nuke.allNodes():
					if node.Class() == "Write":
						self.selectedWriteNodePath = str(node['file'].getValue())
						rl_functions.debugMsg("No Write selected, first path found: %s" % self.selectedWriteNodePath)


			#Pass the instance id of the RenderListWindow that called this (parentWindow) so we run the function in the correct RenderListWindow instance
			ui_main.RenderListWindow.addScriptToList(self.parentWindow, 
				str(self.scriptLEdit.text()), 
				str(self.commentsLEdit.text()), 
				str(self.framesInput), 
				str(nuke.root().name()),
				str(self.selectedWriteNodePath), 
				self.selectedWriteNode)

		else:
			rl_functions.debugMsg("User input failed frame range regex")
			nuke.message("Please enter a valid frame range!\neg. 1-100")

		self.close()