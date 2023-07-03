
try:
    from PySide import QtGui
    from PySide import QtCore
    from PySide.QtGui import *
    from PySide.QtCore import *
except ImportError:
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from PySide2 import QtCore
    from PySide2 import QtWidgets as QtGui
    from PySide2 import QtWidgets

try:
    import PySide as pyside
except:
    import PySide2 as pyside

from operator import itemgetter
from nukescripts import panels
import nukescripts
import nuke
import os
import copy
import collections
import inspect
import traceback
import json

class LayerShuffler(QtGui.QMainWindow):

    def __init__(self, parent = None):

        """
        Create the main window, setup the UI and update UI elements
        to fill in discovered information. Also, create starting attributes
        for various functionalities and restore preferences.
        """

        QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.layerShufflerDir, self.presetsDir = self.findBaseDirectories()

        # Initialize preferences.
        self.settings = QSettings(os.path.join(self.layerShufflerDir, "preferences.ini"), QSettings.IniFormat)
        self.settings.setFallbacksEnabled(False)
        
        self.updateInformation(onCreation = True)
        self.passSignalConnections()

        # Initialize base attributes.
        self.shuffleIndexDict = {}
        self.shuffleIndexDict_missingEntries = {}
        self.storedNodes = {}
        self.nodeTreePreset_buffer = {}
        self.nodeTreePreset_buffer_missingEntires = {}
        self.distanceMult = 1

        self.infoPanel = None

        # This attribute will be used to establish a base line for
        # a start to the Renderer Rebuild functionality. It will bes
        # dictated by the amount of custom nodes that the user adds
        # to any one layer.
        self.rebuildStart_highestY = 0

        self.restorePreferences(self)

        # Installs an event filter to trigger a function to save preferences
        # when the user drags and drops items in these two lists.
        self.listWidget_mainPasses.installEventFilter(self)
        self.listWidget_aov.installEventFilter(self)


    def eventFilter(self, sender, event):

        """
        This event filter will save the main list widgets' user order preferences
        when they drag and drop items.
        """
        
        if event.type() == QEvent.ChildRemoved:
            self.savePreferences(self, sender.objectName())

        return False

    def savePreferences(self, ui, widgetName):

        """
        Saves the current settings on the widget from the passed widgetName.
        """

        for name, obj in inspect.getmembers(ui):
            if name == widgetName:
                if isinstance(obj, QComboBox):
                    index = obj.currentIndex()
                    text = obj.itemText(index)
                    self.settings.setValue(name, text)

                if isinstance(obj, QLineEdit):
                    value = obj.text()
                    self.settings.setValue(name, value)

                if isinstance(obj, QCheckBox):
                    state = obj.isChecked()
                    self.settings.setValue(name, state)

                if isinstance(obj, QSlider) or isinstance(obj, QSpinBox):
                    value = obj.value()
                    self.settings.setValue(name, value)

                if name == "btn_selectColor":
                    value = obj.styleSheet()
                    self.settings.setValue(name, value)

                if isinstance(obj, QListWidget):
                    newValue = [str(obj.item(i).text()) for i in range(obj.count())]

                    oldValue = self.settings.value(name)

                    if oldValue:
                        for i in newValue:
                            if i in oldValue:
                                oldValue.remove(i)

                        newValue.extend(oldValue)

                    self.settings.setValue(name, newValue)

    def restorePreferences(self, ui, widgetObj = None, widgetName = None):

        """
        Restore the values that were last saved in the preferences file.
        """

        # Preferences only need to be restored for the following objects:
        objNames = set(["lineEdit_mainPassesTitle_input", "lineEdit_aovsTitle_input",
                        "check_removeExrRestriction", "check_selectionOnly", 
                        "check_unlockShuffleOrdering", "btn_selectColor",
                        "comboBox_rebuildDirection","comboBox_rendererSelectionDropdown",
                        "numField_nodeDistanceMult", "slider_nodeDistanceMult",
                        "listWidget_mainPasses", "listWidget_aov"])
        objects = []

        # If widgetName and widgetObj have been passed, the script will only
        # iterate over those, otherwise it will iterate through the whole UI.
        if widgetName and widgetObj and widgetName in objNames:
            objects = [(widgetName, widgetObj)]
        else:
            objects = inspect.getmembers(ui)

        for name, obj in objects:
            if name in objNames:
                if isinstance(obj, QComboBox):
                    index = obj.currentIndex()

                    value = (self.settings.value(name))

                    if value == "" or not value:
                        continue

                    index = obj.findText(value) 

                    obj.setCurrentIndex(index)

                if isinstance(obj, QLineEdit):
                    value = (self.settings.value(name))
                    if value:
                        obj.setText(value)

                if isinstance(obj, QCheckBox):
                    value = self.settings.value(name)
                    if value == "true" or value == "True" or value == "TRUE" or value == True:
                        value = True
                        obj.setChecked(value)
                    if value == "false" or value == "False" or value == "FALSE" or value == False:
                        value = False
                        obj.setChecked(value)

                if isinstance(obj, QSlider) or isinstance(obj, QSpinBox):
                    value = self.settings.value(name)
                    if value:
                        obj.setValue(int(value))

                if name == "btn_selectColor":
                    value = self.settings.value(name)
                    obj.setStyleSheet(value)

                if isinstance(obj, QListWidget):
                    value = self.settings.value(name)

                    if value:
                        currentItems = [str(obj.item(i).text()) for i in range(obj.count())]
                        layersInCurNode = []
                        newValue = []

                        curNode = nuke.toNode(self.label_selNode.text())

                        if curNode:
                            layersInCurNode = self.gatherLayers(curNode)

                        for v in value:
                            if v in layersInCurNode:
                                newValue.append(v)

                        if newValue:
                            for val in newValue:
                                if val in currentItems:
                                    obj.takeItem(obj.row(obj.findItems(val, Qt.MatchExactly)[0]))

                            leftovers = [str(obj.item(i).text()) for i in range(obj.count())]
                            obj.clear()
                            obj.addItems(newValue)
                            if leftovers:
                                obj.addItems(leftovers)


    def removeDuplicates(self, seq):

        """
        Remove duplicates from a provided sequence.
        """

        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))]

    def missingEntriesHandler(self, dictToCheck, missingEntriesStorage):

        """
        Checks all the entries in the "dictToCheck" and moves any
        missing ones to "missingEntriesStorage". Also, runs a check
        through the latter to recover any entries that may have been returned.
        """

        # Attempt to bring back deleted items if they have been detected.
        if missingEntriesStorage:
            for n in missingEntriesStorage:
                try:
                    nuke.exists(n.name())
                    dictToCheck[n] = missingEntriesStorage[n]
                    del missingEntriesStorage[n]
                except ValueError:
                    continue

        # Check if the shuffled nodes from dictToCheck exist. Move them to the
        # secondary dict if they can't be found.
        for node in dictToCheck:
            try:
                nuke.exists(node.name())
            except ValueError:
                missingEntriesStorage[node] = dictToCheck[node]
                continue

        # Remove the missing entries from dictToCheck.
        if missingEntriesStorage:
            for k in missingEntriesStorage:
                if k in dictToCheck:
                    del dictToCheck[k]

    def findBaseDirectories(self):

        """
        Finds the base directories for layerShuffler and nodeTreePresets,
        the latter of which will be created if it doesn't exist.
        """

        # Find the layerShuffler directory.
        layerShufflerDir = os.path.dirname(__file__)

        # For testing the tool directly in Script Editor.
        if __name__ == "__main__":
            layerShufflerDir += "/layerShuffler"
        
        presetsDir = layerShufflerDir + "/nodeTreePresets"

        # Create "nodeTreePresets" folder if it doesn't exist.
        if not os.path.isdir(presetsDir):
            os.mkdir(presetsDir)

        return layerShufflerDir, presetsDir

    def gatherLayers(self, targetNode, useOrder = False, reorderForRebuild = False):

        """
        Gather the layers from the targetNode.
        """

        # Create a list with the channels output by the selected node
        # and a list with the layers Nuke recognizes.
        channels = targetNode.channels()
        nukeLayers = nuke.layers()
        nukeLayers.remove("rgb")
        nukeLayers.remove("rgba")
        nukeLayers.remove("alpha")

        # Reformat the "channels" list to contain only the layer names
        # without channel extensions.
        layerNames = []
        for i in channels:
            t = i.split(".")
            t.pop(1)
            layerNames.extend(t)
        
        # Create a list of your render passes.
        # This step is needed because Nuke will gather every layer it can find in the Node graph,
        # even if they are not within the connected flow of nodes.
        # This ensures 'passes' contains only the user's passes.
        passes = []
        for layer in nukeLayers:
            if layer in layerNames:
                passes.append(layer)

        if not useOrder:
            return passes

        # This section deals with ordering the "passes" list based on user's ordering.
        elif useOrder:
            mainPasses = passes[:]
            mainPasses_remnantPasses = passes[:]

            aovs = passes[:]
            aovs_remnantPasses = passes[:]

            mainPasses_userOrder = [str(self.listWidget_mainPasses.item(i).text()) for i in range(self.listWidget_mainPasses.count())]
            aovs_userOrder = [str(self.listWidget_aov.item(i).text()) for i in range(self.listWidget_aov.count())]

            for item in mainPasses_userOrder:
                if item in mainPasses:
                    mainPasses.append(mainPasses.pop(mainPasses.index(item)))
                    mainPasses_remnantPasses.remove(item)

            for rem in mainPasses_remnantPasses:
                mainPasses.remove(rem)


            for item in aovs_userOrder:
                if item in aovs:
                    aovs.append(aovs.pop(aovs.index(item)))
                    aovs_remnantPasses.remove(item)

            for rem in aovs_remnantPasses:
                aovs.remove(rem)

            mainPasses.extend(aovs_remnantPasses)
            aovs.extend(aovs_remnantPasses)

            if not reorderForRebuild:
                return passes, mainPasses, aovs

            # This section orders the main passes based on the selected renderer preset.
            elif reorderForRebuild:
                rebuildGuide = {}
                if self.comboBox_rendererSelectionDropdown.currentText() == "Arnold":
                    if self.radioBtn_primaryArnold.isChecked():
                        comboBoxesList = [self.comboBox_directDiffuse, self.comboBox_indirectDiffuse, self.comboBox_directSpec,
                                            self.comboBox_indirectSpec, self.comboBox_directCoat, self.comboBox_indirectCoat,
                                            self.comboBox_directTransmission, self.comboBox_indirectTransmission,
                                            self.comboBox_directSss, self.comboBox_indirectSss, self.comboBox_directVolume,
                                            self.comboBox_indirectVolume, self.comboBox_emission]
                    elif self.radioBtn_secondaryArnold.isChecked():
                        comboBoxesList = [self.comboBox_direct, self.comboBox_indirect, self.comboBox_emissionSecondary]

                    # Create the Rebuild Guide based on how many boxes have passes assigned to them
                    for ind, b in enumerate(comboBoxesList):
                        if not str(b.currentText()) == "None":
                            rebuildGuide[str(b.currentText())] = ind

                elif self.comboBox_rendererSelectionDropdown.currentText() == "VRay":
                    if self.radioBtn_advancedVray.isChecked():
                        comboBoxesList = [self.comboBox_diffuseFilter, self.comboBox_rawLighting, self.comboBox_rawGi,
                                            self.comboBox_rawReflection, self.comboBox_reflectionFilter,
                                            self.comboBox_rawRefraction, self.comboBox_refractionFilter,
                                            self.comboBox_specularAdvanced, self.comboBox_sss2advanced, self.comboBox_selfIlluminationAdvanced,
                                            self.comboBox_causticsAdvanced, self.comboBox_atmosphereAdvanced]
                    elif self.radioBtn_basicVray.isChecked():
                        comboBoxesList = [self.comboBox_lighting, self.comboBox_gi, self.comboBox_reflection,
                                            self.comboBox_refraction, self.comboBox_specularBasic, self.comboBox_sss2basic,
                                            self.comboBox_selfIlluminationBasic, self.comboBox_causticsBasic, self.comboBox_atmosphereBasic]

                    # Create the Rebuild Guide based on how many boxes have passes assigned to them.
                    for ind, b in enumerate(comboBoxesList):
                        if not str(b.currentText()) == "None":
                            rebuildGuide[str(b.currentText())] = ind

                else:
                    return passes, mainPasses, aovs

                # Create extra helper elements to aid reordering the passes.
                mp_loopList = mainPasses[:]

                mainPasses_remnantPasses = mainPasses[:]

                mainPasses = []

                try:
                    if rebuildGuide:
                        for elem in mp_loopList:
                            if elem in rebuildGuide:
                                mainPasses.append(elem)
                                mainPasses_remnantPasses.remove(elem)
                except NameError:
                    pass

                # Sort the passes based on the rebuildGuide before appending the rest.
                mainPasses = sorted(mainPasses, key = lambda cur: rebuildGuide[cur])

                mainPasses.extend(mainPasses_remnantPasses)

                return passes, mainPasses, aovs

    def gatherData_manyNodes(self, nodes):

        """
        Gathers data about a node that has been passed to the function.
        """

        # Find the top-left position to use as an origin to
        # a local coordinate system of the selected nodes.
        minX = None
        minY = None
        for n in nodes:
            if minX == None or n.xpos() < minX:
                minX = n.xpos()

            if minY == None or n.ypos() < minY:
                minY = n.ypos()

        localBaseDot = nuke.Node("Dot", inpanel = False)

        localBaseDot.setXYpos(minX, minY)

        # Grab the coordinates of the spot.
        startX = localBaseDot.xpos()
        startY = localBaseDot.ypos()

        # Delete the Dot.
        nukescripts.node_delete()

        # Store node info in a dict.
        tempStorage = {}
        
        for node in nodes:
            knobsDict = {}
            knobsToStore = [k for k in node.allKnobs()]
            knobsToStore = [knob for knob in knobsToStore if not any(knob.name() == n
                            for n in ["name", "selected", "xpos", "ypos"])]

            # Store information about the knobs.
            for knob in knobsToStore:
                if knob.name() == "":
                    continue
                knobsDict[knob.name()] = knob.value()

            connectionsDict = {}

            # Store connections information.
            for i in range(node.inputs()):
                try:
                    connectionsDict[i] = node.input(i).name()
                except:
                    continue

            nodesInGrp_storageDict = {}

            if node.Class() == "Group":
                with nuke.toNode(node.name()):
                    nodesInGrp = nuke.allNodes()

                    nodesInGrp_storageDict = self.gatherData_manyNodes(nodesInGrp)

            # Save all the necessary information about the node.
            tempStorage[node.name()] = {"nodeType": node.Class(),
                                        "xOffset": node.xpos() - startX,
                                        "yOffset": node.ypos() - startY,
                                        "knobsInfo": knobsDict,
                                        "connections": connectionsDict,
                                        "nodesInside": nodesInGrp_storageDict}

        return tempStorage

    def restoreNodeStructure(self, nodesDict):

        """
        Restores the saved structure of nodes from nodesDict.
        """

        connectionsRestore = {}

        # Create a starting dot, which will be created where the user has
        # last clicked in the Node Graph, and then save the coordinates
        # of the dot and delete it. Those coords will be the relative
        # base for rebuilding the preset.
        localBaseDot = nuke.Node("Dot", inpanel = False)

        # Get starting coords.
        startX = localBaseDot.xpos()
        startY = localBaseDot.ypos()

        # Delete the dot.
        nukescripts.node_delete()

        for entry in nodesDict:
            # Unpack the current entry's information.
            nodeType = nodesDict[entry]["nodeType"]
            x = nodesDict[entry]["xOffset"]
            y = nodesDict[entry]["yOffset"]
            knobs_values = nodesDict[entry]["knobsInfo"]
            connectionsDict = nodesDict[entry]["connections"]
            nodesInGrp = nodesDict[entry]["nodesInside"]

            newNode = nuke.Node(nodeType, inpanel = False)

            # Restore the entry's knobs.
            for knob in knobs_values:
                if knob in [i.name() for i in newNode.allKnobs()]:
                    try:
                        newNode[knob].setValue(knobs_values[knob])
                    except:
                        continue

            newNode.setXYpos(startX + x, startY + y)

            # Save the newly created nodes into a dict
            # to rebuild connections.
            connectionsRestore[newNode] = {"connections": connectionsDict, "originalName": entry}

            newNode.setSelected(False)

            # If entry is a Group node, restore nodes inside.
            if nodeType == "Group":
                with nuke.toNode(newNode.name()):
                    self.restoreNodeStructure(nodesInGrp)
            
        # Restore the connections.
        for n in connectionsRestore:

            for ind in connectionsRestore[n]["connections"]:
                nodeToConnect = connectionsRestore[n]["connections"][ind]

                for entry in connectionsRestore:
                    if connectionsRestore[entry]["originalName"] == nodeToConnect:
                        n.setInput(int(ind), entry)

        bufferSet = set(connectionsRestore)

        return bufferSet






    # -----------------------------------------------------------------------------------------------------------------------
    # The following section contains functions that update UI elements and their info.
    # -----------------------------------------------------------------------------------------------------------------------

    def updateInformation(self, onCreation = False):

        """
        The purpose of this function is to update relevant information in the UI to match
        the current state of the Node Graph. Includes information about the current node,
        the origin file name of the node stream and the layers that nuke sees in the stream.
        """

        try:
            n = nuke.selectedNode()
            print (n)
        except ValueError:
            if onCreation:
                nuke.message("No node selected. Please select a node and hit \"Update\".")
            else:
                nuke.message("Please select a node.")
            return

        fileName = n.metadata("input/filename")

        self.label_selNode.setText(n.knob("name").value())
        if fileName:
            self.label_fileName.setText(os.path.basename(fileName))
        else:
            self.label_fileName.setText("File name not found")

        if not onCreation:
            # Store user's selection.
            mainPassesSelection = [str(t.text()) for t in self.listWidget_mainPasses.selectedItems()]
            aovsSelection = [str(t.text()) for t in self.listWidget_aov.selectedItems()]

        # Delete any existing items in the list widgets.
        self.listWidget_mainPasses.clear()
        self.listWidget_aov.clear()

        layerNames = self.gatherLayers(n)

        self.listWidget_mainPasses.addItems(layerNames)
        self.listWidget_aov.addItems(layerNames)

        self.restorePreferences(self, self.listWidget_mainPasses, self.listWidget_mainPasses.objectName())
        self.restorePreferences(self, self.listWidget_aov, self.listWidget_aov.objectName())

        self.updateRebuildOptionsDropdowns()

        if not onCreation:
            # Restore user's selection.
            if mainPassesSelection:
                listWidget = self.listWidget_mainPasses
                curMainPasses = [str(listWidget.item(i).text()) for i in range(listWidget.count())]

                for item in mainPassesSelection:
                    if item in curMainPasses:
                        listWidget_item = listWidget.findItems(item, Qt.MatchExactly)[0]

                        listWidget.setCurrentItem(listWidget.item(listWidget.row(listWidget_item)), QItemSelectionModel.Select)

            if aovsSelection:
                listWidget = self.listWidget_aov
                curAovs = [str(listWidget.item(i).text()) for i in range(listWidget.count())]

                for item in aovsSelection:
                    if item in curAovs:
                        listWidget_item = listWidget.findItems(item, Qt.MatchExactly)[0]

                        listWidget.setCurrentItem(listWidget.item(listWidget.row(listWidget_item)), QItemSelectionModel.Select)

    def updateRebuildOptionsDropdowns(self):

        """
        Stand-alone function to handle the updating of every dropdown combo box
        in the Rebuild options tab. It will attempt to find each corresponding
        pass in the layers of the file stream if its name is the same as default.
        """


        layers = self.gatherLayers(nuke.toNode(str(self.label_selNode.text())))

        if not layers:
            return

        # Find all dropdown boxes to insert all the layers into them.
        comboBoxes = [getattr(self, s) for s in dir(self) if "comboBox_" in s]
        comboBoxes.remove(self.comboBox_rendererSelectionDropdown)
        comboBoxes.remove(self.comboBox_rendererSelectionDropdown_alt)
        comboBoxes.remove(self.comboBox_rebuildDirection)
        comboBoxes.remove(self.comboBox_rebuildDirection_alt)

        # Populate comboBoxes with the gathered layers.
        for box in comboBoxes:
            box.clear()
            box.addItem("None")
            box.insertSeparator(1)
            box.addItems(layers)

        # Set every dropdown box to its corresponding layer.
        for lay in layers:
            # Detect default Arnold layers.
            if lay == "diffuse_direct":
                self.comboBox_directDiffuse.setCurrentIndex(self.comboBox_directDiffuse.findText(lay))
            elif lay == "diffuse_indirect":
                self.comboBox_indirectDiffuse.setCurrentIndex(self.comboBox_indirectDiffuse.findText(lay))
            elif lay == "diffuse" and "diffuse_direct" not in layers and "diffuse_indirect" not in layers:
                self.comboBox_directDiffuse.setCurrentIndex(self.comboBox_directDiffuse.findText(lay))

            elif lay == "specular_direct":
                self.comboBox_directSpec.setCurrentIndex(self.comboBox_directSpec.findText(lay))
            elif lay == "specular_indirect":
                self.comboBox_indirectSpec.setCurrentIndex(self.comboBox_indirectSpec.findText(lay))
            elif lay == "specular" and "specular_direct" not in layers and "specular_indirect" not in layers:
                self.comboBox_directSpec.setCurrentIndex(self.comboBox_directSpec.findText(lay))

            elif lay == "coat_direct":
                self.comboBox_directCoat.setCurrentIndex(self.comboBox_directCoat.findText(lay))
            elif lay == "coat_indirect":
                self.comboBox_indirectCoat.setCurrentIndex(self.comboBox_indirectCoat.findText(lay))
            elif lay == "coat" and "coat_direct" not in layers and "coat_indirect" not in layers:
                self.comboBox_directCoat.setCurrentIndex(self.comboBox_directCoat.findText(lay))

            elif lay == "transmission_direct":
                self.comboBox_directTransmission.setCurrentIndex(self.comboBox_directTransmission.findText(lay))
            elif lay == "transmission_indirect":
                self.comboBox_indirectTransmission.setCurrentIndex(self.comboBox_indirectTransmission.findText(lay))
            elif lay == "transmission" and "transmission_direct" not in layers and "transmission_indirect" not in layers:
                self.comboBox_directTransmission.setCurrentIndex(self.comboBox_directTransmission.findText(lay))

            elif lay == "sss_direct":
                self.comboBox_directSss.setCurrentIndex(self.comboBox_directSss.findText(lay))
            elif lay == "sss_indirect":
                self.comboBox_indirectSss.setCurrentIndex(self.comboBox_indirectSss.findText(lay))
            elif lay == "sss" and "sss_direct" not in layers and "sss_indirect" not in layers:
                self.comboBox_directSss.setCurrentIndex(self.comboBox_directSss.findText(lay))

            elif lay == "volume_direct":
                self.comboBox_directVolume.setCurrentIndex(self.comboBox_directVolume.findText(lay))
            elif lay == "volume_indirect":
                self.comboBox_indirectVolume.setCurrentIndex(self.comboBox_indirectVolume.findText(lay))
            elif lay == "volume" and "volume_direct" not in layers and "volume_indirect" not in layers:
                self.comboBox_directVolume.setCurrentIndex(self.comboBox_directVolume.findText(lay))

            elif lay == "emission":
                self.comboBox_emission.setCurrentIndex(self.comboBox_emission.findText(lay))
                self.comboBox_emissionSecondary.setCurrentIndex(self.comboBox_emissionSecondary.findText(lay))

            elif lay == "direct":
                self.comboBox_direct.setCurrentIndex(self.comboBox_direct.findText(lay))
            elif lay == "indirect":
                self.comboBox_indirect.setCurrentIndex(self.comboBox_indirect.findText(lay))

            # Detect VRay default layers.
            elif lay == "VRayDiffuseFilter":
                self.comboBox_diffuseFilter.setCurrentIndex(self.comboBox_diffuseFilter.findText(lay))
            elif lay == "VRayRawLighting":
                self.comboBox_rawLighting.setCurrentIndex(self.comboBox_rawLighting.findText(lay))
            elif lay == "VRayRawGlobalIllumination":
                self.comboBox_rawGi.setCurrentIndex(self.comboBox_rawGi.findText(lay))
            elif lay == "VRayRawReflection":
                self.comboBox_rawReflection.setCurrentIndex(self.comboBox_rawReflection.findText(lay))
            elif lay == "VRayReflectionFilter":
                self.comboBox_reflectionFilter.setCurrentIndex(self.comboBox_reflectionFilter.findText(lay))
            elif lay == "VRayRawRefraction":
                self.comboBox_rawRefraction.setCurrentIndex(self.comboBox_rawRefraction.findText(lay))
            elif lay == "VRayRefractionFilter":
                self.comboBox_refractionFilter.setCurrentIndex(self.comboBox_refractionFilter.findText(lay))

            elif lay == "VRayLighting":
                self.comboBox_lighting.setCurrentIndex(self.comboBox_lighting.findText(lay))
            elif lay == "VRayGlobalIllumination":
                self.comboBox_gi.setCurrentIndex(self.comboBox_gi.findText(lay))
            elif lay == "VRayReflection":
                self.comboBox_reflection.setCurrentIndex(self.comboBox_reflection.findText(lay))
            elif lay == "VRayRefraction":
                self.comboBox_refraction.setCurrentIndex(self.comboBox_refraction.findText(lay))

            elif lay == "VRaySpecular":
                self.comboBox_specularAdvanced.setCurrentIndex(self.comboBox_specularAdvanced.findText(lay))
                self.comboBox_specularBasic.setCurrentIndex(self.comboBox_specularBasic.findText(lay))
            elif lay == "VRaySSS2":
                self.comboBox_sss2advanced.setCurrentIndex(self.comboBox_sss2advanced.findText(lay))
                self.comboBox_sss2basic.setCurrentIndex(self.comboBox_sss2basic.findText(lay))
            elif lay == "VRaySelfIllumination":
                self.comboBox_selfIlluminationAdvanced.setCurrentIndex(self.comboBox_selfIlluminationAdvanced.findText(lay))
                self.comboBox_selfIlluminationBasic.setCurrentIndex(self.comboBox_selfIlluminationBasic.findText(lay))
            elif lay == "VRayCaustics":
                self.comboBox_causticsAdvanced.setCurrentIndex(self.comboBox_causticsAdvanced.findText(lay))
                self.comboBox_causticsBasic.setCurrentIndex(self.comboBox_causticsBasic.findText(lay))
            elif lay == "VRayAtmosphere":
                self.comboBox_atmosphereAdvanced.setCurrentIndex(self.comboBox_atmosphereAdvanced.findText(lay))
                self.comboBox_atmosphereBasic.setCurrentIndex(self.comboBox_atmosphereBasic.findText(lay))

    def update_tabInfo(self):

        """
        This function is called when the current tab selection changes.
        If the "Add Nodes" tab is selected, update the passes lists
        with the selected layers to be shuffled.
        If the "Saved Node Trees" tab is selected, updates the presets list
        with any discovered json files in the special directory inside
        the Layer Shuffler's directory.
        """

        if str(self.tabWidget.tabText(self.tabWidget.currentIndex())) == "Add Nodes":
            self.label_mainPassesSelection.setText("\"" + str(self.lineEdit_mainPassesTitle_input.text()) + "\" selection")
            self.label_aovsSelection.setText("\"" + str(self.lineEdit_aovsTitle_input.text()) + "\" selection")

            # Block the signals to avoid overwriting any existing stored selections.
            self.listWidget_mainPassesSelection.blockSignals(True)
            self.listWidget_aovsSelection.blockSignals(True)

            self.listWidget_mainPassesSelection.clear()
            for item in self.listWidget_mainPasses.selectedItems():
                self.listWidget_mainPassesSelection.addItem(item.text())

            self.listWidget_aovsSelection.clear()
            for item in self.listWidget_aov.selectedItems():
                self.listWidget_aovsSelection.addItem(item.text())

            # Unblock signals again.
            self.listWidget_mainPassesSelection.blockSignals(False)
            self.listWidget_aovsSelection.blockSignals(False)

            self.restoreLayerSelections()
        elif str(self.tabWidget.tabText(self.tabWidget.currentIndex())) == "Saved Node Trees":
            discoveredPresetFiles = []
            for file in os.listdir(self.presetsDir):
                if file.endswith(".json"):
                    discoveredPresetFiles.append(file.split(".json")[0])

            self.listWidget_savedPresets.clear()
            self.listWidget_savedPresets.addItems(discoveredPresetFiles)
        else:
            return





    # -----------------------------------------------------------------------------------------------------------------------
    # The following section contains handlers that are connected to Qt signals in the UI.
    # -----------------------------------------------------------------------------------------------------------------------

    def resetCurrentOrderToDefault(self, listWidget):

        """
        Reset the listWidget to the default that the Shuffler would normally use.
        """

        # Save original selection.
        originalSelection = [str(i.text()) for i in listWidget.selectedItems()]

        passes = self.gatherLayers(nuke.toNode(str(self.label_selNode.text())))

        # Delete any existing items in the list widgets.
        listWidget.clear()

        for p in passes:
            listWidget.addItem(p)

        # Restore original selection.
        for item in originalSelection:
            listWidget_item = listWidget.findItems(item, Qt.MatchExactly)[0]

            listWidget.setCurrentItem(listWidget.item(listWidget.row(listWidget_item)), QItemSelectionModel.Select)

    def selectAllBtn(self, listWidget, emitSignal = True):

        """
        Arbitrary function to apply to "Select All" buttons.
        """

        listWidget.blockSignals(True)

        for i in range(listWidget.count()):
            listWidget.setCurrentItem(listWidget.item(i), QItemSelectionModel.Select)

        listWidget.scrollToItem(listWidget.item(0))

        listWidget.blockSignals(False)

        if emitSignal:
            # Signals were blocked earlier to avoid inefficiently
            # calling a callback function that is tied to some list
            # widgets for no reason, however, one signal still needs
            # to be emitted for that function.
            listWidget.itemSelectionChanged.emit()

    def clearSelectionBtn(self, listWidget, emitSignal = True):

        """
        Arbitrary function to apply to "Clear Selection" buttons.
        """

        listWidget.blockSignals(True)

        for item in listWidget.selectedItems():
            listWidget.setCurrentItem(item, QItemSelectionModel.Clear)

        listWidget.scrollToItem(listWidget.item(0))

        listWidget.blockSignals(False)

        if emitSignal:
            # Signals were blocked earlier to avoid inefficiently
            # calling a callback function that is tied to some list
            # widgets for no reason, however, one signal still needs
            # to be emitted for that function.
            listWidget.itemSelectionChanged.emit()

    def selectRemainingBtn(self, cur_listWidget, subtraction_listWidget):

        """
        Arbitrary function to apply to "Select remaining" button.
        """

        self.clearSelectionBtn(cur_listWidget)

        subtractionItemNames = []

        for item in subtraction_listWidget.selectedItems():
            subtractionItemNames.append(str(item.text()))

        remainingItemsList = []

        for i in range(cur_listWidget.count()):
            remainingItemsList.append(str(cur_listWidget.item(i).text()))

        for string in subtractionItemNames:
            if string in remainingItemsList:
                remainingItemsList.remove(string)

        fullItemsList = []

        for i in range(cur_listWidget.count()):
            fullItemsList.append(cur_listWidget.item(i))

        for item in fullItemsList:
            if str(item.text()) in remainingItemsList:
                cur_listWidget.setCurrentItem(item, QItemSelectionModel.Select)

        cur_listWidget.scrollToItem(cur_listWidget.item(0))

    def setBackdropColor(self):

        """
        This function will call a Nuke color wheel to allow the user to select a color for their backdrops.
        The function will also handle conversions between PySide and Nuke's way of storing colors.
        """
        
        nkCol = nuke.getColor(int('%02x%02x%02x%02x' % self.btn_selectColor.palette().button().color().getRgb(), 16))
        r = 0xFF & nkCol >> 24
        g = 0xFF & nkCol >> 16
        b = 0xFF & nkCol >> 8

        self.btn_selectColor.setStyleSheet("background-color:rgb(" + str(r) + "," + str(g) + "," + str(b) + ");")

    def unlockOrdering(self, state):

        """
        This callback function unlocks the ability to reorder items in the main
        passes lists in the "Shuffler" tab.
        """

        if state == True:
            self.listWidget_mainPasses.setDragDropMode(QAbstractItemView.InternalMove)
            self.listWidget_aov.setDragDropMode(QAbstractItemView.InternalMove)

        if state == False:
            self.listWidget_mainPasses.setDragDropMode(QAbstractItemView.NoDragDrop)
            self.listWidget_aov.setDragDropMode(QAbstractItemView.NoDragDrop)

    def selectShuffled(self):

        """
        Selects all the items from the most recent Shuffle action that can be found.
        """

        if not self.shuffleIndexDict:
            return

        self.missingEntriesHandler(self.shuffleIndexDict, self.shuffleIndexDict_missingEntries)

        curSelection = nuke.selectedNodes()

        for n in curSelection:
            n.setSelected(False)

        # Select the shuffled nodes from shuffleIndexDict.
        for node in self.shuffleIndexDict:
            node.setSelected(True)

        # If no nodes have been selected, return original selection.
        if not nuke.selectedNodes():
            for no in curSelection:
                no.setSelected(True)

    def selectSpawned(self):

        """
        Selects all the items from the most node tree preset spawn that can be found.
        """

        if not self.nodeTreePreset_buffer:
            return

        self.missingEntriesHandler(self.nodeTreePreset_buffer,
                                    self.nodeTreePreset_buffer_missingEntires)

        curSelection = nuke.selectedNodes()

        for n in curSelection:
            n.setSelected(False)

        # Select the spawned nodes from nodeTreePreset_buffer.
        for node in self.nodeTreePreset_buffer:
            node.setSelected(True)

        # If no nodes have been selected, return original selection.
        if not nuke.selectedNodes():
            for no in curSelection:
                no.setSelected(True)

    def changeRendererOptions(self, ind):

        """
        This function will look at the user's selection for the Renderer of choice
        and change the corresponding fields. The functon will be called upon the
        changing of dropdown options.
        """

        self.comboBox_rendererSelectionDropdown.blockSignals(True)
        self.comboBox_rendererSelectionDropdown_alt.blockSignals(True)

        self.comboBox_rendererSelectionDropdown.setCurrentIndex(ind)
        self.comboBox_rendererSelectionDropdown_alt.setCurrentIndex(ind)

        if self.comboBox_rendererSelectionDropdown.currentText() == "Arnold":
            self.stackedWidget_rebuildOptions.setCurrentIndex(1)
        elif self.comboBox_rendererSelectionDropdown.currentText() == "VRay":
            self.stackedWidget_rebuildOptions.setCurrentIndex(2)
        else:
            self.stackedWidget_rebuildOptions.setCurrentIndex(0)

        self.comboBox_rendererSelectionDropdown.blockSignals(False)
        self.comboBox_rendererSelectionDropdown_alt.blockSignals(False)

    def distanceMultHandler(self, widget):

        """
        This function will be called when the user interacts with the Distance Mult
        widgets. The "widget" parameter informs the function if it needs to change
        either the slider or the field's value based on the user's actions.
        """

        if widget == self.slider_nodeDistanceMult:
            # Block signals to prevent calling the function again.
            self.numField_nodeDistanceMult.blockSignals(True)
            if not self.slider_nodeDistanceMult.value() < 10 and not self.slider_nodeDistanceMult.value() > 99:
                firstDigit = str(self.slider_nodeDistanceMult.value())[0]
                secondDigit = str(self.slider_nodeDistanceMult.value())[1]

                if int(secondDigit) < 5:
                    newValue = int(firstDigit)
                else:
                    newValue = int(firstDigit) + 1
            elif self.slider_nodeDistanceMult.value() == 100:
                newValue = 10
            else:
                # Set it to slider's value anyway so it can trigger
                # the function again for the numField. That will cause
                # this function to truncate the number between 1 and 10.
                newValue = self.slider_nodeDistanceMult.value()

            self.numField_nodeDistanceMult.setValue(newValue)

            # Change the class attribute to match the num field's number
            # which will be carried through the relevant functions.
            self.distanceMult = self.numField_nodeDistanceMult.value()

            # Unblock signals.
            self.numField_nodeDistanceMult.blockSignals(False)

        elif widget == self.numField_nodeDistanceMult:
            # Ensure value isn't higher than 10.
            if self.numField_nodeDistanceMult.value() > 10:
                self.numField_nodeDistanceMult.setValue(10)
                # Return because changing the value above emits a new
                # "valueChanged" signal anyway.
                return
            # Ensure value isn't lower than 1.
            elif self.numField_nodeDistanceMult.value() < 1:
                self.numField_nodeDistanceMult.setValue(1)
                # Return because changing the value above emits a new
                # "valueChanged" signal anyway.
                return

            self.slider_nodeDistanceMult.setValue(self.numField_nodeDistanceMult.value() * 10)

            # Change the class attribute to match the num field's number
            # which will be carried through the relevant functions.
            self.distanceMult = self.numField_nodeDistanceMult.value()

    def sectionNamesHandler(self):

        """
        This function is called when the user finishes editing the custom name fields
        for the layer selection lists and ensures the fields aren't empty.
        """

        if not str(self.lineEdit_mainPassesTitle_input.text()):
            self.lineEdit_mainPassesTitle_input.setText("Main Passes")

        if not str(self.lineEdit_aovsTitle_input.text()):
            self.lineEdit_aovsTitle_input.setText("AOVs")

    def renamingHandler(self, name, mode = "node", listWidget = None):

        """
        This function handles renaming to ensure each name remains unique.
        """

        # Ensure name is a string and initialize num.
        name = str(name)
        num = 1

        # Default functionality for the function. Creates a unique name for
        # a Nuke node.
        if mode == "node":
            if nuke.exists(name):
                while True:
                    if nuke.exists(name + str(num)) == False:
                        return name + str(num)
                    num += 1
            else:
                return name

        # This mode is meant to be used on list widgets, if one has been passed
        # to the function.
        elif mode == "list" and not listWidget == None:
            listItems = set([str(listWidget.item(i).text()) for i in range(listWidget.count())])
            if name in listItems:
                while True:
                    if num < 10:
                        if name + "_" + str(0) + str(num) not in listItems:
                            return name + "_" + str(0) + str(num)
                    else:
                        if name + "_" + str(num) not in listItems:
                            return name + "_" + str(num)
                    num += 1
            else:
                return name

    def storedNodes_deletionHandler(self, mode):

        """
        Deletes stored node entries in "Add Nodes" tab, based on the called mode.
        """

        if mode == "all":
            self.listWidget_storedNodes.clear()
            self.storedNodes = {}
        elif mode == "entry":
            try:
                toDelete = self.listWidget_storedNodes.selectedItems()[0]
            except IndexError:
                return

            if str(toDelete.text()) in self.storedNodes:
                del self.storedNodes[str(toDelete.text())]

            self.listWidget_storedNodes.takeItem(self.listWidget_storedNodes.row(toDelete))

    def storeSelectedNodes(self, single = False):

        """
        Store the nodes that have been selected in the Node graph and create
        entries for them in the "Add Nodes" tab list widget.
        """

        # Get selected nodes that can have inputs and outputs, and store the list widget.
        if not single:
            toAdd = [n for n in nuke.selectedNodes() if not n.maxInputs() == 0 and not n.maxOutputs() == 0]
        else:
            if not nuke.selectedNode().maxInputs() == 0 and not nuke.selectedNode().maxInputs() == 0:
                # Make it a list to avoid writing extensive checks
                # in the following part of this function.
                toAdd = [nuke.selectedNode()]
        
        list_widget = self.listWidget_storedNodes

        if not toAdd:
            return

        # Select all items in both layer selection lists to create
        # the default behavior.
        self.selectAllBtn(self.listWidget_mainPassesSelection, emitSignal = False)
        self.selectAllBtn(self.listWidget_aovsSelection, emitSignal = False)

        mainPasses_sel = set([str(i.text()) for i in self.listWidget_mainPassesSelection.selectedItems()])
        aovs_sel = set([str(i.text()) for i in self.listWidget_aovsSelection.selectedItems()])

        for node in toAdd:
            self.clearSelectionBtn(list_widget)

            list_widget.addItem(self.renamingHandler(node.Class(), mode = "list", listWidget = list_widget))

            knobsDict = {}
            knobsToStore = [k for k in node.allKnobs()]
            knobsToStore = [knob for knob in knobsToStore if not any(knob.name() == n
                            for n in ["name", "selected", "xpos", "ypos"])]

            for ind, knob in enumerate(knobsToStore):
                if knob.name() == "":
                    continue

                knobsDict[knob.name()] = (knob.value(), ind)

            nodesInGrp_storageDict = {}

            # Store information about node by putting the name of the list widget
            # item as key in the dictionary and associating the settings as values
            # with their own dictionaries inside.
            if node.Class() == "Group":
                with nuke.toNode(node.name()):
                    nodesInGrp = nuke.allNodes()

                    nodesInGrp_storageDict = self.gatherData_manyNodes(nodesInGrp)

            self.storedNodes[str(list_widget.item(list_widget.count() - 1).text())] = {"nodeType": node.Class(),
                                                                                        "mainPasses_selection": mainPasses_sel,
                                                                                        "aovs_selection": aovs_sel,
                                                                                        "knobsInfo": knobsDict,
                                                                                        "nodesInside": nodesInGrp_storageDict}

        list_widget.setCurrentItem(list_widget.item(list_widget.count() - 1))

    def updateEntry(self):

        """
        Updates the selected entry in the "Add Nodes" tab's list widget with the
        currently selected node in the Node Graph.
        """

        list_widget = self.listWidget_storedNodes
        
        if not list_widget.selectedItems():
            return
        elif not nuke.selectedNodes():
            nuke.message("Please select a node in the Node Graph.")
            return
        else:
            if nuke.selectedNode().maxInputs() == 0 or nuke.selectedNode().maxInputs() == 0:
                return

        # Find and remove the selected entry in the list widget.
        listWidget_itemName = str(list_widget.selectedItems()[0].text())

        del self.storedNodes[listWidget_itemName]

        listWidget_item = list_widget.findItems(listWidget_itemName, Qt.MatchExactly)[0]

        itemRow = list_widget.row(listWidget_item)

        # Delete the item.
        list_widget.takeItem(itemRow)

        # Store the new selected node.
        self.storeSelectedNodes(single = True)

        # Take out the newly created list widget item and
        # move it to the position of the previous item.
        newItem = list_widget.takeItem(list_widget.row(list_widget.selectedItems()[0]))
        list_widget.insertItem(itemRow, newItem)

        list_widget.setCurrentItem(newItem)

    def recreateStoredNodeEntry(self, nodeEntry, mode = "free"):

        """
        Recreates a node that has been stored in the built-in dict.
        """

        # Unpacking nodeEntry's information.
        nodeClass = self.storedNodes[nodeEntry]["nodeType"]
        knobs_values = self.storedNodes[nodeEntry]["knobsInfo"]
        nodesInGrp = self.storedNodes[nodeEntry]["nodesInside"]

        # Storing user's selection to restore later.
        startingSelection = nuke.selectedNodes()

        # If this function is called by the Shuffle actions,
        # it won't deselect the nodes, which is vital for that.
        if mode == "free":
            for n in startingSelection:
                n.setSelected(False)

        # Create the node and restore its values.
        newNode = nuke.Node(nodeClass, inpanel = False)
        newNode_knobs = set([i.name() for i in newNode.allKnobs()])
        for knob in knobs_values:
            if knob in newNode_knobs:
                try:
                    newNode[knob].setValue(knobs_values[knob][0])
                except:
                    continue

        if nodeClass == "Group":
            with nuke.toNode(newNode.name()):
                self.restoreNodeStructure(nodesInGrp)

        if mode == "free":
            # Restore original user selection.
            for n in nuke.selectedNodes():
                n.setSelected(False)

            for sel in startingSelection:
                sel.setSelected(True)

        return newNode

    def recreateStoredNodeEntry_wrapper(self):

        """
        This function exists to check whether a list widget item
        is selected before calling recreateStoredNodeEntry.
        """

        if not self.listWidget_storedNodes.selectedItems():
            return
        else:
            self.recreateStoredNodeEntry(str(self.listWidget_storedNodes.selectedItems()[0].text()))

    def getInfo_forStoredNode(self, listItem, storedNodesDict):

        """
        Gather information about the selected list item and format it
        to be displayed in a Nuke display window.
        """

        info = "Showing stored information for: %s." % listItem
        info += "\n" + "-" * 50
        knobs_values = []

        for k in storedNodesDict[listItem]["knobsInfo"]:
            knobs_values.append((k, storedNodesDict[listItem]["knobsInfo"][k][0], storedNodesDict[listItem]["knobsInfo"][k][1]))

        # Sort by original order of knobs.
        knobs_values = sorted(knobs_values, key = itemgetter(2))
        
        for k, v, ind in knobs_values:
            info += "\n%s - %s" % (str(k), str(v))

        info += "\n" + "-" * 50
        info += "\nSelected Layers in %s:\n" % str(self.label_mainPassesSelection.text())

        for item in storedNodesDict[listItem]["mainPasses_selection"]:
            info += "\n" + item

        info += "\n" + "-" * 50
        info += "\nSelected Layers in %s:\n" % str(self.label_aovsSelection.text())

        for item in storedNodesDict[listItem]["aovs_selection"]:
            info += "\n" + item

        return info

    def showInfo_forStoredNode(self, targetItem):

        """
        Show information about the stored node in a separate window.
        """

        # Clear previous instance of infoPanel.
        if self.infoPanel:
            self.infoPanel.destroy()
            self.infoPanel = None

        # Create the panel and open it.
        self.infoPanel = panels.PythonPanel("Show info: %s" % targetItem)
        self.textKnob = nuke.Text_Knob("")
        self.textKnob.setValue(self.getInfo_forStoredNode(targetItem, self.storedNodes))

        self.infoPanel.addKnob(self.textKnob)
        self.infoPanel.addToPane()

        self.infoPanel.show()

    def showInfo_forStoredNode_wrapper(self, targetItem = None):

        """
        Wrapper function which checks if a list widget item is
        selected when the "show info" button is pressed.
        """

        # If targetItem has been passed, it means this function is called
        # by double-clicking an item in the list widget which passes the
        # item as the targetItem.
        if targetItem:
            self.showInfo_forStoredNode(str(targetItem.text()))
        else:
            if not self.listWidget_storedNodes.selectedItems():
                return
            else:
                self.showInfo_forStoredNode(str(self.listWidget_storedNodes.selectedItems()[0].text()))

    def addPremultSandwich(self):

        """
        In the "Add Nodes" tab's list widget, add an Unpremult node entry
        in the beginning of the list and then a Premult node entry at the
        end of the list. 
        """

        list_widget = self.listWidget_storedNodes

        # Select all items in both layer selection lists to create
        # the default behavior.
        self.selectAllBtn(self.listWidget_mainPassesSelection, emitSignal = False)
        self.selectAllBtn(self.listWidget_aovsSelection, emitSignal = False)

        mainPasses_sel = set([str(i.text()) for i in self.listWidget_mainPassesSelection.selectedItems()])
        aovs_sel = set([str(i.text()) for i in self.listWidget_aovsSelection.selectedItems()])
        
        # Create the list widget items.
        list_widget.insertItem(0, self.renamingHandler("Unpremult", mode = "list", listWidget = list_widget))
        list_widget.addItem(self.renamingHandler("Premult", mode = "list", listWidget = list_widget))

        # Store information about the nodes by putting the name of the list widget
        # item as key in the dictionary and associating the settings as values
        # with their own dictionaries inside.
        self.storedNodes[str(list_widget.item(0).text())] = {"nodeType": "Unpremult",
                                                            "mainPasses_selection": mainPasses_sel,
                                                            "aovs_selection": aovs_sel,
                                                            "knobsInfo": {},
                                                            "nodesInside": {}}
        self.storedNodes[str(list_widget.item(list_widget.count() - 1).text())] = {"nodeType": "Premult",
                                                                                    "mainPasses_selection": mainPasses_sel,
                                                                                    "aovs_selection": aovs_sel,
                                                                                    "knobsInfo": {},
                                                                                    "nodesInside": {}}

        list_widget.setCurrentItem(list_widget.item(list_widget.count() - 1))

    def restoreLayerSelections(self):

        """
        This function will be called when a different item is selected
        in the "Add Nodes" tab's list widget to return the corresponding
        item's layer selection.
        """

        if not self.listWidget_storedNodes.selectedItems():
            return

        selectedItem_name = str(self.listWidget_storedNodes.selectedItems()[0].text())

        # Clear selections in the layer list widgets and prevent emission of an
        # itemSelectionChanged signal to avoid overwriting the stored selections.
        self.clearSelectionBtn(self.listWidget_mainPassesSelection, emitSignal = False)
        self.clearSelectionBtn(self.listWidget_aovsSelection, emitSignal = False)

        if selectedItem_name not in self.storedNodes:
            return
        
        mainPasses_sel = self.storedNodes[selectedItem_name]["mainPasses_selection"]
        aovs_sel = self.storedNodes[selectedItem_name]["aovs_selection"]

        # Block signals to prevent overwriting of saved layer selections.
        self.listWidget_mainPassesSelection.blockSignals(True)
        self.listWidget_aovsSelection.blockSignals(True)

        for name in mainPasses_sel:
            if self.listWidget_mainPassesSelection.findItems(name, Qt.MatchExactly):
                listWidget_item = self.listWidget_mainPassesSelection.findItems(name, Qt.MatchExactly)[0]
                itemRow = self.listWidget_mainPassesSelection.row(listWidget_item)

                self.listWidget_mainPassesSelection.setCurrentItem(self.listWidget_mainPassesSelection.item(itemRow), QItemSelectionModel.Select)

        for name in aovs_sel:
            if self.listWidget_aovsSelection.findItems(name, Qt.MatchExactly):
                listWidget_item = self.listWidget_aovsSelection.findItems(name, Qt.MatchExactly)[0]
                itemRow = self.listWidget_aovsSelection.row(listWidget_item)

                self.listWidget_aovsSelection.setCurrentItem(self.listWidget_aovsSelection.item(itemRow), QItemSelectionModel.Select)

        # Unblock signals again.
        self.listWidget_mainPassesSelection.blockSignals(False)
        self.listWidget_aovsSelection.blockSignals(False)

    def saveLayerSelections(self):

        """
        Callback function to be called when selection has changed
        in the "Add Nodes" tab's Layer Selection list widgets.
        The function will store overwrite the new selections with
        the existing layer selections in the built-in dictionary
        for the currently selected stored node entry.
        """

        if not self.listWidget_storedNodes.selectedItems():
            return

        nodeEntry = str(self.listWidget_storedNodes.selectedItems()[0].text())

        new_mainPasses_sel = set([str(i.text()) for i in self.listWidget_mainPassesSelection.selectedItems()])
        new_aovs_sel = set([str(i.text()) for i in self.listWidget_aovsSelection.selectedItems()])

        self.storedNodes[nodeEntry]["mainPasses_selection"] = new_mainPasses_sel
        self.storedNodes[nodeEntry]["aovs_selection"] = new_aovs_sel
    
    def saveNodeTreePreset(self):

        """
        Save the selected nodes' information into a dict and then
        dumps it out to json format.
        """

        presetName = str(self.lineEdit_presetName.text())
        selectedNodeTree = nuke.selectedNodes()

        if not selectedNodeTree:
            return

        if not presetName:
            return

        try:
            with open("%s/%s.json" % (self.presetsDir, presetName), "w") as jsonFile:

                # Clear any current selection.
                for sel in selectedNodeTree:
                    sel.setSelected(False)

                tempStorageDict = self.gatherData_manyNodes(selectedNodeTree)

                json.dump(tempStorageDict, jsonFile, sort_keys = True)
        except:
            nuke.message("Error saving to or creating file:\n\n"
                            + str(traceback.format_exc()))
            return

        listWidget = self.listWidget_savedPresets
        listItems = set([str(listWidget.item(i).text())
                        for i in range(listWidget.count())])

        # Create a new item in the list widget if an item with the name doesn't exist.
        # Else, it is assumed that the user wants to overwrite the preset.
        if presetName not in listItems:
            listWidget.addItem(presetName)
            listWidget.setCurrentRow(listWidget.count() - 1)

        # Clear the entered text in the Preset Name input field.
        self.lineEdit_presetName.clear()

        # Restore user selection.
        for sel in nuke.selectedNodes():
            sel.setSelected(False)

        for sel in selectedNodeTree:
            sel.setSelected(True)

    def spawnNodeTreePreset(self):

        """
        Import the json file from the selected preset, recreate the nodes
        and restore their knobs and connections.
        """

        # Get the selected preset name.
        try:
            presetName = str(self.listWidget_savedPresets.selectedItems()[0].text())
        except IndexError:
            return

        # Load JSON file.
        with open("%s/%s.json" % (self.presetsDir, presetName), "r") as presetFile:
            importedPreset = json.load(presetFile)

        # Clear the current buffer dict to ensure only
        # the new nodes remain in it.
        self.nodeTreePreset_buffer = {}

        userSelection = nuke.selectedNodes()

        # Deselect any current selection.
        for sel in userSelection:
            sel.setSelected(False)

        try:
            self.nodeTreePreset_buffer = self.restoreNodeStructure(importedPreset)
        except:
            nuke.message("Error loading preset:\n\n"
                            + str(traceback.format_exc()))
            return

        # Restore user selection.
        for sel in nuke.selectedNodes():
            sel.setSelected(False)

        for sel in userSelection:
            sel.setSelected(True)

    def deleteNodeTreePreset(self):

        """
        Deletes the selected node tree preset entry and the associated file.
        """

        # Get the selected preset name.
        try:
            listItem = self.listWidget_savedPresets.selectedItems()[0]
            presetName = str(listItem.text())
        except IndexError:
            return

        filePath = "%s/%s.json" % (self.presetsDir, presetName)

        if os.path.isfile(filePath):
            os.remove(filePath)

        # Delete related list widget item.
        self.listWidget_savedPresets.takeItem(self.listWidget_savedPresets.row(listItem))





    # -----------------------------------------------------------------------------------------------------------------------
    # The following section contains the functions that perform the Shuffle and Rebuild.
    # -----------------------------------------------------------------------------------------------------------------------

    def findLastConnected(self, nodeToStartFrom, recursion = False):

        """
        Recursive function which will find the last connected node
        that is part of the current Shuffle.
        """

        if not recursion:
            self.missingEntriesHandler(self.shuffleIndexDict, self.shuffleIndexDict_missingEntries)

        connections = nuke.dependentNodes(nuke.INPUTS | nuke.HIDDEN_INPUTS, nodeToStartFrom)

        toReturn = nodeToStartFrom

        if connections:
            for node in connections:
                if node in self.shuffleIndexDict:
                    toReturn = self.findLastConnected(node, recursion = True)

            return toReturn
        else:
            return toReturn

    def shufflingLoop(self, passesList, enumStart, startingX, startingY, section, startDot):

        """
        Create as many branches of Shuffle nodes as the number of passes
        in the passes list.
        """

        for index, item in enumerate(passesList, enumStart):

            # Initialize some variables and clear them at every iteration,
            # to prevent some 'if' statements from errorring.
            nodesToAdd = []
            createdNodes = []
            layerSelection = None
            recNode = None

            dot = nuke.nodes.Dot()
            offset = startingX + 250 * self.distanceMult
            dot.setXYpos(offset, startingY)
            ypos = dot.ypos()
            xpos = dot.xpos()
            dot.connectInput(0, nuke.selectedNode())
            dot.knob("name").setValue(self.renamingHandler("Dot_" + item))
            # Clear selection and ensure Dot is selected so next steps connect automatically.
            for n in nuke.selectedNodes():
                n.setSelected(False)
            dot.setSelected(True)

            # Shuffle
            shuf = nuke.Node("Shuffle2", inpanel=False)
            xpos = shuf.xpos()
            offset = ypos + 250
            shuf.setXYpos(xpos,offset)
            shuf.knob("in1").setValue(item)
            shuf.knob("name").setValue(self.renamingHandler(item))
            shuf.knob("postage_stamp").setValue(True)

            # Create the nodes from the "Add Nodes" tab, if any were stored.
            if self.listWidget_storedNodes.count() > 0:
                nodesToAdd = [str(self.listWidget_storedNodes.item(i).text()) for i in range(self.listWidget_storedNodes.count())]

                if section == str(self.lineEdit_mainPassesTitle_input.text()):
                    layerSelection = "mainPasses_selection"
                elif section == str(self.lineEdit_aovsTitle_input.text()):
                    layerSelection = "aovs_selection"

                recNode = None
                for n in nodesToAdd:
                    if recNode:
                        prevNode = recNode
                    # The following 'if' statements check if the current
                    # shuffling loop is in the "Other" section.
                    if layerSelection:
                        if item in self.storedNodes[n][layerSelection]:
                            recNode = self.recreateStoredNodeEntry(n, mode = "shuffled")
                            if recNode.Class() == "Group":
                                recNode.setXYpos(prevNode.xpos(), prevNode.ypos())
                                recNode.connectInput(0, prevNode)
                            recNode.setXYpos(recNode.xpos(), recNode.ypos() + 40 * self.distanceMult)
                            createdNodes.append(recNode)
                    else:
                        recNode = self.recreateStoredNodeEntry(n, mode = "shuffled")
                        if recNode.Class() == "Group":
                            recNode.setXYpos(prevNode.xpos(), prevNode.ypos())
                            recNode.connectInput(0, prevNode)
                        recNode.setXYpos(recNode.xpos(), recNode.ypos() + 40 * self.distanceMult)
                        createdNodes.append(recNode)

                if recNode:
                    # Memorize the lowest point of created nodes during the Shuffle,
                    # to establish a base line for the Rebuild later on.
                    if self.rebuildStart_highestY:
                        if recNode.ypos() < self.rebuildStart_highestY:
                            self.rebuildStart_highestY = recNode.ypos()
                    else:
                        self.rebuildStart_highestY = recNode.ypos()
            else:
                # Memorize the lowest point of created nodes during the Shuffle,
                # to establish a base line for the Rebuild later on.
                if self.rebuildStart_highestY:
                    if shuf.ypos() < self.rebuildStart_highestY:
                        self.rebuildStart_highestY = shuf.ypos()
                else:
                    self.rebuildStart_highestY = shuf.ypos()

            # Clear selection, then select Shuffle and newly created nodes to
            # add them to the autobackdrop.
            for n in nuke.selectedNodes():
                n.setSelected(False)
            shuf.setSelected(True)

            if createdNodes:
                for node in createdNodes:
                    node.setSelected(True)

            # Backdrop
            backd = nukescripts.autobackdrop.autoBackdrop()
            # Center Y position of backdrop to shuffle node.
            ypos = shuf.ypos()-((111/2)-14)
            # Offset Y upwards.
            ypos -= 150
            # Center X position of backdrop to shuffle node.
            xpos = shuf.xpos()-((222/2)-41-10)
            backd.setXYpos(int(xpos), int(ypos))

            backd.knob("bdheight").setValue(backd["bdheight"].value() + 185 - 50)
            backd.knob("bdwidth").setValue(backd["bdwidth"].value() * 2)
            # If user hasn't selected their own color, use a default ('if' statement),
            # otherwise use their selection ('else' statement).
            if self.btn_selectColor.palette().button().color().getRgb() == (76, 76, 76, 255):
                hexColor = int('%02x%02x%02x%02x' % (0*255,0.533*255,0.318*255,1),16)
            else:
                hexColor = int('%02x%02x%02x%02x' % self.btn_selectColor.palette().button().color().getRgb(),16)
            backd.knob("tile_color").setValue(hexColor)
            backd.knob("label").setValue(item)
            backd.knob("name").setValue(self.renamingHandler("Backdrop_" + item))
            backd.knob("note_font_size").setValue(25)

            # Autobackdrop will behave weirdly if only 1 node is selected,
            # in which case the width and height of the backdrop need to be
            # adjusted manually.
            if len(nuke.selectedNodes()) == 1:
                backd.knob("bdwidth").setValue(backd.knob("bdwidth").value() + 160)
                backd.knob("bdheight").setValue(backd.knob("bdheight").value() + 50)

            # Clear selection.
            for n in nuke.selectedNodes():
                n.setSelected(False)

            # Select Dot again and carry over the X and Y positions to next iteration.
            dot.setSelected(True)
            startingY = dot.ypos()
            startingX = dot.xpos()

            # Add new elements to shuffleIndexDict.
            for t in (dot, shuf, backd):
                self.shuffleIndexDict[t] = {"shuffleIndex": index, "layerName": item, "section": section}

            if createdNodes:
                for n in createdNodes:
                    self.shuffleIndexDict[n] = {"shuffleIndex": index, "layerName": item, "section": section}

        # Clear selection.
        for n in nuke.selectedNodes():
            n.setSelected(False)

        keysToDelete = []

        for connection in nuke.dependentNodes(nuke.INPUTS | nuke.HIDDEN_INPUTS, startDot):
            if connection in self.shuffleIndexDict and self.shuffleIndexDict[connection]["section"] == section:
                highestIndex = 0
                for key in self.shuffleIndexDict:
                    try:
                        nuke.exists(key.name())
                        if self.shuffleIndexDict[key]["section"] == section:
                            key.setSelected(True)
                        if self.shuffleIndexDict[key]["shuffleIndex"] > highestIndex:
                            highestIndex = self.shuffleIndexDict[key]["shuffleIndex"]
                    except KeyError:
                        continue
                    except ValueError:
                        keysToDelete.append(key)
                        continue
                # Create the section's backdrop.
                if len(nuke.selectedNodes()) == 3:
                    # 3 because there's always only 3 nodes in a single Shuffle sub-tree
                    # and the backdrop needs to have different dimensions if it contains only 1 sub-tree.
                    sectionBackd = nukescripts.autobackdrop.autoBackdrop()
                    sectionBackd.knob("bdheight").setValue(sectionBackd.knob("bdheight").value() + 39)
                    sectionBackd.knob("bdwidth").setValue(sectionBackd.knob("bdwidth").value() + 106 - 45)

                    sectionBackd.knob("bdheight").setValue(sectionBackd.knob("bdheight").value() + 40 + 46 - 6)
                    sectionBackd.setYpos(sectionBackd.ypos() - 40)

                    # The section backdrop will not envelop the entire Shuffled section
                    # if the last Shuffled layer does only contains a Shuffle. This follow block
                    # ensures that the backdrop is extended if the last layer is only the Shuffle node.
                    for node in nuke.selectedNodes():
                        if node.Class() == "Shuffle2" and self.shuffleIndexDict[node]["shuffleIndex"] == highestIndex:
                            if self.findLastConnected(node) == node:
                                sectionBackd.knob("bdwidth").setValue(sectionBackd.knob("bdwidth").value() + 34)
                else:
                    sectionBackd = nukescripts.autobackdrop.autoBackdrop()
                    sectionBackd.knob("bdheight").setValue(sectionBackd.knob("bdheight").value() + 39)
                    sectionBackd.knob("bdwidth").setValue(sectionBackd.knob("bdwidth").value() + 106 - 45)

                    sectionBackd.knob("bdheight").setValue(sectionBackd.knob("bdheight").value() + 40 - 6)
                    sectionBackd.setYpos(sectionBackd.ypos() - 40)

                    # The section backdrop will not envelop the entire Shuffled section
                    # if the last Shuffled layer does only contains a Shuffle. This follow block
                    # ensures that the backdrop is extended if the last layer is only the Shuffle node.
                    for node in nuke.selectedNodes():
                        if node.Class() == "Shuffle2" and self.shuffleIndexDict[node]["shuffleIndex"] == highestIndex:
                            if self.findLastConnected(node) == node:
                                sectionBackd.knob("bdwidth").setValue(sectionBackd.knob("bdwidth").value() + 34)

                sectionBackd.knob("label").setValue(section)
                sectionBackd.knob("note_font_size").setValue(70)
                self.shuffleIndexDict[sectionBackd] = {}

        for k in keysToDelete:
            del self.shuffleIndexDict[k]

        # Clear selection and select "dot".
        for n in nuke.selectedNodes():
            n.setSelected(False)
        dot.setSelected(True)

    def shuffleLayers(self, targetNode, extending = False):

        """
        Shuffle the layers to corresponding Backdrops, respecting user options in UI.
        """

        # Do nothing if "Shuffle Selected Only" checkbox is checked but nothing is selected.
        if self.check_selectionOnly.isChecked() and len(self.listWidget_mainPasses.selectedItems()) == 0 and len(self.listWidget_aov.selectedItems()) == 0:
            return

        self.missingEntriesHandler(self.shuffleIndexDict, self.shuffleIndexDict_missingEntries)

        if extending:
            # Duplicate shuffleIndexDict to restore at the end.
            self.shuffleIndexDict_originalCopy = copy.copy(self.shuffleIndexDict)

        # Clear "shuffleIndexDict" for the new Shuffle.
        self.shuffleIndexDict = {}

        # Check if the incoming node stream is connected to an EXR file. If not, ask the user
        # if they wish to continue anyway.
        if not self.check_removeExrRestriction.isChecked():
            if not targetNode.metadata("input/filereader") == "exr":
                userDecision = nuke.ask("The selected node isn't connected to an OpenEXR file. Continue anyway?")
                if userDecision == False:
                    return
                else:
                    pass

        # Initialize necessary variables.
        pases = []
        other = []
        other_prep = []

        gathered_mainPasses = []
        mainPasses = []
        remnants_mainPasses = []

        gathered_aovs = []
        aovs = []
        remnants_aovs = []

        # Gather the passes based on whether user wants to use Rebuild.
        if self.check_useRebuild.isChecked():
            passes, gathered_mainPasses, gathered_aovs = self.gatherLayers(targetNode, useOrder = True, reorderForRebuild = True)

        else:
            passes, gathered_mainPasses, gathered_aovs = self.gatherLayers(targetNode, useOrder = True)
        
        if not passes:
            return

        # Copy gathered passes lists.
        remnants_mainPasses = gathered_mainPasses[:]
        remnants_aovs = gathered_aovs[:]

        mainPassesSelection = [str(t.text()) for t in self.listWidget_mainPasses.selectedItems()]
        aovsSelection = [str(t.text()) for t in self.listWidget_aov.selectedItems()]

        # The following section populates the "mainPasses" and "aovs" lists with the user's selection,
        # while removing the corresponding items from the "remnants" lists for later use.

        if gathered_mainPasses:
            for p in gathered_mainPasses:
                if p in mainPassesSelection:
                    mainPasses.append(p)
                    remnants_mainPasses.remove(p)

        if gathered_aovs:
            for p in gathered_aovs:
                if p in aovsSelection:
                    aovs.append(p)
                    remnants_aovs.remove(p)

        # Finalise "other" by adding the remaining (unselected) items.
        other_prep.extend(remnants_mainPasses)
        other_prep.extend(remnants_aovs)

        other_prep = self.removeDuplicates(other_prep)

        for item in other_prep:
            if item not in mainPassesSelection and item not in aovsSelection:
                other.append(item)

        # Reorder "other" to match the original order of the layers.
        for it in passes:
            if it in other:
                other.append(other.pop(other.index(it)))

        # Clear selection.
        for n in nuke.selectedNodes():
            n.setSelected(False)

        # Create the first dot.
        firstDot = nuke.Node("Dot", inpanel=False)
        firstDot.setInput(0, targetNode)
        startingDot = firstDot
        xpos = targetNode.xpos()
        ypos = targetNode.ypos()
        if not extending:
            ypos += 34
        offset = xpos + 400
        startingDot.setXYpos(offset, ypos)
        ypos = startingDot.ypos()
        xpos = startingDot.xpos()

        # Find highest index.
        if extending:
            dotList = []

            for node in self.shuffleIndexDict_originalCopy:
                if node.Class() == "Dot":
                    try:
                        dotList.append((node, self.shuffleIndexDict_originalCopy[node]["shuffleIndex"]))
                    except KeyError:
                        pass
            if dotList:
                dotList = sorted(dotList, key = itemgetter(1))
                lastDot = max(dotList, key = itemgetter(1))[0]

                currentShuffleIndex = self.shuffleIndexDict_originalCopy[lastDot]["shuffleIndex"]
            else:
                currentShuffleIndex = 1
        else:
            currentShuffleIndex = 1

        # Shuffle the "Main Passes" (left side) list.
        if mainPasses:
            self.shufflingLoop(mainPasses, currentShuffleIndex, xpos, ypos, str(self.lineEdit_mainPassesTitle_input.text()), startingDot)
            startingDot = nuke.selectedNode()
            ypos = startingDot.ypos()
            xpos = startingDot.xpos() + 230
            if extending:
                currentShuffleIndex = self.shuffleIndexDict[startingDot]["shuffleIndex"] + 1
            else:
                currentShuffleIndex = self.shuffleIndexDict[startingDot]["shuffleIndex"] + 1

        # Shuffle the "AOVs" (right side) list.
        if aovs:
            self.shufflingLoop(aovs, currentShuffleIndex, xpos, ypos, str(self.lineEdit_aovsTitle_input.text()), startingDot)
            startingDot = nuke.selectedNode()
            ypos = startingDot.ypos()
            xpos = startingDot.xpos() + 230
            if extending:
                currentShuffleIndex = self.shuffleIndexDict[startingDot]["shuffleIndex"] + 1
            else:
                currentShuffleIndex = self.shuffleIndexDict[startingDot]["shuffleIndex"] + 1

        # Shuffle the rest, unless specified not to do so by user.
        if not self.check_selectionOnly.isChecked():
            if other:
                self.shufflingLoop(other, currentShuffleIndex, xpos, ypos, "Other", startingDot)

        # Clear selection.
        for n in nuke.selectedNodes():
            n.setSelected(False)

        return firstDot

    def rendererRebuild(self, renderer, mode, direction):

        """
        Rebuild the render passes based on user options.
        """

        distanceNum = 200 * self.distanceMult
        baseLine = self.rebuildStart_highestY + 88

        if renderer == "Arnold":
            if mode == "primary":
                # Prepare for rebuild.
                directDiffuse = str(self.comboBox_directDiffuse.currentText())
                indirectDiffuse = str(self.comboBox_indirectDiffuse.currentText())
                directSpecular = str(self.comboBox_directSpec.currentText())
                indirectSpecular = str(self.comboBox_indirectSpec.currentText())
                directCoat = str(self.comboBox_directCoat.currentText())
                indirectCoat = str(self.comboBox_indirectCoat.currentText())
                directTransmission = str(self.comboBox_directTransmission.currentText())
                indirectTransmission = str(self.comboBox_indirectTransmission.currentText())
                directSss = str(self.comboBox_directSss.currentText())
                indirectSss = str(self.comboBox_indirectSss.currentText())
                directVolume = str(self.comboBox_directVolume.currentText())
                indirectVolume = str(self.comboBox_indirectVolume.currentText())
                emission = str(self.comboBox_emission.currentText())

                # Replace the variables above with their corresponding node pointers.
                for n in self.shuffleIndexDict:
                    if n.Class() == "Shuffle2":
                        replaceWith = self.findLastConnected(n)

                        if n['in'].value() == directDiffuse:
                            directDiffuse = replaceWith
                        elif n['in'].value() == indirectDiffuse:
                            indirectDiffuse = replaceWith
                        elif n['in'].value() == directSpecular:
                            directSpecular = replaceWith
                        elif n['in'].value() == indirectSpecular:
                            indirectSpecular = replaceWith
                        elif n['in'].value() == directCoat:
                            directCoat = replaceWith
                        elif n['in'].value() == indirectCoat:
                            indirectCoat = replaceWith
                        elif n['in'].value() == directTransmission:
                            directTransmission = replaceWith
                        elif n['in'].value() == indirectTransmission:
                            indirectTransmission = replaceWith
                        elif n['in'].value() == directSss:
                            directSss = replaceWith
                        elif n['in'].value() == indirectSss:
                            indirectSss = replaceWith
                        elif n['in'].value() == directVolume:
                            directVolume = replaceWith
                        elif n['in'].value() == indirectVolume:
                            indirectVolume = replaceWith
                        elif n['in'].value() == emission:
                            emission = replaceWith

                allPasses_initial = [directDiffuse, indirectDiffuse, directSpecular, indirectSpecular,
                                directCoat, indirectCoat, directTransmission, indirectTransmission,
                                directSss, indirectSss, directVolume, indirectVolume, emission] 

                allPasses = allPasses_initial[:]

                for elem in allPasses_initial:
                    try:
                        nuke.exists(elem.name())
                    except:
                        allPasses.remove(elem)

                # Clear selection.
                for n in nuke.selectedNodes():
                    n.setSelected(False)

                merges_firstLayer = []
                addLater = []

                # Rebuild.
                if direction == "Horizontal":
                    for p in allPasses:
                        if not p == "None" and self.shuffleIndexDict[p]["section"] == str(self.lineEdit_mainPassesTitle_input.text()):
                            if p == directDiffuse and indirectDiffuse not in allPasses:
                                p.setSelected(True)
                                d = nuke.Node("Dot", inpanel = False)
                                d.setXYpos(d.xpos(), baseLine + 4 + distanceNum*2)
                                p.setSelected(False)
                                d.setSelected(False)
                                addLater.append((d, 0))
                            elif directDiffuse in allPasses and p == directDiffuse:
                                p.setSelected(True)
                                mergeNode = nuke.Node("Merge2", inpanel = False)
                                mergeNode['operation'].setValue("plus")
                                mergeNode.setXYpos(p.xpos(), baseLine + distanceNum)
                                mergeNode.setInput(0, p)
                                d = nuke.Node("Dot", inpanel = False)
                                d.setXYpos(d.xpos(), mergeNode.ypos() + 4 + distanceNum)
                                d.setSelected(False)
                                p.setSelected(False)
                                mergeNode.setSelected(False)
                                merges_firstLayer.append((mergeNode, 0))
                                addLater.append((d, 0))
                            elif indirectDiffuse in allPasses and p == indirectDiffuse:
                                p.setSelected(True)
                                d = nuke.Node("Dot", inpanel = False)
                                d.setXYpos(d.xpos(), baseLine + 4 + distanceNum)
                                p.setSelected(False)
                                d.setSelected(False)
                                mergeNode.setInput(1, d)
                                self.shuffleIndexDict[d] = {}

                            if p == directSpecular and indirectSpecular not in allPasses:
                                p.setSelected(True)
                                mergeNode = nuke.Node("Merge2", inpanel = False)
                                mergeNode['operation'].setValue("plus")
                                mergeNode.setXYpos(p.xpos(), baseLine + distanceNum*2)
                                p.setSelected(False)
                                mergeNode.setSelected(False)
                                addLater.append((mergeNode, 1))
                            elif directSpecular in allPasses and p == directSpecular:
                                p.setSelected(True)
                                mergeNode = nuke.Node("Merge2", inpanel = False)
                                mergeNode['operation'].setValue("plus")
                                mergeNode.setXYpos(p.xpos(), baseLine + distanceNum)
                                mergeNode.setInput(0, p)
                                p.setSelected(False)
                                mergeNode.setSelected(False)
                                merges_firstLayer.append((mergeNode, 1))
                            elif indirectSpecular in allPasses and p == indirectSpecular:
                                p.setSelected(True)
                                d = nuke.Node("Dot", inpanel = False)
                                d.setXYpos(d.xpos(), baseLine + 4 + distanceNum)
                                p.setSelected(False)
                                d.setSelected(False)
                                mergeNode.setInput(1, d)
                                self.shuffleIndexDict[d] = {}

                            if p == directCoat and indirectCoat not in allPasses:
                                p.setSelected(True)
                                mergeNode = nuke.Node("Merge2", inpanel = False)
                                mergeNode['operation'].setValue("plus")
                                mergeNode.setXYpos(p.xpos(), baseLine + distanceNum*2)
                                p.setSelected(False)
                                mergeNode.setSelected(False)
                                addLater.append((mergeNode, 2))
                            elif directCoat in allPasses and p == directCoat:
                                p.setSelected(True)
                                mergeNode = nuke.Node("Merge2", inpanel = False)
                                mergeNode['operation'].setValue("plus")
                                mergeNode.setXYpos(p.xpos(), baseLine + distanceNum)
                                mergeNode.setInput(0, p)
                                p.setSelected(False)
                                mergeNode.setSelected(False)
                                merges_firstLayer.append((mergeNode, 2))
                            elif indirectCoat in allPasses and p == indirectCoat:
                                p.setSelected(True)
                                d = nuke.Node("Dot", inpanel = False)
                                d.setXYpos(d.xpos(), baseLine + 4 + distanceNum)
                                p.setSelected(False)
                                d.setSelected(False)
                                mergeNode.setInput(1, d)
                                self.shuffleIndexDict[d] = {}

                            if p == directTransmission and indirectTransmission not in allPasses:
                                p.setSelected(True)
                                mergeNode = nuke.Node("Merge2", inpanel = False)
                                mergeNode['operation'].setValue("plus")
                                mergeNode.setXYpos(p.xpos(), baseLine + distanceNum*2)
                                p.setSelected(False)
                                mergeNode.setSelected(False)
                                addLater.append((mergeNode, 3))
                            elif directTransmission in allPasses and p == directTransmission:
                                p.setSelected(True)
                                mergeNode = nuke.Node("Merge2", inpanel = False)
                                mergeNode['operation'].setValue("plus")
                                mergeNode.setXYpos(p.xpos(), baseLine + distanceNum)
                                mergeNode.setInput(0, p)
                                p.setSelected(False)
                                mergeNode.setSelected(False)
                                merges_firstLayer.append((mergeNode, 3))
                            elif indirectTransmission in allPasses and p == indirectTransmission:
                                p.setSelected(True)
                                d = nuke.Node("Dot", inpanel = False)
                                d.setXYpos(d.xpos(), baseLine + 4 + distanceNum)
                                p.setSelected(False)
                                d.setSelected(False)
                                mergeNode.setInput(1, d)
                                self.shuffleIndexDict[d] = {}

                            if p == directSss and indirectSss not in allPasses:
                                p.setSelected(True)
                                mergeNode = nuke.Node("Merge2", inpanel = False)
                                mergeNode['operation'].setValue("plus")
                                mergeNode.setXYpos(p.xpos(), baseLine + distanceNum*2)
                                p.setSelected(False)
                                mergeNode.setSelected(False)
                                addLater.append((mergeNode, 4))
                            elif directSss in allPasses and p == directSss:
                                p.setSelected(True)
                                mergeNode = nuke.Node("Merge2", inpanel = False)
                                mergeNode['operation'].setValue("plus")
                                mergeNode.setXYpos(p.xpos(), baseLine + distanceNum)
                                mergeNode.setInput(0, p)
                                p.setSelected(False)
                                mergeNode.setSelected(False)
                                merges_firstLayer.append((mergeNode, 4))
                            elif indirectSss in allPasses and p == indirectSss:
                                p.setSelected(True)
                                d = nuke.Node("Dot", inpanel = False)
                                d.setXYpos(d.xpos(), baseLine + 4 + distanceNum)
                                p.setSelected(False)
                                d.setSelected(False)
                                mergeNode.setInput(1, d)
                                self.shuffleIndexDict[d] = {}

                            if p == directVolume and indirectVolume not in allPasses:
                                p.setSelected(True)
                                mergeNode = nuke.Node("Merge2", inpanel = False)
                                mergeNode['operation'].setValue("plus")
                                mergeNode.setXYpos(p.xpos(), baseLine + distanceNum*2)
                                p.setSelected(False)
                                mergeNode.setSelected(False)
                                addLater.append((mergeNode, 5))
                            elif directVolume in allPasses and p == directVolume:
                                p.setSelected(True)
                                mergeNode = nuke.Node("Merge2", inpanel = False)
                                mergeNode['operation'].setValue("plus")
                                mergeNode.setXYpos(p.xpos(), baseLine + distanceNum)
                                mergeNode.setInput(0, p)
                                p.setSelected(False)
                                mergeNode.setSelected(False)
                                merges_firstLayer.append((mergeNode, 5))
                            elif indirectVolume in allPasses and p == indirectVolume:
                                p.setSelected(True)
                                d = nuke.Node("Dot", inpanel = False)
                                d.setXYpos(d.xpos(), baseLine + 4 + distanceNum)
                                p.setSelected(False)
                                d.setSelected(False)
                                mergeNode.setInput(1, d)
                                self.shuffleIndexDict[d] = {}

                            if emission in allPasses and p == emission:
                                p.setSelected(True)
                                mergeNode = nuke.Node("Merge2", inpanel = False)
                                mergeNode['operation'].setValue("plus")
                                mergeNode.setXYpos(p.xpos(), baseLine + distanceNum*2)
                                p.setSelected(False)
                                mergeNode.setSelected(False)
                                addLater.append((mergeNode, 6))

                    merges_secondLayer = []

                    for mer, ind in merges_firstLayer:
                        if ind == 0:
                            continue
                        else:
                            mer.setSelected(True)
                            newMerge = nuke.Node("Merge2", inpanel = False)
                            newMerge['operation'].setValue("plus")
                            newMerge.setXYpos(mer.xpos(), mer.ypos() + distanceNum)
                            mer.setSelected(False)
                            newMerge.setSelected(False)
                            merges_secondLayer.append((newMerge, ind))

                    merges_secondLayer.extend(addLater)

                    merges_secondLayer = sorted(merges_secondLayer, key = itemgetter(1))

                    # Reorder the merges_secondLayer list to ensure whatever remains
                    # has the correct ordered index.
                    reorderedMerges_secondLayer = []

                    for t in merges_secondLayer:
                        reorderedMerges_secondLayer.append((t[0], merges_secondLayer.index(t)))

                    # Create a temp guide dict.
                    quickDict = {}

                    for k, i in reorderedMerges_secondLayer:
                        quickDict[i] = k

                    # Final input connections.
                    for node, ind in reorderedMerges_secondLayer:
                        if node.Class() == "Merge2" and not ind == 0:
                            node.setInput(0, quickDict[ind-1])

                    # Add newly created items to shuffleIndexDict.
                    for item, i in merges_firstLayer:
                        self.shuffleIndexDict[item] = {}
                    for it, i in reorderedMerges_secondLayer:
                        self.shuffleIndexDict[it] = {}

                    return newMerge
                
                elif direction == "Vertical":
                    for p in allPasses:
                        if not p == "None" and self.shuffleIndexDict[p]["section"] == str(self.lineEdit_mainPassesTitle_input.text()):
                            if p == directDiffuse and indirectDiffuse not in allPasses:
                                merges_firstLayer.append((p, 0))
                            elif directDiffuse in allPasses and p == directDiffuse:
                                p.setSelected(True)
                                mergeNode = nuke.Node("Merge2", inpanel = False)
                                mergeNode['operation'].setValue("plus")
                                mergeNode.setXYpos(p.xpos(), baseLine + distanceNum)
                                nukescripts.swapAB(mergeNode)
                                p.setSelected(False)
                                mergeNode.setSelected(False)
                                merges_firstLayer.append((mergeNode, 0))
                            elif indirectDiffuse in allPasses and p == indirectDiffuse:
                                p.setSelected(True)
                                d = nuke.Node("Dot", inpanel = False)
                                d.setXYpos(d.xpos(), baseLine + 4 + distanceNum)
                                p.setSelected(False)
                                d.setSelected(False)
                                mergeNode.setInput(1, d)
                                self.shuffleIndexDict[d] = {}

                            if p == directSpecular and indirectSpecular not in allPasses:
                                merges_firstLayer.append((p, 1))
                            elif directSpecular in allPasses and p == directSpecular:
                                p.setSelected(True)
                                mergeNode = nuke.Node("Merge2", inpanel = False)
                                mergeNode['operation'].setValue("plus")
                                mergeNode.setXYpos(p.xpos(), baseLine + distanceNum)
                                nukescripts.swapAB(mergeNode)
                                p.setSelected(False)
                                mergeNode.setSelected(False)
                                merges_firstLayer.append((mergeNode, 1))
                            elif indirectSpecular in allPasses and p == indirectSpecular:
                                p.setSelected(True)
                                d = nuke.Node("Dot", inpanel = False)
                                d.setXYpos(d.xpos(), baseLine + 4 + distanceNum)
                                p.setSelected(False)
                                d.setSelected(False)
                                mergeNode.setInput(1, d)
                                self.shuffleIndexDict[d] = {}

                            if p == directCoat and indirectCoat not in allPasses:
                                merges_firstLayer.append((p, 2))
                            elif directCoat in allPasses and p == directCoat:
                                p.setSelected(True)
                                mergeNode = nuke.Node("Merge2", inpanel = False)
                                mergeNode['operation'].setValue("plus")
                                mergeNode.setXYpos(p.xpos(), baseLine + distanceNum)
                                nukescripts.swapAB(mergeNode)
                                p.setSelected(False)
                                mergeNode.setSelected(False)
                                merges_firstLayer.append((mergeNode, 2))
                            elif indirectCoat in allPasses and p == indirectCoat:
                                p.setSelected(True)
                                d = nuke.Node("Dot", inpanel = False)
                                d.setXYpos(d.xpos(), baseLine + 4 + distanceNum)
                                p.setSelected(False)
                                d.setSelected(False)
                                mergeNode.setInput(1, d)
                                self.shuffleIndexDict[d] = {}

                            if p == directTransmission and indirectTransmission not in allPasses:
                                merges_firstLayer.append((p, 3))
                            elif directTransmission in allPasses and p == directTransmission:
                                p.setSelected(True)
                                mergeNode = nuke.Node("Merge2", inpanel = False)
                                mergeNode['operation'].setValue("plus")
                                mergeNode.setXYpos(p.xpos(), baseLine + distanceNum)
                                nukescripts.swapAB(mergeNode)
                                p.setSelected(False)
                                mergeNode.setSelected(False)
                                merges_firstLayer.append((mergeNode, 3))
                            elif indirectTransmission in allPasses and p == indirectTransmission:
                                p.setSelected(True)
                                d = nuke.Node("Dot", inpanel = False)
                                d.setXYpos(d.xpos(), baseLine + 4 + distanceNum)
                                p.setSelected(False)
                                d.setSelected(False)
                                mergeNode.setInput(1, d)
                                self.shuffleIndexDict[d] = {}

                            if p == directSss and indirectSss not in allPasses:
                                merges_firstLayer.append((p, 4))
                            elif directSss in allPasses and p == directSss:
                                p.setSelected(True)
                                mergeNode = nuke.Node("Merge2", inpanel = False)
                                mergeNode['operation'].setValue("plus")
                                mergeNode.setXYpos(p.xpos(), baseLine + distanceNum)
                                nukescripts.swapAB(mergeNode)
                                p.setSelected(False)
                                mergeNode.setSelected(False)
                                merges_firstLayer.append((mergeNode, 4))
                            elif indirectSss in allPasses and p == indirectSss:
                                p.setSelected(True)
                                d = nuke.Node("Dot", inpanel = False)
                                d.setXYpos(d.xpos(), baseLine + 4 + distanceNum)
                                p.setSelected(False)
                                d.setSelected(False)
                                mergeNode.setInput(1, d)
                                self.shuffleIndexDict[d] = {}

                            if p == directVolume and indirectVolume not in allPasses:
                                merges_firstLayer.append((p, 5))
                            elif directVolume in allPasses and p == directVolume:
                                p.setSelected(True)
                                mergeNode = nuke.Node("Merge2", inpanel = False)
                                mergeNode['operation'].setValue("plus")
                                mergeNode.setXYpos(p.xpos(), baseLine + distanceNum)
                                nukescripts.swapAB(mergeNode)
                                p.setSelected(False)
                                mergeNode.setSelected(False)
                                merges_firstLayer.append((mergeNode, 5))
                            elif indirectVolume in allPasses and p == indirectVolume:
                                p.setSelected(True)
                                d = nuke.Node("Dot", inpanel = False)
                                d.setXYpos(d.xpos(), baseLine + 4 + distanceNum)
                                p.setSelected(False)
                                d.setSelected(False)
                                mergeNode.setInput(1, d)
                                self.shuffleIndexDict[d] = {}

                            if emission in allPasses and p == emission:
                                merges_firstLayer.append((p, 6))

                    # Add newly created items to shuffleIndexDict.
                    for item, i in merges_firstLayer:
                        self.shuffleIndexDict[item] = {}

                    for mer, ind in merges_firstLayer:
                        if ind == 0:
                            mer.setSelected(True)
                            newMerge = nuke.Node("Merge2", inpanel = False)
                            newMerge['operation'].setValue("plus")
                            nukescripts.swapAB(newMerge)
                            if mer.Class() == "Shuffle2":
                                newMerge.setXYpos(mer.xpos(), mer.ypos() + distanceNum*2)
                            else:
                                newMerge.setXYpos(mer.xpos(), mer.ypos() + distanceNum)
                            mer.setSelected(False)
                            # Add newly created Merges to shuffleIndexDict.
                            self.shuffleIndexDict[newMerge] = {}
                        else:
                            newMerge.connectInput(1, mer)
                            xPos = newMerge.xpos()
                            yPos = newMerge.ypos()
                            newMerge.setSelected(False)
                            mer.setSelected(True)
                            newDot = nuke.Node("Dot", inpanel = False)
                            newDot.setXYpos(newDot.xpos(), yPos + 4)
                            newDot.setSelected(False)
                            mer.setSelected(False)
                            newMerge.setSelected(True)

                            # Add newly created Dots to shuffleIndexDict.
                            self.shuffleIndexDict[newDot] = {}

                            if ind < len(merges_firstLayer) - 1:
                                newMerge = nuke.Node("Merge2", inpanel = False)
                                newMerge['operation'].setValue("plus")
                                newMerge.setXYpos(xPos, yPos + distanceNum)
                                nukescripts.swapAB(newMerge)
                                # Add newly created Merges to shuffleIndexDict.
                                self.shuffleIndexDict[newMerge] = {}

                    return newMerge

            if mode == "secondary":
                # Prepare for rebuild.
                direct = str(self.comboBox_direct.currentText())
                indirect = str(self.comboBox_indirect.currentText())
                emissionSecondary = str(self.comboBox_emissionSecondary.currentText())

                # Replace the variables above with their corresponding node pointers.
                for n in self.shuffleIndexDict:
                    if n.Class() == "Shuffle2":
                        replaceWith = self.findLastConnected(n)

                        if n['in'].value() == direct:
                            direct = replaceWith
                        elif n['in'].value() == indirect:
                            indirect = replaceWith
                        elif n['in'].value() == emissionSecondary:
                            emissionSecondary = replaceWith

                allPasses_initial = [direct, indirect, emissionSecondary]

                allPasses = allPasses_initial[:]

                for elem in allPasses_initial:
                    try:
                        nuke.exists(elem.name())
                    except:
                        allPasses.remove(elem)

                # Clear selection.
                for n in nuke.selectedNodes():
                    n.setSelected(False)

                merges = []

                # Rebuild.
                if direction == "Horizontal":
                    for p in allPasses:
                        if not p == "None" and self.shuffleIndexDict[p]["section"] == str(self.lineEdit_mainPassesTitle_input.text()):
                            if p == direct:
                                p.setSelected(True)
                                d = nuke.Node("Dot", inpanel = False)
                                d.setXYpos(d.xpos(), baseLine + 4 + distanceNum)
                                p.setSelected(False)
                                d.setSelected(False)
                                merges.append((d, 0))

                            elif p == indirect:
                                p.setSelected(True)
                                mergeNode = nuke.Node("Merge2", inpanel = False)
                                mergeNode['operation'].setValue("plus")
                                mergeNode.setXYpos(p.xpos(), baseLine + distanceNum)
                                p.setSelected(False)
                                mergeNode.setSelected(False)
                                merges.append((mergeNode, 1))

                            elif emissionSecondary in allPasses and p == emissionSecondary:
                                p.setSelected(True)
                                mergeNode = nuke.Node("Merge2", inpanel = False)
                                mergeNode['operation'].setValue("plus")
                                mergeNode.setXYpos(p.xpos(), baseLine + distanceNum)
                                p.setSelected(False)
                                mergeNode.setSelected(False)
                                merges.append((mergeNode, 2))
                
                elif direction == "Vertical":
                    for ind, p in enumerate(allPasses):
                        if not p == "None":
                            if ind == 0:
                                p.setSelected(True)
                                mergeNode = nuke.Node("Merge2", inpanel = False)
                                mergeNode['operation'].setValue("plus")
                                mergeNode.setXYpos(p.xpos(), baseLine + distanceNum)
                                nukescripts.swapAB(mergeNode)
                                p.setSelected(False)
                                mergeNode.setSelected(False)
                                self.shuffleIndexDict[mergeNode] = {}
                            else:
                                mergeNode.setInput(1, p)
                                xPos = mergeNode.xpos()
                                yPos = mergeNode.ypos()
                                mergeNode.setSelected(False)
                                p.setSelected(True)
                                d = nuke.Node("Dot", inpanel = False)
                                d.setXYpos(d.xpos(), yPos + 4)
                                p.setSelected(False)
                                d.setSelected(False)
                                mergeNode.setSelected(True)

                                # Add newly created Dots to shuffleIndexDict.
                                self.shuffleIndexDict[d] = {}

                                if ind < len(allPasses) - 1:
                                    mergeNode = nuke.Node("Merge2", inpanel = False)
                                    mergeNode['operation'].setValue("plus")
                                    mergeNode.setXYpos(xPos, yPos + distanceNum)
                                    nukescripts.swapAB(mergeNode)
                                    # Add newly created Merges to shuffleIndexDict.
                                    self.shuffleIndexDict[mergeNode] = {}
                    return mergeNode

                merges = sorted(merges, key = itemgetter(1))

                # Reorder the merges list to ensure whatever remains
                # has the correct ordered index.
                reorderedMerges = []

                for t in merges:
                    reorderedMerges.append((t[0], merges.index(t)))

                quickDict = {}

                for k, i in reorderedMerges:
                    quickDict[i] = k

                for m, ind in reorderedMerges:
                    if m.Class() == "Merge2" and not ind == 0:
                        m.setInput(0, quickDict[ind-1])

                # Add newly created items to shuffleIndexDict.
                for item, i in reorderedMerges:
                    self.shuffleIndexDict[item] = {}

                return mergeNode

        elif renderer == "VRay":
            if mode == "advanced":
                # Prepare for rebuild.
                diffuseFilter = str(self.comboBox_diffuseFilter.currentText())
                rawLighting = str(self.comboBox_rawLighting.currentText())
                rawGi = str(self.comboBox_rawGi.currentText())
                rawReflection = str(self.comboBox_rawReflection.currentText())
                reflectionFilter = str(self.comboBox_reflectionFilter.currentText())
                rawRefraction = str(self.comboBox_rawRefraction.currentText())
                refractionFilter = str(self.comboBox_refractionFilter.currentText())
                specularAdvanced = str(self.comboBox_specularAdvanced.currentText())
                sss2advanced = str(self.comboBox_sss2advanced.currentText())
                selfIlluminationAdvanced = str(self.comboBox_selfIlluminationAdvanced.currentText())
                causticsAdvanced = str(self.comboBox_causticsAdvanced.currentText())
                atmosphereAdvanced = str(self.comboBox_atmosphereAdvanced.currentText())

                # Replace the variables above with their corresponding node pointers.
                for n in self.shuffleIndexDict:
                    if n.Class() == "Shuffle2":
                        replaceWith = self.findLastConnected(n)

                        if n['in'].value() == diffuseFilter:
                            diffuseFilter = replaceWith
                        elif n['in'].value() == rawLighting:
                            rawLighting = replaceWith
                        elif n['in'].value() == rawGi:
                            rawGi = replaceWith
                        elif n['in'].value() == rawReflection:
                            rawReflection = replaceWith
                        elif n['in'].value() == reflectionFilter:
                            reflectionFilter = replaceWith
                        elif n['in'].value() == rawRefraction:
                            rawRefraction = replaceWith
                        elif n['in'].value() == refractionFilter:
                            refractionFilter = replaceWith
                        elif n['in'].value() == specularAdvanced:
                            specularAdvanced = replaceWith
                        elif n['in'].value() == sss2advanced:
                            sss2advanced = replaceWith
                        elif n['in'].value() == selfIlluminationAdvanced:
                            selfIlluminationAdvanced = replaceWith
                        elif n['in'].value() == causticsAdvanced:
                            causticsAdvanced = replaceWith
                        elif n['in'].value() == atmosphereAdvanced:
                            atmosphereAdvanced = replaceWith

                allPasses_initial = [diffuseFilter, rawLighting, rawGi, rawReflection, reflectionFilter,
                                    rawRefraction, refractionFilter, specularAdvanced, sss2advanced,
                                    selfIlluminationAdvanced, causticsAdvanced, atmosphereAdvanced]
                allPasses = allPasses_initial[:]

                for elem in allPasses_initial:
                    try:
                        nuke.exists(elem.name())
                    except:
                        allPasses.remove(elem)

                merges_firstLayer = []
                merges_secondLayer = []

                # Clear selection.
                for n in nuke.selectedNodes():
                    n.setSelected(False)

                # Rebuild.
                if direction == "Horizontal":
                    for p in allPasses:
                        if self.shuffleIndexDict[p]["section"] == str(self.lineEdit_mainPassesTitle_input.text()):
                            if p == diffuseFilter and not p == "None":
                                p.setSelected(True)
                                d = nuke.Node("Dot", inpanel = False)
                                d.setXYpos(d.xpos(), baseLine + 4 + distanceNum*2)
                                p.setSelected(False)
                                d.setSelected(False)
                                merges_secondLayer.append((d, 0))
                            elif p == diffuseFilter and p == "None":
                                continue

                            elif p == rawLighting:
                                if rawLighting == "None":
                                    nuke.message("Raw Lighting is set to \"None\"!")
                                    return
                                elif diffuseFilter == "None":
                                    p.setSelected(True)
                                    d = nuke.Node("Dot", inpanel = False)
                                    d.setXYpos(d.xpos(), baseLine + 4 + distanceNum*2)
                                    p.setSelected(False)
                                    d.setSelected(False)
                                    merges_secondLayer.append((d, 0))
                                elif not diffuseFilter == "None":
                                    p.setSelected(True)
                                    rawLightingDot = nuke.Node("Dot", inpanel = False)
                                    rawLightingDot.setXYpos(rawLightingDot.xpos(), baseLine + 4 + distanceNum)
                                    p.setSelected(False)
                                    rawLightingDot.setSelected(False)
                                    self.shuffleIndexDict[rawLightingDot] = {}

                            elif p == rawGi:
                                if rawGi == "None":
                                    nuke.message("Raw Global Illumination is set to \"None\"!")
                                    return
                                elif diffuseFilter == "None":
                                    p.setSelected(True)
                                    mergeNode = nuke.Node("Merge2", inpanel = False)
                                    mergeNode['operation'].setValue("plus")
                                    mergeNode.setXYpos(p.xpos(), baseLine + distanceNum*2)
                                    p.setSelected(False)
                                    mergeNode.setSelected(False)
                                    merges_secondLayer.append((mergeNode, 1))
                                elif not diffuseFilter == "None":
                                    p.setSelected(True)
                                    mergeNode = nuke.Node("Merge2", inpanel = False)
                                    mergeNode['operation'].setValue("plus")
                                    mergeNode.setXYpos(p.xpos(), baseLine + distanceNum)
                                    mergeNode.setInput(0, p)
                                    mergeNode.setInput(1, rawLightingDot)
                                    p.setSelected(False)
                                    mergeNode.setSelected(False)
                                    merges_firstLayer.append((mergeNode, 0))

                            elif p == rawReflection:
                                if not reflectionFilter == "None":
                                    rawReflection.setSelected(True)
                                    rawReflectionDot = nuke.Node("Dot", inpanel = False)
                                    rawReflectionDot.setXYpos(rawReflectionDot.xpos(), baseLine + 4 + distanceNum)
                                    rawReflection.setSelected(False)
                                    rawReflectionDot.setSelected(False)
                                    self.shuffleIndexDict[rawReflectionDot] = {}

                                    reflectionFilter.setSelected(True)
                                    mergeNode = nuke.Node("Merge2", inpanel = False)
                                    mergeNode['operation'].setValue("multiply")
                                    mergeNode.setXYpos(reflectionFilter.xpos(), baseLine + distanceNum)
                                    mergeNode.setInput(0, reflectionFilter)
                                    mergeNode.setInput(1, rawReflectionDot)
                                    mergeNode.setSelected(False)
                                    reflectionFilter.setSelected(False)
                                    merges_firstLayer.append((mergeNode, 1))
                                else:
                                    p.setSelected(True)
                                    mergeNode = nuke.Node("Merge2", inpanel = False)
                                    mergeNode['operation'].setValue("plus")
                                    mergeNode.setXYpos(p.xpos(), baseLine + distanceNum*2)
                                    mergeNode.setSelected(False)
                                    p.setSelected(False)
                                    merges_secondLayer.append((mergeNode, 2))

                            elif p == rawRefraction:
                                if not refractionFilter == "None":
                                    rawRefraction.setSelected(True)
                                    rawRefractionDot = nuke.Node("Dot", inpanel = False)
                                    rawRefractionDot.setXYpos(rawRefractionDot.xpos(), baseLine + 4 + distanceNum)
                                    rawRefraction.setSelected(False)
                                    rawRefractionDot.setSelected(False)
                                    self.shuffleIndexDict[rawRefractionDot] = {}

                                    refractionFilter.setSelected(True)
                                    mergeNode = nuke.Node("Merge2", inpanel = False)
                                    mergeNode['operation'].setValue("multiply")
                                    mergeNode.setXYpos(refractionFilter.xpos(), baseLine + distanceNum)
                                    mergeNode.setInput(0, refractionFilter)
                                    mergeNode.setInput(1, rawRefractionDot)
                                    mergeNode.setSelected(False)
                                    refractionFilter.setSelected(False)
                                    merges_firstLayer.append((mergeNode, 2))
                                else:
                                    p.setSelected(True)
                                    mergeNode = nuke.Node("Merge2", inpanel = False)
                                    mergeNode['operation'].setValue("plus")
                                    mergeNode.setXYpos(p.xpos(), baseLine + distanceNum*2)
                                    mergeNode.setSelected(False)
                                    p.setSelected(False)
                                    merges_secondLayer.append((mergeNode, 3))

                            else:
                                if p == "None" or p == reflectionFilter or p == refractionFilter:
                                    continue
                                else:
                                    p.setSelected(True)
                                    mergeNode = nuke.Node("Merge2", inpanel = False)
                                    mergeNode['operation'].setValue("plus")
                                    mergeNode.setXYpos(p.xpos(), baseLine + distanceNum*2)
                                    p.setSelected(False)
                                    mergeNode.setSelected(False)    

                                    if p == specularAdvanced:
                                        merges_secondLayer.append((mergeNode, 4))

                                    elif p == sss2advanced:
                                        merges_secondLayer.append((mergeNode, 5))

                                    elif p == selfIlluminationAdvanced:
                                        merges_secondLayer.append((mergeNode, 6))

                                    elif p == causticsAdvanced:
                                        merges_secondLayer.append((mergeNode, 7))

                                    elif p == atmosphereAdvanced:
                                        merges_secondLayer.append((mergeNode, 8))

                elif direction == "Vertical":
                    for p in allPasses:
                        if self.shuffleIndexDict[p]["section"] == str(self.lineEdit_mainPassesTitle_input.text()):
                            if p == diffuseFilter and not p == "None":
                                merges_firstLayer.append((p, 0))
                            elif p == diffuseFilter and p == "None":
                                continue

                            elif p == rawLighting:
                                if rawLighting == "None":
                                    nuke.message("Raw Lighting is set to \"None\"!")
                                    return
                                elif diffuseFilter == "None":
                                    merges_firstLayer.append((p, 0))
                                elif not diffuseFilter == "None":
                                    p.setSelected(True)
                                    rawLightingDot = nuke.Node("Dot", inpanel = False)
                                    rawLightingDot.setXYpos(rawLightingDot.xpos(), baseLine + 4 + distanceNum)
                                    p.setSelected(False)
                                    rawLightingDot.setSelected(False)
                                    self.shuffleIndexDict[rawLightingDot] = {}

                            elif p == rawGi:
                                if rawGi == "None":
                                    nuke.message("Raw Global Illumination is set to \"None\"!")
                                    return
                                elif diffuseFilter == "None":
                                    merges_firstLayer.append((p, 1))
                                elif not diffuseFilter == "None":
                                    p.setSelected(True)
                                    mergeNode = nuke.Node("Merge2", inpanel = False)
                                    mergeNode['operation'].setValue("plus")
                                    mergeNode.setXYpos(p.xpos(), baseLine + distanceNum)
                                    nukescripts.swapAB(mergeNode)
                                    mergeNode.setInput(1, rawLightingDot)
                                    p.setSelected(False)
                                    mergeNode.setSelected(False)
                                    merges_firstLayer.append((mergeNode, 1))

                            elif p == rawReflection:
                                if not reflectionFilter == "None":
                                    rawReflection.setSelected(True)
                                    rawReflectionDot = nuke.Node("Dot", inpanel = False)
                                    rawReflectionDot.setXYpos(rawReflectionDot.xpos(), baseLine + 4 + distanceNum)
                                    rawReflection.setSelected(False)
                                    rawReflectionDot.setSelected(False)
                                    self.shuffleIndexDict[rawReflectionDot] = {}

                                    reflectionFilter.setSelected(True)
                                    mergeNode = nuke.Node("Merge2", inpanel = False)
                                    mergeNode['operation'].setValue("multiply")
                                    mergeNode.setXYpos(reflectionFilter.xpos(), baseLine + distanceNum)
                                    nukescripts.swapAB(mergeNode)
                                    mergeNode.setInput(1, rawReflectionDot)
                                    mergeNode.setSelected(False)
                                    reflectionFilter.setSelected(False)
                                    merges_firstLayer.append((mergeNode, 2))
                                else:
                                    merges_firstLayer.append((p, 2))

                            elif p == rawRefraction:
                                if not refractionFilter == "None":
                                    rawRefraction.setSelected(True)
                                    rawRefractionDot = nuke.Node("Dot", inpanel = False)
                                    rawRefractionDot.setXYpos(rawRefractionDot.xpos(), baseLine + 4 + distanceNum)
                                    rawRefraction.setSelected(False)
                                    rawRefractionDot.setSelected(False)
                                    self.shuffleIndexDict[rawRefractionDot] = {}

                                    refractionFilter.setSelected(True)
                                    mergeNode = nuke.Node("Merge2", inpanel = False)
                                    mergeNode['operation'].setValue("multiply")
                                    mergeNode.setXYpos(refractionFilter.xpos(), baseLine + distanceNum)
                                    mergeNode.setInput(0, refractionFilter)
                                    mergeNode.setInput(1, rawRefractionDot)
                                    mergeNode.setSelected(False)
                                    refractionFilter.setSelected(False)
                                    merges_firstLayer.append((mergeNode, 3))
                                else:
                                    merges_firstLayer.append((p, 3))

                            else:
                                if p == "None" or p == reflectionFilter or p == refractionFilter:
                                    continue
                                else:
                                    if p == specularAdvanced:
                                        merges_firstLayer.append((p, 4))

                                    elif p == sss2advanced:
                                        merges_firstLayer.append((p, 5))

                                    elif p == selfIlluminationAdvanced:
                                        merges_firstLayer.append((p, 6))

                                    elif p == causticsAdvanced:
                                        merges_firstLayer.append((p, 7))

                                    elif p == atmosphereAdvanced:
                                        merges_firstLayer.append((p, 8))

                    for mer, i in merges_firstLayer:
                        if i == 0:
                            mer.setSelected(True)
                            mergeNode = nuke.Node("Merge2", inpanel = False)

                            if diffuseFilter and mer == diffuseFilter:
                                mergeNode['operation'].setValue("multiply")
                            else:
                                mergeNode['operation'].setValue("plus")

                            mergeNode.setXYpos(mer.xpos(), baseLine + distanceNum*2)
                            nukescripts.swapAB(mergeNode)

                            # Add newly created Merges to shuffleIndexDict.
                            self.shuffleIndexDict[mergeNode] = {}
                        else:
                            mergeNode.connectInput(1, mer)
                            xPos = mergeNode.xpos()
                            yPos = mergeNode.ypos()
                            mergeNode.setSelected(False)
                            mer.setSelected(True)
                            newDot = nuke.Node("Dot", inpanel = False)
                            newDot.setXYpos(newDot.xpos(), yPos + 4)
                            newDot.setSelected(False)
                            mer.setSelected(False)
                            mergeNode.setSelected(True)

                            # Add newly created Dots to shuffleIndexDict.
                            self.shuffleIndexDict[newDot] = {}

                            if i < len(merges_firstLayer) - 1:
                                mergeNode = nuke.Node("Merge2", inpanel = False)
                                mergeNode['operation'].setValue("plus")
                                mergeNode.setXYpos(xPos, yPos + distanceNum)
                                nukescripts.swapAB(mergeNode)

                                # Add newly created Merges to shuffleIndexDict.
                                self.shuffleIndexDict[mergeNode] = {}

                            if mer.Class() == "Merge2":
                                self.shuffleIndexDict[mer] = {}
                    return mergeNode

                for mer, i in merges_firstLayer:
                    mer.setSelected(True)
                    mergeNode = nuke.Node("Merge2", inpanel = False)

                    if diffuseFilter and not diffuseFilter == "None" and i == 0:
                        mergeNode['operation'].setValue("multiply")
                    else:
                        mergeNode['operation'].setValue("plus")

                    mergeNode.setXYpos(mer.xpos(), mer.ypos() + distanceNum)
                    mergeNode.setSelected(False)
                    mer.setSelected(False)
                    merges_secondLayer.append((mergeNode, i))

                merges_secondLayer = sorted(merges_secondLayer, key = itemgetter(1))

                # Reorder the merges_secondLayer list to ensure whatever remains
                # has the correct ordered index.
                reorderedMerges = []
                for t in merges_secondLayer:
                    reorderedMerges.append((t[0], merges_secondLayer.index(t)))

                # Create a temp guide dict.
                quickDict = {}

                for k, i in reorderedMerges:
                    quickDict[i] = k

                for m, ind in reorderedMerges:
                    if m.Class() == "Merge2" and not ind == 0:
                        m.setInput(0, quickDict[ind-1])

                # Add newly created items to shuffleIndexDict.
                for item, i in merges_firstLayer:
                    self.shuffleIndexDict[item] = {}
                for it, i in reorderedMerges:
                    self.shuffleIndexDict[it] = {}

                lastMerge = max(reorderedMerges, key = itemgetter(1))[0]

                return lastMerge

            elif mode == "basic":
                # Prepare for rebuild.
                lighting = str(self.comboBox_lighting.currentText())
                gi = str(self.comboBox_gi.currentText())
                reflection = str(self.comboBox_reflection.currentText())
                refraction = str(self.comboBox_refraction.currentText())
                specularBasic = str(self.comboBox_specularBasic.currentText())
                sss2basic = str(self.comboBox_sss2basic.currentText())
                selfIlluminationBasic = str(self.comboBox_selfIlluminationBasic.currentText())
                causticsBasic = str(self.comboBox_causticsBasic.currentText())
                atmosphereBasic = str(self.comboBox_atmosphereBasic.currentText())

                # Replace the variables above with their corresponding node pointers.
                for n in self.shuffleIndexDict:
                    if n.Class() == "Shuffle2":
                        replaceWith = self.findLastConnected(n)

                        if n['in'].value() == lighting:
                            lighting = replaceWith
                        elif n['in'].value() == gi:
                            gi = replaceWith
                        elif n['in'].value() == reflection:
                            reflection = replaceWith
                        elif n['in'].value() == refraction:
                            refraction = replaceWith
                        elif n['in'].value() == specularBasic:
                            specularBasic = replaceWith
                        elif n['in'].value() == sss2basic:
                            sss2basic = replaceWith
                        elif n['in'].value() == selfIlluminationBasic:
                            selfIlluminationBasic = replaceWith
                        elif n['in'].value() == causticsBasic:
                            causticsBasic = replaceWith
                        elif n['in'].value() == atmosphereBasic:
                            atmosphereBasic = replaceWith

                allPasses_initial = [lighting, gi, reflection, refraction, specularBasic,
                                sss2basic, selfIlluminationBasic, causticsBasic, atmosphereBasic]
                allPasses = allPasses_initial[:]

                for elem in allPasses_initial:
                    try:
                        nuke.exists(elem.name())
                    except:
                        allPasses.remove(elem)

                # Clear selection.
                for n in nuke.selectedNodes():
                    n.setSelected(False)

                firstEncounter = ""
                merges = []

                # Rebuild.
                if direction == "Horizontal":
                    for p in allPasses:
                        if self.shuffleIndexDict[p]["section"] == str(self.lineEdit_mainPassesTitle_input.text()):
                            if p == "None":
                                continue
                            else:
                                # Remember the first encountered item that is not "None".
                                if not firstEncounter:
                                    firstEncounter = p

                                if p == lighting or p == firstEncounter:
                                    p.setSelected(True)
                                    d = nuke.Node("Dot", inpanel = False)
                                    d.setXYpos(d.xpos(), baseLine + 4 + distanceNum)
                                    p.setSelected(False)
                                    d.setSelected(False)
                                    merges.append((d, 0))
                                else:
                                    p.setSelected(True)
                                    mergeNode = nuke.Node("Merge2", inpanel = False)
                                    mergeNode['operation'].setValue("plus")
                                    mergeNode.setXYpos(p.xpos(), baseLine + distanceNum)
                                    p.setSelected(False)
                                    mergeNode.setSelected(False)

                                    if p == gi:
                                        merges.append((mergeNode, 1))

                                    elif p == reflection:
                                        merges.append((mergeNode, 2))

                                    elif p == refraction:
                                        merges.append((mergeNode, 3))

                                    elif p == specularBasic:
                                        merges.append((mergeNode, 4))

                                    elif p == sss2basic:
                                        merges.append((mergeNode, 5))

                                    elif p == selfIlluminationBasic:
                                        merges.append((mergeNode, 6))

                                    elif p == causticsBasic:
                                        merges.append((mergeNode, 7))

                                    elif p == atmosphereBasic:
                                        merges.append((mergeNode, 8))

                elif direction == "Vertical":
                    for p in allPasses:
                        if self.shuffleIndexDict[p]["section"] == str(self.lineEdit_mainPassesTitle_input.text()):
                            for ind, p in enumerate(allPasses):
                                if not p == "None":
                                    if ind == 0:
                                        p.setSelected(True)
                                        mergeNode = nuke.Node("Merge2", inpanel = False)
                                        mergeNode['operation'].setValue("plus")
                                        mergeNode.setXYpos(p.xpos(), baseLine + distanceNum)
                                        nukescripts.swapAB(mergeNode)
                                        p.setSelected(False)
                                        mergeNode.setSelected(False)
                                        self.shuffleIndexDict[mergeNode] = {}
                                    else:
                                        mergeNode.setInput(1, p)
                                        xPos = mergeNode.xpos()
                                        yPos = mergeNode.ypos()
                                        mergeNode.setSelected(False)
                                        p.setSelected(True)
                                        d = nuke.Node("Dot", inpanel = False)
                                        d.setXYpos(d.xpos(), yPos + 4)
                                        p.setSelected(False)
                                        d.setSelected(False)
                                        mergeNode.setSelected(True)

                                        # Add newly created Dots to shuffleIndexDict.
                                        self.shuffleIndexDict[d] = {}

                                        if ind < len(allPasses) - 1:
                                            mergeNode = nuke.Node("Merge2", inpanel = False)
                                            mergeNode['operation'].setValue("plus")
                                            mergeNode.setXYpos(xPos, yPos + distanceNum)
                                            nukescripts.swapAB(mergeNode)
                                            # Add newly created Merges to shuffleIndexDict.
                                            self.shuffleIndexDict[mergeNode] = {}
                            
                            return mergeNode

                # Reorder the merges list to ensure whatever remains
                # has the correct ordered index.
                reorderedMerges = []

                for t in merges:
                    reorderedMerges.append((t[0], merges.index(t)))

                # Create a temp guide dict.
                quickDict = {}

                for k, i in reorderedMerges:
                    quickDict[i] = k

                # Final input connections.
                for node, ind in reorderedMerges:
                    if node.Class() == "Merge2" and not ind == 0:
                        node.setInput(0, quickDict[ind-1])

                # Add newly created items to shuffleIndexDict.
                for item, i in reorderedMerges:
                    self.shuffleIndexDict[item] = {}

                return mergeNode

    def startShuffle(self):

        """
        This function serves as a wrapper for the relevant functions which perform the Shuffle.
        """

        targetedNode = nuke.toNode(str(self.label_selNode.text()))
        print(f"line 3123 {targetedNode}")

        try:
            nuke.exists(targetedNode.name())
        except:
            nuke.message("\"Selected Node\" no longer exists!")
            return

        # Clear the remembered base line for the Rebuild, so it'll correspond
        # to the new Shuffle.
        self.rebuildStart_highestY = 0

        # Save user's selection to restore at the end.
        startingSelection = nuke.selectedNodes()

        if not self.check_extendShuffled.isChecked():
            initialDot = self.shuffleLayers(targetedNode)
            initialIndex = 0

            # Add the first dot to shuffleIndexDict.
            self.shuffleIndexDict[initialDot] = {"shuffleIndex": initialIndex, "layerName": "initial_dot", "section": str(self.lineEdit_mainPassesTitle_input.text())}
        else:
            dotList = []

            if self.findLastConnected(targetedNode) == targetedNode:
                nuke.message("Extending failed - current Shuffle not found.")
                return

            if self.shuffleIndexDict:
                for node in self.shuffleIndexDict:
                    if node.Class() == "Dot":
                        try:
                            dotList.append((node, self.shuffleIndexDict[node]["shuffleIndex"]))
                        except KeyError:
                            pass

            if dotList:
                dotList = sorted(dotList, key = itemgetter(1))
                lastDot = max(dotList, key = itemgetter(1))[0]

                initialIndex = self.shuffleIndexDict[lastDot]["shuffleIndex"] + 1

                initialDot = self.shuffleLayers(lastDot, extending = True)

                # Add the first dot to shuffleIndexDict.
                self.shuffleIndexDict[initialDot] = {"shuffleIndex": initialIndex, "layerName": "initial_dot", "section": str(self.lineEdit_mainPassesTitle_input.text())}

        if self.check_useRebuild.isChecked():
            if str(self.comboBox_rendererSelectionDropdown.currentText()) == "Arnold":
                selectedRenderer = "Arnold"
                if self.radioBtn_primaryArnold.isChecked():
                    selectedMode = "primary"
                elif self.radioBtn_secondaryArnold.isChecked():
                    selectedMode = "secondary"
            elif str(self.comboBox_rendererSelectionDropdown.currentText()) == "VRay":
                selectedRenderer = "VRay"
                if self.radioBtn_advancedVray.isChecked():
                    selectedMode = "advanced"
                elif self.radioBtn_basicVray.isChecked():
                    selectedMode = "basic"
            else:
                return

            rebDir = str(self.comboBox_rebuildDirection.currentText())

            lastNode = self.rendererRebuild(selectedRenderer, selectedMode, direction = rebDir)
            
            # The following section of this 'if' statement creates
            # a Copy node after the Rebuild to transfer the original Alpha.
            if nuke.selectedNodes():
                for selected in nuke.selectedNodes():
                    selected.setSelected(False)

            xpos = initialDot.xpos()
            ypos = lastNode.ypos()

            intermediateDot = nuke.Node("Dot", inpanel = False)
            intermediateDot.setXYpos(xpos, ypos + 200 * self.distanceMult)
            intermediateDot.setInput(0, initialDot)

            alphaCopy = nuke.Node("Copy", inpanel = False)
            alphaCopy.setXYpos(lastNode.xpos(), intermediateDot.ypos() - 10)
            alphaCopy.setInput(0, intermediateDot)
            alphaCopy.setInput(1, lastNode)
            nukescripts.swapAB(alphaCopy)

            self.shuffleIndexDict[intermediateDot] = {}
            self.shuffleIndexDict[alphaCopy] = {}

        if self.check_extendShuffled.isChecked():
            # Combine the extension with the original Shuffle.
            self.shuffleIndexDict_newCopy = copy.copy(self.shuffleIndexDict)
            self.shuffleIndexDict = copy.copy(self.shuffleIndexDict_originalCopy)
            self.shuffleIndexDict.update(self.shuffleIndexDict_newCopy)

            del self.shuffleIndexDict_newCopy
            del self.shuffleIndexDict_originalCopy

        # Clear selection.
        for n in nuke.selectedNodes():
            n.setSelected(False)
        # Return to original user selection.
        for sel in reversed(startingSelection):
            sel.setSelected(True)





    # -----------------------------------------------------------------------------------------------------------------------
    # The rest, from here on, is the function definitions for passing the Signal connections
    # and the converted code from Qt Designer.
    # -----------------------------------------------------------------------------------------------------------------------

    def passSignalConnections(self):

        """
        Pass the relevant functions to their corresponding button or other widget
        when the UI is first created.
        """

        # Connect the button widgets' signals to actions.
        self.btn_updateTarget.clicked.connect(self.updateInformation)

        self.btn_mainPasses_selectAll.clicked.connect(lambda: self.selectAllBtn(self.listWidget_mainPasses))
        self.btn_aov_selectRemaining.clicked.connect(lambda: self.selectRemainingBtn(self.listWidget_aov, self.listWidget_mainPasses))
        self.btn_mainPasses_clearSel.clicked.connect(lambda: self.clearSelectionBtn(self.listWidget_mainPasses))
        self.btn_aov_clearSel.clicked.connect(lambda: self.clearSelectionBtn(self.listWidget_aov))
        self.btn_mainPasses_resetOrder.clicked.connect(lambda: self.resetCurrentOrderToDefault(self.listWidget_mainPasses))
        self.btn_aovs_resetOrder.clicked.connect(lambda: self.resetCurrentOrderToDefault(self.listWidget_aov))

        self.btn_selectColor.clicked.connect(self.setBackdropColor)

        self.btn_recreateNode.clicked.connect(lambda: self.recreateStoredNodeEntry_wrapper())
        self.btn_showInfo.clicked.connect(self.showInfo_forStoredNode_wrapper)
        self.btn_deleteEntry.clicked.connect(lambda: self.storedNodes_deletionHandler(mode = "entry"))
        self.btn_deleteAll.clicked.connect(lambda: self.storedNodes_deletionHandler(mode = "all"))
        self.btn_premultSandwich.clicked.connect(self.addPremultSandwich)

        self.btn_storeSelected.clicked.connect(self.storeSelectedNodes)
        self.btn_updateEntry.clicked.connect(self.updateEntry)

        self.btn_mainPassesSelection_selectAll.clicked.connect(lambda: self.selectAllBtn(self.listWidget_mainPassesSelection))
        self.btn_aovsSelection_selectAll.clicked.connect(lambda: self.selectAllBtn(self.listWidget_aovsSelection))
        self.btn_mainPassesSelection_clearSel.clicked.connect(lambda: self.clearSelectionBtn(self.listWidget_mainPassesSelection))
        self.btn_aovsSelection_clearSel.clicked.connect(lambda: self.clearSelectionBtn(self.listWidget_aovsSelection))

        self.btn_savePreset.clicked.connect(self.saveNodeTreePreset)
        self.btn_spawnPreset.clicked.connect(self.spawnNodeTreePreset)
        self.btn_deletePreset.clicked.connect(self.deleteNodeTreePreset)
        self.btn_selectLastSpawn.clicked.connect(self.selectSpawned)

        self.btn_shuffleAction.clicked.connect(self.startShuffle)
        self.btn_selectShuffled.clicked.connect(self.selectShuffled)

        # Connect list widgets' signals to actions.
        self.listWidget_storedNodes.itemDoubleClicked.connect(lambda i: self.showInfo_forStoredNode_wrapper(i))

        self.listWidget_storedNodes.itemSelectionChanged.connect(self.restoreLayerSelections)

        self.listWidget_mainPassesSelection.itemSelectionChanged.connect(self.saveLayerSelections)
        self.listWidget_aovsSelection.itemSelectionChanged.connect(self.saveLayerSelections)

        # Connect the Renderer Rebuild options widgets' signals to actions.
        self.comboBox_rendererSelectionDropdown.currentIndexChanged.connect(lambda index: self.changeRendererOptions(index))
        self.comboBox_rendererSelectionDropdown_alt.currentIndexChanged.connect(lambda index: self.changeRendererOptions(index))

        self.comboBox_rebuildDirection.currentIndexChanged.connect(lambda index: self.comboBox_rebuildDirection_alt.setCurrentIndex(index))
        self.comboBox_rebuildDirection_alt.currentIndexChanged.connect(lambda index: self.comboBox_rebuildDirection.setCurrentIndex(index))

        self.check_useRebuild.toggled.connect(lambda state: self.check_useRebuild_alt.setChecked(state))
        self.check_useRebuild_alt.toggled.connect(lambda state: self.check_useRebuild.setChecked(state))

        # Connect the Distance Mult widgets' signals to actions.
        self.numField_nodeDistanceMult.valueChanged.connect(lambda: self.distanceMultHandler(self.numField_nodeDistanceMult))
        self.slider_nodeDistanceMult.valueChanged.connect(lambda: self.distanceMultHandler(self.slider_nodeDistanceMult))

        # Connect the custom Layer lists' name fields' signals to handler.
        self.lineEdit_mainPassesTitle_input.editingFinished.connect(self.sectionNamesHandler)
        self.lineEdit_aovsTitle_input.editingFinished.connect(self.sectionNamesHandler)

        # Connect the "Add Nodes" update function for when the tab is selected.
        self.tabWidget.currentChanged.connect(self.update_tabInfo)

        # Connect the "Unlock ordering" function on checking of the relevant checkbox.
        self.check_unlockShuffleOrdering.toggled.connect(lambda state: self.unlockOrdering(state))

        # Connect preference saving.
        self.lineEdit_mainPassesTitle_input.editingFinished.connect(lambda: self.savePreferences(self, self.lineEdit_mainPassesTitle_input.objectName()))
        self.lineEdit_aovsTitle_input.editingFinished.connect(lambda: self.savePreferences(self, self.lineEdit_aovsTitle_input.objectName()))

        self.btn_mainPasses_resetOrder.clicked.connect(lambda: self.savePreferences(self, self.btn_mainPasses_resetOrder.objectName()))
        self.btn_aovs_resetOrder.clicked.connect(lambda: self.savePreferences(self, self.btn_aovs_resetOrder.objectName()))

        self.check_removeExrRestriction.toggled.connect(lambda: self.savePreferences(self, self.check_removeExrRestriction.objectName()))
        self.check_selectionOnly.toggled.connect(lambda: self.savePreferences(self, self.check_selectionOnly.objectName()))
        self.check_unlockShuffleOrdering.toggled.connect(lambda: self.savePreferences(self, self.check_unlockShuffleOrdering.objectName()))

        self.btn_selectColor.clicked.connect(lambda: self.savePreferences(self, self.btn_selectColor.objectName()))

        self.comboBox_rebuildDirection.currentIndexChanged.connect(lambda: self.savePreferences(self, self.comboBox_rebuildDirection.objectName()))
        self.comboBox_rendererSelectionDropdown.currentIndexChanged.connect(lambda: self.savePreferences(self, self.comboBox_rendererSelectionDropdown.objectName()))

        self.numField_nodeDistanceMult.valueChanged.connect(lambda: self.savePreferences(self, self.numField_nodeDistanceMult.objectName()))
        self.slider_nodeDistanceMult.sliderReleased.connect(lambda: self.savePreferences(self, self.slider_nodeDistanceMult.objectName()))

    def setupUi(self, LayerShufflerWin):
        LayerShufflerWin.setObjectName("LayerShufflerWin")
        LayerShufflerWin.resize(451, 719)
        LayerShufflerWin.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.centralwidget = QtGui.QWidget(LayerShufflerWin)
        self.centralwidget.setEnabled(True)
        self.centralwidget.setMouseTracking(False)
        self.centralwidget.setAutoFillBackground(False)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_3 = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.shuffleAction_mainLayoutBottom = QtGui.QHBoxLayout()
        self.shuffleAction_mainLayoutBottom.setObjectName("shuffleAction_mainLayoutBottom")
        self.shuffleAction_layout = QtGui.QGridLayout()
        self.shuffleAction_layout.setSizeConstraint(QtGui.QLayout.SetFixedSize)
        self.shuffleAction_layout.setObjectName("shuffleAction_layout")
        self.check_removeExrRestriction = QtGui.QCheckBox(self.centralwidget)
        self.check_removeExrRestriction.setObjectName("check_removeExrRestriction")
        self.shuffleAction_layout.addWidget(self.check_removeExrRestriction, 2, 2, 1, 1)
        self.check_extendShuffled = QtGui.QCheckBox(self.centralwidget)
        self.check_extendShuffled.setObjectName("check_extendShuffled")
        self.shuffleAction_layout.addWidget(self.check_extendShuffled, 2, 1, 1, 1)
        self.btn_selectShuffled = QtGui.QPushButton(self.centralwidget)
        self.btn_selectShuffled.setObjectName("btn_selectShuffled")
        self.shuffleAction_layout.addWidget(self.btn_selectShuffled, 2, 4, 1, 1)
        self.btn_shuffleAction = QtGui.QPushButton(self.centralwidget)
        self.btn_shuffleAction.setMinimumSize(QtCore.QSize(120, 0))
        self.btn_shuffleAction.setObjectName("btn_shuffleAction")
        self.shuffleAction_layout.addWidget(self.btn_shuffleAction, 2, 0, 1, 1)
        self.shuffleAction_mainLayoutBottom.addLayout(self.shuffleAction_layout)
        self.gridLayout_3.addLayout(self.shuffleAction_mainLayoutBottom, 2, 0, 1, 1)
        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setTabPosition(QtGui.QTabWidget.North)
        self.tabWidget.setMovable(True)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_shuffler = QtGui.QWidget()
        self.tab_shuffler.setObjectName("tab_shuffler")
        self.tab_shuffler_layout = QtGui.QGridLayout(self.tab_shuffler)
        self.tab_shuffler_layout.setObjectName("tab_shuffler_layout")
        self.shuffler_actionsLayout = QtGui.QGridLayout()
        self.shuffler_actionsLayout.setObjectName("shuffler_actionsLayout")
        self.shuffler_actions_listsLayout = QtGui.QHBoxLayout()
        self.shuffler_actions_listsLayout.setObjectName("shuffler_actions_listsLayout")
        self.shuffler_mainPassesLayout = QtGui.QGridLayout()
        self.shuffler_mainPassesLayout.setObjectName("shuffler_mainPassesLayout")
        self.shuffler_mainPasses_buttonsLayout = QtGui.QHBoxLayout()
        self.shuffler_mainPasses_buttonsLayout.setObjectName("shuffler_mainPasses_buttonsLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.shuffler_mainPasses_buttonsLayout.addItem(spacerItem)
        self.btn_mainPasses_selectAll = QtGui.QPushButton(self.tab_shuffler)
        self.btn_mainPasses_selectAll.setObjectName("btn_mainPasses_selectAll")
        self.shuffler_mainPasses_buttonsLayout.addWidget(self.btn_mainPasses_selectAll)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.shuffler_mainPasses_buttonsLayout.addItem(spacerItem1)
        self.btn_mainPasses_clearSel = QtGui.QPushButton(self.tab_shuffler)
        self.btn_mainPasses_clearSel.setObjectName("btn_mainPasses_clearSel")
        self.shuffler_mainPasses_buttonsLayout.addWidget(self.btn_mainPasses_clearSel)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.shuffler_mainPasses_buttonsLayout.addItem(spacerItem2)
        self.shuffler_mainPassesLayout.addLayout(self.shuffler_mainPasses_buttonsLayout, 4, 0, 1, 1)
        self.listWidget_mainPasses = QtGui.QListWidget(self.tab_shuffler)
        self.listWidget_mainPasses.setProperty("cursor", QtCore.Qt.ArrowCursor)
        self.listWidget_mainPasses.setDragDropMode(QtGui.QAbstractItemView.NoDragDrop)
        self.listWidget_mainPasses.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.listWidget_mainPasses.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.listWidget_mainPasses.setObjectName("listWidget_mainPasses")
        self.shuffler_mainPassesLayout.addWidget(self.listWidget_mainPasses, 2, 0, 1, 1)
        self.shuffler_mainPasses_titleLayout = QtGui.QHBoxLayout()
        self.shuffler_mainPasses_titleLayout.setObjectName("shuffler_mainPasses_titleLayout")
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.shuffler_mainPasses_titleLayout.addItem(spacerItem3)
        self.lineEdit_mainPassesTitle_input = QtGui.QLineEdit(self.tab_shuffler)
        self.lineEdit_mainPassesTitle_input.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_mainPassesTitle_input.setObjectName("lineEdit_mainPassesTitle_input")
        self.shuffler_mainPasses_titleLayout.addWidget(self.lineEdit_mainPassesTitle_input)
        spacerItem4 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.shuffler_mainPasses_titleLayout.addItem(spacerItem4)
        self.shuffler_mainPassesLayout.addLayout(self.shuffler_mainPasses_titleLayout, 0, 0, 1, 1)
        self.btn_mainPasses_resetOrder = QtGui.QPushButton(self.tab_shuffler)
        self.btn_mainPasses_resetOrder.setObjectName("btn_mainPasses_resetOrder")
        self.shuffler_mainPassesLayout.addWidget(self.btn_mainPasses_resetOrder, 5, 0, 1, 1)
        self.shuffler_actions_listsLayout.addLayout(self.shuffler_mainPassesLayout)
        self.shuffler_aovLayout = QtGui.QGridLayout()
        self.shuffler_aovLayout.setObjectName("shuffler_aovLayout")
        self.shuffler_aov_titleLayout = QtGui.QHBoxLayout()
        self.shuffler_aov_titleLayout.setObjectName("shuffler_aov_titleLayout")
        spacerItem5 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.shuffler_aov_titleLayout.addItem(spacerItem5)
        self.lineEdit_aovsTitle_input = QtGui.QLineEdit(self.tab_shuffler)
        self.lineEdit_aovsTitle_input.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_aovsTitle_input.setObjectName("lineEdit_aovsTitle_input")
        self.shuffler_aov_titleLayout.addWidget(self.lineEdit_aovsTitle_input)
        spacerItem6 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.shuffler_aov_titleLayout.addItem(spacerItem6)
        self.shuffler_aovLayout.addLayout(self.shuffler_aov_titleLayout, 0, 0, 1, 1)
        self.shuffler_aov_buttonsLayout = QtGui.QHBoxLayout()
        self.shuffler_aov_buttonsLayout.setObjectName("shuffler_aov_buttonsLayout")
        spacerItem7 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.shuffler_aov_buttonsLayout.addItem(spacerItem7)
        self.btn_aov_selectRemaining = QtGui.QPushButton(self.tab_shuffler)
        self.btn_aov_selectRemaining.setObjectName("btn_aov_selectRemaining")
        self.shuffler_aov_buttonsLayout.addWidget(self.btn_aov_selectRemaining)
        spacerItem8 = QtGui.QSpacerItem(30, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.shuffler_aov_buttonsLayout.addItem(spacerItem8)
        self.btn_aov_clearSel = QtGui.QPushButton(self.tab_shuffler)
        self.btn_aov_clearSel.setObjectName("btn_aov_clearSel")
        self.shuffler_aov_buttonsLayout.addWidget(self.btn_aov_clearSel)
        spacerItem9 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.shuffler_aov_buttonsLayout.addItem(spacerItem9)
        self.shuffler_aovLayout.addLayout(self.shuffler_aov_buttonsLayout, 4, 0, 1, 1)
        self.listWidget_aov = QtGui.QListWidget(self.tab_shuffler)
        self.listWidget_aov.setDragDropMode(QtGui.QAbstractItemView.NoDragDrop)
        self.listWidget_aov.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.listWidget_aov.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.listWidget_aov.setObjectName("listWidget_aov")
        self.shuffler_aovLayout.addWidget(self.listWidget_aov, 2, 0, 1, 1)
        self.btn_aovs_resetOrder = QtGui.QPushButton(self.tab_shuffler)
        self.btn_aovs_resetOrder.setObjectName("btn_aovs_resetOrder")
        self.shuffler_aovLayout.addWidget(self.btn_aovs_resetOrder, 5, 0, 1, 1)
        self.shuffler_actions_listsLayout.addLayout(self.shuffler_aovLayout)
        self.shuffler_actionsLayout.addLayout(self.shuffler_actions_listsLayout, 0, 0, 1, 1)
        self.grpBox_extraOptions = QtGui.QGroupBox(self.tab_shuffler)
        self.grpBox_extraOptions.setObjectName("grpBox_extraOptions")
        self.gridLayout_5 = QtGui.QGridLayout(self.grpBox_extraOptions)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.colorSelect_layout = QtGui.QHBoxLayout()
        self.colorSelect_layout.setObjectName("colorSelect_layout")
        self.label_backdropsColor = QtGui.QLabel(self.grpBox_extraOptions)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_backdropsColor.sizePolicy().hasHeightForWidth())
        self.label_backdropsColor.setSizePolicy(sizePolicy)
        self.label_backdropsColor.setAlignment(QtCore.Qt.AlignCenter)
        self.label_backdropsColor.setObjectName("label_backdropsColor")
        self.colorSelect_layout.addWidget(self.label_backdropsColor)
        self.btn_selectColor = QtGui.QPushButton(self.grpBox_extraOptions)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_selectColor.sizePolicy().hasHeightForWidth())
        self.btn_selectColor.setSizePolicy(sizePolicy)
        self.btn_selectColor.setObjectName("btn_selectColor")
        self.colorSelect_layout.addWidget(self.btn_selectColor)
        self.gridLayout_5.addLayout(self.colorSelect_layout, 2, 0, 1, 1)
        self.extraOptions_topLayout = QtGui.QGridLayout()
        self.extraOptions_topLayout.setObjectName("extraOptions_topLayout")
        self.check_unlockShuffleOrdering = QtGui.QCheckBox(self.grpBox_extraOptions)
        self.check_unlockShuffleOrdering.setObjectName("check_unlockShuffleOrdering")
        self.extraOptions_topLayout.addWidget(self.check_unlockShuffleOrdering, 2, 0, 1, 1)
        self.check_selectionOnly = QtGui.QCheckBox(self.grpBox_extraOptions)
        self.check_selectionOnly.setObjectName("check_selectionOnly")
        self.extraOptions_topLayout.addWidget(self.check_selectionOnly, 1, 0, 1, 1)
        self.comboBox_rebuildDirection = QtGui.QComboBox(self.grpBox_extraOptions)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_rebuildDirection.sizePolicy().hasHeightForWidth())
        self.comboBox_rebuildDirection.setSizePolicy(sizePolicy)
        self.comboBox_rebuildDirection.setObjectName("comboBox_rebuildDirection")
        self.comboBox_rebuildDirection.addItem("")
        self.comboBox_rebuildDirection.addItem("")
        self.extraOptions_topLayout.addWidget(self.comboBox_rebuildDirection, 2, 2, 1, 1)
        self.rebuildCheckbox_layout = QtGui.QHBoxLayout()
        self.rebuildCheckbox_layout.setObjectName("rebuildCheckbox_layout")
        self.check_useRebuild = QtGui.QCheckBox(self.grpBox_extraOptions)
        self.check_useRebuild.setEnabled(True)
        self.check_useRebuild.setObjectName("check_useRebuild")
        self.rebuildCheckbox_layout.addWidget(self.check_useRebuild)
        self.comboBox_rendererSelectionDropdown = QtGui.QComboBox(self.grpBox_extraOptions)
        self.comboBox_rendererSelectionDropdown.setObjectName("comboBox_rendererSelectionDropdown")
        self.comboBox_rendererSelectionDropdown.addItem("")
        self.comboBox_rendererSelectionDropdown.addItem("")
        self.comboBox_rendererSelectionDropdown.addItem("")
        self.rebuildCheckbox_layout.addWidget(self.comboBox_rendererSelectionDropdown)
        self.extraOptions_topLayout.addLayout(self.rebuildCheckbox_layout, 1, 2, 1, 1)
        self.gridLayout_5.addLayout(self.extraOptions_topLayout, 0, 0, 1, 1)
        self.nodeDistanceMult_layout = QtGui.QHBoxLayout()
        self.nodeDistanceMult_layout.setObjectName("nodeDistanceMult_layout")
        self.label_nodeDIstanceMult = QtGui.QLabel(self.grpBox_extraOptions)
        self.label_nodeDIstanceMult.setObjectName("label_nodeDIstanceMult")
        self.nodeDistanceMult_layout.addWidget(self.label_nodeDIstanceMult)
        self.numField_nodeDistanceMult = QtGui.QSpinBox(self.grpBox_extraOptions)
        self.numField_nodeDistanceMult.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        self.numField_nodeDistanceMult.setProperty("value", 1)
        self.numField_nodeDistanceMult.setObjectName("numField_nodeDistanceMult")
        self.nodeDistanceMult_layout.addWidget(self.numField_nodeDistanceMult)
        self.slider_nodeDistanceMult = QtGui.QSlider(self.grpBox_extraOptions)
        self.slider_nodeDistanceMult.setMinimum(10)
        self.slider_nodeDistanceMult.setMaximum(100)
        self.slider_nodeDistanceMult.setOrientation(QtCore.Qt.Horizontal)
        self.slider_nodeDistanceMult.setObjectName("slider_nodeDistanceMult")
        self.nodeDistanceMult_layout.addWidget(self.slider_nodeDistanceMult)
        self.gridLayout_5.addLayout(self.nodeDistanceMult_layout, 4, 0, 1, 1)
        self.line_distanceMultDivider = QtGui.QFrame(self.grpBox_extraOptions)
        self.line_distanceMultDivider.setFrameShape(QtGui.QFrame.HLine)
        self.line_distanceMultDivider.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_distanceMultDivider.setObjectName("line_distanceMultDivider")
        self.gridLayout_5.addWidget(self.line_distanceMultDivider, 3, 0, 1, 1)
        self.line_colorSelectDivider = QtGui.QFrame(self.grpBox_extraOptions)
        self.line_colorSelectDivider.setFrameShape(QtGui.QFrame.HLine)
        self.line_colorSelectDivider.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_colorSelectDivider.setObjectName("line_colorSelectDivider")
        self.gridLayout_5.addWidget(self.line_colorSelectDivider, 1, 0, 1, 1)
        self.shuffler_actionsLayout.addWidget(self.grpBox_extraOptions, 2, 0, 1, 1)
        self.tab_shuffler_layout.addLayout(self.shuffler_actionsLayout, 1, 0, 1, 1)
        self.shuffler_informationLayout = QtGui.QHBoxLayout()
        self.shuffler_informationLayout.setObjectName("shuffler_informationLayout")
        self.grpBox_selNode = QtGui.QGroupBox(self.tab_shuffler)
        self.grpBox_selNode.setObjectName("grpBox_selNode")
        self.horizontalLayout = QtGui.QHBoxLayout(self.grpBox_selNode)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_selNode = QtGui.QLabel(self.grpBox_selNode)
        self.label_selNode.setObjectName("label_selNode")
        self.horizontalLayout.addWidget(self.label_selNode)
        self.btn_updateTarget = QtGui.QPushButton(self.grpBox_selNode)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_updateTarget.sizePolicy().hasHeightForWidth())
        self.btn_updateTarget.setSizePolicy(sizePolicy)
        self.btn_updateTarget.setObjectName("btn_updateTarget")
        self.horizontalLayout.addWidget(self.btn_updateTarget)
        self.shuffler_informationLayout.addWidget(self.grpBox_selNode)
        self.grpBox_fileName = QtGui.QGroupBox(self.tab_shuffler)
        self.grpBox_fileName.setObjectName("grpBox_fileName")
        self.grpBox_fileName_layout = QtGui.QVBoxLayout(self.grpBox_fileName)
        self.grpBox_fileName_layout.setObjectName("grpBox_fileName_layout")
        self.label_fileName = QtGui.QLabel(self.grpBox_fileName)
        self.label_fileName.setObjectName("label_fileName")
        self.grpBox_fileName_layout.addWidget(self.label_fileName)
        self.shuffler_informationLayout.addWidget(self.grpBox_fileName)
        self.tab_shuffler_layout.addLayout(self.shuffler_informationLayout, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_shuffler, "")
        self.tab_rendererRebuild = QtGui.QWidget()
        self.tab_rendererRebuild.setObjectName("tab_rendererRebuild")
        self.tab_rendererRebuild_layout = QtGui.QGridLayout(self.tab_rendererRebuild)
        self.tab_rendererRebuild_layout.setObjectName("tab_rendererRebuild_layout")
        self.rebuildOptions_topLayout = QtGui.QGridLayout()
        self.rebuildOptions_topLayout.setObjectName("rebuildOptions_topLayout")
        self.check_useRebuild_alt = QtGui.QCheckBox(self.tab_rendererRebuild)
        self.check_useRebuild_alt.setObjectName("check_useRebuild_alt")
        self.rebuildOptions_topLayout.addWidget(self.check_useRebuild_alt, 0, 0, 1, 1)
        self.comboBox_rebuildDirection_alt = QtGui.QComboBox(self.tab_rendererRebuild)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_rebuildDirection_alt.sizePolicy().hasHeightForWidth())
        self.comboBox_rebuildDirection_alt.setSizePolicy(sizePolicy)
        self.comboBox_rebuildDirection_alt.setObjectName("comboBox_rebuildDirection_alt")
        self.comboBox_rebuildDirection_alt.addItem("")
        self.comboBox_rebuildDirection_alt.addItem("")
        self.rebuildOptions_topLayout.addWidget(self.comboBox_rebuildDirection_alt, 0, 4, 1, 1)
        self.comboBox_rendererSelectionDropdown_alt = QtGui.QComboBox(self.tab_rendererRebuild)
        self.comboBox_rendererSelectionDropdown_alt.setEnabled(True)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboBox_rendererSelectionDropdown_alt.sizePolicy().hasHeightForWidth())
        self.comboBox_rendererSelectionDropdown_alt.setSizePolicy(sizePolicy)
        self.comboBox_rendererSelectionDropdown_alt.setObjectName("comboBox_rendererSelectionDropdown_alt")
        self.comboBox_rendererSelectionDropdown_alt.addItem("")
        self.comboBox_rendererSelectionDropdown_alt.addItem("")
        self.comboBox_rendererSelectionDropdown_alt.addItem("")
        self.rebuildOptions_topLayout.addWidget(self.comboBox_rendererSelectionDropdown_alt, 0, 2, 1, 1)
        self.tab_rendererRebuild_layout.addLayout(self.rebuildOptions_topLayout, 0, 0, 1, 1)
        self.stackedWidget_rebuildOptions = QtGui.QStackedWidget(self.tab_rendererRebuild)
        self.stackedWidget_rebuildOptions.setObjectName("stackedWidget_rebuildOptions")
        self.page_none = QtGui.QWidget()
        self.page_none.setObjectName("page_none")
        self.PLACEHOLDER_page_layout = QtGui.QGridLayout(self.page_none)
        self.PLACEHOLDER_page_layout.setObjectName("PLACEHOLDER_page_layout")
        self.stackedWidget_rebuildOptions.addWidget(self.page_none)
        self.page_arnold = QtGui.QWidget()
        self.page_arnold.setObjectName("page_arnold")
        self.gridLayout_4 = QtGui.QGridLayout(self.page_arnold)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.grpBox_arnold = QtGui.QGroupBox(self.page_arnold)
        self.grpBox_arnold.setObjectName("grpBox_arnold")
        self.gridLayout_7 = QtGui.QGridLayout(self.grpBox_arnold)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.radioBtn_primaryArnold = QtGui.QRadioButton(self.grpBox_arnold)
        self.radioBtn_primaryArnold.setChecked(True)
        self.radioBtn_primaryArnold.setObjectName("radioBtn_primaryArnold")
        self.gridLayout_7.addWidget(self.radioBtn_primaryArnold, 0, 0, 1, 1)
        self.radioBtn_secondaryArnold = QtGui.QRadioButton(self.grpBox_arnold)
        self.radioBtn_secondaryArnold.setObjectName("radioBtn_secondaryArnold")
        self.gridLayout_7.addWidget(self.radioBtn_secondaryArnold, 4, 0, 1, 1)
        self.primary_layout = QtGui.QGridLayout()
        self.primary_layout.setObjectName("primary_layout")
        self.grpBox_specular = QtGui.QGroupBox(self.grpBox_arnold)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.grpBox_specular.sizePolicy().hasHeightForWidth())
        self.grpBox_specular.setSizePolicy(sizePolicy)
        self.grpBox_specular.setObjectName("grpBox_specular")
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.grpBox_specular)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_directSpec = QtGui.QLabel(self.grpBox_specular)
        self.label_directSpec.setObjectName("label_directSpec")
        self.verticalLayout_4.addWidget(self.label_directSpec)
        self.comboBox_directSpec = QtGui.QComboBox(self.grpBox_specular)
        self.comboBox_directSpec.setObjectName("comboBox_directSpec")
        self.comboBox_directSpec.addItem("")
        self.verticalLayout_4.addWidget(self.comboBox_directSpec)
        self.label_indirectSpec = QtGui.QLabel(self.grpBox_specular)
        self.label_indirectSpec.setObjectName("label_indirectSpec")
        self.verticalLayout_4.addWidget(self.label_indirectSpec)
        self.comboBox_indirectSpec = QtGui.QComboBox(self.grpBox_specular)
        self.comboBox_indirectSpec.setObjectName("comboBox_indirectSpec")
        self.comboBox_indirectSpec.addItem("")
        self.verticalLayout_4.addWidget(self.comboBox_indirectSpec)
        self.primary_layout.addWidget(self.grpBox_specular, 1, 1, 1, 1)
        self.grpBox_diffuse = QtGui.QGroupBox(self.grpBox_arnold)
        self.grpBox_diffuse.setObjectName("grpBox_diffuse")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.grpBox_diffuse)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_directDiffuse = QtGui.QLabel(self.grpBox_diffuse)
        self.label_directDiffuse.setObjectName("label_directDiffuse")
        self.verticalLayout_2.addWidget(self.label_directDiffuse)
        self.comboBox_directDiffuse = QtGui.QComboBox(self.grpBox_diffuse)
        self.comboBox_directDiffuse.setObjectName("comboBox_directDiffuse")
        self.comboBox_directDiffuse.addItem("")
        self.verticalLayout_2.addWidget(self.comboBox_directDiffuse)
        self.label_indirectDiffuse = QtGui.QLabel(self.grpBox_diffuse)
        self.label_indirectDiffuse.setObjectName("label_indirectDiffuse")
        self.verticalLayout_2.addWidget(self.label_indirectDiffuse)
        self.comboBox_indirectDiffuse = QtGui.QComboBox(self.grpBox_diffuse)
        self.comboBox_indirectDiffuse.setObjectName("comboBox_indirectDiffuse")
        self.comboBox_indirectDiffuse.addItem("")
        self.verticalLayout_2.addWidget(self.comboBox_indirectDiffuse)
        self.primary_layout.addWidget(self.grpBox_diffuse, 1, 0, 1, 1)
        self.grpBox_volume = QtGui.QGroupBox(self.grpBox_arnold)
        self.grpBox_volume.setObjectName("grpBox_volume")
        self.verticalLayout_9 = QtGui.QVBoxLayout(self.grpBox_volume)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.label_directVolume = QtGui.QLabel(self.grpBox_volume)
        self.label_directVolume.setObjectName("label_directVolume")
        self.verticalLayout_9.addWidget(self.label_directVolume)
        self.comboBox_directVolume = QtGui.QComboBox(self.grpBox_volume)
        self.comboBox_directVolume.setObjectName("comboBox_directVolume")
        self.comboBox_directVolume.addItem("")
        self.verticalLayout_9.addWidget(self.comboBox_directVolume)
        self.label_indirectVolume = QtGui.QLabel(self.grpBox_volume)
        self.label_indirectVolume.setObjectName("label_indirectVolume")
        self.verticalLayout_9.addWidget(self.label_indirectVolume)
        self.comboBox_indirectVolume = QtGui.QComboBox(self.grpBox_volume)
        self.comboBox_indirectVolume.setObjectName("comboBox_indirectVolume")
        self.comboBox_indirectVolume.addItem("")
        self.verticalLayout_9.addWidget(self.comboBox_indirectVolume)
        self.primary_layout.addWidget(self.grpBox_volume, 2, 2, 1, 1)
        self.grpBox_coat = QtGui.QGroupBox(self.grpBox_arnold)
        self.grpBox_coat.setObjectName("grpBox_coat")
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.grpBox_coat)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_directCoat = QtGui.QLabel(self.grpBox_coat)
        self.label_directCoat.setObjectName("label_directCoat")
        self.verticalLayout_5.addWidget(self.label_directCoat)
        self.comboBox_directCoat = QtGui.QComboBox(self.grpBox_coat)
        self.comboBox_directCoat.setObjectName("comboBox_directCoat")
        self.comboBox_directCoat.addItem("")
        self.verticalLayout_5.addWidget(self.comboBox_directCoat)
        self.label_indirectCoat = QtGui.QLabel(self.grpBox_coat)
        self.label_indirectCoat.setObjectName("label_indirectCoat")
        self.verticalLayout_5.addWidget(self.label_indirectCoat)
        self.comboBox_indirectCoat = QtGui.QComboBox(self.grpBox_coat)
        self.comboBox_indirectCoat.setObjectName("comboBox_indirectCoat")
        self.comboBox_indirectCoat.addItem("")
        self.verticalLayout_5.addWidget(self.comboBox_indirectCoat)
        self.primary_layout.addWidget(self.grpBox_coat, 1, 2, 1, 1)
        self.grpBox_sss = QtGui.QGroupBox(self.grpBox_arnold)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.grpBox_sss.sizePolicy().hasHeightForWidth())
        self.grpBox_sss.setSizePolicy(sizePolicy)
        self.grpBox_sss.setObjectName("grpBox_sss")
        self.verticalLayout_8 = QtGui.QVBoxLayout(self.grpBox_sss)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.label_directSss = QtGui.QLabel(self.grpBox_sss)
        self.label_directSss.setObjectName("label_directSss")
        self.verticalLayout_8.addWidget(self.label_directSss)
        self.comboBox_directSss = QtGui.QComboBox(self.grpBox_sss)
        self.comboBox_directSss.setObjectName("comboBox_directSss")
        self.comboBox_directSss.addItem("")
        self.verticalLayout_8.addWidget(self.comboBox_directSss)
        self.label_indirectSss = QtGui.QLabel(self.grpBox_sss)
        self.label_indirectSss.setObjectName("label_indirectSss")
        self.verticalLayout_8.addWidget(self.label_indirectSss)
        self.comboBox_indirectSss = QtGui.QComboBox(self.grpBox_sss)
        self.comboBox_indirectSss.setObjectName("comboBox_indirectSss")
        self.comboBox_indirectSss.addItem("")
        self.verticalLayout_8.addWidget(self.comboBox_indirectSss)
        self.primary_layout.addWidget(self.grpBox_sss, 2, 1, 1, 1)
        self.grpBox_transmission = QtGui.QGroupBox(self.grpBox_arnold)
        self.grpBox_transmission.setObjectName("grpBox_transmission")
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.grpBox_transmission)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.label_directTransmission = QtGui.QLabel(self.grpBox_transmission)
        self.label_directTransmission.setObjectName("label_directTransmission")
        self.verticalLayout_6.addWidget(self.label_directTransmission)
        self.comboBox_directTransmission = QtGui.QComboBox(self.grpBox_transmission)
        self.comboBox_directTransmission.setObjectName("comboBox_directTransmission")
        self.comboBox_directTransmission.addItem("")
        self.verticalLayout_6.addWidget(self.comboBox_directTransmission)
        self.label_indirectTransmission = QtGui.QLabel(self.grpBox_transmission)
        self.label_indirectTransmission.setObjectName("label_indirectTransmission")
        self.verticalLayout_6.addWidget(self.label_indirectTransmission)
        self.comboBox_indirectTransmission = QtGui.QComboBox(self.grpBox_transmission)
        self.comboBox_indirectTransmission.setObjectName("comboBox_indirectTransmission")
        self.comboBox_indirectTransmission.addItem("")
        self.verticalLayout_6.addWidget(self.comboBox_indirectTransmission)
        self.primary_layout.addWidget(self.grpBox_transmission, 2, 0, 1, 1)
        self.grpBox_emission = QtGui.QGroupBox(self.grpBox_arnold)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.grpBox_emission.sizePolicy().hasHeightForWidth())
        self.grpBox_emission.setSizePolicy(sizePolicy)
        self.grpBox_emission.setObjectName("grpBox_emission")
        self.verticalLayout_7 = QtGui.QVBoxLayout(self.grpBox_emission)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.comboBox_emission = QtGui.QComboBox(self.grpBox_emission)
        self.comboBox_emission.setObjectName("comboBox_emission")
        self.comboBox_emission.addItem("")
        self.verticalLayout_7.addWidget(self.comboBox_emission)
        self.primary_layout.addWidget(self.grpBox_emission, 3, 0, 1, 1)
        self.gridLayout_7.addLayout(self.primary_layout, 1, 0, 1, 1)
        self.secondary_layout = QtGui.QGridLayout()
        self.secondary_layout.setObjectName("secondary_layout")
        self.grpBox_emissionSecondary = QtGui.QGroupBox(self.grpBox_arnold)
        self.grpBox_emissionSecondary.setObjectName("grpBox_emissionSecondary")
        self.verticalLayout_12 = QtGui.QVBoxLayout(self.grpBox_emissionSecondary)
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.comboBox_emissionSecondary = QtGui.QComboBox(self.grpBox_emissionSecondary)
        self.comboBox_emissionSecondary.setObjectName("comboBox_emissionSecondary")
        self.comboBox_emissionSecondary.addItem("")
        self.verticalLayout_12.addWidget(self.comboBox_emissionSecondary)
        self.secondary_layout.addWidget(self.grpBox_emissionSecondary, 0, 2, 1, 1)
        self.grpBox_direct = QtGui.QGroupBox(self.grpBox_arnold)
        self.grpBox_direct.setObjectName("grpBox_direct")
        self.verticalLayout_10 = QtGui.QVBoxLayout(self.grpBox_direct)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.comboBox_direct = QtGui.QComboBox(self.grpBox_direct)
        self.comboBox_direct.setObjectName("comboBox_direct")
        self.comboBox_direct.addItem("")
        self.verticalLayout_10.addWidget(self.comboBox_direct)
        self.secondary_layout.addWidget(self.grpBox_direct, 0, 0, 1, 1)
        self.grpBox_indirect = QtGui.QGroupBox(self.grpBox_arnold)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.grpBox_indirect.sizePolicy().hasHeightForWidth())
        self.grpBox_indirect.setSizePolicy(sizePolicy)
        self.grpBox_indirect.setObjectName("grpBox_indirect")
        self.verticalLayout_11 = QtGui.QVBoxLayout(self.grpBox_indirect)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.comboBox_indirect = QtGui.QComboBox(self.grpBox_indirect)
        self.comboBox_indirect.setObjectName("comboBox_indirect")
        self.comboBox_indirect.addItem("")
        self.verticalLayout_11.addWidget(self.comboBox_indirect)
        self.secondary_layout.addWidget(self.grpBox_indirect, 0, 1, 1, 1)
        self.gridLayout_7.addLayout(self.secondary_layout, 5, 0, 1, 1)
        spacerItem10 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_7.addItem(spacerItem10, 6, 0, 1, 1)
        self.line_vrayDivider = QtGui.QFrame(self.grpBox_arnold)
        self.line_vrayDivider.setMinimumSize(QtCore.QSize(0, 5))
        self.line_vrayDivider.setFrameShape(QtGui.QFrame.HLine)
        self.line_vrayDivider.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_vrayDivider.setObjectName("line_vrayDivider")
        self.gridLayout_7.addWidget(self.line_vrayDivider, 2, 0, 1, 1)
        self.gridLayout_4.addWidget(self.grpBox_arnold, 0, 1, 1, 1)
        self.stackedWidget_rebuildOptions.addWidget(self.page_arnold)
        self.page_vray = QtGui.QWidget()
        self.page_vray.setObjectName("page_vray")
        self.gridLayout = QtGui.QGridLayout(self.page_vray)
        self.gridLayout.setObjectName("gridLayout")
        self.grpBox_vray = QtGui.QGroupBox(self.page_vray)
        self.grpBox_vray.setObjectName("grpBox_vray")
        self.gridLayout_8 = QtGui.QGridLayout(self.grpBox_vray)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.radioBtn_advancedVray = QtGui.QRadioButton(self.grpBox_vray)
        self.radioBtn_advancedVray.setChecked(True)
        self.radioBtn_advancedVray.setObjectName("radioBtn_advancedVray")
        self.gridLayout_8.addWidget(self.radioBtn_advancedVray, 0, 0, 1, 1)
        self.basicVray_layout = QtGui.QGridLayout()
        self.basicVray_layout.setObjectName("basicVray_layout")
        self.groupBox_selfIlluminationBasic = QtGui.QGroupBox(self.grpBox_vray)
        self.groupBox_selfIlluminationBasic.setObjectName("groupBox_selfIlluminationBasic")
        self.verticalLayout_19 = QtGui.QVBoxLayout(self.groupBox_selfIlluminationBasic)
        self.verticalLayout_19.setObjectName("verticalLayout_19")
        self.comboBox_selfIlluminationBasic = QtGui.QComboBox(self.groupBox_selfIlluminationBasic)
        self.comboBox_selfIlluminationBasic.setObjectName("comboBox_selfIlluminationBasic")
        self.comboBox_selfIlluminationBasic.addItem("")
        self.verticalLayout_19.addWidget(self.comboBox_selfIlluminationBasic)
        self.basicVray_layout.addWidget(self.groupBox_selfIlluminationBasic, 2, 0, 1, 1)
        self.groupBox_causticsBasic = QtGui.QGroupBox(self.grpBox_vray)
        self.groupBox_causticsBasic.setObjectName("groupBox_causticsBasic")
        self.verticalLayout_20 = QtGui.QVBoxLayout(self.groupBox_causticsBasic)
        self.verticalLayout_20.setObjectName("verticalLayout_20")
        self.comboBox_causticsBasic = QtGui.QComboBox(self.groupBox_causticsBasic)
        self.comboBox_causticsBasic.setObjectName("comboBox_causticsBasic")
        self.comboBox_causticsBasic.addItem("")
        self.verticalLayout_20.addWidget(self.comboBox_causticsBasic)
        self.basicVray_layout.addWidget(self.groupBox_causticsBasic, 2, 1, 1, 1)
        self.groupBox_refraction = QtGui.QGroupBox(self.grpBox_vray)
        self.groupBox_refraction.setObjectName("groupBox_refraction")
        self.verticalLayout_17 = QtGui.QVBoxLayout(self.groupBox_refraction)
        self.verticalLayout_17.setObjectName("verticalLayout_17")
        self.comboBox_refraction = QtGui.QComboBox(self.groupBox_refraction)
        self.comboBox_refraction.setObjectName("comboBox_refraction")
        self.comboBox_refraction.addItem("")
        self.verticalLayout_17.addWidget(self.comboBox_refraction)
        self.basicVray_layout.addWidget(self.groupBox_refraction, 1, 0, 1, 1)
        self.groupBox_specularBasic = QtGui.QGroupBox(self.grpBox_vray)
        self.groupBox_specularBasic.setObjectName("groupBox_specularBasic")
        self.verticalLayout_18 = QtGui.QVBoxLayout(self.groupBox_specularBasic)
        self.verticalLayout_18.setObjectName("verticalLayout_18")
        self.comboBox_specularBasic = QtGui.QComboBox(self.groupBox_specularBasic)
        self.comboBox_specularBasic.setObjectName("comboBox_specularBasic")
        self.comboBox_specularBasic.addItem("")
        self.verticalLayout_18.addWidget(self.comboBox_specularBasic)
        self.basicVray_layout.addWidget(self.groupBox_specularBasic, 1, 1, 1, 1)
        self.groupBox_gi = QtGui.QGroupBox(self.grpBox_vray)
        self.groupBox_gi.setObjectName("groupBox_gi")
        self.verticalLayout_15 = QtGui.QVBoxLayout(self.groupBox_gi)
        self.verticalLayout_15.setObjectName("verticalLayout_15")
        self.comboBox_gi = QtGui.QComboBox(self.groupBox_gi)
        self.comboBox_gi.setObjectName("comboBox_gi")
        self.comboBox_gi.addItem("")
        self.verticalLayout_15.addWidget(self.comboBox_gi)
        self.basicVray_layout.addWidget(self.groupBox_gi, 0, 1, 1, 1)
        self.groupBox_reflection = QtGui.QGroupBox(self.grpBox_vray)
        self.groupBox_reflection.setObjectName("groupBox_reflection")
        self.verticalLayout_16 = QtGui.QVBoxLayout(self.groupBox_reflection)
        self.verticalLayout_16.setObjectName("verticalLayout_16")
        self.comboBox_reflection = QtGui.QComboBox(self.groupBox_reflection)
        self.comboBox_reflection.setObjectName("comboBox_reflection")
        self.comboBox_reflection.addItem("")
        self.verticalLayout_16.addWidget(self.comboBox_reflection)
        self.basicVray_layout.addWidget(self.groupBox_reflection, 0, 2, 1, 1)
        self.grpBox_lighting = QtGui.QGroupBox(self.grpBox_vray)
        self.grpBox_lighting.setObjectName("grpBox_lighting")
        self.verticalLayout_14 = QtGui.QVBoxLayout(self.grpBox_lighting)
        self.verticalLayout_14.setObjectName("verticalLayout_14")
        self.comboBox_lighting = QtGui.QComboBox(self.grpBox_lighting)
        self.comboBox_lighting.setObjectName("comboBox_lighting")
        self.comboBox_lighting.addItem("")
        self.verticalLayout_14.addWidget(self.comboBox_lighting)
        self.basicVray_layout.addWidget(self.grpBox_lighting, 0, 0, 1, 1)
        self.groupBox_atmosphereBasic = QtGui.QGroupBox(self.grpBox_vray)
        self.groupBox_atmosphereBasic.setObjectName("groupBox_atmosphereBasic")
        self.verticalLayout_21 = QtGui.QVBoxLayout(self.groupBox_atmosphereBasic)
        self.verticalLayout_21.setObjectName("verticalLayout_21")
        self.comboBox_atmosphereBasic = QtGui.QComboBox(self.groupBox_atmosphereBasic)
        self.comboBox_atmosphereBasic.setObjectName("comboBox_atmosphereBasic")
        self.comboBox_atmosphereBasic.addItem("")
        self.verticalLayout_21.addWidget(self.comboBox_atmosphereBasic)
        self.basicVray_layout.addWidget(self.groupBox_atmosphereBasic, 2, 2, 1, 1)
        self.groupBox_sss2basic = QtGui.QGroupBox(self.grpBox_vray)
        self.groupBox_sss2basic.setObjectName("groupBox_sss2basic")
        self.verticalLayout_13 = QtGui.QVBoxLayout(self.groupBox_sss2basic)
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.comboBox_sss2basic = QtGui.QComboBox(self.groupBox_sss2basic)
        self.comboBox_sss2basic.setObjectName("comboBox_sss2basic")
        self.comboBox_sss2basic.addItem("")
        self.verticalLayout_13.addWidget(self.comboBox_sss2basic)
        self.basicVray_layout.addWidget(self.groupBox_sss2basic, 1, 2, 1, 1)
        self.gridLayout_8.addLayout(self.basicVray_layout, 4, 0, 1, 1)
        self.radioBtn_basicVray = QtGui.QRadioButton(self.grpBox_vray)
        self.radioBtn_basicVray.setObjectName("radioBtn_basicVray")
        self.gridLayout_8.addWidget(self.radioBtn_basicVray, 3, 0, 1, 1)
        self.advancedVray_layout = QtGui.QVBoxLayout()
        self.advancedVray_layout.setObjectName("advancedVray_layout")
        self.grpBox_lightingVrayAdvanced = QtGui.QGroupBox(self.grpBox_vray)
        self.grpBox_lightingVrayAdvanced.setObjectName("grpBox_lightingVrayAdvanced")
        self.gridLayout_10 = QtGui.QGridLayout(self.grpBox_lightingVrayAdvanced)
        self.gridLayout_10.setObjectName("gridLayout_10")
        self.label_diffuseFIlter = QtGui.QLabel(self.grpBox_lightingVrayAdvanced)
        self.label_diffuseFIlter.setObjectName("label_diffuseFIlter")
        self.gridLayout_10.addWidget(self.label_diffuseFIlter, 0, 0, 1, 1)
        self.comboBox_diffuseFilter = QtGui.QComboBox(self.grpBox_lightingVrayAdvanced)
        self.comboBox_diffuseFilter.setObjectName("comboBox_diffuseFilter")
        self.comboBox_diffuseFilter.addItem("")
        self.gridLayout_10.addWidget(self.comboBox_diffuseFilter, 1, 0, 1, 1)
        self.label_rawLighting = QtGui.QLabel(self.grpBox_lightingVrayAdvanced)
        self.label_rawLighting.setObjectName("label_rawLighting")
        self.gridLayout_10.addWidget(self.label_rawLighting, 0, 1, 1, 1)
        self.label_rawGi = QtGui.QLabel(self.grpBox_lightingVrayAdvanced)
        self.label_rawGi.setObjectName("label_rawGi")
        self.gridLayout_10.addWidget(self.label_rawGi, 0, 2, 1, 1)
        self.comboBox_rawLighting = QtGui.QComboBox(self.grpBox_lightingVrayAdvanced)
        self.comboBox_rawLighting.setObjectName("comboBox_rawLighting")
        self.comboBox_rawLighting.addItem("")
        self.gridLayout_10.addWidget(self.comboBox_rawLighting, 1, 1, 1, 1)
        self.comboBox_rawGi = QtGui.QComboBox(self.grpBox_lightingVrayAdvanced)
        self.comboBox_rawGi.setObjectName("comboBox_rawGi")
        self.comboBox_rawGi.addItem("")
        self.gridLayout_10.addWidget(self.comboBox_rawGi, 1, 2, 1, 1)
        self.advancedVray_layout.addWidget(self.grpBox_lightingVrayAdvanced)
        self.reflectionRefraction_layout = QtGui.QHBoxLayout()
        self.reflectionRefraction_layout.setObjectName("reflectionRefraction_layout")
        self.grpBox_reflectionAdvanced = QtGui.QGroupBox(self.grpBox_vray)
        self.grpBox_reflectionAdvanced.setObjectName("grpBox_reflectionAdvanced")
        self.gridLayout_12 = QtGui.QGridLayout(self.grpBox_reflectionAdvanced)
        self.gridLayout_12.setObjectName("gridLayout_12")
        self.comboBox_reflectionFilter = QtGui.QComboBox(self.grpBox_reflectionAdvanced)
        self.comboBox_reflectionFilter.setObjectName("comboBox_reflectionFilter")
        self.comboBox_reflectionFilter.addItem("")
        self.gridLayout_12.addWidget(self.comboBox_reflectionFilter, 1, 1, 1, 1)
        self.comboBox_rawReflection = QtGui.QComboBox(self.grpBox_reflectionAdvanced)
        self.comboBox_rawReflection.setObjectName("comboBox_rawReflection")
        self.comboBox_rawReflection.addItem("")
        self.gridLayout_12.addWidget(self.comboBox_rawReflection, 0, 1, 1, 1)
        self.label_rawReflection = QtGui.QLabel(self.grpBox_reflectionAdvanced)
        self.label_rawReflection.setObjectName("label_rawReflection")
        self.gridLayout_12.addWidget(self.label_rawReflection, 0, 0, 1, 1)
        self.label_reflectionFilter = QtGui.QLabel(self.grpBox_reflectionAdvanced)
        self.label_reflectionFilter.setObjectName("label_reflectionFilter")
        self.gridLayout_12.addWidget(self.label_reflectionFilter, 1, 0, 1, 1)
        self.reflectionRefraction_layout.addWidget(self.grpBox_reflectionAdvanced)
        self.grpBox_refractionAdvanced = QtGui.QGroupBox(self.grpBox_vray)
        self.grpBox_refractionAdvanced.setObjectName("grpBox_refractionAdvanced")
        self.gridLayout_13 = QtGui.QGridLayout(self.grpBox_refractionAdvanced)
        self.gridLayout_13.setObjectName("gridLayout_13")
        self.label_rawRefraction = QtGui.QLabel(self.grpBox_refractionAdvanced)
        self.label_rawRefraction.setObjectName("label_rawRefraction")
        self.gridLayout_13.addWidget(self.label_rawRefraction, 0, 0, 1, 1)
        self.comboBox_rawRefraction = QtGui.QComboBox(self.grpBox_refractionAdvanced)
        self.comboBox_rawRefraction.setObjectName("comboBox_rawRefraction")
        self.comboBox_rawRefraction.addItem("")
        self.gridLayout_13.addWidget(self.comboBox_rawRefraction, 0, 1, 1, 1)
        self.comboBox_refractionFilter = QtGui.QComboBox(self.grpBox_refractionAdvanced)
        self.comboBox_refractionFilter.setObjectName("comboBox_refractionFilter")
        self.comboBox_refractionFilter.addItem("")
        self.gridLayout_13.addWidget(self.comboBox_refractionFilter, 1, 1, 1, 1)
        self.label_refractionFilter = QtGui.QLabel(self.grpBox_refractionAdvanced)
        self.label_refractionFilter.setObjectName("label_refractionFilter")
        self.gridLayout_13.addWidget(self.label_refractionFilter, 1, 0, 1, 1)
        self.reflectionRefraction_layout.addWidget(self.grpBox_refractionAdvanced)
        self.advancedVray_layout.addLayout(self.reflectionRefraction_layout)
        self.advancedMisc_layout = QtGui.QGridLayout()
        self.advancedMisc_layout.setObjectName("advancedMisc_layout")
        self.grpBox_causticsAdvanced = QtGui.QGroupBox(self.grpBox_vray)
        self.grpBox_causticsAdvanced.setObjectName("grpBox_causticsAdvanced")
        self.verticalLayout_26 = QtGui.QVBoxLayout(self.grpBox_causticsAdvanced)
        self.verticalLayout_26.setObjectName("verticalLayout_26")
        self.comboBox_causticsAdvanced = QtGui.QComboBox(self.grpBox_causticsAdvanced)
        self.comboBox_causticsAdvanced.setObjectName("comboBox_causticsAdvanced")
        self.comboBox_causticsAdvanced.addItem("")
        self.verticalLayout_26.addWidget(self.comboBox_causticsAdvanced)
        self.advancedMisc_layout.addWidget(self.grpBox_causticsAdvanced, 1, 0, 1, 1)
        self.grpBox_atmosphereAdvanced = QtGui.QGroupBox(self.grpBox_vray)
        self.grpBox_atmosphereAdvanced.setObjectName("grpBox_atmosphereAdvanced")
        self.verticalLayout_27 = QtGui.QVBoxLayout(self.grpBox_atmosphereAdvanced)
        self.verticalLayout_27.setObjectName("verticalLayout_27")
        self.comboBox_atmosphereAdvanced = QtGui.QComboBox(self.grpBox_atmosphereAdvanced)
        self.comboBox_atmosphereAdvanced.setObjectName("comboBox_atmosphereAdvanced")
        self.comboBox_atmosphereAdvanced.addItem("")
        self.verticalLayout_27.addWidget(self.comboBox_atmosphereAdvanced)
        self.advancedMisc_layout.addWidget(self.grpBox_atmosphereAdvanced, 1, 1, 1, 1)
        self.grpBox_specularAdvanced = QtGui.QGroupBox(self.grpBox_vray)
        self.grpBox_specularAdvanced.setObjectName("grpBox_specularAdvanced")
        self.verticalLayout_23 = QtGui.QVBoxLayout(self.grpBox_specularAdvanced)
        self.verticalLayout_23.setObjectName("verticalLayout_23")
        self.comboBox_specularAdvanced = QtGui.QComboBox(self.grpBox_specularAdvanced)
        self.comboBox_specularAdvanced.setObjectName("comboBox_specularAdvanced")
        self.comboBox_specularAdvanced.addItem("")
        self.verticalLayout_23.addWidget(self.comboBox_specularAdvanced)
        self.advancedMisc_layout.addWidget(self.grpBox_specularAdvanced, 0, 0, 1, 1)
        self.grpBox_sss2advanced = QtGui.QGroupBox(self.grpBox_vray)
        self.grpBox_sss2advanced.setObjectName("grpBox_sss2advanced")
        self.verticalLayout_24 = QtGui.QVBoxLayout(self.grpBox_sss2advanced)
        self.verticalLayout_24.setObjectName("verticalLayout_24")
        self.comboBox_sss2advanced = QtGui.QComboBox(self.grpBox_sss2advanced)
        self.comboBox_sss2advanced.setObjectName("comboBox_sss2advanced")
        self.comboBox_sss2advanced.addItem("")
        self.verticalLayout_24.addWidget(self.comboBox_sss2advanced)
        self.advancedMisc_layout.addWidget(self.grpBox_sss2advanced, 0, 1, 1, 1)
        self.grpBox_selfIlluminationAdvanced = QtGui.QGroupBox(self.grpBox_vray)
        self.grpBox_selfIlluminationAdvanced.setObjectName("grpBox_selfIlluminationAdvanced")
        self.verticalLayout_25 = QtGui.QVBoxLayout(self.grpBox_selfIlluminationAdvanced)
        self.verticalLayout_25.setObjectName("verticalLayout_25")
        self.comboBox_selfIlluminationAdvanced = QtGui.QComboBox(self.grpBox_selfIlluminationAdvanced)
        self.comboBox_selfIlluminationAdvanced.setObjectName("comboBox_selfIlluminationAdvanced")
        self.comboBox_selfIlluminationAdvanced.addItem("")
        self.verticalLayout_25.addWidget(self.comboBox_selfIlluminationAdvanced)
        self.advancedMisc_layout.addWidget(self.grpBox_selfIlluminationAdvanced, 0, 2, 1, 1)
        self.advancedVray_layout.addLayout(self.advancedMisc_layout)
        self.gridLayout_8.addLayout(self.advancedVray_layout, 1, 0, 1, 1)
        self.line_arnoldDivider = QtGui.QFrame(self.grpBox_vray)
        self.line_arnoldDivider.setMinimumSize(QtCore.QSize(0, 5))
        self.line_arnoldDivider.setFrameShape(QtGui.QFrame.HLine)
        self.line_arnoldDivider.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_arnoldDivider.setObjectName("line_arnoldDivider")
        self.gridLayout_8.addWidget(self.line_arnoldDivider, 2, 0, 1, 1)
        self.gridLayout.addWidget(self.grpBox_vray, 0, 0, 1, 1)
        self.stackedWidget_rebuildOptions.addWidget(self.page_vray)
        self.tab_rendererRebuild_layout.addWidget(self.stackedWidget_rebuildOptions, 1, 0, 1, 1)
        self.tabWidget.addTab(self.tab_rendererRebuild, "")
        self.tab_addNodes = QtGui.QWidget()
        self.tab_addNodes.setObjectName("tab_addNodes")
        self.gridLayout_9 = QtGui.QGridLayout(self.tab_addNodes)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.line_addNodesDivider = QtGui.QFrame(self.tab_addNodes)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.line_addNodesDivider.sizePolicy().hasHeightForWidth())
        self.line_addNodesDivider.setSizePolicy(sizePolicy)
        self.line_addNodesDivider.setMinimumSize(QtCore.QSize(0, 20))
        self.line_addNodesDivider.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_addNodesDivider.setFrameShape(QtGui.QFrame.HLine)
        self.line_addNodesDivider.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_addNodesDivider.setObjectName("line_addNodesDivider")
        self.gridLayout_9.addWidget(self.line_addNodesDivider, 1, 0, 1, 1)
        self.addNodes_storedNodesLayout = QtGui.QGridLayout()
        self.addNodes_storedNodesLayout.setObjectName("addNodes_storedNodesLayout")
        self.listWidget_storedNodes = QtGui.QListWidget(self.tab_addNodes)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listWidget_storedNodes.sizePolicy().hasHeightForWidth())
        self.listWidget_storedNodes.setSizePolicy(sizePolicy)
        self.listWidget_storedNodes.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.listWidget_storedNodes.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.listWidget_storedNodes.setMovement(QtGui.QListView.Snap)
        self.listWidget_storedNodes.setObjectName("listWidget_storedNodes")
        self.addNodes_storedNodesLayout.addWidget(self.listWidget_storedNodes, 1, 0, 1, 1)
        self.storedNodes_helperButtonsLayout = QtGui.QVBoxLayout()
        self.storedNodes_helperButtonsLayout.setObjectName("storedNodes_helperButtonsLayout")
        self.btn_recreateNode = QtGui.QPushButton(self.tab_addNodes)
        self.btn_recreateNode.setObjectName("btn_recreateNode")
        self.storedNodes_helperButtonsLayout.addWidget(self.btn_recreateNode)
        self.btn_showInfo = QtGui.QPushButton(self.tab_addNodes)
        self.btn_showInfo.setObjectName("btn_showInfo")
        self.storedNodes_helperButtonsLayout.addWidget(self.btn_showInfo)
        self.btn_deleteEntry = QtGui.QPushButton(self.tab_addNodes)
        self.btn_deleteEntry.setObjectName("btn_deleteEntry")
        self.storedNodes_helperButtonsLayout.addWidget(self.btn_deleteEntry)
        self.btn_deleteAll = QtGui.QPushButton(self.tab_addNodes)
        self.btn_deleteAll.setObjectName("btn_deleteAll")
        self.storedNodes_helperButtonsLayout.addWidget(self.btn_deleteAll)
        self.addNodes_storedNodesLayout.addLayout(self.storedNodes_helperButtonsLayout, 1, 2, 1, 1)
        self.label_nodesToAdd = QtGui.QLabel(self.tab_addNodes)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_nodesToAdd.sizePolicy().hasHeightForWidth())
        self.label_nodesToAdd.setSizePolicy(sizePolicy)
        self.label_nodesToAdd.setMinimumSize(QtCore.QSize(0, 15))
        self.label_nodesToAdd.setAlignment(QtCore.Qt.AlignCenter)
        self.label_nodesToAdd.setObjectName("label_nodesToAdd")
        self.addNodes_storedNodesLayout.addWidget(self.label_nodesToAdd, 0, 0, 1, 1)
        self.btn_premultSandwich = QtGui.QPushButton(self.tab_addNodes)
        self.btn_premultSandwich.setObjectName("btn_premultSandwich")
        self.addNodes_storedNodesLayout.addWidget(self.btn_premultSandwich, 2, 2, 1, 1)
        self.storedNodesBtns_layout = QtGui.QHBoxLayout()
        self.storedNodesBtns_layout.setObjectName("storedNodesBtns_layout")
        self.btn_storeSelected = QtGui.QPushButton(self.tab_addNodes)
        self.btn_storeSelected.setObjectName("btn_storeSelected")
        self.storedNodesBtns_layout.addWidget(self.btn_storeSelected)
        self.btn_updateEntry = QtGui.QPushButton(self.tab_addNodes)
        self.btn_updateEntry.setObjectName("btn_updateEntry")
        self.storedNodesBtns_layout.addWidget(self.btn_updateEntry)
        self.addNodes_storedNodesLayout.addLayout(self.storedNodesBtns_layout, 2, 0, 1, 1)
        self.gridLayout_9.addLayout(self.addNodes_storedNodesLayout, 0, 0, 1, 1)
        self.grpBox_whichLayers = QtGui.QGroupBox(self.tab_addNodes)
        self.grpBox_whichLayers.setObjectName("grpBox_whichLayers")
        self.gridLayout_2 = QtGui.QGridLayout(self.grpBox_whichLayers)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.addNodes_selectionLayout = QtGui.QGridLayout()
        self.addNodes_selectionLayout.setHorizontalSpacing(12)
        self.addNodes_selectionLayout.setObjectName("addNodes_selectionLayout")
        self.label_aovsSelection = QtGui.QLabel(self.grpBox_whichLayers)
        self.label_aovsSelection.setMinimumSize(QtCore.QSize(0, 15))
        self.label_aovsSelection.setAlignment(QtCore.Qt.AlignCenter)
        self.label_aovsSelection.setObjectName("label_aovsSelection")
        self.addNodes_selectionLayout.addWidget(self.label_aovsSelection, 0, 1, 1, 1)
        self.selectionLayout_buttonsRight = QtGui.QHBoxLayout()
        self.selectionLayout_buttonsRight.setObjectName("selectionLayout_buttonsRight")
        spacerItem11 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.selectionLayout_buttonsRight.addItem(spacerItem11)
        self.btn_aovsSelection_selectAll = QtGui.QPushButton(self.grpBox_whichLayers)
        self.btn_aovsSelection_selectAll.setObjectName("btn_aovsSelection_selectAll")
        self.selectionLayout_buttonsRight.addWidget(self.btn_aovsSelection_selectAll)
        spacerItem12 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.selectionLayout_buttonsRight.addItem(spacerItem12)
        self.btn_aovsSelection_clearSel = QtGui.QPushButton(self.grpBox_whichLayers)
        self.btn_aovsSelection_clearSel.setObjectName("btn_aovsSelection_clearSel")
        self.selectionLayout_buttonsRight.addWidget(self.btn_aovsSelection_clearSel)
        spacerItem13 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.selectionLayout_buttonsRight.addItem(spacerItem13)
        self.addNodes_selectionLayout.addLayout(self.selectionLayout_buttonsRight, 2, 1, 1, 1)
        self.listWidget_aovsSelection = QtGui.QListWidget(self.grpBox_whichLayers)
        self.listWidget_aovsSelection.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.listWidget_aovsSelection.setObjectName("listWidget_aovsSelection")
        self.addNodes_selectionLayout.addWidget(self.listWidget_aovsSelection, 1, 1, 1, 1)
        self.label_mainPassesSelection = QtGui.QLabel(self.grpBox_whichLayers)
        self.label_mainPassesSelection.setMinimumSize(QtCore.QSize(0, 15))
        self.label_mainPassesSelection.setAlignment(QtCore.Qt.AlignCenter)
        self.label_mainPassesSelection.setObjectName("label_mainPassesSelection")
        self.addNodes_selectionLayout.addWidget(self.label_mainPassesSelection, 0, 0, 1, 1)
        self.listWidget_mainPassesSelection = QtGui.QListWidget(self.grpBox_whichLayers)
        self.listWidget_mainPassesSelection.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.listWidget_mainPassesSelection.setObjectName("listWidget_mainPassesSelection")
        self.addNodes_selectionLayout.addWidget(self.listWidget_mainPassesSelection, 1, 0, 1, 1)
        self.selectionLayout_buttonsLeft = QtGui.QHBoxLayout()
        self.selectionLayout_buttonsLeft.setObjectName("selectionLayout_buttonsLeft")
        spacerItem14 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.selectionLayout_buttonsLeft.addItem(spacerItem14)
        self.btn_mainPassesSelection_selectAll = QtGui.QPushButton(self.grpBox_whichLayers)
        self.btn_mainPassesSelection_selectAll.setObjectName("btn_mainPassesSelection_selectAll")
        self.selectionLayout_buttonsLeft.addWidget(self.btn_mainPassesSelection_selectAll)
        spacerItem15 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.selectionLayout_buttonsLeft.addItem(spacerItem15)
        self.btn_mainPassesSelection_clearSel = QtGui.QPushButton(self.grpBox_whichLayers)
        self.btn_mainPassesSelection_clearSel.setObjectName("btn_mainPassesSelection_clearSel")
        self.selectionLayout_buttonsLeft.addWidget(self.btn_mainPassesSelection_clearSel)
        spacerItem16 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.selectionLayout_buttonsLeft.addItem(spacerItem16)
        self.addNodes_selectionLayout.addLayout(self.selectionLayout_buttonsLeft, 2, 0, 1, 1)
        self.gridLayout_2.addLayout(self.addNodes_selectionLayout, 0, 0, 1, 1)
        self.gridLayout_9.addWidget(self.grpBox_whichLayers, 2, 0, 1, 1)
        self.tabWidget.addTab(self.tab_addNodes, "")
        self.tab_savedNodeTrees = QtGui.QWidget()
        self.tab_savedNodeTrees.setObjectName("tab_savedNodeTrees")
        self.gridLayout_6 = QtGui.QGridLayout(self.tab_savedNodeTrees)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.presetsButtons_layout = QtGui.QHBoxLayout()
        self.presetsButtons_layout.setObjectName("presetsButtons_layout")
        self.btn_spawnPreset = QtGui.QPushButton(self.tab_savedNodeTrees)
        self.btn_spawnPreset.setObjectName("btn_spawnPreset")
        self.presetsButtons_layout.addWidget(self.btn_spawnPreset)
        self.btn_deletePreset = QtGui.QPushButton(self.tab_savedNodeTrees)
        self.btn_deletePreset.setObjectName("btn_deletePreset")
        self.presetsButtons_layout.addWidget(self.btn_deletePreset)
        self.gridLayout_6.addLayout(self.presetsButtons_layout, 6, 0, 1, 1)
        self.btn_savePreset = QtGui.QPushButton(self.tab_savedNodeTrees)
        self.btn_savePreset.setObjectName("btn_savePreset")
        self.gridLayout_6.addWidget(self.btn_savePreset, 2, 0, 1, 1)
        self.presetName_layout = QtGui.QHBoxLayout()
        self.presetName_layout.setObjectName("presetName_layout")
        self.label_presetName = QtGui.QLabel(self.tab_savedNodeTrees)
        self.label_presetName.setObjectName("label_presetName")
        self.presetName_layout.addWidget(self.label_presetName)
        self.lineEdit_presetName = QtGui.QLineEdit(self.tab_savedNodeTrees)
        self.lineEdit_presetName.setObjectName("lineEdit_presetName")
        self.presetName_layout.addWidget(self.lineEdit_presetName)
        self.gridLayout_6.addLayout(self.presetName_layout, 0, 0, 1, 1)
        self.listWidget_savedPresets = QtGui.QListWidget(self.tab_savedNodeTrees)
        self.listWidget_savedPresets.setObjectName("listWidget_savedPresets")
        self.gridLayout_6.addWidget(self.listWidget_savedPresets, 3, 0, 1, 1)
        self.btn_selectLastSpawn = QtGui.QPushButton(self.tab_savedNodeTrees)
        self.btn_selectLastSpawn.setObjectName("btn_selectLastSpawn")
        self.gridLayout_6.addWidget(self.btn_selectLastSpawn, 8, 0, 1, 1)
        self.line = QtGui.QFrame(self.tab_savedNodeTrees)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout_6.addWidget(self.line, 7, 0, 1, 1)
        self.tabWidget.addTab(self.tab_savedNodeTrees, "")
        self.gridLayout_3.addWidget(self.tabWidget, 1, 0, 1, 1)
        LayerShufflerWin.setCentralWidget(self.centralwidget)

        self.retranslateUi(LayerShufflerWin)
        self.tabWidget.setCurrentIndex(0)
        self.stackedWidget_rebuildOptions.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(LayerShufflerWin)
        LayerShufflerWin.setTabOrder(self.btn_shuffleAction, self.check_extendShuffled)
        LayerShufflerWin.setTabOrder(self.check_extendShuffled, self.check_removeExrRestriction)
        LayerShufflerWin.setTabOrder(self.check_removeExrRestriction, self.btn_selectShuffled)
        LayerShufflerWin.setTabOrder(self.btn_selectShuffled, self.btn_updateTarget)
        LayerShufflerWin.setTabOrder(self.btn_updateTarget, self.lineEdit_mainPassesTitle_input)
        LayerShufflerWin.setTabOrder(self.lineEdit_mainPassesTitle_input, self.lineEdit_aovsTitle_input)
        LayerShufflerWin.setTabOrder(self.lineEdit_aovsTitle_input, self.listWidget_mainPasses)
        LayerShufflerWin.setTabOrder(self.listWidget_mainPasses, self.btn_mainPasses_selectAll)
        LayerShufflerWin.setTabOrder(self.btn_mainPasses_selectAll, self.btn_mainPasses_clearSel)
        LayerShufflerWin.setTabOrder(self.btn_mainPasses_clearSel, self.listWidget_aov)
        LayerShufflerWin.setTabOrder(self.listWidget_aov, self.btn_aov_selectRemaining)
        LayerShufflerWin.setTabOrder(self.btn_aov_selectRemaining, self.btn_aov_clearSel)
        LayerShufflerWin.setTabOrder(self.btn_aov_clearSel, self.check_selectionOnly)
        LayerShufflerWin.setTabOrder(self.check_selectionOnly, self.check_useRebuild)
        LayerShufflerWin.setTabOrder(self.check_useRebuild, self.comboBox_rendererSelectionDropdown)
        LayerShufflerWin.setTabOrder(self.comboBox_rendererSelectionDropdown, self.check_unlockShuffleOrdering)
        LayerShufflerWin.setTabOrder(self.check_unlockShuffleOrdering, self.comboBox_rebuildDirection)
        LayerShufflerWin.setTabOrder(self.comboBox_rebuildDirection, self.btn_selectColor)
        LayerShufflerWin.setTabOrder(self.btn_selectColor, self.numField_nodeDistanceMult)
        LayerShufflerWin.setTabOrder(self.numField_nodeDistanceMult, self.slider_nodeDistanceMult)
        LayerShufflerWin.setTabOrder(self.slider_nodeDistanceMult, self.check_useRebuild_alt)
        LayerShufflerWin.setTabOrder(self.check_useRebuild_alt, self.radioBtn_primaryArnold)
        LayerShufflerWin.setTabOrder(self.radioBtn_primaryArnold, self.comboBox_directDiffuse)
        LayerShufflerWin.setTabOrder(self.comboBox_directDiffuse, self.comboBox_indirectDiffuse)
        LayerShufflerWin.setTabOrder(self.comboBox_indirectDiffuse, self.comboBox_directSpec)
        LayerShufflerWin.setTabOrder(self.comboBox_directSpec, self.comboBox_indirectSpec)
        LayerShufflerWin.setTabOrder(self.comboBox_indirectSpec, self.comboBox_directCoat)
        LayerShufflerWin.setTabOrder(self.comboBox_directCoat, self.comboBox_indirectCoat)
        LayerShufflerWin.setTabOrder(self.comboBox_indirectCoat, self.comboBox_directTransmission)
        LayerShufflerWin.setTabOrder(self.comboBox_directTransmission, self.comboBox_indirectTransmission)
        LayerShufflerWin.setTabOrder(self.comboBox_indirectTransmission, self.comboBox_directSss)
        LayerShufflerWin.setTabOrder(self.comboBox_directSss, self.comboBox_indirectSss)
        LayerShufflerWin.setTabOrder(self.comboBox_indirectSss, self.comboBox_directVolume)
        LayerShufflerWin.setTabOrder(self.comboBox_directVolume, self.comboBox_indirectVolume)
        LayerShufflerWin.setTabOrder(self.comboBox_indirectVolume, self.comboBox_emission)
        LayerShufflerWin.setTabOrder(self.comboBox_emission, self.radioBtn_secondaryArnold)
        LayerShufflerWin.setTabOrder(self.radioBtn_secondaryArnold, self.comboBox_direct)
        LayerShufflerWin.setTabOrder(self.comboBox_direct, self.comboBox_indirect)
        LayerShufflerWin.setTabOrder(self.comboBox_indirect, self.comboBox_emissionSecondary)
        LayerShufflerWin.setTabOrder(self.comboBox_emissionSecondary, self.radioBtn_advancedVray)
        LayerShufflerWin.setTabOrder(self.radioBtn_advancedVray, self.comboBox_diffuseFilter)
        LayerShufflerWin.setTabOrder(self.comboBox_diffuseFilter, self.comboBox_rawLighting)
        LayerShufflerWin.setTabOrder(self.comboBox_rawLighting, self.comboBox_rawGi)
        LayerShufflerWin.setTabOrder(self.comboBox_rawGi, self.comboBox_rawReflection)
        LayerShufflerWin.setTabOrder(self.comboBox_rawReflection, self.comboBox_reflectionFilter)
        LayerShufflerWin.setTabOrder(self.comboBox_reflectionFilter, self.comboBox_rawRefraction)
        LayerShufflerWin.setTabOrder(self.comboBox_rawRefraction, self.comboBox_refractionFilter)
        LayerShufflerWin.setTabOrder(self.comboBox_refractionFilter, self.comboBox_specularAdvanced)
        LayerShufflerWin.setTabOrder(self.comboBox_specularAdvanced, self.comboBox_sss2advanced)
        LayerShufflerWin.setTabOrder(self.comboBox_sss2advanced, self.comboBox_selfIlluminationAdvanced)
        LayerShufflerWin.setTabOrder(self.comboBox_selfIlluminationAdvanced, self.comboBox_causticsAdvanced)
        LayerShufflerWin.setTabOrder(self.comboBox_causticsAdvanced, self.comboBox_atmosphereAdvanced)
        LayerShufflerWin.setTabOrder(self.comboBox_atmosphereAdvanced, self.radioBtn_basicVray)
        LayerShufflerWin.setTabOrder(self.radioBtn_basicVray, self.comboBox_lighting)
        LayerShufflerWin.setTabOrder(self.comboBox_lighting, self.comboBox_gi)
        LayerShufflerWin.setTabOrder(self.comboBox_gi, self.comboBox_reflection)
        LayerShufflerWin.setTabOrder(self.comboBox_reflection, self.comboBox_refraction)
        LayerShufflerWin.setTabOrder(self.comboBox_refraction, self.comboBox_specularBasic)
        LayerShufflerWin.setTabOrder(self.comboBox_specularBasic, self.comboBox_sss2basic)
        LayerShufflerWin.setTabOrder(self.comboBox_sss2basic, self.comboBox_selfIlluminationBasic)
        LayerShufflerWin.setTabOrder(self.comboBox_selfIlluminationBasic, self.comboBox_causticsBasic)
        LayerShufflerWin.setTabOrder(self.comboBox_causticsBasic, self.comboBox_atmosphereBasic)
        LayerShufflerWin.setTabOrder(self.comboBox_atmosphereBasic, self.listWidget_storedNodes)
        LayerShufflerWin.setTabOrder(self.listWidget_storedNodes, self.btn_storeSelected)
        LayerShufflerWin.setTabOrder(self.btn_storeSelected, self.btn_updateEntry)
        LayerShufflerWin.setTabOrder(self.btn_updateEntry, self.btn_premultSandwich)
        LayerShufflerWin.setTabOrder(self.btn_premultSandwich, self.btn_recreateNode)
        LayerShufflerWin.setTabOrder(self.btn_recreateNode, self.btn_showInfo)
        LayerShufflerWin.setTabOrder(self.btn_showInfo, self.btn_deleteEntry)
        LayerShufflerWin.setTabOrder(self.btn_deleteEntry, self.btn_deleteAll)
        LayerShufflerWin.setTabOrder(self.btn_deleteAll, self.listWidget_mainPassesSelection)
        LayerShufflerWin.setTabOrder(self.listWidget_mainPassesSelection, self.btn_mainPassesSelection_selectAll)
        LayerShufflerWin.setTabOrder(self.btn_mainPassesSelection_selectAll, self.btn_mainPassesSelection_clearSel)
        LayerShufflerWin.setTabOrder(self.btn_mainPassesSelection_clearSel, self.listWidget_aovsSelection)
        LayerShufflerWin.setTabOrder(self.listWidget_aovsSelection, self.btn_aovsSelection_selectAll)
        LayerShufflerWin.setTabOrder(self.btn_aovsSelection_selectAll, self.btn_aovsSelection_clearSel)
        LayerShufflerWin.setTabOrder(self.btn_aovsSelection_clearSel, self.tabWidget)
        LayerShufflerWin.setTabOrder(self.tabWidget, self.btn_mainPasses_resetOrder)
        LayerShufflerWin.setTabOrder(self.btn_mainPasses_resetOrder, self.btn_aovs_resetOrder)
        LayerShufflerWin.setTabOrder(self.btn_aovs_resetOrder, self.comboBox_rebuildDirection_alt)
        LayerShufflerWin.setTabOrder(self.comboBox_rebuildDirection_alt, self.comboBox_rendererSelectionDropdown_alt)
        LayerShufflerWin.setTabOrder(self.comboBox_rendererSelectionDropdown_alt, self.lineEdit_presetName)
        LayerShufflerWin.setTabOrder(self.lineEdit_presetName, self.btn_savePreset)
        LayerShufflerWin.setTabOrder(self.btn_savePreset, self.listWidget_savedPresets)
        LayerShufflerWin.setTabOrder(self.listWidget_savedPresets, self.btn_spawnPreset)
        LayerShufflerWin.setTabOrder(self.btn_spawnPreset, self.btn_deletePreset)
        LayerShufflerWin.setTabOrder(self.btn_deletePreset, self.btn_selectLastSpawn)

    def retranslateUi(self, LayerShufflerWin):
        try:
            LayerShufflerWin.setWindowTitle(QtGui.QApplication.translate("LayerShufflerWin", "LayerShuffler", None, QtGui.QApplication.UnicodeUTF8))
            self.check_removeExrRestriction.setText(QtGui.QApplication.translate("LayerShufflerWin", "Skip EXR check", None, QtGui.QApplication.UnicodeUTF8))
            self.check_extendShuffled.setText(QtGui.QApplication.translate("LayerShufflerWin", "Extend Shuffled", None, QtGui.QApplication.UnicodeUTF8))
            self.btn_selectShuffled.setText(QtGui.QApplication.translate("LayerShufflerWin", "Select Last Shuffle", None, QtGui.QApplication.UnicodeUTF8))
            self.btn_shuffleAction.setText(QtGui.QApplication.translate("LayerShufflerWin", "Shuffle2", None, QtGui.QApplication.UnicodeUTF8))
            self.btn_mainPasses_selectAll.setText(QtGui.QApplication.translate("LayerShufflerWin", "Select All", None, QtGui.QApplication.UnicodeUTF8))
            self.btn_mainPasses_clearSel.setText(QtGui.QApplication.translate("LayerShufflerWin", "Clear Selection", None, QtGui.QApplication.UnicodeUTF8))
            self.lineEdit_mainPassesTitle_input.setText(QtGui.QApplication.translate("LayerShufflerWin", "Main Passes", None, QtGui.QApplication.UnicodeUTF8))
            self.btn_mainPasses_resetOrder.setText(QtGui.QApplication.translate("LayerShufflerWin", "Reset Order", None, QtGui.QApplication.UnicodeUTF8))
            self.lineEdit_aovsTitle_input.setText(QtGui.QApplication.translate("LayerShufflerWin", "AOVs", None, QtGui.QApplication.UnicodeUTF8))
            self.btn_aov_selectRemaining.setText(QtGui.QApplication.translate("LayerShufflerWin", "Select Remaining", None, QtGui.QApplication.UnicodeUTF8))
            self.btn_aov_clearSel.setText(QtGui.QApplication.translate("LayerShufflerWin", "Clear Selection", None, QtGui.QApplication.UnicodeUTF8))
            self.btn_aovs_resetOrder.setText(QtGui.QApplication.translate("LayerShufflerWin", "Reset Order", None, QtGui.QApplication.UnicodeUTF8))
            self.grpBox_extraOptions.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "Extra Options", None, QtGui.QApplication.UnicodeUTF8))
            self.label_backdropsColor.setText(QtGui.QApplication.translate("LayerShufflerWin", "Layer backdrops color:", None, QtGui.QApplication.UnicodeUTF8))
            self.btn_selectColor.setText(QtGui.QApplication.translate("LayerShufflerWin", "Select color", None, QtGui.QApplication.UnicodeUTF8))
            self.check_unlockShuffleOrdering.setText(QtGui.QApplication.translate("LayerShufflerWin", "Unlock Shuffle Ordering", None, QtGui.QApplication.UnicodeUTF8))
            self.check_selectionOnly.setText(QtGui.QApplication.translate("LayerShufflerWin", "Shuffle selected layers only", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_rebuildDirection.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "Horizontal", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_rebuildDirection.setItemText(1, QtGui.QApplication.translate("LayerShufflerWin", "Vertical", None, QtGui.QApplication.UnicodeUTF8))
            self.check_useRebuild.setText(QtGui.QApplication.translate("LayerShufflerWin", "Use Rebuild for:", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_rendererSelectionDropdown.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_rendererSelectionDropdown.setItemText(1, QtGui.QApplication.translate("LayerShufflerWin", "Arnold", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_rendererSelectionDropdown.setItemText(2, QtGui.QApplication.translate("LayerShufflerWin", "VRay", None, QtGui.QApplication.UnicodeUTF8))
            self.label_nodeDIstanceMult.setText(QtGui.QApplication.translate("LayerShufflerWin", "Node Distance Multiplier", None, QtGui.QApplication.UnicodeUTF8))
            self.numField_nodeDistanceMult.setPrefix(QtGui.QApplication.translate("LayerShufflerWin", "x", None, QtGui.QApplication.UnicodeUTF8))
            self.grpBox_selNode.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "Selected Node", None, QtGui.QApplication.UnicodeUTF8))
            self.label_selNode.setText(QtGui.QApplication.translate("LayerShufflerWin", "N/A", None, QtGui.QApplication.UnicodeUTF8))
            self.btn_updateTarget.setText(QtGui.QApplication.translate("LayerShufflerWin", "Update", None, QtGui.QApplication.UnicodeUTF8))
            self.grpBox_fileName.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "File name", None, QtGui.QApplication.UnicodeUTF8))
            self.label_fileName.setText(QtGui.QApplication.translate("LayerShufflerWin", "N/A", None, QtGui.QApplication.UnicodeUTF8))
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_shuffler), QtGui.QApplication.translate("LayerShufflerWin", "Shuffler", None, QtGui.QApplication.UnicodeUTF8))
            self.check_useRebuild_alt.setText(QtGui.QApplication.translate("LayerShufflerWin", "Use Rebuild for:", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_rebuildDirection_alt.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "Horizontal", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_rebuildDirection_alt.setItemText(1, QtGui.QApplication.translate("LayerShufflerWin", "Vertical", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_rendererSelectionDropdown_alt.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_rendererSelectionDropdown_alt.setItemText(1, QtGui.QApplication.translate("LayerShufflerWin", "Arnold", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_rendererSelectionDropdown_alt.setItemText(2, QtGui.QApplication.translate("LayerShufflerWin", "VRay", None, QtGui.QApplication.UnicodeUTF8))
            self.grpBox_arnold.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "Arnold", None, QtGui.QApplication.UnicodeUTF8))
            self.radioBtn_primaryArnold.setText(QtGui.QApplication.translate("LayerShufflerWin", "Direct/Indirect passes", None, QtGui.QApplication.UnicodeUTF8))
            self.radioBtn_secondaryArnold.setText(QtGui.QApplication.translate("LayerShufflerWin", "Only Direct/Indirect", None, QtGui.QApplication.UnicodeUTF8))
            self.grpBox_specular.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "Specular", None, QtGui.QApplication.UnicodeUTF8))
            self.label_directSpec.setText(QtGui.QApplication.translate("LayerShufflerWin", "Direct", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_directSpec.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.label_indirectSpec.setText(QtGui.QApplication.translate("LayerShufflerWin", "Indirect", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_indirectSpec.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.grpBox_diffuse.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "Diffuse", None, QtGui.QApplication.UnicodeUTF8))
            self.label_directDiffuse.setText(QtGui.QApplication.translate("LayerShufflerWin", "Direct", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_directDiffuse.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.label_indirectDiffuse.setText(QtGui.QApplication.translate("LayerShufflerWin", "Indirect", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_indirectDiffuse.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.grpBox_volume.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "Volume", None, QtGui.QApplication.UnicodeUTF8))
            self.label_directVolume.setText(QtGui.QApplication.translate("LayerShufflerWin", "Direct", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_directVolume.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.label_indirectVolume.setText(QtGui.QApplication.translate("LayerShufflerWin", "Indirect", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_indirectVolume.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.grpBox_coat.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "Coat", None, QtGui.QApplication.UnicodeUTF8))
            self.label_directCoat.setText(QtGui.QApplication.translate("LayerShufflerWin", "Direct", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_directCoat.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.label_indirectCoat.setText(QtGui.QApplication.translate("LayerShufflerWin", "Indirect", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_indirectCoat.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.grpBox_sss.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "SSS", None, QtGui.QApplication.UnicodeUTF8))
            self.label_directSss.setText(QtGui.QApplication.translate("LayerShufflerWin", "Direct", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_directSss.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.label_indirectSss.setText(QtGui.QApplication.translate("LayerShufflerWin", "Indirect", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_indirectSss.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.grpBox_transmission.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "Transmission", None, QtGui.QApplication.UnicodeUTF8))
            self.label_directTransmission.setText(QtGui.QApplication.translate("LayerShufflerWin", "Direct", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_directTransmission.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.label_indirectTransmission.setText(QtGui.QApplication.translate("LayerShufflerWin", "Indirect", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_indirectTransmission.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.grpBox_emission.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "Emission", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_emission.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.grpBox_emissionSecondary.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "Emission", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_emissionSecondary.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.grpBox_direct.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "Direct", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_direct.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.grpBox_indirect.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "Indirect", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_indirect.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.grpBox_vray.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "VRay", None, QtGui.QApplication.UnicodeUTF8))
            self.radioBtn_advancedVray.setText(QtGui.QApplication.translate("LayerShufflerWin", "Advanced", None, QtGui.QApplication.UnicodeUTF8))
            self.groupBox_selfIlluminationBasic.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "VRaySelfIllumination", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_selfIlluminationBasic.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.groupBox_causticsBasic.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "VRayCaustics", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_causticsBasic.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.groupBox_refraction.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "VRayRefraction", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_refraction.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.groupBox_specularBasic.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "VRaySpecular", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_specularBasic.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.groupBox_gi.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "VRayGlobalIllumination", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_gi.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.groupBox_reflection.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "VRayReflection", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_reflection.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.grpBox_lighting.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "VRayLighting", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_lighting.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.groupBox_atmosphereBasic.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "VRayAtmosphere", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_atmosphereBasic.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.groupBox_sss2basic.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "VRaySSS2", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_sss2basic.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.radioBtn_basicVray.setText(QtGui.QApplication.translate("LayerShufflerWin", "Basic", None, QtGui.QApplication.UnicodeUTF8))
            self.grpBox_lightingVrayAdvanced.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "Lighting", None, QtGui.QApplication.UnicodeUTF8))
            self.label_diffuseFIlter.setText(QtGui.QApplication.translate("LayerShufflerWin", "VRayDiffuseFilter", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_diffuseFilter.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.label_rawLighting.setText(QtGui.QApplication.translate("LayerShufflerWin", "VRayRawLighting", None, QtGui.QApplication.UnicodeUTF8))
            self.label_rawGi.setText(QtGui.QApplication.translate("LayerShufflerWin", "VRayRawGlobalIllumination", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_rawLighting.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_rawGi.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.grpBox_reflectionAdvanced.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "Reflection", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_reflectionFilter.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_rawReflection.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.label_rawReflection.setText(QtGui.QApplication.translate("LayerShufflerWin", "VRayRawReflection", None, QtGui.QApplication.UnicodeUTF8))
            self.label_reflectionFilter.setText(QtGui.QApplication.translate("LayerShufflerWin", "VRayReflectionFilter", None, QtGui.QApplication.UnicodeUTF8))
            self.grpBox_refractionAdvanced.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "Refraction", None, QtGui.QApplication.UnicodeUTF8))
            self.label_rawRefraction.setText(QtGui.QApplication.translate("LayerShufflerWin", "VRayRawRefraction", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_rawRefraction.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_refractionFilter.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.label_refractionFilter.setText(QtGui.QApplication.translate("LayerShufflerWin", "VRayRefractionFilter", None, QtGui.QApplication.UnicodeUTF8))
            self.grpBox_causticsAdvanced.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "VRayCaustics", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_causticsAdvanced.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.grpBox_atmosphereAdvanced.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "VRayAtmosphere", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_atmosphereAdvanced.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.grpBox_specularAdvanced.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "VRaySpecular", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_specularAdvanced.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.grpBox_sss2advanced.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "VRaySSS2", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_sss2advanced.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.grpBox_selfIlluminationAdvanced.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "VRaySelfIllumination", None, QtGui.QApplication.UnicodeUTF8))
            self.comboBox_selfIlluminationAdvanced.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None, QtGui.QApplication.UnicodeUTF8))
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_rendererRebuild), QtGui.QApplication.translate("LayerShufflerWin", "Rebuild Options", None, QtGui.QApplication.UnicodeUTF8))
            self.btn_recreateNode.setText(QtGui.QApplication.translate("LayerShufflerWin", "Recreate node", None, QtGui.QApplication.UnicodeUTF8))
            self.btn_showInfo.setText(QtGui.QApplication.translate("LayerShufflerWin", "Show info", None, QtGui.QApplication.UnicodeUTF8))
            self.btn_deleteEntry.setText(QtGui.QApplication.translate("LayerShufflerWin", "Delete entry", None, QtGui.QApplication.UnicodeUTF8))
            self.btn_deleteAll.setText(QtGui.QApplication.translate("LayerShufflerWin", "Delete All", None, QtGui.QApplication.UnicodeUTF8))
            self.label_nodesToAdd.setText(QtGui.QApplication.translate("LayerShufflerWin", "Nodes to add after Shuffle", None, QtGui.QApplication.UnicodeUTF8))
            self.btn_premultSandwich.setText(QtGui.QApplication.translate("LayerShufflerWin", "Premult Sandwich", None, QtGui.QApplication.UnicodeUTF8))
            self.btn_storeSelected.setText(QtGui.QApplication.translate("LayerShufflerWin", "Store selected nodes from Node Graph", None, QtGui.QApplication.UnicodeUTF8))
            self.btn_updateEntry.setText(QtGui.QApplication.translate("LayerShufflerWin", "Update Entry", None, QtGui.QApplication.UnicodeUTF8))
            self.grpBox_whichLayers.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "Which Layers", None, QtGui.QApplication.UnicodeUTF8))
            self.label_aovsSelection.setText(QtGui.QApplication.translate("LayerShufflerWin", "AOVs selection", None, QtGui.QApplication.UnicodeUTF8))
            self.btn_aovsSelection_selectAll.setText(QtGui.QApplication.translate("LayerShufflerWin", "Select All", None, QtGui.QApplication.UnicodeUTF8))
            self.btn_aovsSelection_clearSel.setText(QtGui.QApplication.translate("LayerShufflerWin", "Clear Selection", None, QtGui.QApplication.UnicodeUTF8))
            self.label_mainPassesSelection.setText(QtGui.QApplication.translate("LayerShufflerWin", "Main Passes selection", None, QtGui.QApplication.UnicodeUTF8))
            self.btn_mainPassesSelection_selectAll.setText(QtGui.QApplication.translate("LayerShufflerWin", "Select All", None, QtGui.QApplication.UnicodeUTF8))
            self.btn_mainPassesSelection_clearSel.setText(QtGui.QApplication.translate("LayerShufflerWin", "Clear Selection", None, QtGui.QApplication.UnicodeUTF8))
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_addNodes), QtGui.QApplication.translate("LayerShufflerWin", "Add Nodes", None, QtGui.QApplication.UnicodeUTF8))
            self.btn_spawnPreset.setText(QtGui.QApplication.translate("LayerShufflerWin", "Spawn Preset", None, QtGui.QApplication.UnicodeUTF8))
            self.btn_deletePreset.setText(QtGui.QApplication.translate("LayerShufflerWin", "Delete Preset", None, QtGui.QApplication.UnicodeUTF8))
            self.btn_savePreset.setText(QtGui.QApplication.translate("LayerShufflerWin", "Save selected nodes as Preset", None, QtGui.QApplication.UnicodeUTF8))
            self.label_presetName.setText(QtGui.QApplication.translate("LayerShufflerWin", "Preset Name:", None, QtGui.QApplication.UnicodeUTF8))
            self.btn_selectLastSpawn.setText(QtGui.QApplication.translate("LayerShufflerWin", "Select Last Spawn", None, QtGui.QApplication.UnicodeUTF8))
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_savedNodeTrees), QtGui.QApplication.translate("LayerShufflerWin", "Saved Node Trees", None, QtGui.QApplication.UnicodeUTF8))
        except:
            LayerShufflerWin.setWindowTitle(QtGui.QApplication.translate("LayerShufflerWin", "LayerShuffler", None))
            self.check_removeExrRestriction.setText(QtGui.QApplication.translate("LayerShufflerWin", "Skip EXR check", None))
            self.check_extendShuffled.setText(QtGui.QApplication.translate("LayerShufflerWin", "Extend Shuffled", None))
            self.btn_selectShuffled.setText(QtGui.QApplication.translate("LayerShufflerWin", "Select Last Shuffle", None))
            self.btn_shuffleAction.setText(QtGui.QApplication.translate("LayerShufflerWin", "Shuffle2", None))
            self.btn_mainPasses_selectAll.setText(QtGui.QApplication.translate("LayerShufflerWin", "Select All", None))
            self.btn_mainPasses_clearSel.setText(QtGui.QApplication.translate("LayerShufflerWin", "Clear Selection", None))
            self.lineEdit_mainPassesTitle_input.setText(QtGui.QApplication.translate("LayerShufflerWin", "Main Passes", None))
            self.btn_mainPasses_resetOrder.setText(QtGui.QApplication.translate("LayerShufflerWin", "Reset Order", None))
            self.lineEdit_aovsTitle_input.setText(QtGui.QApplication.translate("LayerShufflerWin", "AOVs", None))
            self.btn_aov_selectRemaining.setText(QtGui.QApplication.translate("LayerShufflerWin", "Select Remaining", None))
            self.btn_aov_clearSel.setText(QtGui.QApplication.translate("LayerShufflerWin", "Clear Selection", None))
            self.btn_aovs_resetOrder.setText(QtGui.QApplication.translate("LayerShufflerWin", "Reset Order", None))
            self.grpBox_extraOptions.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "Extra Options", None))
            self.label_backdropsColor.setText(QtGui.QApplication.translate("LayerShufflerWin", "Layer backdrops color:", None))
            self.btn_selectColor.setText(QtGui.QApplication.translate("LayerShufflerWin", "Select color", None))
            self.check_unlockShuffleOrdering.setText(QtGui.QApplication.translate("LayerShufflerWin", "Unlock Shuffle Ordering", None))
            self.check_selectionOnly.setText(QtGui.QApplication.translate("LayerShufflerWin", "Shuffle selected layers only", None))
            self.comboBox_rebuildDirection.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "Horizontal", None))
            self.comboBox_rebuildDirection.setItemText(1, QtGui.QApplication.translate("LayerShufflerWin", "Vertical", None))
            self.check_useRebuild.setText(QtGui.QApplication.translate("LayerShufflerWin", "Use Rebuild for:", None))
            self.comboBox_rendererSelectionDropdown.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.comboBox_rendererSelectionDropdown.setItemText(1, QtGui.QApplication.translate("LayerShufflerWin", "Arnold", None))
            self.comboBox_rendererSelectionDropdown.setItemText(2, QtGui.QApplication.translate("LayerShufflerWin", "VRay", None))
            self.label_nodeDIstanceMult.setText(QtGui.QApplication.translate("LayerShufflerWin", "Node Distance Multiplier", None))
            self.numField_nodeDistanceMult.setPrefix(QtGui.QApplication.translate("LayerShufflerWin", "x", None))
            self.grpBox_selNode.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "Selected Node", None))
            self.label_selNode.setText(QtGui.QApplication.translate("LayerShufflerWin", "N/A", None))
            self.btn_updateTarget.setText(QtGui.QApplication.translate("LayerShufflerWin", "Update", None))
            self.grpBox_fileName.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "File name", None))
            self.label_fileName.setText(QtGui.QApplication.translate("LayerShufflerWin", "N/A", None))
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_shuffler), QtGui.QApplication.translate("LayerShufflerWin", "Shuffler", None))
            self.check_useRebuild_alt.setText(QtGui.QApplication.translate("LayerShufflerWin", "Use Rebuild for:", None))
            self.comboBox_rebuildDirection_alt.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "Horizontal", None))
            self.comboBox_rebuildDirection_alt.setItemText(1, QtGui.QApplication.translate("LayerShufflerWin", "Vertical", None))
            self.comboBox_rendererSelectionDropdown_alt.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.comboBox_rendererSelectionDropdown_alt.setItemText(1, QtGui.QApplication.translate("LayerShufflerWin", "Arnold", None))
            self.comboBox_rendererSelectionDropdown_alt.setItemText(2, QtGui.QApplication.translate("LayerShufflerWin", "VRay", None))
            self.grpBox_arnold.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "Arnold", None))
            self.radioBtn_primaryArnold.setText(QtGui.QApplication.translate("LayerShufflerWin", "Direct/Indirect passes", None))
            self.radioBtn_secondaryArnold.setText(QtGui.QApplication.translate("LayerShufflerWin", "Only Direct/Indirect", None))
            self.grpBox_specular.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "Specular", None))
            self.label_directSpec.setText(QtGui.QApplication.translate("LayerShufflerWin", "Direct", None))
            self.comboBox_directSpec.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.label_indirectSpec.setText(QtGui.QApplication.translate("LayerShufflerWin", "Indirect", None))
            self.comboBox_indirectSpec.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.grpBox_diffuse.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "Diffuse", None))
            self.label_directDiffuse.setText(QtGui.QApplication.translate("LayerShufflerWin", "Direct", None))
            self.comboBox_directDiffuse.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.label_indirectDiffuse.setText(QtGui.QApplication.translate("LayerShufflerWin", "Indirect", None))
            self.comboBox_indirectDiffuse.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.grpBox_volume.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "Volume", None))
            self.label_directVolume.setText(QtGui.QApplication.translate("LayerShufflerWin", "Direct", None))
            self.comboBox_directVolume.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.label_indirectVolume.setText(QtGui.QApplication.translate("LayerShufflerWin", "Indirect", None))
            self.comboBox_indirectVolume.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.grpBox_coat.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "Coat", None))
            self.label_directCoat.setText(QtGui.QApplication.translate("LayerShufflerWin", "Direct", None))
            self.comboBox_directCoat.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.label_indirectCoat.setText(QtGui.QApplication.translate("LayerShufflerWin", "Indirect", None))
            self.comboBox_indirectCoat.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.grpBox_sss.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "SSS", None))
            self.label_directSss.setText(QtGui.QApplication.translate("LayerShufflerWin", "Direct", None))
            self.comboBox_directSss.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.label_indirectSss.setText(QtGui.QApplication.translate("LayerShufflerWin", "Indirect", None))
            self.comboBox_indirectSss.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.grpBox_transmission.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "Transmission", None))
            self.label_directTransmission.setText(QtGui.QApplication.translate("LayerShufflerWin", "Direct", None))
            self.comboBox_directTransmission.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.label_indirectTransmission.setText(QtGui.QApplication.translate("LayerShufflerWin", "Indirect", None))
            self.comboBox_indirectTransmission.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.grpBox_emission.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "Emission", None))
            self.comboBox_emission.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.grpBox_emissionSecondary.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "Emission", None))
            self.comboBox_emissionSecondary.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.grpBox_direct.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "Direct", None))
            self.comboBox_direct.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.grpBox_indirect.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "Indirect", None))
            self.comboBox_indirect.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.grpBox_vray.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "VRay", None))
            self.radioBtn_advancedVray.setText(QtGui.QApplication.translate("LayerShufflerWin", "Advanced", None))
            self.groupBox_selfIlluminationBasic.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "VRaySelfIllumination", None))
            self.comboBox_selfIlluminationBasic.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.groupBox_causticsBasic.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "VRayCaustics", None))
            self.comboBox_causticsBasic.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.groupBox_refraction.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "VRayRefraction", None))
            self.comboBox_refraction.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.groupBox_specularBasic.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "VRaySpecular", None))
            self.comboBox_specularBasic.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.groupBox_gi.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "VRayGlobalIllumination", None))
            self.comboBox_gi.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.groupBox_reflection.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "VRayReflection", None))
            self.comboBox_reflection.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.grpBox_lighting.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "VRayLighting", None))
            self.comboBox_lighting.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.groupBox_atmosphereBasic.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "VRayAtmosphere", None))
            self.comboBox_atmosphereBasic.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.groupBox_sss2basic.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "VRaySSS2", None))
            self.comboBox_sss2basic.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.radioBtn_basicVray.setText(QtGui.QApplication.translate("LayerShufflerWin", "Basic", None))
            self.grpBox_lightingVrayAdvanced.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "Lighting", None))
            self.label_diffuseFIlter.setText(QtGui.QApplication.translate("LayerShufflerWin", "VRayDiffuseFilter", None))
            self.comboBox_diffuseFilter.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.label_rawLighting.setText(QtGui.QApplication.translate("LayerShufflerWin", "VRayRawLighting", None))
            self.label_rawGi.setText(QtGui.QApplication.translate("LayerShufflerWin", "VRayRawGlobalIllumination", None))
            self.comboBox_rawLighting.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.comboBox_rawGi.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.grpBox_reflectionAdvanced.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "Reflection", None))
            self.comboBox_reflectionFilter.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.comboBox_rawReflection.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.label_rawReflection.setText(QtGui.QApplication.translate("LayerShufflerWin", "VRayRawReflection", None))
            self.label_reflectionFilter.setText(QtGui.QApplication.translate("LayerShufflerWin", "VRayReflectionFilter", None))
            self.grpBox_refractionAdvanced.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "Refraction", None))
            self.label_rawRefraction.setText(QtGui.QApplication.translate("LayerShufflerWin", "VRayRawRefraction", None))
            self.comboBox_rawRefraction.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.comboBox_refractionFilter.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.label_refractionFilter.setText(QtGui.QApplication.translate("LayerShufflerWin", "VRayRefractionFilter", None))
            self.grpBox_causticsAdvanced.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "VRayCaustics", None))
            self.comboBox_causticsAdvanced.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.grpBox_atmosphereAdvanced.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "VRayAtmosphere", None))
            self.comboBox_atmosphereAdvanced.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.grpBox_specularAdvanced.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "VRaySpecular", None))
            self.comboBox_specularAdvanced.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.grpBox_sss2advanced.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "VRaySSS2", None))
            self.comboBox_sss2advanced.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.grpBox_selfIlluminationAdvanced.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "VRaySelfIllumination", None))
            self.comboBox_selfIlluminationAdvanced.setItemText(0, QtGui.QApplication.translate("LayerShufflerWin", "None", None))
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_rendererRebuild), QtGui.QApplication.translate("LayerShufflerWin", "Rebuild Options", None))
            self.btn_recreateNode.setText(QtGui.QApplication.translate("LayerShufflerWin", "Recreate node", None))
            self.btn_showInfo.setText(QtGui.QApplication.translate("LayerShufflerWin", "Show info", None))
            self.btn_deleteEntry.setText(QtGui.QApplication.translate("LayerShufflerWin", "Delete entry", None))
            self.btn_deleteAll.setText(QtGui.QApplication.translate("LayerShufflerWin", "Delete All", None))
            self.label_nodesToAdd.setText(QtGui.QApplication.translate("LayerShufflerWin", "Nodes to add after Shuffle", None))
            self.btn_premultSandwich.setText(QtGui.QApplication.translate("LayerShufflerWin", "Premult Sandwich", None))
            self.btn_storeSelected.setText(QtGui.QApplication.translate("LayerShufflerWin", "Store selected nodes from Node Graph", None))
            self.btn_updateEntry.setText(QtGui.QApplication.translate("LayerShufflerWin", "Update Entry", None))
            self.grpBox_whichLayers.setTitle(QtGui.QApplication.translate("LayerShufflerWin", "Which Layers", None))
            self.label_aovsSelection.setText(QtGui.QApplication.translate("LayerShufflerWin", "AOVs selection", None))
            self.btn_aovsSelection_selectAll.setText(QtGui.QApplication.translate("LayerShufflerWin", "Select All", None))
            self.btn_aovsSelection_clearSel.setText(QtGui.QApplication.translate("LayerShufflerWin", "Clear Selection", None))
            self.label_mainPassesSelection.setText(QtGui.QApplication.translate("LayerShufflerWin", "Main Passes selection", None))
            self.btn_mainPassesSelection_selectAll.setText(QtGui.QApplication.translate("LayerShufflerWin", "Select All", None))
            self.btn_mainPassesSelection_clearSel.setText(QtGui.QApplication.translate("LayerShufflerWin", "Clear Selection", None))
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_addNodes), QtGui.QApplication.translate("LayerShufflerWin", "Add Nodes", None))
            self.btn_spawnPreset.setText(QtGui.QApplication.translate("LayerShufflerWin", "Spawn Preset", None))
            self.btn_deletePreset.setText(QtGui.QApplication.translate("LayerShufflerWin", "Delete Preset", None))
            self.btn_savePreset.setText(QtGui.QApplication.translate("LayerShufflerWin", "Save selected nodes as Preset", None))
            self.label_presetName.setText(QtGui.QApplication.translate("LayerShufflerWin", "Preset Name:", None))
            self.btn_selectLastSpawn.setText(QtGui.QApplication.translate("LayerShufflerWin", "Select Last Spawn", None))
            self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_savedNodeTrees), QtGui.QApplication.translate("LayerShufflerWin", "Saved Node Trees", None))
