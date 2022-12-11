#!/usr/bin/env python

"""Locometry.py - Snap geo to vertices"""

__author__      = "Kim Ranzani"
__copyright__   = "Copyright 2022, Kim Ranzani"



import nuke, nukescripts
import math


nuke.menu( 'Nuke' ).addCommand( 'Locometry/Snap/Selected Node', lambda: loco_snap(1))
nuke.menu( 'Nuke' ).addCommand( 'Locometry/Snap/Axis', lambda: loco_snap(2))
nuke.menu( 'Nuke' ).addCommand( 'Locometry/Snap/Card', lambda: loco_snap(3))
nuke.menu( 'Nuke' ).addCommand( 'Locometry/Snap/Sphere', lambda: loco_snap(4))
nuke.menu( 'Nuke' ).addCommand( 'Locometry/Snap/Cube', lambda: loco_snap(5))
nuke.menu( 'Nuke' ).addCommand( 'Locometry/Snap/Cylinder', lambda: loco_snap(6))


def loco_snap(option):
	
	if len(list(nukescripts.snap3d.selectedPoints()))==3:

		if option == 1:
			nodeToLoco = nuke.selectedNode()
		if option == 2:
			nodeToLoco = nuke.createNode('Axis')
		if option == 3:
			nodeToLoco = nuke.createNode('Card')
		if option == 4:
			nodeToLoco = nuke.createNode('Sphere')
		if option == 5:
			nodeToLoco = nuke.createNode('Cube')
		if option == 6:
			nodeToLoco = nuke.createNode('Cylinder')
	
		nodeToLoco.setXYpos(-100,-100)
		locoNode = nuke.createNode('CurveTool')   
		locoNode['beforeFrameRender'].setValue('Locometry.calculate()')
		locoNode['afterRender'].setValue('nuke.delete(nuke.thisNode())')
		k=locoNode.knob("go")
		nodeToLoco.setSelected(True)
		k.execute()
	else:
		nuke.message('LOCOMETRY: Select exactly 3 vertices.')
	
	

def getPoints():
 
	P=[]
	for v in nukescripts.snap3d.selectedPoints():
		P.append(v)
	P =[P[0],P[1],P[2]] 
	print(P)  
	return P



def calculate():
   

    P = getPoints()
    A = P[1] - P[0]
    B = P[2] - P[0]

    A.normalize()

    N = A.cross(B) #create the normal of A and B

    N.normalize()

    C = N.cross(A) #create the orthogonal axis

    centroid = (P[0]+P[1]+P[2])/3

    #generate the Rotation Matrix Colums
    r11 = A[0]
    r21 = A[1]
    r31 = A[2]
    r12 = C[0]
    r22 = C[1]
    r32 = C[2]
    r13 = N[0]
    r23 = N[1]
    r33 = N[2]

    #generate Euler Angles
    rx=math.atan2(r32,r33)
    ry=math.atan2(-r31,math.sqrt( r32**2 + r33**2))
    rz=math.atan2(r21,r11)

    nuke.selectedNode()['translate'].setAnimated()
    nuke.selectedNode()['rotate'].setAnimated()
    nuke.selectedNode()['rot_order'].setValue(0)
    nuke.selectedNode()['translate'].setValue([centroid[0],centroid[1],centroid[2]])
    nuke.selectedNode()['rotate'].setValue([math.degrees(rx),math.degrees(ry),math.degrees(rz)])


