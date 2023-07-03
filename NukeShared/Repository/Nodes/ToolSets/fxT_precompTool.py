"""======================================================================================================================

DEVELOPER: Tor Andreassen - www.fxtor.net
DATE: October 28, 2021
VERSION: v1.3


DESCRIPTION:

    This file contains the code that run in the fxT_precomp Switch and fxT_precompController
    It's put in this external file so that your nuke script using these precompTools won't have
    multiple nodes with duplicate code since nuke scripts can contain many of these fxT_precomp switches

    This file works together with the fxT_precompSetup and the fxT_precompController toolsets


USAGE:

    copy this python file into your .nuke directory and make sure you can access the location of this file in the init py.file

    example:

    put this in your init.py file:
        nuke.pluginAddPath('./fxT_tools/fxT_pythonTools')

    put this in your menu.py file:
        import fxT_precompTool

======================================================================================================================"""
import nuke

def usePrecomp():
    global fxT_forceCompPipe
    fxT_forceCompPipe = 0
    try:
        mee = nuke.thisNode()
        me = mee.input(1).name()
        topnode_name = nuke.tcl("full_name [topnode %s]" % me)


        ### PATH EDIT HERE (textfield for preComp name)         
        pathy = str(nuke.toNode(topnode_name)['file'].getValue().rsplit(".").__getitem__(0))

        ### split and join precompName path to your specific preference here:
        pathy = pathy.split("/")
        pathy = pathy[-1]
        ### END PATH EDIT

        mee['precompName'].setEnabled(True)
        mee['precompName'].setValue(pathy)
        mee['precompName'].setEnabled(False)

        mee['tile_color'].setValue(0x3d962bff)
        mee['label'].setValue('PRECOMP')

        nuke.toNode(topnode_name)['tile_color'].setValue(0x3d962bff)

        mee['which'].setValue(1)
        mee['status'].setValue("[<font color='green'>v</font>]")

    except:
        fxT_forceCompPipe = 1
        mee = nuke.thisNode()
        mee['tile_color'].setValue(0xff0000ff)
        mee['precompName'].setEnabled(True)
        mee['precompName'].setValue('')
        mee['precompName'].setEnabled(False)
        mee['label'].setValue('COMP')
        mee['which'].setValue(0)
        mee['status'].setValue("[<font color='dark red'>x</font>]")
        nuke.message(str(mee.name())+': input pipe 1 does not have a preComp Read Node, please try again when node has the right inputs.\n\ncurrently comp is being used as precomp does not exist')

    #set backdrop color
    mee = nuke.thisNode()
    allBDs = nuke.allNodes('BackdropNode')
    nodeBackdrops = []

    # store original selection
    originalSelection = nuke.selectedNodes()

    for bd in allBDs:
        # clear original selection
        for n in nuke.allNodes():
            n.setSelected(False)
        # select backdrop nodes
        bd.selectNodes()
        #store new selection
        bdNodes = nuke.selectedNodes()
        if mee in bdNodes:
            nodeBackdrops.append(bd)

    # restore previous selection
    for n in nuke.selectedNodes():
        n.setSelected(n in originalSelection)

    for i in nodeBackdrops:
        if fxT_forceCompPipe == 0:
            i['tile_color'].setValue(658974719)
        elif fxT_forceCompPipe == 1:
            i['tile_color'].setValue(1593835520)


##########################################################################################################

