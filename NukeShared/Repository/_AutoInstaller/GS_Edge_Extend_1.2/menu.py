''' Add this to your menu.py '''

import nuke
##GS Tools##

toolbar = nuke.menu("Nodes")
m = toolbar.addMenu("GS_Tools", icon="GS_Icon.png")
m_Edge_Extend = m.addMenu("Edge_Extend",icon="GS_Icon_Edge_Extend.png")

m_Edge_Extend.addCommand("Edge_Extend", "nuke.createNode(\"GS_Edge_Extend\")", icon="GS_Icon_Edge_Extend.png")
