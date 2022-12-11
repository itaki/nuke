# itaki tools
# Import itaki tools python files
import nuke
import i_tools
import backdrop_presets


# itaki tools Nuke Menu Definitions
itaki_menu = nuke.menu('Nuke').addMenu('itaki')
itaki_menu.addCommand('Preset Backdrop', 'backdrop_presets.backdrop_presets()', 'ctrl+alt+b')


# itaki tools Toolbar Definitions
toolbar = nuke.menu('Nodes')
i_menu = toolbar.addMenu('itaki', icon='itaki.png')
i_menu.addCommand('backdrop_preset', 'nuke.createNode("backdrop_preset")', icon='backdrop.png')

