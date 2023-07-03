# NukeShared v2.6 - Max van Leeuwen - maxvanleeuwen.com/nukeshared


import os
import webbrowser
import platform
import random
import getpass


try: #if the universal counting var exists, add 1 to its value - else start it at 0
    menuID += 1
except NameError:
    menuID = 0
menuIDString = '{:03}'.format(menuID + 1) #get the current menu.py count (start at <001> so user won't be confused)

NukeSharedStr	= "[NukeShared v2.6%s] "
NukeSharedPrint = NukeSharedStr % ((" (" + menuIDString + ")") if initID > 0 else ("")) #text to show on prints (only show NukeShared count if more than 1 instance is installed)


#load all init.py variables from the right init.py

currroot 			= 		u_currroot[menuID]
root 				= 		u_root[menuID]
root_req 			= 		u_root_req[menuID]
autorun_menu		=		u_autorun_menu[menuID]
menutype			=		u_menutype[menuID] 

open_dir_name 		= 		u_open_dir_name[menuID]
replace_underscore	=		u_replace_underscore[menuID]
load_same_name_py	=		u_load_same_name_py[menuID]

ignore 				= 		u_ignore[menuID]
autoinstaller 		= 		u_autoinstaller[menuID]
openfolderbutton	=		u_openfolderbutton[menuID]
showconfirmation 	= 		u_showconfirmation[menuID]
custommessage 		= 		u_custommessage[menuID]
showstats 			= 		u_showstats[menuID]
write_active_user 	= 		u_write_active_user[menuID]
blacklisted			=		u_blacklisted[menuID]
cached 				= 		u_cached[menuID]
cache_chance 		= 		u_cache_chance[menuID]
cache_notification 	= 		u_cache_notification[menuID]
cache_message 		= 		u_cache_message[menuID]
wrongversion		=		u_wrongversion[menuID]
cachenow			=		u_cachenow[menuID]

pyFound 			=		u_pyFound[menuID]
viewerprocessFound	=		u_viewerprocessFound[menuID]

# end load variables


ItemCount = 0 #stats


def mt(MenuType): #make a MenuType Python variable name - e.g.: 'Node Graph' -> '_NodeGraph'
	
	return ('_' + MenuType.replace(' ', ''))

