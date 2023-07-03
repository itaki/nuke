# NukeShared v2.6 - Max van Leeuwen - maxvanleeuwen.com/nukeshared


# Default configuration (will be overwritten by the Settings.py file, if it exists):


open_dir_name 		= 	'Open NukeShared repository here'			# Text to show on button to open folder in file browser.
replace_underscore	=	False										# Auto-replace underscores ('_') with a space (' ') in the UI.
load_same_name_py	=	True										# Add the Python file to the UI when the .gizmo with the same name is right next to it in the same folder (will add '.py' to UI name).

autoinstaller 		= 	'autoinstaller.dat'							# Name of the empty file in the directories you want to load using their own menu.py/init.py (same as the '_AutoInstaller' folder, but for the current folder only).
openfolderbutton 	=	'openfolderbutton.dat' 						# Name of the empty file to put in a toolbar/menubar folder of which you want there to be a button with the name <open_dir_name>.
ignore 				= 	'ignore.dat' 								# Name of the empty file in the directories you want to completely ignore when scanning (subdirectories will still be scanned). Exclude users by writing their usernames in this file!

showconfirmation 	= 	True										# Show a confirmation print in the console when this instance of NukeShared has been loaded.
custommessage 		=	'Done!'
showstats 			=	True										# Print the amount of plugins and scripts loaded at the end of the confirmation.

write_active_user 	= 	False										# Enable user logging by making files with usernames, generated like this: 'NukeShared/Configuration/user_activity/JohnSmith.dat'.
user_blacklist		=	True										# Enable blacklisting users (to blacklist a user, add a username.dat file to the 'NukeShared/Configuration/user_blacklist' folder, or copy the existing user from the user 'user_activity' folder).

cached 				= 	False										# Cache a generated menu.py and init.py file. This mainly exists for debugging purposes - it shows exactly what commands NukeShared sends to Nuke on startup. This might be a small speed improvement for slow servers and big repositories.
cache_chance 		= 	1											# The chance (randomly 1 in every cache_chance) of having to cache the new list. Set to -1 to never update the existing cache.
cache_notification 	= 	True										# Show a message when your computer has to write the cache.
cache_message 		= 	'You are the chosen one. Writing cache.'	# What message the currently caching computer should see.

one_version_only	=	False										# Only load NukeShared for a specific Nuke version.
this_version_only	=	"11.3v4"									# If one_version_only is enabled, enter the version NukeShared should be exclusively loaded on here (e.g. "11.2v3").


# End default configuration


import os
import random
import inspect
import getpass
import platform


try: #if the universal counting var exists, add 1 to its value - else start it at 0
	initID += 1
except NameError:
	initID = 0
initIDString = '{:03}'.format(initID + 1) #start counting amount of init.py files at 1 in logs so user won't be confused


NukeSharedStr	= "[NukeShared v2.6%s] "
NukeSharedPrint = NukeSharedStr % (' (' + initIDString + ')' if initIDString != "001" else '') #don't show initID in message when it is the first NukeShared


currroot = os.path.dirname(os.path.realpath(__file__)).replace("\\", "/") #get the full path of the current location (<Z:/dir>)
root = os.path.dirname(currroot) + "/Repository/" #get the repository path (<Z:/Repository/>)
root_req = os.path.dirname(currroot) + "/Required/"


# Load user Settings.py file
configPath = os.path.dirname(currroot).replace('\\', '/') + '/Configuration/Settings.py'
if os.path.isfile(configPath):
	try:
		exec(open(configPath).read()) #run the Settings.py file as a python script
	except Exception as e:
		print (NukeSharedPrint + "Configuration file ('Settings.py') not loaded properly. Error:\n" + NukeSharedPrint + str(e)) #if something goes wrong, print the error


dir_OFX = 			"_OFXPlugins"
dir_OCIO = 			"_OCIO"
dir_Fonts =			"_Fonts"
dir_autorun =		"_Autorun"
dir_shortcuts = 	"_Shortcuts"
dir_viewerprocess = "_ViewerProcesses"
dir_autoinstaller = "_AutoInstaller"
MenuTypes = ['Nuke', 'Pane', 'Nodes', 'Properties', 'Animation', 'Viewer', 'Node Graph', 'Axis'] #all possible menu types in Nuke


