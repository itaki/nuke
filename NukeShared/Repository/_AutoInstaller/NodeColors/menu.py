#===================================
# NODE COLORS TOOLBAR
# Version: 2.0.1
# Author: Aaron Marine
# Last Modified: September 17, 2021
#===================================
import sys    
import nuke



# CUSTOM TOOLBAR
#========================
toolbar3 = nuke.toolbar('NodeColors')



# TOOLBAR 3 - NODE COLORS
#=========================
# Set Color - Default
def nodeColor_default():
	for n in nuke.selectedNodes():
		n.knob('tile_color').setValue(0x00000000)
toolbar3.addCommand('Set Color - Default', 'nodeColor_default()', icon='color_default.png')

# Set Color - White
def nodeColor_white():
	for n in nuke.selectedNodes():
		n.knob('tile_color').setValue(0xFFFFFF00)
toolbar3.addCommand('Set Color - White', 'nodeColor_white()', icon='color_white.png')

# Set Color - Gray
def nodeColor_gray():
	for n in nuke.selectedNodes():
		n.knob('tile_color').setValue(0x59595900)
toolbar3.addCommand('Set Color - Gray', 'nodeColor_gray()', icon='color_gray.png')

# Set Color - Black
def nodeColor_black():
	for n in nuke.selectedNodes():
		n.knob('tile_color').setValue(0x20202000)
toolbar3.addCommand('Set Color - Black', 'nodeColor_black()', icon='color_black.png')

# Set Color - Red
def nodeColor_red():
	for n in nuke.selectedNodes():
		n.knob('tile_color').setValue(0xFF000000)
toolbar3.addCommand('Set Color - Red', 'nodeColor_red()', icon='color_red.png')

# Set Color - Orange
def nodeColor_orange():
	for n in nuke.selectedNodes():
		n.knob('tile_color').setValue(0xFF880000)
toolbar3.addCommand('Set Color - Orange', 'nodeColor_orange()', icon='color_orange.png')

# Set Color - Yellow
def nodeColor_yellow():
	for n in nuke.selectedNodes():
		n.knob('tile_color').setValue(0xFFFF0000)
toolbar3.addCommand('Set Color - Yellow', 'nodeColor_yellow()', icon='color_yellow.png')

# Set Color - Green
def nodeColor_green():
	for n in nuke.selectedNodes():
		n.knob('tile_color').setValue(0x00FF0000)
toolbar3.addCommand('Set Color - Green', 'nodeColor_green()', icon='color_green.png')

# Set Color - Turquoise
def nodeColor_turquoise():
	for n in nuke.selectedNodes():
		n.knob('tile_color').setValue(0x00FFFF00)
toolbar3.addCommand('Set Color - Turquoise', 'nodeColor_turquoise()', icon='color_turquoise.png')

# Set Color - Blue
def nodeColor_blue():
	for n in nuke.selectedNodes():
		n.knob('tile_color').setValue(0x0000FF00)
toolbar3.addCommand('Set Color - Blue', 'nodeColor_blue()', icon='color_blue.png')

# Set Color - Purple
def nodeColor_purple():
	for n in nuke.selectedNodes():
		n.knob('tile_color').setValue(0xAA00FF00)
toolbar3.addCommand('Set Color - Purple', 'nodeColor_purple()', icon='color_purple.png')

# Set Color - Pink
def nodeColor_pink():
	for n in nuke.selectedNodes():
		n.knob('tile_color').setValue(0xFF00AA00)
toolbar3.addCommand('Set Color - Pink', 'nodeColor_pink()', icon='color_pink.png')

# Set Color - Dark Red
def nodeColor_darkRed():
	for n in nuke.selectedNodes():
		n.knob('tile_color').setValue(0x55000000)
toolbar3.addCommand('Set Color - Dark Red', 'nodeColor_darkRed()', icon='color_darkRed.png')

# Set Color - Dark Brown
def nodeColor_darkBrown():
	for n in nuke.selectedNodes():
		n.knob('tile_color').setValue(0x33221100)
toolbar3.addCommand('Set Color - Dark Brown', 'nodeColor_darkBrown()', icon='color_darkBrown.png')

# Set Color - Dark Yellow
def nodeColor_darkYellow():
	for n in nuke.selectedNodes():
		n.knob('tile_color').setValue(0x28280000)
toolbar3.addCommand('Set Color - Dark Yellow', 'nodeColor_darkYellow()', icon='color_darkYellow.png')

# Set Color - Dark Green
def nodeColor_darkGreen():
	for n in nuke.selectedNodes():
		n.knob('tile_color').setValue(0x00300000)
toolbar3.addCommand('Set Color - Dark Green', 'nodeColor_darkGreen()', icon='color_darkGreen.png')

# Set Color - Dark Turquoise
def nodeColor_darkTurquoise():
	for n in nuke.selectedNodes():
		n.knob('tile_color').setValue(0x00303000)
toolbar3.addCommand('Set Color - Dark Turquoise', 'nodeColor_darkTurquoise()', icon='color_darkTurquoise.png')

# Set Color - Dark Blue
def nodeColor_darkBlue():
	for n in nuke.selectedNodes():
		n.knob('tile_color').setValue(0x00008800)
toolbar3.addCommand('Set Color - Dark Blue', 'nodeColor_darkBlue()', icon='color_darkBlue.png')

# Set Color - Dark Purple
def nodeColor_darkPurple():
	for n in nuke.selectedNodes():
		n.knob('tile_color').setValue(0x44004400)
toolbar3.addCommand('Set Color - Dark Purple', 'nodeColor_darkPurple()', icon='color_darkPurple.png')

# Set Color - Dark Pink
def nodeColor_darkPink():
	for n in nuke.selectedNodes():
		n.knob('tile_color').setValue(0x58002000)
toolbar3.addCommand('Set Color - Dark Pink', 'nodeColor_darkPink()', icon='color_darkPink.png')

# Set Color - Custom
def nodeColor_custom():
	col = nuke.getColor()
	if col:
		for n in nuke.selectedNodes():
			n['tile_color'].setValue(col)
toolbar3.addCommand('Set Color - Custom', 'nodeColor_custom()', icon='color_custom.png')