1. Copy the folder "GS" in your .nuke folder (under C:/Users/...)



2. Add the following lines to your init.py file (right click and edit ) :


#GS Tools
nuke.pluginAddPath('./GS')

nuke.pluginAddPath('./GS/Icons')
nuke.pluginAddPath('./GS/Tools')
nuke.pluginAddPath('./GS/Tools/Interlaced_Video')



3. Add the following lines to your menu.py file (right click and edit ) :

#GS Tools


toolbar = nuke.menu("Nodes")
m = toolbar.addMenu("GS_Tools", icon="GS_Icon.png")
m_Interlaced_video = m.addMenu("Interlaced_video",icon="Interlaced_Icon.png")

m_Interlaced_video.addCommand("Interlaced_video", "nuke.createNode(\"GS_Interlaced_video\")", icon="Interlaced_Icon.png")



Please share and visit my website: www.gerardoschiavone.com