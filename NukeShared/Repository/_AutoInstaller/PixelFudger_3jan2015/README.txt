Pixelfudger for Nuke

TO INSTALL:

Step 1:
Locate and go to the ~/.nuke directory in your system. Usually this is located here:

/Users/username/.nuke (Mac OSX)
/home/username/.nuke (Linux)
C:\Users\username\.nuke (Windows)

Note that directories that start with "." often are hidden by OSes. They usually require to be
accessed via command line terminal or other "special" means. 


Step 2:
Determine if you need to create a fresh init.py and menu.py file or if you need to append to existing 
ones.

	If you don't have init.py and menu.py in ~/.nuke:
	
		Copy everything from the pixelfudger installation zip file in ~/.nuke
		- init.py
		- menu.py
		- pixelfudger/
	
	
	If you do have a custom init.py and menu.py already:
	
		- Copy only the pixelfudger/ directory to ~/.nuke
		
		- add this line to init.py:
		
			nuke.pluginAddPath('pixelfudger')
			
		- add this line to menu.py:
		
			import pixelfudger
		
After a Nuke restart, you should have the Pixelfuger menu in your toolbar.

LICENCE:

You are free to use Pixelfudger gizmos for personal and commercial use as
long as you leave the credit text intact in the source files and in the 
gizmo's knobs.

AUTHOR:
Xavier Bourque
xbourque@gmail.com
www.pixelfudger.com
© 2007-2014