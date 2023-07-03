import sys
import nuke

install_in_nodes_menu = False
install_in_tools_menu = True
install_as_panel = False

def set_node_color(color):
    # if user wants a custom color get color
    if color == None:
        color = nuke.getColor()
    # change all the selected nodes to a color
    for n in nuke.selectedNodes():
        n.knob('tile_color').setValue(color)



def create_menu(location):
    location.addCommand('Default', lambda: set_node_color(0x00000000), icon='color_default.png')
    location.addCommand('White', lambda: set_node_color(0xFFFFFF00), icon='color_white.png')
    location.addCommand('Gray', lambda: set_node_color(0x59595900), icon='color_gray.png')
    location.addCommand('Black', lambda: set_node_color(0x20202000), icon='color_black.png')
    location.addCommand('Red', lambda: set_node_color(0xFF000000), icon='color_red.png')
    location.addCommand('Orange', lambda: set_node_color(0xFF880000), icon='color_orange.png')
    location.addCommand('Yellow', lambda: set_node_color(0xFFFF0000), icon='color_yellow.png')
    location.addCommand('Green', lambda: set_node_color(0x00FF0000), icon='color_green.png')
    location.addCommand('Turquoise', lambda: set_node_color(0x00FFFF00), icon='color_turquoise.png')
    location.addCommand('Blue', lambda: set_node_color(0x0000FF00), icon='color_blue.png')
    location.addCommand('Purple', lambda: set_node_color(0xAA00FF00), icon='color_purple.png')
    location.addCommand('Pink', lambda: set_node_color(0xFF00AA00), icon='color_pink.png')
    location.addCommand('Dark Red', lambda: set_node_color(0x55000000), icon='color_darkRed.png')
    location.addCommand('Dark Brown', lambda: set_node_color(0x33221100), icon='color_darkBrown.png')
    location.addCommand('Dark Yellow', lambda: set_node_color(0x28280000), icon='color_darkYellow.png')
    location.addCommand('Dark Green', lambda: set_node_color(0x00300000), icon='color_darkGreen.png')
    location.addCommand('Dark Turquoise', lambda: set_node_color(0x00303000), icon='color_darkTurquoise.png')
    location.addCommand('Dark Blue', lambda: set_node_color(0x00008800), icon='color_darkBlue.png')
    location.addCommand('Dark Purple', lambda: set_node_color(0x44004400), icon='color_darkPurple.png')
    location.addCommand('Dark Pink', lambda: set_node_color(0x58002000), icon='color_darkPink.png')
    location.addCommand('Custom', lambda: set_node_color(None), icon='color_custom.png')

if install_in_nodes_menu: #
    location = nuke.menu('Nodes').addMenu('Node Colors', icon='color_custom.png')
    create_menu(location)
if install_in_tools_menu:
	location = nuke.menu('Nodes').addMenu('Tools').addMenu('Node Colors', icon='color_custom.png')
	create_menu(location)
if install_as_panel:
	location = nuke.toolbar('Node Colors')
	create_menu(location)