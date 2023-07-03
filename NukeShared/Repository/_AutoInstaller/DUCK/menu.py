import nuke

# DUCK add Menu

toolbar = nuke.menu("Nodes")
show_menu = False
organize = True

if show_menu == True:
    m = toolbar.addMenu("DUCK_v1", "DUCK_icon.png")
    n = m.addMenu("DUCK 1.0")
    n.addCommand("DUCK_Alpha_Edge","nuke.createNode(\"DUCK_Alpha_Edge_v2\")" , icon= "icon_alphaedge.png")
    n.addCommand("DUCK_Green_Killer", "nuke.createNode(\"DUCK_Green_Killer_v2\")" , icon= "icon_greenkiller.png")
    n.addCommand("DUCK_Blue_Killer", "nuke.createNode(\"DUCK_Blue_Killer_v1\")" , icon= "icon_bluekiller.png")
    n.addCommand("DUCK_ObjectID", "nuke.createNode(\"DUCK_objectID_v1\")" , icon= "icon_objectID.png")
    n.addCommand("DUCK_Luma_Keyer", "nuke.createNode(\"DUCK_Luma_Keyer_v1\")" , icon= "icon_lumakeyer.png")
    n.addCommand("DUCK_Smart_Blur", "nuke.createNode(\"DUCK_Smart_Blur_v1\")" ,  icon= "icon_smartblur.png")
    n.addCommand("DUCK_Denoise", "nuke.createNode(\"DUCK_Denoise_v2\")" , icon= "icon_denoise.png")
    n.addCommand("DUCK_Skin_Cleaner", "nuke.createNode(\"DUCK_Skin_Cleaner_v1\")" , icon= "icon_skincleaner.png")
    n.addCommand("DUCK_Heat_Vision", "nuke.createNode(\"DUCK_Heat_Vision_v1\")" , icon= "icon_heatvision.png")
    n.addCommand("DUCK_Night_Vision", "nuke.createNode(\"DUCK_Night_Vision_v3\")" ,  icon= "icon_nightvision.png")

if organize == True: #
    toolbar.addCommand("Filter/Edge Extends/DUCK_Alpha_Edge","nuke.createNode(\"DUCK_Alpha_Edge_v2\")" , icon= "icon_alphaedge.png")
    toolbar.addCommand("Keyer/SPILL/DUCK_Green_Killer", "nuke.createNode(\"DUCK_Green_Killer_v2\")" , icon= "icon_greenkiller.png")
    toolbar.addCommand("Keyer/SPILL/DUCK_Blue_Killer", "nuke.createNode(\"DUCK_Blue_Killer_v1\")" , icon= "icon_bluekiller.png")
    toolbar.addCommand("Keyer/CG/DUCK_ObjectID", "nuke.createNode(\"DUCK_objectID_v1\")" , icon= "icon_objectID.png")
    toolbar.addCommand("Keyer/DUCK_Luma_Keyer", "nuke.createNode(\"DUCK_Luma_Keyer_v1\")" , icon= "icon_lumakeyer.png")
    toolbar.addCommand("Filter/DUCK_Smart_Blur", "nuke.createNode(\"DUCK_Smart_Blur_v1\")" ,  icon= "icon_smartblur.png")
    toolbar.addCommand("Filter/DUCK_Denoise", "nuke.createNode(\"DUCK_Denoise_v2\")" , icon= "icon_denoise.png")
    toolbar.addCommand("Filter/DUCK_Skin_Cleaner", "nuke.createNode(\"DUCK_Skin_Cleaner_v1\")" , icon= "icon_skincleaner.png")
    toolbar.addCommand("Filter/DUCK_Heat_Vision", "nuke.createNode(\"DUCK_Heat_Vision_v1\")" , icon= "icon_heatvision.png")
    toolbar.addCommand("Filter/DUCK_Night_Vision", "nuke.createNode(\"DUCK_Night_Vision_v3\")" ,  icon= "icon_nightvision.png")







