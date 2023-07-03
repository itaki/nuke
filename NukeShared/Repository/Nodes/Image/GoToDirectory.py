# Max van Leeuwen - maxvanleeuwen.com
# GoToDirectory - 1.4
#
# Opens the directory of the path that is currently in the clipboard - except if nodes with a fileKnob are selected, in which case the file paths of the selected nodes will be opened.



import os
import nuke
import subprocess
import sys



GoToDirectoryMessage = '[GoToDirectory] '



# function for converting TCL path to string
def evalTCL(text):

	# make sure it's a string
	text = str(text)

	val = ''
	try:
		val = nuke.tcl("[return \"" + text + "\"]")
	except Exception as e:
		# TCL not working for this string
		pass

	# only allow string type to be returned
	if type(val) is not str:
		val = text
	
	return val



# function that reads clipboard
def get_clipboard_text():

	text = ""

	# get clipboard text
	try:
		from PySide2 import QtWidgets
	except:
		from PySide import QtGui as QtWidgets

	text = QtWidgets.QApplication.clipboard().text()
	
	# return clipboard text
	return text



# open explorer/finder to path
def openFolderFromString(folder, knobName = 'clipboard'):

	# evaluate TCL and make sure all slashes are forward ('/')
	TCLfolder = evalTCL( folder.replace('\\', '/') )
	TCL = not( str(TCLfolder) == str(folder) )


	# reset variable
	foundFolderPath = TCLfolder

	found = False
	projdir = False

	# if the file or folder does not exist
	if not os.path.isdir(foundFolderPath) and not os.path.isfile(foundFolderPath):

		# check if it is a Project Directory relative path
		projectdir = nuke.root()['project_directory'].getValue()
		if projectdir is not '':
			
			# TCL on project directory
			projectdir = evalTCL(projectdir)

			# join paths
			foundFolderPath = os.path.join(projectdir, foundFolderPath)

		projdir = True


	# check if that helped, if not reset
	if not os.path.isdir(foundFolderPath) and not os.path.isfile(foundFolderPath):
		
		projdir = False
		foundFolderPath = TCLfolder


	# check if project directory prefix works
	if not os.path.isdir(foundFolderPath):

		foundFolderPath = os.path.dirname(foundFolderPath)

		# if not, try with its parent dir
		if not os.path.isdir(foundFolderPath):

			# reset variable and ignore project directory
			foundFolderPath = TCLfolder
			projdir = False

		else:

			# project directory prefix works
			found = True


	attempts = 0
	# check if the path is an existing directory (skip if already working with project directory prefix)
	if not os.path.isdir(foundFolderPath) and not found:

		# only try to find a working parent path 3 times
		folderFound = False

		while attempts < 3 and not folderFound:

			# try the parent of the previous folder
			foundFolderPath = os.path.dirname(foundFolderPath)

			if os.path.isdir(foundFolderPath):

				# it works!
				folderFound = True

			else:

				# this folder does not exist
				attempts += 1



	# check if the result is a folder
	if os.path.isdir(foundFolderPath):

		# reverse the backslashes on Windows
		if sys.platform == 'win32':
			BackslashfixPluginsdir = foundFolderPath.replace("/", "\\")

			# and open the path in windows explorer
			os.startfile(BackslashfixPluginsdir)

		else:

			# open for Mac or Linux
			opener ="open" if sys.platform == "darwin" else "xdg-open"
			subprocess.call([opener, foundFolderPath])

		# print result
		message_on_changed_path = GoToDirectoryMessage + ('Original path found: ' + folder + '\n') if projdir or attempts > 1 or TCL else ''
		print (GoToDirectoryMessage + "Opened from " + knobName + '\n' + message_on_changed_path + GoToDirectoryMessage + 'Path: ' + foundFolderPath)


	else:
		
		# print failure
		print (GoToDirectoryMessage + "Not a valid path, checked up to 3 parent directories:\n" + GoToDirectoryMessage + folder)

	# print empty line
	print ('')



# main function
def GoToDirectory():

	# if nodes are selected
	if len(nuke.selectedNodes()) > 0:

		# for each selected node
		for n in nuke.selectedNodes():

			# check if the selected knobs are file paths
			for k in n.knobs():
				if n[k].Class() == 'File_Knob':

					# get its value
					v = n[k].getValue()

					# open folder
					if not v == '':
						knobName = n.name() + '.' + n[k].name()
						openFolderFromString(v, knobName)


	# if no knob paths are opened
	else:

		# open the folder from the string returned by get_clipboard_text()
		openFolderFromString(get_clipboard_text())



# autostart (if not imported)
if __name__ == "__main__":
	GoToDirectory()