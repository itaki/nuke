import nuke

import AOV_selector

ChannelMenu = nuke.menu('Nodes').menu('Channel')

ChannelMenu.addCommand('AOV selector', 'AOV_selector.AOVselector()', 'meta+A')