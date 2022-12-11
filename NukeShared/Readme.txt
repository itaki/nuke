|| NukeShared v2.6 - Max van Leeuwen - maxvanleeuwen.com/nukeshared






|| Installation



1. 	Place the entire 'NukeShared'-folder somewhere you like. Could be on a server, if you want to have multiple computers load their plugins from it.


2.	On each computer you want to load from this repository, add the following line to your .nuke/init.py file (create the file if it does not yet exist):

		nuke.pluginAddPath("path/to/NukeShared")


	The .nuke folder can be found here:

		Linux: /home/<user>/.nuke
		Mac OS X: /Users/<user>/.nuke
		Windows: \Users\<user>\.nuke


3.	That's it!






|| Alternative installation



Adding the path to the NukeShared folder to your Environment Variables is possible as well.






|| The Repository



All folders in the Repository folder refer to a specific panel in Nuke, except for the ones starting with an underscore.
This means that, for instance, dropping a Python script in the folder called 'Animation' will make it appear on the
right-click menu of the Animation knob on all nodes.


See this page by The Foundry for a list with pictures of all panels in Nuke:
	https://learn.foundry.com/nuke/developers/63/pythondevguide/custom_ui.html

Here is what the other (non-panel) folders are for:


	_AutoInstaller
		All folders and subfolders in this folder will be loaded to Nuke as a plugin path, 
		which means init.py and menu.py files are automatically run.
		This folder is meant for plugins that have their own set of files - for instance, 
		simply dragging the entire download folder for Cryptomatte or PixelFudger in there works.

	_Autorun
		All Python files in this folder and its subfolders will be run on Nuke startup.
		There are two subdirectories in this folder that should not be changed or removed: _init and _menu. 
		Place your scripts in the _init folder to have them run on Nuke startup (before UI is loaded), and in _menu to have them load with the UI.

	_Fonts
		This path is added as a FONT environment path to Nuke.

	_OFXPlugins
		This path is added as an OFX environment path to Nuke (if any files/folders are present in the directory).

	_OCIO
		This path is added as an OCIO environment path to Nuke (if any files/folders are present in the directory).
		Keep this folder empty if you do not want to lose Nuke's built-in configs!
		
	_Shortcuts
		Change the contents of the file 'Keyboard_Shortcuts.txt' to quickly remap keyboard shortcuts for any item in the 'Node' bar on the left or the 'Nuke' bar on the top of the screen.

	_ViewerProcesses
		The gizmo's in this folder and its subfolders will be registered as Nuke viewerprocesses in the viewer.






|| The contents explained



There are three folders in the main NukeShared folder (next to this readme file): Configuration, Repository and Required. 
There is also an init.py file.

This is what they're for:


Folder: Repository
	This is where you can place your gizmos, scripts and whatnot! More about how that works down below.


Folder: Required
	These are the files NukeShared needs to be able to load.


File: init.py
	All this python script does is pointing Nuke in the right direction (which is the Required folder).


Folder: Configuration
	In this folder, you can change preferences for NukeShared by editing the contents of the Settings.py file.

	You can add files with the name 'username.dat' to the user_blacklist folder to completely blacklist these users from NukeShared.
	
	See who is using NukeShared by finding the 'username.dat' files that appear in the user_activity folder every time someone opens up Nuke
	(but only if 'write_active_user' is set to True in the settings file).






|| Some more tricks



If you create files with a certain name, NukeShared will treat the folder they are in differently.
Simply add a file with the following name to get a certain effect:


ignore.dat

	Make NukeShared ignore this folder (not its subdirectories).
	Add usernames to this file (one on each line) to exclude them!

	Alternatively, you can enter 'filter_nuke: ' or 'filter_os: ', followed by the versions you want to whitelist to the ignore file.
	
	Example to filter nuke 11.2v3, all versions of nuke 11.3, and nuke 10.5v8:
	filter_nuke: 11.2v3 11.3 10.5v8
	
	Example filtering all three operating systems at the same time:
	filter_os: windows macos linux


autoinstaller.dat

	Ignore all the files in the current folder, except for the 'menu.py' and 'init.py' files.
	Basically the same as placing the current folder (without its subdirectories) in '_AutoInstaller'.


openfolderbutton.dat

	Add an extra item at the end of the current menu in Nuke with the option to open this current folder in the finder/explorer.






|| See maxvanleeuwen.com/nukeshared if you still have questions or if you need to contact me!