def useComp():
    try:
        mee = nuke.thisNode()
        me = mee.input(1).name()
        topnode_name = nuke.tcl("full_name [topnode %s]" % me)
        pathy = str(nuke.toNode(topnode_name)['file'].getValue().rsplit(".").__getitem__(0))
        mee['precompName'].setValue("")

        mee['tile_color'].setValue(0xff0000ff)
        mee['label'].setValue('COMP')

        nuke.toNode(topnode_name)['tile_color'].setValue(0xff0000ff)

        mee['which'].setValue(0)
        mee['status'].setValue("[<font color='dark red'>x</font>]")

    except:
        mee = nuke.thisNode()
        mee['which'].setValue(0)
        mee['tile_color'].setValue(0xff0000ff)
        mee['label'].setValue('COMP')
        mee['status'].setValue("[<font color='dark red'>x</font>]")

        mee['precompName'].setEnabled(True)
        mee['precompName'].setValue('')
        mee['precompName'].setEnabled(False)

        #nuke.message(str(mee.name())+': input pipe 1 does not have a preComp Read Node, please try again when node has the right inputs.\n\ncurrently comp is being used as precomp does not exist')


    #set backdrop color
    mee = nuke.thisNode()
    allBDs = nuke.allNodes('BackdropNode')
    nodeBackdrops = []

    # store original selection
    originalSelection = nuke.selectedNodes()

    for bd in allBDs:
        # clear original selection
        for n in nuke.allNodes():
            n.setSelected(False)
        # select backdrop nodes
        bd.selectNodes()
        #store new selection
        bdNodes = nuke.selectedNodes()
        if mee in bdNodes:
            nodeBackdrops.append(bd)

    # restore previous selection
    for n in nuke.selectedNodes():
        n.setSelected(n in originalSelection)

    for i in nodeBackdrops:
        i['tile_color'].setValue(1593835520)


##########################################################################################################

def makeSticky():
    mee = nuke.thisNode()
    x = mee.xpos()+100
    y = mee.ypos()+50
    stickyName = str(mee.name()+'_sticky')

    if (nuke.toNode(stickyName)):
        nuke.delete(nuke.toNode(stickyName))
    else:
        sticky = nuke.nodes.StickyNote (name=stickyName)
        sticky.setXYpos(x,y)
        sticky['label'].setValue('ON FARM')
        sticky['note_font_size'].setValue(45)
        sticky['tile_color'].setValue(3329493247)


##########################################################################################################

def toggleControllerStatus(): 
    mee = nuke.thisNode()
    status = mee['isLegal'].getValue()
    mee['isLegal'].setValue(not status)
    status = not status

    if (status == 1):
        mee['legalStatus'].setValue("<font color ='green'>&nbsp;&nbsp;&nbsp;&nbsp; This precomp is part of the precompController</font>")
    elif (status == 0):
        mee['legalStatus'].setValue("<font color ='dark red'>&nbsp;&nbsp;&nbsp;&nbsp; This precomp is not part of the precompController</font>")


