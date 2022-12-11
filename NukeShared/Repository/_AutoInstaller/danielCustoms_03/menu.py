###import modules
import nuke
import danielCustoms





#STORE MENUBAR
menubar = nuke.menu("Nuke")

#STORE NODESBAR

toolbar = nuke.menu('Nodes')
'''
#CHANGE DEFAULT FRAMEHOLD
nuke.menu('Nodes').addCommand('Time/FrameHold', 'danielCustoms.customFrameHold()', 'ctrl+shift+f', icon='FrameHold.png')

#CHANGE DEFAULT ROTO COMMAND
nuke.menu('Nodes').addCommand('Draw/Roto', 'danielCustoms.customRotoCommand()')

#CHANGE DEFAULT ROTOPAINT COMMAND
nuke.menu('Nodes').addCommand('Draw/RotoPaint', 'danielCustoms.customRotoPaintCommand()')

#CHANGE DEFAULT BACKDROP COMMAND
nuke.menu('Nodes').addCommand('Other/Backdrop', 'danielCustoms.createBackdrop()')

'''
#ADD DANIEL TOOLBAR MENU
dcmenu = menubar.addMenu("Daniel Customs")

#ADD DANIEL NODES MENU

dcMenuNodes = toolbar.addMenu('Daniel Customs', icon='danielCustoms.png')

##ADD DANIEL TOOLBAR MENU COMMANDS
'''#backdrops
dcmenu.addCommand('Preset Backdrop', 'Victor_Toolset.presetBackdrop()', 'shift+ctrl+b')'''
#bboxB
dcmenu.addCommand('Set all boundingboxes to B','danielCustoms.bboxB()','shift+ctrl+alt+b')
'''#read file check off
dcmenu.addCommand('Turn read file off on all write nodes','danielCustoms.readFileCheckOff()')
#convert gizmos to groups
dcmenu.addCommand('Convert all gizmos to groups','danielCustoms.gizmoToGroupAll()')
dcmenu.addCommand('Convert selected gizmos to groups','danielCustoms.gizmoToGroupSelected()')
'''
##ADD DANIEL NODES MENU COMMANDS
#SourceMatte
dcMenuNodes.addCommand('SourceMatte', 'nuke.createNode("SourceMatte")', icon='sourceMatte.png')
#custom grain
dcMenuNodes.addCommand('GrainCustom', 'nuke.createNode("GrainCustom")', icon='GrainCustom.png')
#V_EdgeMatte
dcMenuNodes.addCommand('V_EdgeMatte', 'nuke.createNode("V_EdgeMatte")', icon='V_EdgeMatte.png')
#TurbulentDisplace
dcMenuNodes.addCommand('TurbulentDisplace', 'nuke.createNode("TurbulentDisplace")', icon='TurbulentDisplace.png')
#PointDisplace
dcMenuNodes.addCommand('PointDisplacement', 'nuke.createNode("PointDisplacement")', icon='PointDisplacement.png')
#DespillMadness
dcMenuNodes.addCommand('DespillMadness', 'nuke.createNode("DespillMadness")',icon='despillmadness.png')
#lp_retile
dcMenuNodes.addCommand('Tiler', 'nuke.createNode("lp_reptile")',icon='tiler.png')
#WireRemover
dcMenuNodes.addCommand('WireRemover', 'nuke.createNode("WireRemover")', icon='WireRemover.png')
#MorphCut
dcMenuNodes.addCommand('MorphCut', 'nuke.createNode("Morph_Dissolve")',icon='MorphCut.png')
#ColorOverlay
dcMenuNodes.addCommand('ColorOverlay', 'nuke.createNode("ColorOverlay")',icon='ColorOverlay.png')
#ChangePass
dcMenuNodes.addCommand('ChangePass', 'nuke.createNode("ChangePass")',icon='ChangePass.png')
#ChangePass
dcMenuNodes.addCommand('Kaleido', 'nuke.createNode("TX_Kaleido")',icon='Kaleido.png')

##Defaults

#merge bounding box to b
nuke.knobDefault('Merge2.bbox','B')
#remove node
nuke.knobDefault('Remove.operation','keep')
nuke.knobDefault('Remove.channels','rgba')


