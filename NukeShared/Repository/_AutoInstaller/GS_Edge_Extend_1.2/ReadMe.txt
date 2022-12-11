1. Copy the folder "GS" in your .nuke folder (under C:/Users/...)



2. Add the following lines to your init.py file (right click and edit ) :


#GS Tools
nuke.pluginAddPath('./GS')

nuke.pluginAddPath('./GS/Icons')
nuke.pluginAddPath('./GS/Tools')
nuke.pluginAddPath('./GS/Tools/Edge_Extend')



3. Add the following lines to your menu.py file (right click and edit ) :

#GS Tools


toolbar = nuke.menu("Nodes")
m = toolbar.addMenu("GS_Tools", icon="GS_Icon.png")
m_Moire = m.addMenu("Moire",icon="GS_Icon_Edge_Extend.png")

m_Moire.addCommand("Edge_Extend", "nuke.createNode(\"GS_Edge_Extend\")", icon="GS_Icon_Edge_Extend.png")


Please share and visit my website: www.gerardoschiavone.com