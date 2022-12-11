import nuke
import nukescripts

###Create function for bbox to B
def bboxB():
    for i in nuke.selectedNodes():
        try:
            i.knob('bbox').setValue('B')
        except:
            pass
###Create function for turning read file off
def readFileCheckOff():
    for i in nuke.allNodes():
        if i.Class() == "Write":
            i.knob('reading').setValue(0)

###Create function for custom Frame Hold
def customFrameHold():
    nuke.createNode("FrameHold.gizmo")
    nuke.selectedNode().knob('first_frame').setValue(nuke.frame())



###Create function for custom RotoPaint Command
def customRotoPaintCommand():
    #Store selected nodes
    try:
        n = nuke.selectedNode()
        nClass = n.Class()
    except:
        nClass = 'banaan'

    if nClass == 'Tracker4' :   
        n.knob('transform').setValue('match-move') 
        nName = n.knob('name').getValue()
        #create and store roto
        roto = nuke.createNode('RotoPaint')
        rotoName = roto.knob('name').getValue()
        #link transforms
        roto.knob('translate').setExpression('parent.' + nName + '.translate')
        roto.knob('rotate').setExpression('parent.' + nName + '.rotate')
        roto.knob('scale').setExpression('parent.' + nName + '.scale')
        roto.knob('center').setExpression('parent.' + nName + '.center')
        #clear input
        roto.setInput(0,None)
        #set position
        roto.setXpos(n.xpos() + 100)
        roto.setYpos(n.ypos() + 100)
    else:
        nuke.createNode('RotoPaint')




###Create function for custom Roto Command
def customRotoCommand():
    #Store selected nodes
    try:
        n = nuke.selectedNode()
        nClass = n.Class()
    except:
        nClass = 'banaan'

    if nClass == 'Tracker4' :
        n.knob('transform').setValue('match-move')     
        nName = n.knob('name').getValue()
        #create and store roto
        roto = nuke.createNode('Roto')
        rotoName = roto.knob('name').getValue()
        #link transforms
        roto.knob('translate').setExpression('parent.' + nName + '.translate')
        roto.knob('rotate').setExpression('parent.' + nName + '.rotate')
        roto.knob('scale').setExpression('parent.' + nName + '.scale')
        roto.knob('center').setExpression('parent.' + nName + '.center')
        #clear input
        roto.setInput(0,None)
        #set position
        roto.setXpos(n.xpos() + 100)
        roto.setYpos(n.ypos() + 100)
    else:
        nuke.createNode('Roto')
###Create function that converts gizmos to groups
def emptySelection():
    #a function to deselect all nodes
    for i in nuke.selectedNodes():
        i.knob('selected').setValue(False)

def gizmoToGroup(gizmo):
    #store attributes
    try:
        input0 = gizmo.input(0)
    except:
        pass
    try:
        input1 = gizmo.input(1)
    except:
        pass
    try:
        input2 = gizmo.input(2)
    except:
        pass
    try:
        input3 = gizmo.input(3)
    except:
        pass
    

    xpos = gizmo.xpos()
    ypos = gizmo.ypos()
    name = gizmo.knob('name').getValue()


    #copy Gizmo To group
    emptySelection()
    gizmo.knob('selected').setValue(True)
    nuke.tcl('copy_gizmo_to_group [ selected_node ]')



    nuke.delete(gizmo)


    n = nuke.selectedNode()

    #set attributes
    try:
        n.setInput(0,input0)
    except:
        pass
    try:
        n.setInput(1,input1)
    except:
        pass
    try:
        n.setInput(2,input2)
    except:
        pass
    try:
        n.setInput(3,input3)
    except:
        pass


    n.setXpos(xpos)
    n.setYpos(ypos)
    n.knob('name').setValue(name)
    
###Create function that converts all gizmos to groups
def gizmoToGroupAll():
    for i in nuke.allNodes():
        if i.knob('gizmo_file'):
            
            try:
                gizmoToGroup(i)
           
            except:
                pass

###Create function that converts selected gizmos to groups
def gizmoToGroupSelected():
    for i in nuke.selectedNodes():
        if i.knob('gizmo_file'):
            
            try:
                gizmoToGroup(i)
           
            except:
                pass

### Custom backdrop creation function
def createBackdrop():
    ns = nuke.selectedNodes()
    n = nukescripts.autoBackdrop()
    n.knob('note_font').setValue('Avenir Black')
    n.knob('label').setValue('<center><img src=InsertIcon.png>')
    try:
        xPosList = []
        for i in ns:
            xPosList.append(i.xpos())
        fontSize = (max(xPosList)-min(xPosList))*.1
        if fontSize < 30:
            fontSize = 30
        n.knob('note_font_size').setValue(int(fontSize))
    except:
        pass
    nuke.show(n,0)