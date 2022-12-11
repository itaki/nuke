# NukeShared v2.6 configuration file
# Using a better text editor than Notepad is recommended!


open_dir_name 		= 	'Open NukeShared repository here'			# Text to show on button to open folder in file browser.
replace_underscore	=	False										# Auto-replace underscores ('_') with a space (' ') in the UI.
load_same_name_py	=	True										# Add the Python file to the UI when the .gizmo with the same name is right next to it in the same folder (will add '.py' to UI name).

autoinstaller 		= 	'autoinstaller.dat'							# Name of the empty file in the directories you want to load using their own menu.py/init.py (same as the '_AutoInstaller' folder, but for the current folder only).
openfolderbutton 	=	'openfolderbutton.dat' 						# Name of the empty file to put in a toolbar/menubar folder of which you want there to be a button with the name <open_dir_name>.
ignore 				= 	'ignore.dat' 								# Name of the empty file in the directories you want to completely ignore when scanning (subdirectories will still be scanned). Exclude users by writing their usernames in this file!

showconfirmation 	= 	True										# Show a confirmation print in the console when this instance of NukeShared has been loaded.
custommessage 		=	'Done!'
showstats 			=	True										# Print the amount of plugins and scripts loaded at the end of the confirmation.

write_active_user 	= 	True										# Enable user logging by making files with usernames, generated like this: 'NukeShared/Configuration/user_activity/JohnSmith.dat'.
user_blacklist		=	True										# Enable blacklisting users (to blacklist a user, add a username.dat file to the 'NukeShared/Configuration/user_blacklist' folder, or copy the existing user from the user 'user_activity' folder).

cached 				= 	False										# Cache a generated menu.py and init.py file. This mainly exists for debugging purposes - it shows exactly what commands NukeShared sends to Nuke on startup. This might be a small speed improvement for slow servers and big repositories.
cache_chance 		= 	1											# The chance (randomly 1 in every cache_chance) of having to cache the new list. Set to -1 to never update the existing cache.
cache_notification 	= 	True										# Show a message when your computer has to write the cache.
cache_message 		= 	'You are the chosen one. Writing cache.'	# What message the currently caching computer should see.

one_version_only	=	False										# Only load NukeShared for a specific Nuke version.
this_version_only	=	"11.3v4"									# If one_version_only is enabled, enter the version NukeShared should be exclusively loaded on.