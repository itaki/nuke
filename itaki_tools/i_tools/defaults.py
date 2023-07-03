import nuke
import os

############################################################
# defaults module
#   contains default settings
#       knob default values



# Set knob defaults for multiple nodes: Heirarchy - knob name : knob value : nodes
knob_defaults = {
    'channels': {
        'rgb': [
                'Add',
                'ColorCorrect',
                'Grade',
                'Laplacian',
        ],
        'rgba': [
                'Blur',
                'BumpBoss',
                'Clamp',
                'Constant',
                'Defocus',
                'Dilate',
                'Dilate',
                'DirBlurWrapper',
                'EdgeBlur',
                'Emboss',
                'FilterErode',
                'FrameBlend',
                'Gamma',
                'Glint',
                'IDistort',
                'Multiply',
                'Remove',
                'Roto',
                'Sharpen',
                'Soften',
                'TransformMasked',
                'VectorBlur',
                'Write',
                'ZBlur',
                'ZDefocus2',
                'ZSlice',
        ],
    }
}
for knob, vals in knob_defaults.items():
    for val, nodes in vals.items():
        for node in nodes:
            nuke.knobDefault('{0}.{1}'.format(node, knob), val)


#

# Set global knob defaults by name independent of node. 
# All nodes that have this knob name will have their defaultl overriden.
defaults = {
    'shutteroffset': 'centred',
    'note_font': 'Gotham-Book',
}
for knob, val in defaults.items():
    nuke.knobDefault(knob, val)


# Add default favorite directories that appear in the file browser.
favorite_dirs = {
    # 'dev': '/TuxedoMask/dev',
    # 'vault': '/cave/vault',
    # 'hdri': '/cave/vault/hdri',
    # 'stock': '/cave/vault/stock',
    # 'proj': '/cave/proj',
}
for name, path in sorted(list(favorite_dirs.items()), key=lambda k_v: k_v[0]):
    nuke.addFavoriteDir(name, path, nuke.IMAGE | nuke.SCRIPT | nuke.GEO | nuke.PYTHON)









# Initialize uistate
# Populate the uistate.ini file with some sane defaults.
# User overrides will stay in place
# https://support.foundry.com/hc/en-us/articles/360006950439-Q100538-How-to-set-default-values-for-knobs-and-preferences-stored-in-uistate-ini

try:
    from PySide2.QtCore import QSettings, QRect, QSize
except ImportError:
    from PySide.QtCore import QSettings, QRect, QSize

settings = QSettings(os.path.expanduser('~/.nuke/uistate.ini'), QSettings.IniFormat)

def setval(key, value):
    # Set uistate key if it is not yet defined
    if settings.value(key):
        return
    else:
        settings.setValue(key, value)

# General
setval('askedAboutAnalyticsInVersion12', 'true')
setval('showSplashScreen', 'false')
setval('submitUsageStatistics', 'false')


# Nuke
#setval('Nuke/startupWorkspace', 'comp_float')

# ColorPicker
# The sub-sections HSV RGB Swatches etc get converted to "\" when loaded in the uistate
setval('ColorPicker/Dynamic', 'true')
setval('ColorPicker/ShownColorSpaces/HSV', 'true')
setval('ColorPicker/ShownColorSpaces/RGB', 'true')
setval('ColorPicker/ShownColorSpaces/Swatches', 'false')
setval('ColorPicker/ShownColorSpaces/TMI', 'true')
setval('ColorPicker/ShownColorSpaces/Wheel', 'true')

# WindowLocations
# Has to be a QRect object, which gets translated to @Rect() in the uistate
setval('WindowLocations/ColorPicker', QRect(621, 574, 1041, 370))

# scripteditor
setval('scripteditor/SaveAndLoadHistory', 'true')

# FileBrowser
setval('FileBrowser/preview', 'true')
setval('FileBrowser/size', QSize(1050, 1050))