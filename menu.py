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
# FORMAT
# Formats I like
nuke.addFormat( '1560 1560 square_1.5K' )
# Add new format and use that
nuke.addFormat( '3072 1620 Company3' )
nuke.knobDefault("Root.format", "Company3") 
# ADM
#nuke.addFormat( '4096 2480 ADM_4K' )
#nuke.knobDefault("Root.format", "ADM_4K") 
# Ted Lasso Alexa
#nuke.knobDefault("Root.format", "TL_4K") 
# Horizon
nuke.addFormat( '4312 2274 Horizon' )
#nuke.knobDefault("Root.format", "Horizon") 
# Project Settings > Default format: 4K_DCP 4096x2160 
#nuke.knobDefault("Root.format", "4K_DCP") 
# Project Settings > Default format: UHD_4K 3840x2160 
#nuke.knobDefault("Root.format", "UHD_4K")  
# Project Settings > Default format: HD_1080 1920x1080 
#nuke.knobDefault("Root.format", "HD_1080") 
# Project Settings > Default format: TL 4448x3096 
#nuke.knobDefault("Root.format", "TL") 



# ----------
# FRAME RATE
# Project Settings > Default FPS: 23.976
nuke.knobDefault("Root.fps", "23.976") 
# Project Settings > Default FPS: 24
# nuke.knobDefault("Root.fps", "24") 
# Project Settings > Default FPS: 29.976q
#nuke.knobDefault("Root.fps", "29.976") 


# ----------
# Read mode
nuke.knobDefault("Read.colorspace","sRGB")
nuke.knobDefault("Read.frame_mode","start at")
nuke.knobDefault("Read.frame","0")
# ----------
# RENDER MODE
#nuke.knobDefault("Root.render_mode", "classic" )
nuke.knobDefault("Root.render_mode", "top-down" )



# --------------------------------------------------------------
# ❗WRITE NODE SETTINGS ::::::::::::::::::::::::::::::::::::::::::
# --------------------------------------------------------------
nuke.knobDefault("Write.create_directories", "1")
# ----------
# ❓RENDER Output Transform
nuke.knobDefault("Write.colorspace","sRGB") # Use this for cg and AE workflows
#nuke.knobDefault("Write.colorspace","rec709")
#nuke.knobDefault("Write.colorspace","linear")

# ----------
# ❓DEFAULT RENDER FILE TYPE - Settings are for each individual file type and won't affect the others
nuke.knobDefault("Write.file_type","exr")
#nuke.knobDefault("Write.file_type","mov")
#nuke.knobDefault("Write.file_type","dpx")
#nuke.knobDefault("Write.file_type","png")
#nuke.knobDefault("Write.file_type","tiff")

nuke.knobDefault("Write.channels","rgba")

# ----------
# ❓ EXR SETTINGS
# 16 bit half is FOR BEAUTY and rough AOVs. Fine AOVs should be 32bit float.
nuke.knobDefault("Write.exr.datatype","16 bit half")
# 32 bit float is FOR AOVs at the highest quality.
#nuke.knobDefault("Write.exr.datatype","32 bit float")
#### DWA compression is the best for EXRs. It's lossy compression but the AOVs are zip compressed.
'''
Lossy Channel names:
R, G, B, Y, RY, BY (capital channel names are required)

RLE compressed:
A

Zip compressed - All other channel names not fitting the above:
Red, red, r, Green, green, g, Blue, blue, b, x, y, z, U, u, V, v, etc... Be careful with x,y,z as if it's named Y it will be lossy.
'''
#nuke.knobDefault("Write.exr.compression","DWAA") # DWAB is smaller but slower to read
#nuke.knobDefault("Write.exr.dw_compression_level","1") # almost lossless - note: 0 is larger than piz or zip
#nuke.knobDefault("Write.exr.dw_compression_level","10") # good balance. Highest you'd want to go for green screen is 25
#nuke.knobDefault("Write.exr.dw_compression_level","45") # standard but too lossy for green screen
#nuke.knobDefault("Write.exr.dw_compression_level","150") # lossy
#nuke.knobDefault("Write.exr.dw_compression_level","500") # proxy
# For lossless beauty, better for grain and slower to read. 32 scanlines
#nuke.knobDefault("Write.exr.compression","PIZ")
# For lossless beauty, better for CGI and faster to read. 1 or 16 scanlines
#nuke.knobDefault("Write.exr.compression","Zip (1 scanline)")
#nuke.knobDefault("Write.exr.compression","Zip (16 scanlines)")
nuke.knobDefault("Write.exr.compression","PIZ Wavelet (32 scanlines)")

