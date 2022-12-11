import nuke
import nukescripts
import os
import re

def absFilePaths(nodes):
    for n in nodes:
        nPath = str(nuke.filename(n))
        n['file'].setValue(nPath)

def nodeWithFile():
    fileKnobNodes = [i for i in nuke.allNodes(recurseGroups=True) if nukescripts.searchreplace.__NodeHasFileKnob(i)]
    return fileKnobNodes

def searchReplaceProjDir(nodes):
    searchstr = str(nuke.root().knob('project_directory').evaluate() + "/")
    replacestr = ''
    try:
        for f in nodes:
            v = str(nuke.filename(f))
            repl = re.sub(searchstr, replacestr, v)
            try:
                f['file'].setValue(repl)
            except NameError:
                pass
    except TypeError:
            nuke.message('Project directory set, no nodes selected for change')

def newUserKnob(knob, value):
    knob.setValue(value)
    return knob

def selectNodesPanel():
    p = nukescripts.PythonPanel('Conform file paths to Project Directory')
    p.nodesSelection = nuke.Enumeration_Knob('nodesSel', 'Nodes selections', ['All nodes', 'Selected nodes only', 'Exclude selected nodes'])
    p.checkReadGeo = newUserKnob(nuke.Boolean_Knob('checkReadGeo', 'Exclude ReadGeo nodes', '0'), 0)
    p.readGeoText = nuke.Text_Knob('readGeoText', '', 'Will affect configured scenegraph')
    for k in (p.nodesSelection, p.checkReadGeo, p.readGeoText):
        k.setFlag(0x1000)
        p.addKnob(k)

    if p.showModalDialog():
        if p.nodesSelection.value() == 'All nodes':
            Sel = nodeWithFile()
        elif p.nodesSelection.value() == 'Selected nodes only':
            Sel = nuke.selectedNodes()
        else:
            Sel = nodeWithFile()
            for i in nuke.selectedNodes():
                try:
                    Sel.remove(i)
                except ValueError:
                    pass

        if p.checkReadGeo.value():
            try:
                for n in nuke.allNodes():
                    if n.Class() == 'ReadGeo2':
                        Sel.remove(n)
            except ValueError:
                pass

        return Sel


def setProjDir(var):
    if var == 0:
        try:
            filepath = os.path.dirname(nuke.getFilename('Set Project Directory'))
        except (TypeError, ValueError):
            nuke.message('Project directory not set!')
    elif var == 1:
        filepath = '[join [lrange [split [file dirname [knob root.name]] "/"] 0 end-0] "/"]'
    elif var == 2:
        filepath = '[join [lrange [split [file dirname [knob root.name]] "/"] 0 end-1] "/"]'
    elif var == 3:
        filepath = '[join [lrange [split [file dirname [knob root.name]] "/"] 0 end-2] "/"]'
    elif var == 4:
        filepath = '[join [lrange [split [file dirname [knob root.name]] "/"] 0 end-3] "/"]'
    else:
        filepath = '[join [lrange [split [file dirname [knob root.name]] "/"] 0 end-4] "/"]'

    changeNodes = selectNodesPanel()
    absFilePaths(changeNodes)
    nuke.root().knob("project_directory").setValue(filepath)
    searchReplaceProjDir(changeNodes)


def absFilePathsSel():
    try:
        absFilePaths(nuke.selectedNodes())
    except NameError:
        nuke.message('No "file" knob found in selected Nodes.')

def SelNodeWithFile():
    for n in nodeWithFile():
        n.knob('selected').setValue('True')

nodeMenu = nuke.menu('Nuke').findItem('Edit/Node')
nodeMenu.addCommand('Custom/Convert file path to absolute', 'setProjDir.absFilePathsSel()')
nodeMenu.addCommand('Custom/Select nodes with File Knob', 'setProjDir.SelNodeWithFile()')

fileMenu = nuke.menu('Nuke').findItem('File').addMenu('Set Project Directory')
fileMenu.addCommand('Custom path', 'setProjDir.setProjDir(0)')


def addRelPathCommand():
    fileMenu.addCommand(re.escape(nuke.script_directory().rsplit('/',4)[0]), 'setProjDir.setProjDir(5)')
    fileMenu.addCommand(re.escape(nuke.script_directory().rsplit('/',3)[0]), 'setProjDir.setProjDir(4)')
    fileMenu.addCommand(re.escape(nuke.script_directory().rsplit('/',2)[0]), 'setProjDir.setProjDir(3)')
    fileMenu.addCommand(re.escape(nuke.script_directory().rsplit('/',1)[0]), 'setProjDir.setProjDir(2)')
    fileMenu.addCommand(re.escape(nuke.script_directory().rsplit('/',0)[0]), 'setProjDir.setProjDir(1)')

#Add relative project directory to File menu when a script is open
nuke.addOnScriptLoad(addRelPathCommand, nodeClass='Root')
