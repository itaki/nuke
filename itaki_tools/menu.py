# itaki tools
# Import itaki tools python files
import nuke
import nukescripts
import os
#from i_tools import defaults
from i_tools import formats
from i_tools import output
from i_tools import edit_nodes
from i_tools import backdrop_presets
from i_tools import backdropper
from i_tools import script_library
from i_tools import attach_closest_node
from i_tools import defaults


import node_color_toolbar

# Shortcuts

# itaki tools Nuke Menu Definitions
itaki_menu = nuke.menu('Nuke').addMenu('itaki')
itaki_menu.addCommand('Preset Backdrop', 'backdrop_presets.backdrop_presets()', 'shift+b')

#bm = backdrops.BackdropManager()
#itaki_menu.addCommand('new preset backdrop', 'bm.create_popup_menu()', 'shift+v')

# Get closest node script
itaki_menu.addCommand('Attach input to closest node', 'attach_closest_node.connect_to_closest()', 'a', shortcutContext=2)
itaki_menu.addCommand('Attach output to closest node', 'attach_closest_node.connect_to_closest(direction=1)', 'alt+a', shortcutContext=2)



itaki_menu.addCommand('test', 'script_library.test("This is my test print")')

##

# itaki tools Toolbar Definitions
toolbar = nuke.menu('Nodes')
i_menu = toolbar.addMenu('itaki', icon='itaki.png')

# add tracker TRS checkbox toggling to the toolbar
from i_tools.updateTrackerTRS import *
i_menu.addCommand('Toggle Tracker TRS/Toggle Tracker Translate', 'update_tracker_TRS(True,  False, False)', 'alt+shift+t', icon='Tracker4.png', shortcutContext=2)
i_menu.addCommand('Toggle Tracker TRS/Toggle Tracker Rotate', 'update_tracker_TRS(False, True,  False)', 'alt+shift+r', icon='Tracker4.png', shortcutContext=2)
i_menu.addCommand('Toggle Tracker TRS/Toggle Tracker Scale', 'update_tracker_TRS(False, False, True)', 'alt+shift+s', icon='Tracker4.png', shortcutContext=2)

#i_menu.addCommand('backdrop_preset', 'backdrop_presets.backdrop_presets()', icon='Backdrop.png')
#i_menu.addCommand('backdrop_preset', 'nuke.createNode("backdrop_preset")', icon='backdrop.png')

# import talk_to_nodes
# tester = talk_to_nodes.Threadtester()
# tester.start_thread()

# Timekeeper is a thread that will continue running it the background forever. 
import shot_clock

nuke.addOnScriptLoad(shot_clock.logger.logit)
nuke.addOnScriptSave(shot_clock.logger.logit)

#import node_viewer_test
# Get closest node script


# Icon toolbox

# import IconPanel

# def addIconPanel():
#     global iconPanel
#     iconPanel = IconPanel.IconPanel()
#     return iconPanel.addToPane()
 
# paneMenu = nuke.menu( 'Pane' )
# paneMenu.addCommand( 'Universal Icons', addIconPanel )
# nukescripts.registerPanel('com.ohufx.iconPanel', addIconPanel)

# import all_icons

# all_icons = icon_drop_down_panel()
from i_tools import icon_drop_down_panel

itaki_menu = nuke.menu('Nuke').addMenu('itaki')
itaki_menu.addCommand('Show all icons', 'icon_drop_down_panel')

# itaki_menu = nuke.menu('Nuke').addMenu('itaki')
# itaki_menu.addCommand('print all icons', 'all_icons.get_icons()')


# Franklins backdrop
# from i_tools import F_Backdrop
# nukescripts.autoBackdrop = F_Backdrop.autoBackdrop # Original backdrop function replacement
# nuke.menu('Nodes').addCommand( 'Other/Backdrop', 'F_Backdrop.autoBackdrop()', 'alt+b', 'Backdrop.png')

