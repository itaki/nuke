import nuke
import sys
import os
import re

### SET TEMP DIRECTORY
from itaki_tools.i_tools import set_cache_disk
PREFERRED_CACHE_DISKS = ['panda','Dettifoss','Dettifoss2']
CACHE_DIR = '_caches/nuke'
set_cache_disk.DiskCache(PREFERRED_CACHE_DISKS,CACHE_DIR).set_cache_location()
            


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

################################################################
# install itaki tools / DEV stuff
################################################################
nuke.pluginAddPath('./itaki_tools')

#PLACE PLUGINS FOR SPECIFIC VERSIONS IN CERTAIN PLACES
if str(nuke.NUKE_VERSION_MAJOR)=='11'and str(nuke.NUKE_VERSION_MINOR)=="3":
    nuke.pluginAddPath("./11v3")

if str(nuke.NUKE_VERSION_MAJOR)=='12'and str(nuke.NUKE_VERSION_MINOR)=="1":
    nuke.pluginAddPath("./12v1")

if str(nuke.NUKE_VERSION_MAJOR)=='12' and str(nuke.NUKE_VERSION_MINOR)=="2":
    nuke.pluginAddPath("./12v2")

if str(nuke.NUKE_VERSION_MAJOR)=='13' and str(nuke.NUKE_VERSION_MINOR)=="2":
    nuke.pluginAddPath("./13v2")