def ManualLoad():
	
	global ItemCount
	global pyFound
	global viewerprocessFound


	ToDo_Menu = 'import os' + '\n'
	ToDo_Menu += 'import webbrowser' + '\n'
	ToDo_Menu += '\n\n'


	for MenuType in MenuTypes:
		ToDo_Menu += mt(MenuType) + ' = nuke.menu(\'' + MenuType + '\') \n' #define all menu types, e.g.: _Node_Graph = nuke.menu('Node Graph')
	ToDo_Menu += "\n\n"


	addOnEnd = '' #string to add to Todo_Menu after this loop
	for menutype_path in menutype: #this iterates through all the menutypes

		for froot, fdir, ffiles in os.walk(menutype_path):

			if not NSignoreThis(froot + '/' + ignore) and not os.path.isfile(froot + '/' + autoinstaller): #ignore if the 'ignore'-file is present in the directory, or if the 'autoinstaller'-file is present in the directory

				group = froot.replace('\\', '/') + '/'
				groupIcon = group[:-1] + '.png'
				MenuType = group.replace(root, '').split('/')[0]


				if(os.path.isfile(groupIcon)):

					pathSplit = group[:-1].split('/')
					afterMenuType = group.replace(root, '')[len(MenuType) + 1:-1] #No MenuType, no '/' on ends
					ToDo_Menu += mt(MenuType) + ".addMenu('" + (afterMenuType.replace('_', ' ') if replace_underscore else afterMenuType) + "', icon = '" + groupIcon + "')" + '\n'


				for itemName in os.listdir(group):

					if not itemName.endswith('.png'):

						fullpath = group + itemName
						afterRoot = fullpath.replace(root, '') #does not start or end with '/'
						MenuType = afterRoot.split('/')[0] #e.g.: Node Graph

						afterMenuType = afterRoot[len(MenuType) + 1:] #does not start or end with '/'

						afterMenuTypeNoExt = os.path.splitext(afterMenuType)[0]
						afterMenuTypeNoExtUnderscore = afterMenuTypeNoExt.replace('_', ' ') if replace_underscore else afterMenuTypeNoExt #replace underscore with space if enabled

						itemNameNoExt = (os.path.splitext(os.path.basename(itemName))[0]) if (os.path.isfile(group + itemName)) else (itemName) #might be a folder
						itemExt = os.path.splitext(os.path.basename(itemName))[1] if (os.path.isfile(group + itemName)) else ('') #might be a folder


						iconPath = group + itemNameNoExt + '.png'
						icon = ''
						
						if (os.path.isfile(iconPath)): 
							icon = (", icon = '" + iconPath + "'")


						if (itemExt == '.gizmo'):
							ToDo_Menu += mt(MenuType) + ".addCommand('" + afterMenuTypeNoExtUnderscore + "'" + ", \"nuke.createNode('" + itemName + "')\"" + icon + ")" + '\n' #createNode for gizmos
							ItemCount += 1

						elif (itemExt == '.nk' and os.path.basename(os.path.dirname(fullpath)).lower() != 'toolsets'):
							ToDo_Menu += mt(MenuType) + ".addCommand('" + afterMenuTypeNoExtUnderscore + "'" + ", \"nuke.loadToolset('" + group + itemName + "')\"" + icon + ")" + '\n' #loadToolset for nukescripts
							ItemCount += 1
						
						elif (itemExt == '.py'):
						
							if not (itemName == "menu.py" or itemName == "init.py"): #never load init.py or menu.py files
						
								if (not os.path.isfile(group + itemNameNoExt + '.gizmo')): #only load if no gizmo of the same name exists (if load_same_name is False)
									ToDo_Menu += mt(MenuType) + ".addCommand('" + afterMenuTypeNoExtUnderscore + "'" + ", \"nuke.load('" + itemName + "')\"" + icon + ")" + '\n' #load python
									ItemCount += 1
						
								elif (load_same_name_py and os.path.isfile(group + itemNameNoExt + '.gizmo')):
									ToDo_Menu += mt(MenuType) + ".addCommand('" + afterMenuTypeNoExtUnderscore + ".py'" + ", \"nuke.load('" + itemName + "')\"" + icon + ")" + '\n' #load python
									ItemCount += 1
						
							else:
								pyFound += 1
						
						elif (itemExt == '.dll' or itemExt == '.dylib' or itemExt == '.so'):
							ToDo_Menu += mt(MenuType) + ".addCommand('" + afterMenuTypeNoExtUnderscore + "'" + ", \"nuke.createNode('" + itemNameNoExt + "')\"" + icon + ")" + '\n' #no extension, as shared libraries could be meant for different OS's
							ItemCount += 1

				
				if (MenuType == "Nodes" or MenuType == "Nuke"):
				
					if os.path.isfile(group + openfolderbutton): #if there is an 'openfolderbutton' in this menutype_path, create a divider and button for that
				
						OpenPluginsDir = '' #create the string for the function to open the directory
				
						if platform.system() == "Windows": #Windows
							BackslashfixPluginsdir = group.replace("/", "\\\\\\\\") #double backslashes only on windows, and give them escape characters
							OpenPluginsDir = "os.startfile(\'" + BackslashfixPluginsdir + "\')"
						elif platform.system() == "Darwin": #Mac OS
							BackslashfixPluginsdir = group.replace("\\", "/") #forward slashes only on Mac
							OpenPluginsDir = "webbrowser.open(\'file://" + BackslashfixPluginsdir + "\')"
						else: #Linux
							BackslashfixPluginsdir = group.replace("\\", "/") #forward slashes only on Linux
							OpenPluginsDir = "os.system(\\\"xdg-open \'" + BackslashfixPluginsdir + "\'\\\")"

						afterMenuType = group.replace(root, '')[len(MenuType) + 1:-1] #No MenuType, no '/' on ends
						addOnEnd += '\n'
						addOnEnd += "button = nuke.menu('" + MenuType + "').findItem('" + afterMenuType + "')" + "\n"
						addOnEnd += "button.addSeparator()" + "\n"
						addOnEnd += "button.addCommand('" + open_dir_name + "', \"" + OpenPluginsDir + "\")" + "\n" #add button to open the plugin directory


	ToDo_Menu += addOnEnd #add after loop

	ToDo_Menu += "\n\n\n"


	for autorun in autorun_menu:
		for item in os.listdir(autorun):
			if os.path.isfile(autorun + '/' + item) and not NSignoreThis(autorun + '/' + ignore):
				ToDo_Menu += "nuke.load('" + autorun + item + "')" + '\n'


	#the following string is for cache files to be able to do user logging, if enabled
	WriteActiveUserBlock = r"""
# The following block writes the current username to the 'user_activity'-folder in 'Configuration', as 'write_active_user' is enabled in NukeShared config.

import getpass

username = getpass.getuser()
filedir = '""" + os.path.dirname(currroot) + "/Configuration/" + r"""user_activity'
filename = filedir + '/' + username + '.dat' #extension .dat is necessary when working with Google Drive or other services that do not allow files without extensions

try:
    os.remove(filename) #remove file if it already exists, as creating a new one updates the time stamp on the file
except:
    pass #probably no earlier file found
try:
    os.makedirs(filedir) #create the user activity directory if it does not exist
except:
    pass #directory cannot be made for some reason, doesn't really matter
try:
	open(filename, 'a').close()
except:
	print(NukeSharedPrint + "Could not write user! Path:\n" + NukeSharedPrint + filename) #user file could not be made
"""


	ToDo_Menu += '\n\n\n### The following script is generated for NukeShared internal use only.\n### When using this cache to copy contents from, ignore the following.\n\n\n\n' #when writing cache to file, it should be clear that the following lines are unimportant
	
	ToDo_Menu += 'ItemCount = ' + (str)(ItemCount) + '\n' #stats
	ToDo_Menu += 'pyFound = ' + (str)(pyFound) + '\n'
	ToDo_Menu += 'viewerprocessFound = ' + (str)(viewerprocessFound) + '\n'
	ToDo_Menu += '\n'

	ToDo_Menu += WriteActiveUserBlock if write_active_user else '' #add the script to write the active user to the cache, in case machines are loading from this cache file


	if(cached):

		f = open(cachef, 'w')
		f.write(ToDo_Menu)
		f.close()

		exec(open(cachef).read())

	else:

		exec(ToDo_Menu)


def GetStats():

	stats = (str)(ItemCount) + " item" + ('s' if ItemCount != 1 else '') + ", " + (str)(pyFound) + " init/menu, " + (str)(viewerprocessFound) + " viewerprocess" + ('es' if viewerprocessFound != 1 else '') + "." # the stats string to append at the end of the confirmation (if enabled)
	return stats


cachef = currroot + "/cache_menu.py" #the path to the cache file (<Z:/dir/cache>)
if not blacklisted and not wrongversion:
	
	if(cached):
	
		if(cachenow):
			ManualLoad()
		else:
			if os.path.isfile(cachef):
				exec(open(cachef).read())
			else:
				cachenow = True
				ManualLoad()
	
		if showconfirmation:
			print(NukeSharedPrint + "[cached] " + custommessage + GetStats()) #final confirmation on cached load
	
	else:
	
		ManualLoad()
		if showconfirmation:
			print(NukeSharedPrint + custommessage + (GetStats() if showstats else '')) #final confirmation on regular load