######## MOTION VECTORS
# The next 5 lines are For motion vectors. These settings are the same as smart vector node "Export Write"
# nuke.knobDefault("Write.colorspace","linear")
# nuke.knobDefault("Write.exr.compression","Zip (1 scanline)")
# nuke.knobDefault("Write.exr.metadata","all metadata except input/*")
# nuke.knobDefault("Write.exr.interleave","channels")
# nuke.knobDefault("Write.exr.write_full_layer_names","True")

# ----------
# ❗MOV settings 
#nuke.knobDefault("Write.mov.channels","rgb") # if you use one that's not 4444 it doesn't give you an alpha anyway
# nuke.knobDefault("Write.mov.channels","rgba")
# ❓MOV codec settings and compressionn 
# FOR PRORES
# nuke.knobDefault("Write.mov.mov64_codec","Apple ProRes") # this one doesn't work, but doesn't need to.
# ❓Select either of these two options.
nuke.knobDefault("Write.mov.mov_prores_codec_profile","ProRes 4444 XQ 12-bit") # All channels Extreme Quality
#nuke.knobDefault("Write.mov.mov_prores_codec_profile","ProRes 4:2:2 Proxy 10-bit") # 1/10 the size of 4444, no alpha
# FOR H.264
#nuke.knobDefault("Write.mov.mov64_codec","H.264")




# ----------
# DPX settings
# Write > Default for DPX files: 10bit Log, No Compression
nuke.knobDefault("Write.dpx.datatype","10 bit")
#nuke.knobDefault("Write.dpx.datatype","12 bit")

# ----------
# PNG settings
# Write > Default for PNG files: 16bit, No Compression
#nuke.knobDefault("Write.png.datatype","16 bit")
nuke.knobDefault("Write.png.datatype","8 bit") # mocha requires 8 bit grayscale pngs as mask inputs


# ----------
# TIFF settings
# Write > Default for TIFF files: 16bit, No Compression
nuke.knobDefault("Write.tiff.datatype","16 bit")

# --------------------------------------------------------------
# OTHER NODE SETTINGS ::::::::::::::::::::::::::::::::::::::::::
# --------------------------------------------------------------
# Text > Default font: Helvetica Regular (in Dropbox folder)  
#nuke.knobDefault("Text.font",   "/Path/to/Dropbox/fonts/HelveticaRegular.   ttf")  

# StickyNote > default text size: 40pt  
#nuke.knobDefault("StickyNote.tile_color", "(0.333, 0.333, 0.333)") # this isn't the right way to talk to the node
#nuke.knobDefault("StickyNote.note_font_color", "1, 1, 1") # nor is this
nuke.knobDefault("StickyNote.note_font_size", "20")
nuke.knobDefault("StickyNote.note_font", "Gotham-Book")
nuke.knobDefault("StickyNote.tile_color","3758031103")  
# RotoPaint > Set default tool to brush, set default lifetime for brush and clone to "all frames"  
nuke.knobDefault("RotoPaint.toolbox", "brush {{brush ltt 0} {clone ltt 0}}")  
# Invert -> set to only alpha
nuke.knobDefault("Invert.channels","alpha")
nuke.knobDefault("Blur.label", "[value size]")
nuke.knobDefault("Defocus.label", "[value defocus]")
nuke.knobDefault("Retime.label", "[value input.first] - [value input.last]")


# create a button to automaticaly 


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
# command shift Left mouse button = swap nodes
# option , = square dots
# , = magic dotLinker
# i = view node information


# --------------------------------------------------------------
# CUSTOM GIZMO SWAP ::::::::::::::::::::::::::::::::::::::::::::
# --------------------------------------------------------------
# NOT NEEEDED ANYMORE BECAUSE OF FAVORITES
# #nuke.menu( 'Nodes' ).addCommand( 'Image/Constant', "nuke.createNode( 'Image/ConstantPro' )")


# --------------------------------------------------------------
# CUSTOM  ICONS ::::::::::::::::::::::::::::::::::::::::::::::::
# --------------------------------------------------------------



# Add new menu items here
nuke.menu('Nodes').addMenu("Tools", icon="toolbox_icon.png")
nuke.menu('Nodes').addMenu("Scripts", icon="scripts.png")
