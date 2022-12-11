import presetBackdrop
VictorMenu = nuke.menu('Nuke').addMenu('V!ctor')
VictorMenu.addCommand('Preset Backdrop', 'presetBackdrop.presetBackdrop()', 'ctrl+shift+d')