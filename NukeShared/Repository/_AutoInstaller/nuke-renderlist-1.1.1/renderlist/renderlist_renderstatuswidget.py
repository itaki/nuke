import renderlist as rl_main
import renderlist_functions as rl_functions

from PySide2 import QtGui, QtCore, QtWidgets

"""
RenderStatusWidget is a small widget that appears in the table in the main UI. It's used to display the status of a script in the list
"""

class RenderStatusWidget(QtWidgets.QWidget):
	#A RenderStatusWidget is created for each item in the list whenever the table is updated. The self.n of each RenderStatusWidget corresponds to the nth entry in the renderList[]
	def __init__(self, n):
		super(RenderStatusWidget, self).__init__()

		self.n = n

		self.statusLabel = QtWidgets.QLabel(rl_main.renderList[self.n].status)
		self.setStatus(rl_main.renderList[self.n].status)

		self.hbox = QtWidgets.QHBoxLayout()
		self.hbox.setAlignment(QtCore.Qt.AlignCenter)
		self.hbox.addWidget(self.statusLabel)

		self.setLayout(self.hbox)

	def setStatus(self, status):
		#Sets the text label and color of the RenderStatusWidget

		if status == "Queued":
			rl_main.renderList[self.n].status = status
			self.statusLabel.setText(rl_main.renderList[self.n].status)
			self.statusLabel.setStyleSheet("QLabel { color: rgb(255, 255, 255); font-size: 11px; }") #WHITE - Queued

		if status == "Rendering":
			rl_main.renderList[self.n].status = status
			self.statusLabel.setText(rl_main.renderList[self.n].status+" - "+str(rl_main.renderList[self.n].progress)+"%")
			self.statusLabel.setStyleSheet("QLabel { color: rgb(50, 255, 50); font-size: 11px; }") #GREEN - Rendering

		if status == "Complete":
			rl_main.renderList[self.n].status = status
			self.statusLabel.setText(rl_main.renderList[self.n].status)
			self.statusLabel.setStyleSheet("QLabel { color: rgb(50, 150, 255); font-size: 11px; }") #BLUE - Complete

		if status == "Failed":
			rl_main.renderList[self.n].status = status
			self.statusLabel.setText(rl_main.renderList[self.n].status)
			self.statusLabel.setStyleSheet("QLabel { color: rgb(255, 50, 50); font-size: 11px; }") #RED - Failed