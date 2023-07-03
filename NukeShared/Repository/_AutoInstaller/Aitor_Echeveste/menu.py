Expression_path = "/Users/aitor/.nuke/Expression"
nuke.pluginAddPath(Expression_path)

# AITOR ECHEVESTE TOOLS
toolbar = nuke.toolbar("Nodes")
show_menu = False
organize = True

if show_menu == True:
    m = toolbar.addMenu("Aitor Echeveste", icon="AitorEchevesteNukeLogo.png")
    m.addCommand("aeBrokenEdges", "nuke.createNode(\"aeBrokenEdges\")", icon="BrokenEdges_icon.png")
    m.addCommand("aeAnamorphic", "nuke.createNode(\"aeAnamorphic\")", icon="aeAnamorphic_icon.png")
    m.addCommand("aeFiller", "nuke.createNode(\"aeFiller\")", icon="aeFiller_icon.png")
    m.addCommand("aeBrokenShapes", "nuke.createNode(\"aeBrokenShapes\")", icon="BrokenShapes_icon.png")
    m.addCommand("aePowerPin", "nuke.createNode(\"aePowerPin\")", icon="aePowerPin_icon.png")
    #m.addCommand("aeSnapShot", "nuke.createNode(\"aeSnapShot\")")
    m.addCommand("aeTransform", "nuke.createNode(\"aeTransform\")", icon="aeTransform_icon.png")
    m.addCommand("aeRelight2D", "nuke.createNode(\"aeRelight2D\")", icon="aeReLight2D_icon.png")
    m.addCommand("aeRefracTHOR", "nuke.createNode(\"aeRefracTHOR\")", icon="aeRefracTHOR_icon.png")
    m.addCommand("aeMotionBlur", "nuke.createNode(\"aeMotionBlur\")", icon="aeMotionBlur_icon.png")
    m.addCommand("aePrefMaker", "nuke.createNode(\"aePrefMaker\")", icon="aePrefMaker_icon.png")
    m.addCommand("aeUVChart", "nuke.createNode(\"aeUVChart\")", icon="aeUVChart_icon.png")
    m.addCommand("iSTMap", "nuke.createNode(\"iSTMap\")", icon="iSTMap_icon.png")

if organize == True:
    toolbar.addCommand("Filter/aeBrokenEdges", "nuke.createNode(\"aeBrokenEdges\")", icon="BrokenEdges_icon.png")
    toolbar.addCommand("Filter/aeAnamorphic", "nuke.createNode(\"aeAnamorphic\")", icon="aeAnamorphic_icon.png")
    toolbar.addCommand("Filter/Edge Extends/aeFiller", "nuke.createNode(\"aeFiller\")", icon="aeFiller_icon.png")
    toolbar.addCommand("Filter/aeBrokenShapes", "nuke.createNode(\"aeBrokenShapes\")", icon="BrokenShapes_icon.png")
    toolbar.addCommand("Transform/aePowerPin", "nuke.createNode(\"aePowerPin\")", icon="aePowerPin_icon.png")
    toolbar.addCommand("Transform/aeTransform", "nuke.createNode(\"aeTransform\")", icon="aeTransform_icon.png")
    toolbar.addCommand("Filter/aeRelight2D", "nuke.createNode(\"aeRelight2D\")", icon="aeReLight2D_icon.png")
    toolbar.addCommand("3D/aeRefracTHOR", "nuke.createNode(\"aeRefracTHOR\")", icon="aeRefracTHOR_icon.png")
    toolbar.addCommand("Filter/aeMotionBlur", "nuke.createNode(\"aeMotionBlur\")", icon="aeMotionBlur_icon.png")
    toolbar.addCommand("3D/aePrefMaker", "nuke.createNode(\"aePrefMaker\")", icon="aePrefMaker_icon.png")
    toolbar.addCommand("3D/aeUVChart", "nuke.createNode(\"aeUVChart\")", icon="aeUVChart_icon.png")
    toolbar.addCommand("Transform/iSTMap", "nuke.createNode(\"iSTMap\")", icon="iSTMap_icon.png")