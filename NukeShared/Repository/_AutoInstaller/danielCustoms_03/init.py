## init.py
## loaded by nuke before menu.py


# to add a folder inside the '.nuke' folder -> nuke.pluginAddPath('./myFolder')

nuke.pluginAddPath('./icons')
nuke.pluginAddPath('./python')
nuke.pluginAddPath('./gizmos')
nuke.pluginAddPath('./Collected')
'''
###import modules
import autosave


# Project Settings > Default format: HD 1920x1080  
nuke.knobDefault("Root.format", "HD")  

# Write > Default for EXR files: 16bit Half, No Compression  
#nuke.knobDefault("Write.exr.compression","0")  

# Exposure Tool > Use stops instead of densities  
nuke.knobDefault("EXPTool.mode", "0")  

# Text > Default font: Helvetica Regular (in Dropbox folder)  
#nuke.knobDefault("Text.font",   "/Path/to/Dropbox/fonts/HelveticaRegular.   ttf")  

# StickyNote > default text size: 40pt  
nuke.knobDefault("StickyNote.note_font_size", "40")
nuke.knobDefault("StickyNote.note_font", "Avenir Black")  

# RotoPaint > Set default tool to brush, set default lifetime for brush and clone to "all frames"  
# nuke.knobDefault("RotoPaint.toolbox", "brush {{brush ltt 0} {clone ltt 0} {blur ltt 0} {dodge ltt 0} {smear ltt 0} {eraser ltt 0}}")  

'''