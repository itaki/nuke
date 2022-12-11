''' Add this to your menu.py '''

import nuke
##GS Tools##

toolbar = nuke.menu("Nodes")
m = toolbar.addMenu("GS_Tools", icon="GS_Icon.png")
m_Moire = m.addMenu("Moire",icon="Moire_Icon.png")

m_Moire.addCommand("Moire", "nuke.createNode(\"GS_Moire\")", icon="Moire_Icon.png")