# filter types for ignore files
filter_nuke = 'filter_nuke: '
filter_os = 'filter_os: '


blacklisted = False
if (user_blacklist):
	username = getpass.getuser()
	userfile = os.path.dirname(currroot) + '/Configuration/user_blacklist/' + username + '.dat'
	if(os.path.isfile(userfile)):
		blacklisted = True #skip this entire script if the username.dat is present in the user_blacklist folder and the user_blacklist setting is enabled

wrongversion = False
v = nuke.NUKE_VERSION_STRING #get current nuke version
if one_version_only and v != this_version_only:
	wrongversion = True #skip this entire script if the Nuke version is not allowed in the preferences


#define some variables
cachef = currroot + "/cache_init.py" #the path to the cache file (<Z:/dir/cache>)
cachenow = True if (random.random() <= (1.0 / cache_chance)) else False #determine if this computer should cache the plugin list right now (if cached == True)

autorun = []
viewerprocess = []
menutype = []
autorun_menu = []

pyFound = 0
viewerprocessFound = 0


def NSignoreThis(ignoreFile): # check if an ignore file exists, if the current user is whitelisted, and if software versions are matching
	
	ignore = False

	lines = []

	# if ignore file exists
	if(os.path.isfile(ignoreFile)):

		# ignore
		ignore = True

		with open(ignoreFile) as f:
			lines = f.readlines()


		for line in lines:
			# but if username is in ignore file
			if username == line:
				#allow through
				ignore = False

			# if not, check if this line is actually a filter
			else:

				# filtering nuke
				if filter_nuke in line:
					# collect all items seperated by spaces (get rid of first)
					versions = line.split(' ')
					versions.pop(0)

					# filtering substrings (e.g. 'filter_nuke: 11' should filter '11.2v3')
					for version in versions:
						if version in v:
							#allow through
							ignore = False

				if filter_os in line:
					# collect all items seperated by spaces (get rid of first)
					oslist = line.split(' ')
					oslist.pop(0)

					# get current os
					currOs = ''
					if platform.system() == "Windows": #Windows
						currOs = 'windows'
					elif platform.system() == "Darwin": #Mac OS
						curros = 'macos'
					else: #Linux
						currOs = 'linux'

					# if current os in in list
					for eachOs in oslist:
						if currOs == eachOs.lower():
							#allow through
							ignore = False

	return ignore


def LoadCache(): #load the init file

	f = open(cachef,'r')
	ReadFile = f.read()
	exec(ReadFile)
	f.close()


