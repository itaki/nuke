
import math
import nuke

ControlNode = nuke.thisNode()

SplineWarpList = []

for node in nuke.allNodes(recurseGroups=True):
    if node.Class() == 'SplineWarp3':
        srcNode = node
        SplineWarpList.append(node.name())
        print node.name()
        

CameraList = []
        
for node in nuke.allNodes(recurseGroups=True):
    if node.Class() == 'Camera2':
        srcNode = node
        CameraList.append(node.name())
        print node.name()

SplineWarpList.sort()
Nodeknob = ControlNode.knob('SplineWarp_A')
Nodeknob.setValues(SplineWarpList)

Nodeknob = ControlNode.knob('SplineWarp_B')
Nodeknob.setValues(SplineWarpList)

CameraList.sort()
Nodeknob = ControlNode.knob('CamA_name')
Nodeknob.setValues(CameraList)

Nodeknob = ControlNode.knob('CamB_name')
Nodeknob.setValues(CameraList)
