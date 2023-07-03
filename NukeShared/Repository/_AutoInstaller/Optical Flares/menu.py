# Optical Flares for Nuke 

# add this to your nuke plugin directory. if there is already a menu.py file:
# please add the following lines to the bottom of your menu.py 
# make sure you copy VideoCopilot.png and OpticalFlares.png to the
# same directory

# ------ add the following lines to your menu.py file  ------ 
toolbar = nuke.toolbar("Nodes")
toolbar.addMenu("Draw/FLARES/VideoCopilot", icon="VideoCopilot.png")
toolbar.addCommand( "Draw/FLARES/VideoCopilot/OpticalFlares", "nuke.createNode('OpticalFlares')", icon="OpticalFlares.png")