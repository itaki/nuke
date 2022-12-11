
import math
import nuke

# 
# This set of functions will be used for future releases
#
        
        
def LatlongToProj ( latlX, latlY, CamNode, SrcImg, latlongIm):
    
    height_im = float(SrcImg.height()) 
    width_im = float(SrcImg.width()) 
    h_aperture = CamNode['haperture'].getValue()
    v_aperture = CamNode['vaperture'].getValue()
    focal = CamNode['focal'].getValue()
    w = CamNode['rotate'].getValue()
    
    PtAngleV = w[1] - latlY * 180/float(latlongIm.height()) -90
    PtAngleH = (0.5 - latlX/float(latlongIm.width())) * 360 - w[0]
    
    h_deltaQ = math.tan(math.radians(PtAngleH)) * focal
    v_deltaQ = math.tan(math.radians(PtAngleV)) * focal
    
    PtX = (0.5 - h_deltaQ/h_aperture) * width_im
    PtY = (0.5 - v_deltaQ/v_aperture) * height_im

    return PtX, PtY


def LatlongToProjX ( latlX, width_im , h_aperture, latlong_w, focal, rotcam_x):
    
    PtAngleH = (0.5 - latlX/latlong_w) * 360 - rotcam_x
    h_deltaQ = math.tan(math.radians(PtAngleH)) * focal
    PtX = (0.5 - h_deltaQ/h_aperture) * width_im
    
    return PtX

def LatlongToProjY ( latlY , height_im , v_aperture, latlong_h, focal, rotcam_y):

    
    PtAngleV = rotcam_y - latlY * 180/latlong_h - 90
    v_deltaQ = math.tan(math.radians(PtAngleV)) * focal
    PtY = (0.5 - v_deltaQ/v_aperture) * height_im

    return PtY


def LatlToPrX ( latlX, width_im , h_aperture, latlong_w, focal, rotcam_x):
    
    PtX = (0.5 - math.tan(math.radians((0.5 - latlX/latlong_w) * 360 - rotcam_x)) * focal/h_aperture) * width_im
    
    return PtX



def LatlToPrY ( latlY , height_im , v_aperture, latlong_h, focal, rotcam_y):
   
    PtY = (0.5 - math.tan(math.radians(rotcam_y - latlY * 180/latlong_h - 90)) * focal/v_aperture) * height_im

    return PtY
        

#
# Here TCL formula
#
# ControlCurve - control node
# Bezier1  - control curve
# 
# latlX : ControlCurve.curves.Bezier1.curve_points.5.main.x
# (possible  left.x   right.x   - for tangents)
#
# latlong_w = ControlCurve.LatLong_w
# rotcam_x = ControlCurve.rotate_A.x  ,ControlCurve.rotate_A.y , ControlCurve.rotate_B.x
# focal = ControlCurve.focus_A
# h_aperture = ControlCurve.haperture_A
# width_im = ControlCurve.pic_w
#
#  ...main.x = (0.5 - tan(radians((0.5 - ControlCurve.curves.Bezier1.curve_points.5.main.x/ControlCurve.LatLong_w) * 360 - ControlCurve.rotate_A.y)) * ControlCurve.focus_A/ControlCurve.haperture_A) * ControlCurve.pic_w  
#  ...main.y = (0.5 - tan(radians(ControlCurve.rotate_A.x - ControlCurve.curves.Bezier1.curve_points.5.main.y * 180/ControlCurve.LatLong_h - 90)) * ControlCurve.focus_A/ControlCurve.vaperture_A) * ControlCurve.pic_h  
#  ...left.x = ControlCurve.curves.Bezier1.curve_points.5.right.x/ControlCurve.TanS
#  ...left.y = ControlCurve.curves.Bezier1.curve_points.5.right.y/ControlCurve.TanS
#  ...right.x = ControlCurve.curves.Bezier1.curve_points.5.right.x/ControlCurve.TanS
#  ...right.y = ControlCurve.curves.Bezier1.curve_points.5.right.y/ControlCurve.TanS
#  
#




