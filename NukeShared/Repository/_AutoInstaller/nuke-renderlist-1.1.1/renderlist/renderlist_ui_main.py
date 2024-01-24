import nuke
import re
import subprocess
import os

import renderlist as rl_main
import renderlist_functions as rl_functions
import renderlist_ui_addscript as ui_addscript
import renderlist_ui_getinfo as ui_getinfo
import renderlist_renderstatuswidget as rl_RenderStatusWidget

from PySide2 import QtGui, QtCore, QtWidgets

"""
This is the main UI window and logic for renderlist, handling adding scripts, removing scripts and rendering, and any UI updates that happen as a result
"""

class RenderListWindow(QtWidgets.QWidget):
	#This is the main window of the program
	def __init__(self):
		super(RenderListWindow, self).__init__()

		#Render progress variables
		self.firstFrame = 0
		self.lastFrame = 0
		self.currentFrame = 0
		self.percentComplete = 0

		#Setup window sizing
		self.setGeometry(50, 50, 600, 500)
		self.setMinimumWidth(600)
		self.setMinimumHeight(500)

		#Setup window title
		self.setWindowTitle("Renderlist")

		#Setup widgets
		self.addBtn = QtWidgets.QPushButton("+ Add script")
		self.addBtn.clicked.connect(self.addBtnClicked)
		self.delBtn = QtWidgets.QPushButton("- Delete script")
		self.delBtn.clicked.connect(self.delBtnClicked)
		self.renderBtn = QtWidgets.QPushButton("Render")
		self.renderBtn.clicked.connect(lambda: self.startRender(True))

		self.shutdownCbox = QtWidgets.QCheckBox("Shutdown PC")
		self.shutdownCbox.setToolTip("Shutdown PC when all renders are finished")

		#Setup layouts
		self.leftBtnLayout = QtWidgets.QHBoxLayout()
		self.leftBtnLayout.setAlignment(QtCore.Qt.AlignLeft)

		self.rightBtnLayout = QtWidgets.QHBoxLayout()
		self.rightBtnLayout.setAlignment(QtCore.Qt.AlignRight)

		self.btnLayout = QtWidgets.QHBoxLayout()

		self.vbox = QtWidgets.QVBoxLayout()

		#Add widgets to layouts
		self.leftBtnLayout.addWidget(self.addBtn)
		self.leftBtnLayout.addWidget(self.delBtn)

		self.rightBtnLayout.addWidget(self.shutdownCbox)
		self.rightBtnLayout.addWidget(self.renderBtn)

		self.btnLayout.addLayout(self.leftBtnLayout)
		self.btnLayout.addLayout(self.rightBtnLayout)

		#Render Table
		self.renderTable = QtWidgets.QTableWidget()
		self.renderTable.header = ['Name', 'Frames', 'Status']
		self.renderTable.size = [ 75, 375, 85, 600 ]

		self.renderTable.setColumnCount(len(self.renderTable.header))
		self.renderTable.setHorizontalHeaderLabels(self.renderTable.header)
		self.renderTable.setSortingEnabled(0)
		self.renderTable.setAlternatingRowColors(True)
		self.renderTable.setRowCount(0)
		self.renderTable.horizontalHeader().setStretchLastSection(True)
		self.renderTable.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
		self.renderTable.setShowGrid(False)
		self.renderTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
		self.renderTable.setFocusPolicy(QtCore.Qt.NoFocus)
		self.renderTable.setColumnWidth(0, 250)

		#Render Table RightClick Menu
		self.renderTable.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
		self.renderTableRCInfoAction = QtWidgets.QAction("Get Info...", None)
		self.renderTableRCInfoAction.triggered.connect(self.showInfo)
		self.renderTableRCSep = QtWidgets.QAction(None)
		self.renderTableRCSep.setSeparator(True)
		self.renderTableRCDelAction = QtWidgets.QAction("Delete", None)
		self.renderTableRCDelAction.triggered.connect(self.delBtnClicked)
		self.renderTableRCViewScriptAction = QtWidgets.QAction("Open Script Folder", None)
		self.renderTableRCViewScriptAction.triggered.connect(self.openScriptFolder)
		self.renderTableRCViewRenderAction = QtWidgets.QAction("Open Render Folder", None)
		self.renderTableRCViewRenderAction.triggered.connect(self.openRenderFolder)
		self.renderTable.addAction(self.renderTableRCInfoAction)
		self.renderTable.addAction(self.renderTableRCSep)
		self.renderTable.addAction(self.renderTableRCDelAction)
		#self.renderTable.addAction(self.renderTableRCMUpAction)
		#self.renderTable.addAction(self.renderTableRCMDwnAction)
		self.renderTable.addAction(self.renderTableRCViewScriptAction)
		self.renderTable.addAction(self.renderTableRCViewRenderAction)

		self.vbox.addLayout(self.btnLayout)
		self.vbox.addWidget(self.renderTable)

		self.setLayout(self.vbox)

	def addBtnClicked(self):
		#Shows the "Add Script" window. Called from Add Script button being pressed
		if nuke.root().name() == "Root":
			nuke.message("This script must be saved before it can be added to RenderList!")

		else:
			if rl_main.rendering == False:
				#Passing through 'self' as an argument to make sure the function called in AddScriptWindow references this instance of RenderListWindow (thanks connor)
				self.addScriptWindow = ui_addscript.AddScriptWindow(self)
				self.addScriptWindow.reset()
				self.addScriptWindow.show()
				
			else:
				nuke.message("Can't modify the list when a render is running!")

	def delBtnClicked(self):
		#Removes the currently selected script from the list. Called from Delete Script button being pressed
		modifiers = QtWidgets.QApplication.keyboardModifiers()

		if len(rl_main.renderList) > 0:
			if rl_main.rendering == False:
				if modifiers == QtCore.Qt.AltModifier:
					#Alt clicking allows us to delete all renders in the list
					if nuke.ask("Are you sure you want to delete all items from the list?"):
						del rl_main.renderList[:]
						self.updateTable()
						rl_functions.saveList()
				else:
					selectedRow = self.renderTable.currentRow()

					if rl_main.renderList[selectedRow].status == "Queued":
						if nuke.ask("Are you sure you want to delete "+str(rl_main.renderList[selectedRow].name)+" from the list?"):
							self.removeScriptFromList(selectedRow)

					elif rl_main.renderList[selectedRow].status == "Rendering":
						if nuke.ask(str(rl_main.renderList[selectedRow].name)+" is rendering!\nAre you sure you want to cancel this render and delete it from the list?"):
							self.removeScriptFromList(selectedRow)

					else:
						self.removeScriptFromList(selectedRow)

			else:
				nuke.message("Can't modify the list when a render is running!")

	def startRender(self, clicked):
		#First, checks if any scripts in the list are failed and gives user the choice to re-queue them, then renders the next queued script each time we go in
		if rl_main.rendering == False:
			if len(rl_main.renderList) > 0:
				if clicked == True: #If a human started the render
					
					#Check for failed scripts in the list
					failedScripts = 0
					for script in rl_main.renderList:
						if script.status == "Failed":
							failedScripts = failedScripts + 1

					#If there are failed scripts, ask the user if they want to re-queue them
					if failedScripts > 0:
						if nuke.ask("There are failed renders in the list.\nDo you want to re-queue them?"):
							for script in rl_main.renderList:
								if script.status == "Failed":
									script.status = "Queued"

				for script in rl_main.renderList:
					if script.status == "Queued":
						rl_main.rendering = True
						script.status = "Rendering"
						rl_main.currentlyRendering = script
						self.updateTable()
						
						rl_functions.debugMsg("Rendering script: %s" % rl_main.currentlyRendering.name)

						if rl_main.currentlyRendering.writeNode != "":
							cmdArgs = ['-X', rl_main.currentlyRendering.writeNode, '-F', rl_main.currentlyRendering.frames, rl_main.currentlyRendering.path]
						else:
							cmdArgs = ['-x', '-F', rl_main.currentlyRendering.frames, rl_main.currentlyRendering.path]

						#print("%s %s" % (rl_main.nukeExecPath, cmdArgs))

						self.firstFrame = float(rl_main.currentlyRendering.frames.split("-")[0])
						self.lastFrame = float(rl_main.currentlyRendering.frames.split("-")[1])
						self.currentFrame = self.firstFrame
						self.percentComplete = 0

						renderProcess = QtCore.QProcess(self)
						renderProcess.readyReadStandardOutput.connect(self.handleStdout)
						renderProcess.readyReadStandardError.connect(self.handleStderr)
						renderProcess.stateChanged.connect(self.handleState)
						renderProcess.finished.connect(self.processFinished)
						renderProcess.start(rl_main.nukeExecPath, cmdArgs)
						return

				if self.shutdownCbox.isChecked() == True:
					rl_functions.debugMsg("All renders are done")
					subprocess.call(["shutdown", "-s"])
			else:
				rl_functions.debugMsg("The render list is empty")
		else:
			rl_functions.debugMsg("Already rendering")

	def handleState(self, state):
		states = {
			QtCore.QProcess.NotRunning: 'Not running',
			QtCore.QProcess.Starting: 'Starting',
			QtCore.QProcess.Running: 'Running',
			}
		state_name = states[state]
		#print("State changed: %s" % state_name)

	def handleStdout(self):
		process = self.sender()
		data = process.readAllStandardOutput()
		stdout = bytes(data).decode("utf8")

		progressRe = re.compile("Frame (\d+)")

		m = progressRe.search(stdout)
		if m:
			mInt = int(m.group(1))
			if mInt > self.currentFrame:
				self.currentFrame = mInt
				self.percentComplete = int(round(((self.currentFrame-self.firstFrame)/(self.lastFrame-self.firstFrame+1))*100))
				rl_main.currentlyRendering.progress = self.percentComplete
				self.updateTable()

	def handleStderr(self):
		process = self.sender()
		data = process.readAllStandardError()
		stderr = bytes(data).decode("utf8")
		rl_functions.debugMsg("STDERR DETECTED")

		#There has been stderr, so the script must've failed, right?
		rl_main.currentlyRendering.status = "Failed"
		rl_main.currentlyRendering.errmsg = stderr

	def processFinished(self):
		rl_functions.debugMsg("Process finished")
		if rl_main.currentlyRendering.status == "Failed":
			rl_functions.debugMsg("Render failed with error: %s" % rl_main.currentlyRendering.errmsg)
		else:
			rl_functions.debugMsg("Render finished for %s" % rl_main.currentlyRendering.name)
			rl_main.currentlyRendering.status = "Complete"
		
		rl_main.rendering = False
		rl_functions.saveList()
		self.updateTable()
		self.startRender(False)

	def addScriptToList(self, name, comment, frames, path, renderPath, writeNode):
		#Called when we hit OK on the Add Script window. The AddScript window passes the input collected from the user to this function, which creates a ScriptListItem, fills in all the info, and adds that item to the renderList[]
		newListItem = rl_main.ScriptListItem()
		newListItem.number = len(rl_main.renderList)
		newListItem.name = name
		newListItem.comment = comment
		newListItem.frames = frames
		newListItem.path = path
		newListItem.renderPath = renderPath
		newListItem.writeNode = writeNode
		newListItem.status = "Queued"

		rl_functions.debugMsg("Adding script to render list")
		rl_functions.debugMsg("Number: %s" % str(newListItem.number))
		rl_functions.debugMsg("Name: %s" % (newListItem.name))
		rl_functions.debugMsg("Comment: %s" % (newListItem.comment))
		rl_functions.debugMsg("Frames: %s" % (newListItem.frames))
		rl_functions.debugMsg("Path: %s" % (newListItem.path))
		rl_functions.debugMsg("Render Path: %s" % (newListItem.renderPath))
		rl_functions.debugMsg("Write Node: %s" % (newListItem.writeNode))
		rl_functions.debugMsg("Status: %s" % (newListItem.status))

		rl_main.renderList.append(newListItem)

		rl_functions.debugMsg("Render list contains %s items" % (str(len(rl_main.renderList))))

		rl_functions.saveList()

		self.updateTable()

	def removeScriptFromList(self, num):
		del rl_main.renderList[num]

		for i in range(len(rl_main.renderList)):
			rl_main.renderList[i].number = i

		self.updateTable()

		rl_functions.saveList()

	def updateTable(self):
		#rl_functions.debugMsg("Updating table")
		#Populates the renderTable with the contents of the renderList[]
		self.renderTable.clear()
		self.renderTable.setHorizontalHeaderLabels(self.renderTable.header)
		self.renderTable.setRowCount(len(rl_main.renderList))

		self.RenderStatusWidget = list(range(len(rl_main.renderList)))

		for script in rl_main.renderList:
			rlNameItem = QtWidgets.QTableWidgetItem(script.name)
			rlNameItem.setToolTip(script.path)
			self.renderTable.setItem(script.number, 0, rlNameItem)

			rlFramesItem = QtWidgets.QTableWidgetItem(script.frames)
			rlFramesItem.setTextAlignment(QtCore.Qt.AlignCenter)
			framerange = script.frames.split("-")
			framerange = int(framerange[1])-int(framerange[0])+1
			rlFramesItem.setToolTip(str(framerange)+" frames")
			self.renderTable.setItem(script.number, 1, rlFramesItem)

			self.RenderStatusWidget[script.number] = rl_RenderStatusWidget.RenderStatusWidget(script.number)
			self.renderTable.setCellWidget(script.number, 2, self.RenderStatusWidget[script.number])

	def showInfo(self):
		#Spawn a show info window for the currently selected script
		selectedRow = self.renderTable.currentRow()

		if selectedRow != -1:
			self.infoWindow = ui_getinfo.InfoWindow(selectedRow)
			self.infoWindow.show()

	def openScriptFolder(self):
		selectedRow = self.renderTable.currentRow()

		if selectedRow != -1:
			path = os.path.dirname(rl_main.renderList[selectedRow].path)
			QtGui.QDesktopServices.openUrl(path)

	def openRenderFolder(self):
		selectedRow = self.renderTable.currentRow()

		if selectedRow != -1:
			path = os.path.dirname(rl_main.renderList[selectedRow].renderPath)
			QtGui.QDesktopServices.openUrl(path)