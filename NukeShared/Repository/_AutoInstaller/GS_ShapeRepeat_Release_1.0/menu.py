''' Add this to your menu.py '''

import nuke
##GS Tools##

toolbar = nuke.menu("Nodes")
m = toolbar.addMenu("GS_Tools", icon="GS_Icon.png")
m_ShapeRepeat = m.addMenu("ShapeRepeat",icon="ShapeRepeat_Icon.png")

m_ShapeRepeat.addCommand("ShapeRepeat", "nuke.createNode(\"GS_ShapeRepeat\")", icon="ShapeRepeat_Icon.png")
