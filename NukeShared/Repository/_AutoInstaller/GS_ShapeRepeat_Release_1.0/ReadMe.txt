1. Copy the folder "GS" in your .nuke folder (under C:/Users/...)


2. Add the following lines to your init.py file (right click and edit ) :

#GS Tools
nuke.pluginAddPath('./Icons')
nuke.pluginAddPath('./Tools')
nuke.pluginAddPath('./Tools/ShapeRepeat')


3. Add the following lines to your menu.py file (right click and edit ) :

##GS Tools
toolbar = nuke.toolbar("Nodes")
m = toolbar.addMenu("GS Tools", icon="GS_Icon.png")
m_ShapeRepeat = m.addMenu("ShapeRepeat",icon="ShapeRepeat_Icon.png")

m_ShapeRepeat.addCommand("ShapeRepeat", "nuke.createNode(\"GS_ShapeRepeat\")", icon="GS_Icon.png")


Please share and visit my website: www.gerardoschiavone.com