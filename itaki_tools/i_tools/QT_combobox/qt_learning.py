import nuke
from PySide2 import QtWidgets
 
# Notice that we can actually condense the 2 classes into a single one if we return self in makeUI
class MyBox(QtWidgets.QSpinBox):
    def __init__(self):
        super(MyBox, self).__init__()
        self.setSuffix(" Frame of Roto")
     
    def updateValue(self):
        return
     
    def makeUI(self):
        return self
 
# Create a NoOp node on which we'll add the knob
node = nuke.createNode("NoOp")
knob = nuke.PyCustom_Knob("todo", "To Do:", "MyBox()")
node.addKnob(knob)