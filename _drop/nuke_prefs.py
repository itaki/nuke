#nuke prefrences in init
#############   PUT MY DEFAULTS UNDER HERE
# Make script directoy the project directory
# [python {nuke.script_directory()}]
#https://support.foundry.com/hc/en-us/articles/208961109-Q100154-Relative-file-path-referencing-in-Nuke

# New defaults manager
#nuke.pluginAddPath("default")

#http://doingthatwrong.com/home/2013/9/9/my-custom-nuke-defaults

# # Project Settings > Default format: UHD_4K 3840x2160 
#nuke.knobDefault("Root.format", "UHD_4K")  

# Write > Default for MOV files: PRORes 4444 XQ with ALPHA 
#nuke.knobDefault 
#nuke.knobDefault("Write.mov.codec","Apple ProRes 4444 XQ")
#nuke.knobDefault("Write.mov.channels","rgba")
# Write > Default for EXR files: 16bit Half, No Compression
#nuke.knobDefault("Write.exr.compression","0")

# # Default project settings
# nuke.knobDefault("Root.last_frame", "200")

# # Exposure Tool > Use stops instead of densities  
# #nuke.knobDefault("EXPTool.mode", "0")  

# # Text > Default font: Helvetica Regular (in Dropbox folder)  
#nuke.knobDefault("Text.font",   "/Volumes/roboSloth/_Library/Fonts/H/Helvetica Neue LT Std 33 Thin Extended 2/HelveticaNeueLTStd-ThEx.otf")  

# # StickyNote > default text size: 40pt  
#nuke.knobDefault("StickyNote.note_font_size", "40")  

# # RotoPaint > Set default tool to brush, set default lifetime for brush and clone to "all frames"  
#nuke.knobDefault("RotoPaint.toolbox", "brush {{brush ltt 0} {clone ltt 0}}")  

#nuke.load("pgBokeh")
#nuke.load("OpticalFlow")
#nuke.load("PinTool")



# StickyNote > default text size: 40pt
#nuke.knobDefault("StickyNote.note_font_size", "40")

# RotoPaint > Set default tool to brush, set default lifetime for brush and clone to "all frames"
#nuke.knobDefault("RotoPaint.toolbox", "brush {{brush ltt 0} {clone ltt 0}}")

'''maybe this shortcut works?
closes panels
def close():
[node.hideControlPanel() for node in nuke.allNodes()]
nuke.menu( ‘Nodes’ ).addCommand( ‘close’, ‘close()’ , ‘shift+d’)'''


#nuke things in menu
''' ADD THESE BACK LATER
######################Presets
##Camera back presets
import cam_presets
cam_presets.nodePresetCamera()

##Lens distortion presets
import lensdistortion_presets
lensdistortion_presets.nodePresetLensDistortion()

##Rolling Shutter presets
import rollingshutter_presets
rollingshutter_presets.nodePresetRollingShutter()

##Camera Reformat Presets
import reformat_presets
reformat_presets.nodePresetReformat()

import presetBackdrop
VictorMenu = nuke.menu('Nuke').addMenu('V!ctor')
VictorMenu.addCommand('Preset Backdrop', 'presetBackdrop.presetBackdrop()', 'ctrl+alt+b')


#### add menu item to Edit > Node menu
import convertGizmosToGroups
nuke.menu('Nuke').findItem('Edit/Node').addCommand('Convert Gizmo to Group', 'convertGizmosToGroups.convertGizmosToGroups()', 'ctrl+alt+h')