def ManualInit(): #generate the init file

	global pyFound
	global viewerprocessFound


	ToDo_Init = '' #placeholder for list of actions to evaluate, or read from cache


	for founddir in os.listdir(root): #get all base items

		# go through each folder type


		if founddir == dir_autorun:

			for froot, fdir, ffiles in os.walk(root + founddir): #get all folders in autorun folder

				froot = froot.replace('\\', '/') + '/'

				if not NSignoreThis(froot + ignore):

					if (root + dir_autorun + "/_init/" in froot):
						autorun.append(froot) #add to list of autorun folders
					elif (root + dir_autorun + "/_menu/" in froot):
						autorun_menu.append(froot) #add to list of autoruns to run in menu.py

		elif (founddir == dir_shortcuts):

			for froot, fdir, ffiles in os.walk(root + founddir):

				froot = froot.replace('\\', '/') + '/'

				if not NSignoreThis(froot + ignore):

					ToDo_Init += "nuke.pluginAddPath(\"" + froot + "\")" + "\n" #add folder to plugin list

		elif (founddir == dir_viewerprocess):

			for froot, fdir, ffiles in os.walk(root + founddir):

				froot = froot.replace('\\', '/') + '/'

				if not NSignoreThis(froot + ignore):

					ToDo_Init += "nuke.pluginAddPath(\"" + froot + "\")" + "\n" #add folder to plugin list

					for eachItem in os.listdir(froot):

						ext = os.path.splitext(eachItem)[1]

						if(ext == '.gizmo' or ext == '.gznc'):

							ToDo_Init += "nuke.ViewerProcess.register('" + os.path.splitext(eachItem)[0] + "', nuke.Node, ('" + froot + eachItem + "', ''))" + '\n'
							viewerprocessFound += 1

		elif (founddir == dir_autoinstaller):

			for froot, fdir, ffiles in os.walk(root + founddir):

				froot = froot.replace('\\', '/') + '/'

				if ((os.path.isfile(froot + 'menu.py') or os.path.isfile(froot + 'init.py')) and not NSignoreThis(froot + '/' + ignore)): #only load plugin folder if a menu.py or init.py is present, don't do anything else with these folders
					ToDo_Init += "nuke.pluginAddPath(\"" + froot + "\")" + "\n" #add folder to plugin list

		elif (founddir == dir_OFX):

			# only apply if files are in this folder
			if os.listdir(root + dir_OFX):

				try:

					currOFXEnv = ''
					# check if the environment already exists
					try:
						currOFXEnv = os.environ["OFX_PLUGIN_PATH"]
					except Exception as e:
						pass

					# add new path to environment
					currOFXEnv += (';' if currOFXEnv != '' else '') + root + dir_OFX
					os.environ["OFX_PLUGIN_PATH"] = currOFXEnv

				except Exception as e:

					print (NukeSharedPrint + "Could not set OFX path to: " + (root + dir_OFX) + "\n" + NukeSharedPrint + "Reason: " + str(e))

		elif (founddir == dir_OCIO):

			# only apply if files are in this folder
			if os.listdir(root + dir_OCIO):

				try:

					currOCIOEnv = ''
					# check if the environment already exists
					try:
						currOCIOEnv = os.environ["OCIO"]
					except Exception as e:
						pass

					# add new path to environment
					currOCIOEnv += (';' if currOCIOEnv != '' else '') + root + dir_OCIO
					os.environ["OCIO"] = currOCIOEnv

				except Exception as e:

					print (NukeSharedPrint + "Could not set OCIO path to: " + (root + dir_OCIO) + "\n" + NukeSharedPrint + "Reason: " + str(e))

		elif (founddir == dir_Fonts):

			try:

				currFontEnv = ''
				# check if the environment already exists
				try:
					currFontEnv = os.environ["NUKE_FONT_PATH"]
				except Exception as e:
					pass

				# add new path to environment
				currFontEnv += (';' if currFontEnv != '' else '') + root + dir_Fonts
				os.environ["NUKE_FONT_PATH"] = currFontEnv

			except Exception as e:

				print (NukeSharedPrint + "Could not set font path to: " + (root + dir_Fonts) + "\n" + NukeSharedPrint + "Reason: " + str(e))

		elif (founddir in MenuTypes):

			for froot, fdir, ffiles in os.walk(root + founddir):

				froot = froot.replace('\\', '/') + '/'

				if not NSignoreThis(froot + ignore):
					ToDo_Init += "nuke.pluginAddPath(\"" + froot + "\")" + "\n" #add folder to plugin list

			menutype.append(root + founddir) #add to list of MenuType bases (all MenuTypes mashed togeter for now)

		# if folder is not known to NukeShared, load it as a regular Plugin Path. But check for ignore files!
		else:

			for froot, fdir, ffiles in os.walk(root + founddir):

				froot = froot.replace('\\', '/') + '/'

				if not NSignoreThis(froot + ignore):
					ToDo_Init += "nuke.pluginAddPath(\"" + froot + "\")" + "\n" #add custom folder to plugin list




	for eachPath in menutype:

		for froot, fdir, ffiles in os.walk(eachPath): #get all sub dirs in plugins folder

			froot = froot if froot[len(froot)-1:] == '/' else froot + '/' #always end the path with /

			if not NSignoreThis(froot + '/' + ignore): #ignore
				ToDo_Init += "nuke.pluginAddPath(\"" + froot.replace("\\", "/") + "\")" + "\n" #add every found subfolder as a loaded path so the plugins are already available in Nuke (just not in the GUI yet)

			
	for eachPath in autorun:

		eachPath = eachPath.replace("\\", "/")

		if not NSignoreThis(eachPath + ignore): #ignore

			ToDo_Init += "nuke.pluginAddPath(\"" + eachPath + "\")" + "\n"

			for eachItem in [allFiles for allFiles in os.listdir(eachPath) if os.path.isfile(eachPath + allFiles)]: #only files

				if (eachItem == 'menu.py' or eachItem == 'init.py'):
					pyFound += 1

				else:
					ToDo_Init += "nuke.load('" + eachPath + eachItem + "')" + '\n'


	if(cached): #if caching is enabled, write cache and load from cache, else execute to-be-cached text
	
		f = open(cachef, 'w')
		f.write(ToDo_Init)
		f.close()

		LoadCache()
	
	else:

		exec(ToDo_Init)


