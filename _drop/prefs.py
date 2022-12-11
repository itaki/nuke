import nuke
# Project Settings > Default format: UHD_4K 3840x2160 
nuke.knobDefault("Root.format", "UHD_4K")  
# Write > Default for MOV files: PRORes 4444 XQ with ALPHA 
nuke.knobDefault("Write.mov.codec","Apple ProRes 4444 XQ 12-bit")
nuke.knobDefault("Write.mov.channels","rgba")
# Write > Default for EXR files: 16bit Half, No Compression
#nuke.knobDefault("Write.exr.compression","0")
# RotoPaint > Set default tool to brush, set default lifetime for brush and clone to "all frames"  
nuke.knobDefault("RotoPaint.toolbox", "brush {{brush ltt 0} {clone ltt 0}}")  