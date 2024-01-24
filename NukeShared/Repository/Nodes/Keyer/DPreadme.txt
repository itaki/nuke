By Michael McReynolds 
itaki design studio
itaki.com
michael@itaki.com

Difference Plus v1.1

The clean plate and footage plate need to be stabilzed or matchmoved together and you should degrain your footage and plate before piping them in.  

This gizmo subtracts the clean plate from the footage plate, then adds together the absolute value of all the channels and pumps the result into the alpha channel. 

V1.1 updated the math to get rid of banding.

Just add the gizmo to your gizmo folder, the icon to your icon folder and drop this in your menu.py. DifferencePlus should show up in your keyers menu.

#####################################################################################################################
##Difference Plus by Michael McReynolds of itaki design studio - itaki.com 
nuke.menu("Nodes").addCommand("Keyer/DifferencePlus", "nuke.createNode('DifferencePlus')", icon="DifferencePlus.png")
#####################################################################################################################

Alternatively use nukeshared and put the gizmo and icon in your nodes/keyers directory
https://www.nukepedia.com/python/misc/nukeshared