# --------------------------------------------------------------
# ❗GLOBAL IMPORTS ::::::::::::::::::::::::::::::::::::::::::::::
# --------------------------------------------------------------
import nuke
import nukescripts
import os
#########################################


# Import packages that can't be imported via NukeShared
# Nuke tools for use in VSCode
from NukeTools import NukeServerSocket


from nukescripts import panels
import LayerShuffler
# REGISTRATION - this goes at any point after the Imports
panels.registerWidgetAsPanel("LayerShuffler.LayerShuffler", "Layer Shuffler", "LayerShufflerPanelId")


# --------------------------------------------------------------
# ❗PROJECT SETTINGS :::::::::::::::::::::::::::::::::::::::::::::
# --------------------------------------------------------------


# ----------
# RENDER MODE
#nuke.knobDefault("Root.render_mode", "classic" )
nuke.knobDefault("Root.render_mode", "top-down" )


# --------------------------------------------------------------
# SHORTCUTS ::::::::::::::::::::::::::::::::::::::::::::::::::::
# --------------------------------------------------------------
### SHORTCUTS
# 
# command 1  = stamps
# ~ = hotbox
# v = keyer
# option ~ = scaletree
# option q = channel hotbox
# shift b = backdrop preset
# option z = knob scripter
# a = attach to closest parent
# option a = attach to closest child
# command shift Left mouse button = swap nodes
# option , = square dots
# , = magic dotLinker
# i = view node information
# command e = Change knob vales
# command option v = paste knob values
# command option shift v = paste selected knob values
# shift t = create tracker
# option shift t = toggle transform in tracker
# option shift r = toggle rotation in tracker
# option shift e = toggle scale in tracker
# option k = clone
# option shift k = declone



# --------------------------------------------------------------
# CUSTOM GIZMO SWAP ::::::::::::::::::::::::::::::::::::::::::::
# --------------------------------------------------------------
# NOT NEEEDED ANYMORE BECAUSE OF FAVORITES
# #nuke.menu( 'Nodes' ).addCommand( 'Image/Constant', "nuke.createNode( 'Image/ConstantPro' )")


# --------------------------------------------------------------
# CUSTOM  ICONS ::::::::::::::::::::::::::::::::::::::::::::::::
# --------------------------------------------------------------
# Add my own icons
nuke.menu('Nodes').addMenu("Tools", icon="toolbox_icon.png")
nuke.menu('Nodes').addMenu("Scripts", icon="scripts.png")
nuke.menu('Nodes').addMenu("CG", icon="CG.png")
nuke.menu('Nodes').addMenu("RG Magic Bullet", icon="maxon.png")

