################

"""
	sb_saveRenderBackup
	Simon Bjork
	August 2014
	bjork.simon@gmail.com

	Synopsis: Saves a copy of the current script after a render is complete.
	OS: Windows/OSX/Linux
	
	CAUTION: The script will save a copy every time, no matter if the current state is saved or not. Make sure you empty the backup path every once in a while.

	To install the script:

	- Add the script to your Nuke pluginPath.
	- Add the following to your init.py:

	import sb_saveRenderBackup
	nuke.addAfterRender(sb_saveRenderBackup.sb_saveRenderBackup, (<backup path>))

"""
################

import nuke
import nukescripts
import os
from time import strftime

################

def getFolderSize(path):
   
	total_size = 0
	
	for dirpath, dirnames, filenames in os.walk(path):
		
		for f in filenames:
			
			fp = os.path.join(dirpath, f)
			total_size += os.path.getsize(fp)

	return total_size/1024/1024

def sb_saveRenderBackup(folderPath, folderSizeWarning=1000):

	if not folderPath.endswith("/"):
		folderPath = "{0}/".format(folderPath)

	if not os.path.exists(folderPath):
		try:
			os.makedirs(folderPath)
		except:
			raise Exception ("Can't create folder at:\n\n{0}".format(folderPath))

	# Folder size in mb.
	folderSize = getFolderSize(folderPath)

	if folderSize > folderSizeWarning:
		print "sb_saveRenderBackup are currently using {0} megabytes in {1}. Time to clean up?".format(folderSize, folderPath)

	currScriptPath = nuke.root()["name"].value()

	currScriptName = currScriptPath.split("/")[-1][:-3]

	if not currScriptName:
		currScriptName = "untitled"

	currTime = strftime("%Y-%m-%d_%H-%M-%S")

	# File path for backup script.
	backupFilePath = "{0}{1}_{2}.nk".format(folderPath, currScriptName, currTime)

	# If the script is saved (and not modified), just save a copy of the file.
	if not nuke.modified():

		try:
			nuke.scriptSave(backupFilePath)
			nuke.root()["name"].setValue(currScriptPath)
		except:
			raise Exception ("Could not save a backup of script to {0}".format(backupFilePath))

		return True

	# If the script is modified or not saved, copy nodes instead.
	selNodes = []

	# Select all nodes and save script.
	for i in nuke.allNodes():
		if i["selected"].value() == True:
			selNodes.append(i)
		else:
			i["selected"].setValue(True)

	try:
		# Backup script.
		nuke.nodeCopy(backupFilePath)

		# The Root node isn't saved with nuke.nodeCopy, so it needs to be saved separately.
		# First let's save some knobs manually.
		rootValues = ""
		r = nuke.Root() 
		wantedKnobs = ['inputs', 'frame', 'first_frame', 'last_frame', 'proxy', 'proxy_type', 'proxy_format', 'label']
		for k, v in r.knobs().iteritems(): 
			if not k in wantedKnobs:
				continue
			knobValue = r[k].toScript()
			if not knobValue:
				knobValue = '""'
			if len(knobValue.split(" ")) > 1:
				knobValue = '"' + knobValue + '"'

			rootValues = "{0}\n{1} {2}".format(rootValues, k, knobValue)

		# Add more root knobs via the writeKnobs function.
		# This will add user created knobs as well.
		moreRootKnobs = nuke.root().writeKnobs(nuke.TO_SCRIPT | nuke.WRITE_USER_KNOB_DEFS)
		rootValues = "{0}{1}".format(rootValues, moreRootKnobs)

		# Open saved backup script.
		f = open(backupFilePath,"r")
		savedNodes = f.read()
		f.close()

		# Combine root values with the rest of the nodes.
		allNodes = "Root {0}\n{1}\n{2}\n{3}".format("{", rootValues.strip(), "}", savedNodes)

		f = open(backupFilePath, "w")
		f.write(allNodes)
	except:
		raise Exception ("Could not save a backup of current script to {0}".format(backupFilePath))

	# Deselect all nodes (in groups as well)
	nukescripts.clear_selection_recursive()

	for i in selNodes:
		i["selected"].setValue(True)

	nuke.tprint("sb SaveRenderBackup: Nuke-script successfully backed-up at {0}.".format(backupFilePath))