##########################################################################################################
def controller():
    def disableUndo():
        nuke.Undo().disable() #disable undo function so it doesn not record knob updates
    disableUndo()

    def getPrecompnodes():

        mee = nuke.thisNode()
        switchList =[] #reset list

        #remove all custom knobs
        keepKnobs = ['note_font', 'xpos', 'knobChanged', 'name', 'tile_color', 'hide_input', 'selected', 'autolabel', 'ypos', 'note_font_size', 'label', 'onDestroy', 'note_font_color', 'rootNodeUpdated', 'indicators', 'gl_color', 'onCreate', 'icon', 'updateUI', 'panel', 'help', 'getPrecompnodes','zoom']
        for i in mee.knobs():
            if mee.knob(i).name() not in keepKnobs:
                mee.removeKnob(mee.knob(i))

        #add diviver between button and precomp knobs
        mee.addKnob(nuke.Text_Knob('fxT_precompSwitch_BaseDiv','',''))

        #loop though precomp switches, add them to list and sort list 
        for i in nuke.allNodes('Switch'):
            if (i.knob('isLegal')) and (i.knob('isLegal').value() == 1):
                switchList.append( str(i.name() ))

        switchList.sort()

        #build precomp knobs
        for i in switchList:
            mee.addKnob(nuke.String_Knob(i+'node','node',i))
            mee.knob(i+'node').clearFlag(nuke.STARTLINE)
            mee.knob(i+'node').setEnabled(False)
            mee.addKnob(nuke.String_Knob(i+'precompName','name',nuke.toNode(i)['precompName'].value() ))
            mee.knob(i+'precompName').clearFlag(nuke.STARTLINE)
            mee.knob(i+'precompName').setEnabled(False)

            code = "def code():\n"+"\tif nuke.toNode('" + str(i) + "') is not None:\n\n" + "\t\tnuke.toNode('" + str(i) + "')['usePrecomp'].execute()"+  "\n\t\tnuke.thisNode()['" + str(i) +"status'].setValue(nuke.toNode('"+str(i)+"')['status'].value()"+")" + "\n\t\tnuke.thisNode()['" + str(i) +"precompName'].setValue(nuke.toNode('"+str(i)+"')['precompName'].value()"+")"+"\n\telse:\n"+"\t\tnuke.message('"+str(i)+" does not exist, click update to remove node')"+"\ncode()"

            code2 = "def code2():\n"+"\tif nuke.toNode('" + str(i) + "') is not None:\n\n" + "\t\tnuke.toNode('" + str(i) + "')['useComp'].execute()"+  "\n\t\tnuke.thisNode()['" + str(i) +"status'].setValue(nuke.toNode('"+str(i)+"')['status'].value()"+")" + "\n\t\tnuke.thisNode()['" + str(i) +"precompName'].setValue('')"+"\n\telse:\n"+"\t\tnuke.message('"+str(i)+" does not exist, click update to remove node')"+"\ncode2()"

            code3 = "def code3():\n"+"\tif nuke.toNode('" + str(i) + "') is not None:\n\n" + "\t\tnuke.toNode('" + str(i) + "')['zoom'].execute()"+"\n\telse:\n"+"\t\tnuke.message('"+str(i)+" does not exist, click update to remove node')"+"\ncode3()"

            mee.addKnob(nuke.PyScript_Knob(i+'use_preComp',"<font color='light green'><b>use preComp</b></font>", code ) )
            mee.addKnob(nuke.PyScript_Knob(i+'use_Comp',"<font color='dark red'><b>use Comp</b></font>", code2 ) )
            mee.addKnob(nuke.PyScript_Knob(i+'zoom',"<font color='light grey'><b>zoom</b></font>", code3 ) )

            mee.addKnob(nuke.Text_Knob(str(i)+'status', '',nuke.toNode(i)['status'].value() ))
            mee.knob(i+'status').clearFlag(nuke.STARTLINE)

            mee.addKnob(nuke.Text_Knob(i+'Div','',''))

    getPrecompnodes()

    def updateInputNames():
        try:
            allPrecompSwitches = []
            for i in nuke.thisNode().knobs():
                if i.startswith('fxT_precompSwitch') and 'node' in i:
                    allPrecompSwitches.append(i)

            for i in allPrecompSwitches:
                switchName = nuke.thisNode()[i].value()
                if nuke.toNode(switchName)['tile_color'].value() == 1033251839:
                    nuke.toNode(switchName)['usePrecomp'].execute()
                elif nuke.toNode(switchName)['tile_color'].value() == 4278190335:
                    nuke.toNode(switchName)['useComp'].execute()
                else:
                    pass
        except:
            pass
    updateInputNames()

    # run code again to update precomp-names display. first time this is executed, knobs are built with the values from the precomp switch nodes,
    # then the swiches are updated, and names might have changed based on the precomp-input read node. to update the precomp-names in
    # this node, we build the knobs again to make sure knob vales are correct if the button execution changed the precomp input names
    getPrecompnodes()

    def enableUndo():
        try:
            nuke.Undo().enable() #bring undo back to life 
        except:
            nuke.Undo().enable() # failsafe to make absolutly sure undo records like normal; using try/catch in case some versions of nuke has issues with undo.enable()
    enableUndo()
