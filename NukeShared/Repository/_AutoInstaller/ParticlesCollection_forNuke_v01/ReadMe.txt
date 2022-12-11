TO INSTALL Particles Collection for Nuke”, version 1.0, compatible with Nuke 13
———————————————————————————————————

1. Unzip the archive
2. Drag and drop the folder in your .nuke folder or wherever you prefer
	#in your .nuke folder, path would be something like this:

	#Linux:       /home/login name/.nuke
	#Mac OS X:    /Users/login name/.nuke
	#Windows:     C:\Users\user name\.nuke

3. Add this code to your file init.py (if you don’t have it, create one) and modify the path (do not change the file init.py in the folder Particles) . Don’t put any space at the beginning
   Don't delete letter 'r' before the path	


	nuke.pluginAddPath(r"/Users/yourPath/.nuke/ParticlesCollection”)

4. Run Nuke

——————————————————————

If you have troubles, contact me: andrea.geremia89@gmail.com