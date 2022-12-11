''' Add this to your menu.py '''

import nuke
##GS Tools##

toolbar = nuke.menu("Nodes")
m = toolbar.addMenu("GS_Tools", icon="GS_Icon.png")
m_Interlaced_video = m.addMenu("Interlaced_video",icon="Interlaced_Icon.png")

m_Interlaced_video.addCommand("Interlaced_video", "nuke.createNode(\"GS_Interlaced_video\")", icon="Interlaced_Icon.png")