def SetFormulaForWarp ( BaseCurveName,  PrefixName, CtrlNode):
    pTime =0
    
    
    
    Warpknob = CtrlNode.knob('SplineWarp_' + PrefixName)
    wrpNode = nuke.toNode(Warpknob.value())    
    warpCurve = wrpNode['curves']    
    wrpRoot = warpCurve.rootLayer
    
    
    ctrCurve = CtrlNode['curves']
    ctrRoot = ctrCurve.rootLayer
    
    shape = ctrRoot[0]
    for sh in ctrRoot:
        if sh.name == BaseCurveName:
            shape = sh
    
    wrpShape = wrpRoot[0]
    for wh in ctrRoot:
        if wh.name == 'Bezier2':
            wrpShape = wh    
    
    mainXStr = '(0.5 - tan(radians((0.5 - ControlCurve.curves.%s.curve_points.%s.main.x/ControlCurve.LatLong_w) * 360 - ControlCurve.rotate_%s.y)) * ControlCurve.focus_A/ControlCurve.haperture_A) * ControlCurve.pic_w'  
    mainYStr = '(0.5 - tan(radians(ControlCurve.rotate_%s.x - ControlCurve.curves.%s.curve_points.%s.main.y * 180/ControlCurve.LatLong_h - 90)) * ControlCurve.focus_A/ControlCurve.vaperture_A) * ControlCurve.pic_h'  
    leftXStr = 'ControlCurve.curves.%s.curve_points.%s.left.x * ControlCurve.TanS'
    leftYStr = 'ControlCurve.curves.%s.curve_points.%s.left.y * ControlCurve.TanS'
    rightXStr = 'ControlCurve.curves.%s.curve_points.%s.right.x * ControlCurve.TanS'
    rightYStr = 'ControlCurve.curves.%s.curve_points.%s.right.y * ControlCurve.TanS'
    
    pt_type = 0 
    ptcount = 0
       
    
    for ind,points in enumerate(warpCurve.toElement(BaseCurveName + '/' + BaseCurveName + '_Dest')):        
        aCurveX = points.getPositionAnimCurve(0)
        aCurveY = points.getPositionAnimCurve(1)
        #print ind
        
        # expression for left tangent   
        if pt_type == 0:
            aCurveX.expressionString = leftXStr %(BaseCurveName,str(ptcount))
            aCurveY.expressionString = leftYStr %(BaseCurveName,str(ptcount))
            aCurveX.useExpression = True
            aCurveY.useExpression = True  
            pt_type += 1
        
        # expression for main point  
        elif pt_type == 1:
            aCurveX.expressionString = mainXStr %(BaseCurveName,str(ptcount),PrefixName)
            aCurveY.expressionString = mainYStr %(PrefixName, BaseCurveName,str(ptcount))
            aCurveX.useExpression = True
            aCurveY.useExpression = True   
            pt_type += 1  
            
        # expression for right tangent    
        elif pt_type == 2:
            aCurveX.expressionString = rightXStr %(BaseCurveName,str(ptcount))
            aCurveY.expressionString = rightYStr %(BaseCurveName,str(ptcount))
            aCurveX.useExpression = True
            aCurveY.useExpression = True   
            pt_type = 0   
            ptcount += 1
    
        points.setPositionAnimCurve(0, aCurveX)  
        points.setPositionAnimCurve(1, aCurveY)  
    
    warpCurve.changed()    
    
    #    print wrpShape.serialise()
    
    return                



ControlNode = nuke.toNode('ControlCurve')
#ControlNode = nuke.thisNode()

ctrCurve = ControlNode['curves']



WarpAknob = ControlNode.knob('SplineWarp_A')
WarpANode = nuke.toNode(WarpAknob.value())

WarpBknob = ControlNode.knob('SplineWarp_B')
WarpBNode = nuke.toNode(WarpBknob.value())   

WarpCknob = ControlNode.knob('SplineWarp_C')
WarpCNode = nuke.toNode(WarpCknob.value())  
    

    
CamAName = ControlNode.knob('CamA_name').value()
CamANode = nuke.toNode(CamAName)
    
    
CamBName = ControlNode.knob('CamB_name').value()
CamBNode = nuke.toNode(CamBName)

CamCName = ControlNode.knob('CamC_name').value()
CamCNode = nuke.toNode(CamCName)


wrpNodeA = WarpANode
wrpCurveA = wrpNodeA['curves']

wrpNodeB = WarpBNode
wrpCurveB = wrpNodeB['curves']

wrpNodeC = WarpCNode
wrpCurveC = wrpNodeC['curves']

ControlCurveName = ControlNode.knob('CtrCurvesList').value()


if ControlNode.knob('InfluenceArea').value() == 'AB':
    SetFormulaForWarp ( 'Bezier1',  'A', ControlNode)
    SetFormulaForWarp ( 'Bezier1',  'B', ControlNode)
    #print 'AB'
    
elif ControlNode.knob('InfluenceArea').value() == 'BC':
    SetFormulaForWarp ( 'Bezier2',  'B', ControlNode)
    SetFormulaForWarp ( 'Bezier2',  'C', ControlNode)
    #print 'BC'
