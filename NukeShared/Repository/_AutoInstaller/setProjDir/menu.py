import setProjDir

#Create toolbar with icon
toolbar = nuke.menu('Nodes').addMenu('jj_tools', icon='icon_JJ.png')

#Python menu
Pytmenu = toolbar.addMenu('Python')
Pytmenu.addCommand('Convert file path to absolute', 'setProjDir.absFilePathsSel()')
Pytmenu.addCommand('Select nodes with File Knob', 'setProjDir.SelNodeWithFile()')

#directory for setProjDir
projDirMenu = Pytmenu.addMenu('Set Project Directory')
projDirMenu.addCommand('Custom Path', 'setProjDir.setProjDir(0)')
def addRelPathCommandMenu():
    import re
    projDirMenu.addCommand(re.escape(nuke.script_directory().rsplit('/',4)[0]), 'setProjDir.setProjDir(5)')
    projDirMenu.addCommand(re.escape(nuke.script_directory().rsplit('/',3)[0]), 'setProjDir.setProjDir(4)')
    projDirMenu.addCommand(re.escape(nuke.script_directory().rsplit('/',2)[0]), 'setProjDir.setProjDir(3)')
    projDirMenu.addCommand(re.escape(nuke.script_directory().rsplit('/',1)[0]), 'setProjDir.setProjDir(2)')
    projDirMenu.addCommand(re.escape(nuke.script_directory().rsplit('/',0)[0]), 'setProjDir.setProjDir(1)')

#Add relative project directory to File menu when a script is open
nuke.addOnScriptLoad(addRelPathCommandMenu, nodeClass='Root')
