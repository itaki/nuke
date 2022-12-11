####################################

'''
bjorkvisuals public tools, a.k.a sb Tools.
autor: simon bjork
simon@bjorkvisuals.com
latest update: 2014-10-04
'''

####################################

'''
Import standard Python modules.
'''
import nuke
import os

####################################

'''
Add plugin paths.
'''
nuke.pluginAddPath('./gizmos')
nuke.pluginAddPath('./python')
nuke.pluginAddPath('./icons')

####################################

'''
Import bjorkvisuals Python scripts.
'''
# Import scripts.
import sb_addViewerLuts
import sb_autoRender
import sb_createRead
import sb_saveRenderBackup

####################################

'''
User variables/Folder paths.
'''
# Backup path (Nuke scripts)
nukeBackupPath = "E:/_backup/nuke_backup/"

# Viewer LUTs.
addViewerLutsPath = "E:/color/luts/"

####################################

'''
Set beforeRender callbacks.
'''
nuke.addBeforeRender(sb_autoRender.sb_autoRender)

####################################

'''
Set afterRender callbacks.
'''
nuke.addAfterRender(sb_saveRenderBackup.sb_saveRenderBackup, (nukeBackupPath))

####################################

'''
Custom create read function.
Support for OCIO via the USE_OCIO environment variable (0/1)
'''
# os.environ["USE_OCIO"] = "1"
nukescripts.create_read = sb_createRead.sb_createRead

####################################

'''
Add viewer luts.
'''
sb_addViewerLuts.sb_addViewerLuts(addViewerLutsPath, addCineonLut = True)

####################################