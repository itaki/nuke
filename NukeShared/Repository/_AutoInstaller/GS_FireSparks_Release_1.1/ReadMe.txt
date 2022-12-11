1. Copy the folder "GS" in your .nuke folder (under C:/Users/...)


2. Add the following lines to your init.py file (right click and edit ) :

#GS Tools
nuke.pluginAddPath('./Icons')
nuke.pluginAddPath('./Tools')
nuke.pluginAddPath('./Tools/Firesparks')


3. Add the following lines to your menu.py file (right click and edit ) :

##GS Tools
toolbar = nuke.menu("Nodes")
m = toolbar.addMenu("GS_Tools", icon="GS_Icon.png")
m_FireSparks = m.addMenu("FireSparks",icon="Fire_Icon.png")

m_FireSparks.addCommand("Particle", "nuke.createNode(\"GS_Particle\")", icon="Particle_Icon.png")
m_FireSparks.addCommand("Sparks", "nuke.createNode(\"GS_Sparks\")", icon="Sparks_Icon.png")
m_FireSparks.addCommand("Fire", "nuke.createNode(\"GS_Fire\")", icon="Fire_Icon.png")


Please share and visit my website: www.gerardoschiavone.com