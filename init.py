import nuke
import sys
import os
import re

### SET TEMP DIRECTORY
if os.path.isdir('/Volumes/panda/_caches/Nuke'):
    NUKE_TEMP_DIR = '/Volumes/panda/_caches/Nuke'
elif os.path.isdir('/Volumes/Dettifoss/_caches/Nuke'):
    NUKE_TEMP_DIR = '/Volumes/Dettifoss/_caches/Nuke'
else:
    NUKE_TEMP_DIR = '~/_caches/Nuke'

#########################################
#         install NukeShared
#########################################
nuke.pluginAddPath( './NukeShared' )
#########
# node settings
#nuke.menu( 'Nodes' ).addCommand( 'Draw/Constant', "nuke.createNode( 'ConstantPro' )")
#nuke.menu( 'Nodes' ).addCommand( 'Time/FrameHold', "nuke.createNode( 'FrameHold_DS' )")
################################################################
# install layer suffler
################################################################
nuke.pluginAddPath('./layerShuffler')



#PLACE PLUGINS FOR SPECIFIC VERSIONS IN CERTAIN PLACES
if str(nuke.NUKE_VERSION_MAJOR)=='11'and str(nuke.NUKE_VERSION_MINOR)=="3":
    nuke.pluginAddPath("./11v3")

if str(nuke.NUKE_VERSION_MAJOR)=='12'and str(nuke.NUKE_VERSION_MINOR)=="1":
    nuke.pluginAddPath("./12v1")

if str(nuke.NUKE_VERSION_MAJOR)=='12' and str(nuke.NUKE_VERSION_MINOR)=="2":
    nuke.pluginAddPath("./12v2")

if str(nuke.NUKE_VERSION_MAJOR)=='13' and str(nuke.NUKE_VERSION_MINOR)=="2":
    nuke.pluginAddPath("./13v2")
