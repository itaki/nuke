
import math
import nuke

ControlNode = nuke.thisNode()

try:

    WarpAknob = ControlNode.knob('SplineWarp_A')
    WarpBknob = ControlNode.knob('SplineWarp_B')
    WarpCknob = ControlNode.knob('SplineWarp_C')
    
    
    WarpANode = nuke.toNode(WarpAknob.value())
    
    CamAName = ControlNode.knob('CamA_name').value()
    CamANode = nuke.toNode(CamAName)
    
    
    CamBName = ControlNode.knob('CamB_name').value()
    CamBNode = nuke.toNode(CamBName)
    
    CamCName = ControlNode.knob('CamC_name').value()
    CamCNode = nuke.toNode(CamCName)    
    
    
    ControlNode['haperture_A'].setValue(CamANode['haperture'].getValue())
    ControlNode['vaperture_A'].setValue(CamANode['vaperture'].getValue())
    ControlNode['focus_A'].setValue(CamANode['focal'].getValue())
    
    ControlNode['translate_A'].setExpression( CamAName +".translate.x", 0)
    ControlNode['translate_A'].setExpression( CamAName +".translate.y", 1)
    ControlNode['translate_A'].setExpression( CamAName +".translate.z", 2)
    ControlNode['rotate_A'].setExpression( CamAName +".rotate.x", 0)
    ControlNode['rotate_A'].setExpression( CamAName +".rotate.y", 1)
    ControlNode['rotate_A'].setExpression( CamAName +".rotate.z", 2)
    
    
    ControlNode['haperture_B'].setValue(CamBNode['haperture'].getValue())
    ControlNode['vaperture_B'].setValue(CamBNode['vaperture'].getValue())
    ControlNode['focus_B'].setValue(CamBNode['focal'].getValue())
    
    ControlNode['translate_B'].setExpression( CamBName +".translate.x", 0)
    ControlNode['translate_B'].setExpression( CamBName +".translate.y", 1)
    ControlNode['translate_B'].setExpression( CamBName +".translate.z", 2)
    ControlNode['rotate_B'].setExpression( CamBName +".rotate.x", 0)
    ControlNode['rotate_B'].setExpression( CamBName +".rotate.y", 1)
    ControlNode['rotate_B'].setExpression( CamBName +".rotate.z", 2)
    
    
    ControlNode['translate_C'].setExpression( CamCName +".translate.x", 0)
    ControlNode['translate_C'].setExpression( CamCName +".translate.y", 1)
    ControlNode['translate_C'].setExpression( CamCName +".translate.z", 2)
    ControlNode['rotate_C'].setExpression( CamCName +".rotate.x", 0)
    ControlNode['rotate_C'].setExpression( CamCName +".rotate.y", 1)
    ControlNode['rotate_C'].setExpression( CamCName +".rotate.z", 2)    
    
    
    ControlNode['pic_w'].setValue(WarpANode.width())
    ControlNode['pic_h'].setValue(WarpANode.height())
    
    ControlNode['LatLong_w'].setValue(ControlNode.width())
    ControlNode['LatLong_h'].setValue(ControlNode.height())
    
except:
    nuke.message('Check Cameras and SplineWarps names')
