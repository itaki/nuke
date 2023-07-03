import nuke
def Dots():
    dotList,dotListX= [],[]
    Dsize = int(nuke.toNode("preferences")['dot_node_scale'].value()*12)
    nodes = nuke.selectedNodes()
    count = 0
    same = 1
    old = ""
    for selected in nodes:
        selectedX,selectedY = int(selected.xpos()),int(selected.ypos())
        selectedW,selectedH = int(selected.screenWidth()),int(selected.screenHeight())

        # checking inputs and assigning variables
        try:# check if input 0 is exist
            A = selected.input(0)
            AX = int(A.xpos())
            AY = int(A.ypos())
            AW = int(A.screenWidth())
            AH = int(A.screenHeight())
            AClass = A.Class()
            if count == 0:
                old = A
                count = count+1
            else:
                if old != A:
                    same = 0
        except:
            AX,AY = int(selected.xpos()),int(selected.ypos())
            AW,AH = int(selected.screenWidth()),int(selected.screenHeight())
            AClass = "no classs"
        try:# check if input 1 is exist
            B = selected.input(1)
            BX,BY = int(B.xpos()),int(B.ypos())
            BW,BH = int(B.screenWidth()),int(B.screenHeight())
            BClass = B.Class()
            print (" Input 1 found   " + B['name'].value())
        except:
            BX,BY = int(selected.xpos()),int(selected.ypos())
            BW,BH = int(selected.screenWidth()),int(selected.screenHeight())
            BClass = "no classs"
            print (" no input1 found        ")
        try:# check if input 2 is exist
            C = selected.input(2)
            CX,CY = int(C.xpos()),int(C.ypos())
            CW,CH = int(C.screenWidth()),int(C.screenHeight())
            CClass = C.Class()
            print (" Input 2 found   " + C['name'].value())
        except:
            print (" ")



        # setting position
        if B and not C:#two inputs found
            Dot = nuke.nodes.Dot()
           
            if BX == selectedX or BX-34 == selectedX:# above node case
                print ('above node case')
                t = nuke.selectedNode()
                depB = t.dependencies(nuke.INPUTS)[0]

                try:
                    depA = t.dependencies(nuke.INPUTS)[1]
                except:
                    depA = t.dependencies(nuke.INPUTS)[0]

                depA.setSelected(True)
                x2 = int(depA.xpos())
                y2 = int(depA.ypos())
                w,h = depA.screenWidth(),depA.screenHeight()


                dot = nuke.nodes.Dot()
                dot.setXYpos(int(selectedX-200),int(selectedY+selectedH/2-Dsize/2))
                dot2 = nuke.nodes.Dot()
                if BX-34 == selectedX:
                    dot2.setXYpos(int(selectedX-200),int(y2))
                else:
                    dot2.setXYpos(int(selectedX-200),int(y2+h/2-Dsize/2))
                dot2.setInput(0,depA)
                dot.setInput(0,dot2)
                t.setInput(1,dot)
                nuke.delete(Dot)
            else:#normal merge case
                Dot.setInput(0,B)
                selected.setInput(1,Dot)

                Dot.setXYpos(int(BX+BW/2-Dsize/2),int(selectedY+selectedH/2-Dsize/2))

            if A.Class()== "Dot":
                selected.knob("xpos").setValue(int(AX-selectedW/2+Dsize/2))
            else:        
                selected.knob("xpos").setValue(int(AX))


            print ('two inputs found')
       
        elif C:#three inputs found
             
            if "Scanline" in selected.Class():
                if BClass == "no classs":
                    pass
                else:
                    if B.Class()== "Dot":
                        selected.setXYpos(int(BX-selectedW/2+Dsize/2),int(selectedY))
                    else:
                        selected.setXYpos(int(BX),int(selectedY))

                dot = nuke.nodes.Dot(xpos=CX+CW/2-Dsize/2, ypos=selectedY+selectedH/2-Dsize/2)
                dot.setInput(0,C)
                selected.setInput(2,dot)

                if AClass == "no classs":
                    pass
                else:
                    dot = nuke.nodes.Dot(xpos=AX+AW/2-Dsize/2, ypos=selectedY+selectedH/2-Dsize/2)
                    dot.setInput(0,A)
                    selected.setInput(0,dot)
                print ("Scanline")
            if "Merge" in selected.Class() or "Roto" in selected.Class()or "Keymix" in selected.Class():

                if A.Class()== "Dot":
                    selected.knob("xpos").setValue(int(AX-selectedW/2+Dsize/2))
                else:        
                    selected.knob("xpos").setValue(int(AX))

                dot = nuke.nodes.Dot(xpos=CX+CW/2-Dsize/2, ypos=selectedY+selectedH/2-Dsize/2)
                dot.setInput(0,C)
                selected.setInput(2,dot)

                dot = nuke.nodes.Dot(xpos=BX+BW/2-Dsize/2, ypos=selectedY+selectedH/2-Dsize/2)
                dot.setInput(0,B)
                selected.setInput(1,dot)


                print ('three input found')

        else:#one input found
            print ('one input found')
            Dot = nuke.nodes.Dot()
            Dot.setInput(0,A)
            selected.setInput(0,Dot)        
            Dot.setXYpos(int(selectedX+selectedW/2-Dsize/2),int(AY+AH/2-Dsize/2) )
            dotList.append(Dot)
            dotListX.append(Dot.xpos())