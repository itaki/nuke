import nuke

def kc():
    # collecting node and knob
    n = nuke.thisGroup()
    k = nuke.thisKnob()
    # defining expressions to pass down to retiming nodes
    offset_expression = '(compStart - elemStart) - (frame - compStart) * speed + (frame - compStart)'
    retime_expression_in = 'parent.elemStart'
    retime_expression_out = 'parent.compStart'
    retime_expression_speed = 'parent.speed'
    misc_expression = 'parent.outFrame'
    # going into the Group node
    n.begin()
    input = nuke.toNode('Dot')
    input_dep = input.dependent()
    del_node = input_dep[0]
    n.end()
    # leaving the Group node

    # check for trigger knob
    if k.name() == 'pull_grp':
        # storing selected value from pulldown menu
        selection = k.value()
        # going into the Group node
        n.begin()
        # checking if retiming node placeholder is present
        # if yes - delete it
        if not del_node.Class() == 'Dot':
            nuke.delete(del_node)
        else:
            pass
        input.knob('selected').setValue(True)
        # create retiming node based on pulldown menu selection
        time_node = nuke.createNode(selection, inpanel=False)
        time_node.knob('selected').setValue(False)
        # passing down the expression and adjusting values based on the node class
        if selection == 'TimeOffset':
            time_node.knob('time_offset').setExpression(offset_expression)
        elif selection == "Retime":
            time_node.knob('input.first_lock').setValue(True)
            time_node.knob('output.first_lock').setValue(True)
            time_node.knob('input.first').setExpression(retime_expression_in)
            time_node.knob('output.first').setExpression(retime_expression_out)
            time_node.knob('speed').setExpression(retime_expression_speed)
            time_node.knob('before').setValue("continue")
            time_node.knob('after').setValue("continue")
            time_node.knob('shutter').setValue(0)
        elif selection == "TimeWarp":
            time_node.knob('lookup').setExpression(misc_expression)
        elif selection == "OFlow2" or selection == "Kronos":
            time_node.knob('timing2').setValue('Frame')
            time_node.knob('timingFrame2').setExpression(misc_expression)
        # leaving the Group node
        n.end()
