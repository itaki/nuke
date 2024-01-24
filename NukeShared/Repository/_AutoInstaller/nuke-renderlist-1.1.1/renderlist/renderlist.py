import nuke
import os
import subprocess
import json

import renderlist_functions as rl_functions
import renderlist_ui_main as ui_main

"""
This is the main renderlist script, it initializes all variables when loaded, and handles creating the main window when main() is called from the Nuke menu
"""

#Setup renderlist variables
debugMode = False
rendering = False
currentlyRendering = 0

#Setup renderlist paths
homeFolderPath = os.path.expanduser('~').replace('\\','/') + '/.nuke/RenderList'
nukeExecPath = nuke.env['ExecutablePath']
renderListFilePath = "%s/renderlist.json" % homeFolderPath

#Render list
renderList = []


class ScriptListItem():
	"""This is an item that will represent a Nuke script in the list, it holds the number, name, comment, framerange, path and status of each script
	Statuses can be: Queued, Rendering, Complete, Failed"""
	def __init__(self):
		self.number = ""
		self.name = ""
		self.comment = ""
		self.frames = ""
		self.path = ""
		self.renderPath = ""
		self.writeNode = ""
		self.status = ""
		self.progress = "" #This currently isn't saved to JSON
		self.errmsg = ""


def main():
	# This is called when renderlist is opened from the Nuke menu
	rl_functions.loadList() #Load the json file that contains the list
	renderListWindow.activateWindow()
	renderListWindow.show()
	renderListWindow.updateTable()

renderListWindow = ui_main.RenderListWindow()