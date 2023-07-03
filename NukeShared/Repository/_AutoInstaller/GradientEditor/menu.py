''' Add this to your menu.py '''

##Hagbarth Tools
toolbar = nuke.toolbar("Nodes")
#m = toolbar.addMenu("Hagbarth Tools", icon="h_tools.png")
toolbar.addCommand("Draw/GRADIENTS/GradientEditor", "nuke.createNode(\"h_gradienteditor\")", icon="h_gradienteditor.png")

import ColorGradientUi