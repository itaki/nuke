# --------------------------------------------------------------
# GLOBAL IMPORTS ::::::::::::::::::::::::::::::::::::::::::::::
# --------------------------------------------------------------
import nuke
import nukescripts
import os
#########################################

### PROJECT SETTINGS
## FORMAT
# Project Settings > Default format: 4K_DCP 4096x2160 
nuke.knobDefault("Root.format", "4K_DCP") 
# Project Settings > Default format: UHD_4K 3840x2160 
#nuke.knobDefault("Root.format", "UHD_4K")  
# Project Settings > Default format: HD_1080 1920x1080 
#nuke.knobDefault("Root.format", "HD_1080") 

# FRAME RATE
# Project Settings > Default FPS: 23.976
nuke.knobDefault("Root.fps", "23.976") 
# Project Settings > Default FPS: 24
# nuke.knobDefault("Root.fps", "24") 
# Project Settings > Default FPS: 29.976
#nuke.knobDefault("Root.fps", "29.976") 

# RENDER MODE
#nuke.knobDefault("Root.render_mode", "classic" )
nuke.knobDefault("Root.render_mode", "top-down" )


#### WRITE NODE SETTINGS ####
#This one does work
nuke.knobDefault("Write.mov.channels","rgba")

#nuke.knobDefault("Write.colorspace","sRGB")
nuke.knobDefault("Write.colorspace","rec709")
nuke.knobDefault("Write.file_type","mov")

nuke.knobDefault("Write.mov.mov_prores_codec_profile","ProRes 4444 XQ 12-bit")



# Write > Default for MOV files: PRORes 4444 XQ with ALPHA 

# Write > Default for EXR files: 16bit Half, No Compression
nuke.knobDefault("Write.exr.compression","0")

### OTHER NODE SETTINGS
# RotoPaint > Set default tool to brush, set default lifetime for brush and clone to "all frames"  
nuke.knobDefault("RotoPaint.toolbox", "brush {{brush ltt 0} {clone ltt 0}}")  



