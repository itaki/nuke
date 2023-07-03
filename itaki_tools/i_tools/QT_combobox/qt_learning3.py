from PySide2 import QtWidgets
import nuke
 
# Create a simple class
class SimpleClass(object):
    def makeUI(self):
        return QtWidgets.QPushButton('Test')
 
# Create a NoOp node on which we'll add the knob
node = nuke.createNode("NoOp")
knob = nuke.PyCustom_Knob("test", "Test", "SimpleClass()")
node.addKnob(knob)