if not blacklisted and not wrongversion: #only actually run NukeShared if not blacklisted or wrong version

	if(cached):

		if cache_chance == -1: #never cache
			cachenow = False

		if(cachenow):

			if(cache_notification):
				print(NukeSharedPrint + cache_message)

			ManualInit()

		else:
			if os.path.isfile(cachef):

				LoadCache()

			else:

				if cache_chance == -1:

					print(NukeSharedPrint + "Cache is enabled, but no cache file exists and writing cache is disabled!")

				else:

					cachenow = True

					if(cache_notification):
						print(NukeSharedPrint + cache_message)

					ManualInit()

	else:
		ManualInit()


CreateDicts = False #determines if universal dictionaries should be made or if they already exist
try:
	u_root
except:
	CreateDicts = True


if (CreateDicts): #make dicts for universal variable sharing (init.py files are all loaded before the first menu.py is loaded, which makes sharing data with menu.py files pretty difficult when multiple NukeShared instances are installed)

	u_currroot 						= 		{}
	u_root 							= 		{}
	u_root_req 						= 		{}
	u_autorun_menu					=		{}
	u_menutype 						= 		{}

	u_open_dir_name 				= 		{}
	u_replace_underscore			=		{}
	u_load_same_name_py				=		{}
	u_ignore						=		{}
	u_autoinstaller					=		{}
	u_openfolderbutton				=		{}
	u_showconfirmation				=		{}
	u_custommessage					=		{}
	u_showstats						=		{}
	u_write_active_user				=		{}
	u_blacklisted					=		{}
	u_cached						=		{}
	u_cache_chance					=		{}
	u_cache_notification			=		{}
	u_cache_message					=		{}
	u_wrongversion					=		{}
	u_cachenow						=		{}

	u_pyFound						=		{}
	u_viewerprocessFound			=		{}


#add data to universal dicts
u_currroot[initID]					=		currroot
u_root[initID] 						=		root
u_root_req[initID] 					=		root_req
u_autorun_menu[initID]				=		autorun_menu
u_menutype[initID] 					=		menutype

u_open_dir_name[initID] 			= 		open_dir_name
u_replace_underscore[initID]		=		replace_underscore
u_load_same_name_py[initID]			=		load_same_name_py
u_ignore[initID]					=		ignore
u_autoinstaller[initID]				=		autoinstaller
u_openfolderbutton[initID]			=		openfolderbutton
u_showconfirmation[initID]			=		showconfirmation
u_custommessage[initID]				=		custommessage + ' '
u_showstats[initID]					=		showstats
u_write_active_user[initID]			=		write_active_user
u_blacklisted[initID]				=		blacklisted
u_cached[initID]					=		cached
u_cache_chance[initID]				=		cache_chance
u_cache_notification[initID]		=		cache_notification
u_cache_message[initID]				=		cache_message
u_wrongversion[initID]				=		wrongversion
u_cachenow[initID]					=		cachenow

u_pyFound[initID]					=		pyFound
u_viewerprocessFound[initID]		=		viewerprocessFound