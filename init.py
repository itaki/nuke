import nuke
import sys
import os
import re

### SET TEMP DIRECTORY
from itaki_tools.i_tools import set_cache_disk
PREFERRED_CACHE_DISKS = ['Mercury','Dettifoss','Dettifoss2']
CACHE_DIR = '_caches/nuke'
set_cache_disk.DiskCache(PREFERRED_CACHE_DISKS,CACHE_DIR).set_cache_location()
            


#########################################
#         install NukeShared
#########################################
nuke.pluginAddPath( './NukeShared' )
#########
# node settings
#set a default for rotopaint
# this little buddy doesn't work in the defaults.py file
#  <default node="RotoPaint" knob="toolbox">'''clone { { brush ltt 0 h 0 } { clone ltt 0 h 0} { blur ltt 2} { sharpen ltt 2 h 0}{ smear ltt 2 h 0} { eraser ltt 2 h 0} { reveal ltt 2 h 0} { dodge ltt 2 h 0} { burn ltt 2 h 0} }'''</default>
nuke.knobDefault("RotoPaint.toolbox", '''clone { 
                 { brush ltt 0 h 0 } 
                 { clone ltt 0 h 0} 
                 { blur ltt 2} 
                 { sharpen ltt 2 h 0}
                 { smear ltt 2 h 0} 
                 { eraser ltt 2 h 0} 
                 { reveal ltt 2 h 0} 
                 { dodge ltt 2 h 0} 
                 { burn ltt 2 h 0} 
                 }''')
# this
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
