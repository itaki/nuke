''' Add this to your menu.py '''
import nuke
##GS Tools##

toolbar = nuke.menu("Nodes")
m = toolbar.addMenu("GS_Tools", icon="GS_Icon.png")
m_FireSparks = m.addMenu("FireSparks",icon="Fire_Icon.png")

m_FireSparks.addCommand("Particle", "nuke.createNode(\"GS_Particle\")", icon="Particle_Icon.png")
m_FireSparks.addCommand("Sparks", "nuke.createNode(\"GS_Sparks\")", icon="Sparks_Icon.png")
m_FireSparks.addCommand("Fire", "nuke.createNode(\"GS_Fire\")", icon="Fire_Icon.png")
