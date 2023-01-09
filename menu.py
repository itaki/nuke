# --------------------------------------------------------------
# GLOBAL IMPORTS ::::::::::::::::::::::::::::::::::::::::::::::
# --------------------------------------------------------------
import nuke
import nukescripts
import os
#########################################

# Import packages that can't be imported via NukeShared
# W_hotbox 1.9
import W_hotbox, W_hotboxManager
# KnobScripter 3
import KnobScripter
# Layer Suffler
# IMPORTS - these go in the beginning of your menu.py
from nukescripts import panels
import LayerShuffler
# REGISTRATION - this goes at any point after the Imports
panels.registerWidgetAsPanel("LayerShuffler.LayerShuffler", "Layer Shuffler", "LayerShufflerPanelId")


# --------------------------------------------------------------
# PROJECT SETTINGS :::::::::::::::::::::::::::::::::::::::::::::
# --------------------------------------------------------------
# ----------
# FORMAT
# Project Settings > Default format: 4K_DCP 4096x2160 
nuke.knobDefault("Root.format", "4K_DCP") 
# Project Settings > Default format: UHD_4K 3840x2160 
#nuke.knobDefault("Root.format", "UHD_4K")  
# Project Settings > Default format: HD_1080 1920x1080 
#nuke.knobDefault("Root.format", "HD_1080") 

# ----------
# FRAME RATE
# Project Settings > Default FPS: 23.976
nuke.knobDefault("Root.fps", "23.976") 
# Project Settings > Default FPS: 24
# nuke.knobDefault("Root.fps", "24") 
# Project Settings > Default FPS: 29.976
#nuke.knobDefault("Root.fps", "29.976") 

# ----------
# RENDER MODE
#nuke.knobDefault("Root.render_mode", "classic" )
nuke.knobDefault("Root.render_mode", "top-down" )



# --------------------------------------------------------------
# WRITE NODE SETTINGS ::::::::::::::::::::::::::::::::::::::::::
# --------------------------------------------------------------
# ----------
# General
#nuke.knobDefault("Write.colorspace","sRGB")
nuke.knobDefault("Write.colorspace","rec709")
nuke.knobDefault("Write.file_type","mov")
#nuke.knobDefault("Write.file_type","exr")

# ----------
# MOV settings
#nuke.knobDefault("Write.mov.channels","rgb")
nuke.knobDefault("Write.mov.channels","rgba")
# Write > Default for MOV files: PRORes 4444 XQ
nuke.knobDefault("Write.mov.mov_prores_codec_profile","ProRes 4444 XQ 12-bit")
nuke.knobDefault("Write.png.datatype","16 bit")

# ----------
# EXR settings
# Write > Default for EXR files: 16bit Half, No Compression
nuke.knobDefault("Write.exr.compression","0")

# --------------------------------------------------------------
# OTHER NODE SETTINGS ::::::::::::::::::::::::::::::::::::::::::
# --------------------------------------------------------------
# RotoPaint > Set default tool to brush, set default lifetime for brush and clone to "all frames"  
nuke.knobDefault("RotoPaint.toolbox", "brush {{brush ltt 0} {clone ltt 0}}")  
# Invert -> set to only alpha
nuke.knobDefault("Invert.channels","alpha")

# --------------------------------------------------------------
# SHORTCUTS ::::::::::::::::::::::::::::::::::::::::::::::::::::
# --------------------------------------------------------------
### SHORTCUTS
# for now I'm using preferences
# ~ = hotbox
# v = keyer
# option ~ = scaletree
# option q = channel hotbox
# command shift d = backdrop preset

# --------------------------------------------------------------
# CUSTOM GIZMO SWAP ::::::::::::::::::::::::::::::::::::::::::::
# --------------------------------------------------------------
# #nuke.menu( 'Nodes' ).addCommand( 'Image/Constant', "nuke.createNode( 'Image/ConstantPro' )")


# --------------------------------------------------------------
# CUSTOM  ICONS ::::::::::::::::::::::::::::::::::::::::::::::::
# --------------------------------------------------------------

# Load in your icon directory
nuke.pluginAddPath('icons')

# Replace nukes icons with higher rez versions
nuke.menu('Nodes').addMenu("Image", icon="icon_toolbar_image_HighRes.png")
nuke.menu('Nodes').addMenu("Draw", icon="icon_toolbar_draw_HighRes.png")
nuke.menu('Nodes').addMenu("Time", icon="icon_toolbar_time_HighRes.png")
nuke.menu('Nodes').addMenu("Channel", icon="icon_toolbar_channel_HighRes.png")
nuke.menu('Nodes').addMenu("Color", icon="icon_toolbar_color_HighRes.png")
nuke.menu('Nodes').addMenu("Filter", icon="icon_toolbar_filter_HighRes.png")
nuke.menu('Nodes').addMenu("Keyer", icon="icon_toolbar_keyer_HighRes.png")
nuke.menu('Nodes').addMenu("Merge", icon="icon_toolbar_merge_HighRes.png")
nuke.menu('Nodes').addMenu("Transform", icon="icon_toolbar_transform_HighRes.png")
nuke.menu('Nodes').addMenu("3D", icon="icon_toolbar_3d_HighRes.png")
nuke.menu('Nodes').addMenu("Particles", icon="icon_toolbar_particles_HighRes.png")
nuke.menu('Nodes').addMenu("Deep", icon="icon_toolbar_deep_HighRes.png")
nuke.menu('Nodes').addMenu("Views", icon="icon_toolbar_views_HighRes.png")
nuke.menu('Nodes').addMenu("MetaData", icon="icon_toolbar_metadata_HighRes.png")
nuke.menu('Nodes').addMenu("ToolSets", icon="icon_toolbar_toolsets_HighRes.png")
nuke.menu('Nodes').addMenu("Other", icon="icon_toolbar_other_HighRes.png")
nuke.menu('Nodes').addMenu("FurnaceCore", icon="icon_toolbar_furnace_HighRes.png")
nuke.menu('Nodes').addMenu("AIR", icon="icon_toolbar_AIR_HighRes.png")
nuke.menu('Nodes').addMenu("CaraVR", icon="icon_toolbar_CaraVR_HighRes.png")

# Add new menu items here
nuke.menu('Nodes').addMenu("Tools", icon="toolbox_icon.png")
nuke.menu('Nodes').addMenu("Scripts", icon="icon_toolbar_scripts_HighRes.png")
