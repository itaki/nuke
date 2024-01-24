import nuke
import os
import subprocess
import json

import renderlist as rl_main
import renderlist_ui_main as ui_main

"""
This file contains core functionality of renderlist. Loading, saving, getting script names and frame ranges
"""

def getNukeScriptName():
	#Return only the name of the nuke script. EG: C:/whatever/whatever/myscript.nk becomes myscript.nk
	return os.path.basename(nuke.root().name())

def getNukeFrameRange():
	#Get the current Nuke global frame range, and return it formatted as "000-000"
	frameRange = str(nuke.root().firstFrame())+"-"+str(nuke.root().lastFrame())
	return frameRange

def debugMsg(msg):
	#Writes a debug message with prefix to the Nuke script editor window
	if rl_main.debugMode == True:
		print("[RENDERLIST][DEBUG] %s" % str(msg))

def saveList():
	#Writes the contents of the renderList[] to a JSON file
	debugMsg("Saving RenderList to file...")

	data = {}
	data['scripts'] = []  

	for script in rl_main.renderList:
		data['scripts'].append({  
			'number': script.number,
			'name': script.name,
			'comment': script.comment,
			'frames': script.frames,
			'path': script.path,
			'renderPath' : script.renderPath,
			'writeNode': script.writeNode,
			'status': script.status,
			'errmsg': script.errmsg
		})

	with open(rl_main.renderListFilePath, 'w') as outfile:  
		json.dump(data, outfile)

def loadList():
	#Populates the renderList[] with the contents of the JSON file
	debugMsg("Loading RenderList from file...")

	if os.path.isfile(rl_main.renderListFilePath):
		with open(rl_main.renderListFilePath) as json_file:
			data = json.load(json_file)
			debugMsg("%s items in list file" % (len(data['scripts'])))
			del rl_main.renderList[:] #Clear the renderList

			for script in data['scripts']:
				"""
				debugMsg("Number: "+str(script['number']))
				debugMsg("Name: "+script['name'])
				debugMsg("Comment: "+script['comment'])
				debugMsg("Frames: "+script['frames'])
				debugMsg("Path: "+script['path'])
				debugMsg("Status: "+script['status'])
				debugMsg("ErrMsg: "+script['errmsg'])
				"""

				newListItem = rl_main.ScriptListItem()
				newListItem.number = script['number']
				newListItem.name = script['name']
				newListItem.comment = script['comment']
				newListItem.frames = script['frames']
				newListItem.path = script['path']
				newListItem.renderPath = script['renderPath']
				newListItem.writeNode = script['writeNode']
				newListItem.status = script['status']
				newListItem.errmsg = script['errmsg']

				rl_main.renderList.append(newListItem)

	else:
		debugMsg("RenderList file doesn't exist!")