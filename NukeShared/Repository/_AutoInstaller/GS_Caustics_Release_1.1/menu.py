''' Add this to your menu.py '''

import nuke
##GS Tools##

toolbar = nuke.menu("Nodes")
m = toolbar.addMenu("GS_Tools", icon="GS_Icon.png")
m_Caustics = m.addMenu("Caustics",icon="Caustics_Icon.png")

m_Caustics.addCommand("Caustics", "nuke.createNode(\"GS_Caustics\")", icon="Caustics_Icon.png")
