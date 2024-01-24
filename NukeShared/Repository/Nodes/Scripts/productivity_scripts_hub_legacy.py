# -*- coding: utf-8 -*-
# productivity_scripts_hub v2.10
# philhub 2012-2015
# http://www.nukepedia.com/python/nodegraph/productivity_scripts_hub
# a set (or a hub ;-) of python scripts to help organising, working in Nuke.
# Among others there is :
# "copy node and keep inputs" which is formerly coded for the link_node
# but is also very handy for multi-connections nodes (Merge, Switch,...)
# link node handles now TCL driven paths
# 
# for node in nuke.allNodes(group=nuke.root(),recurseGroups=True)


import nuke, nukescripts
import webbrowser, os, re, inspect, subprocess, math, ast
import os.path as op
# import nukescripts.rollingAutoSave     # built-in python script in C:\Program Files\Nuke6.3v5\plugins\nukescripts
# from mat3 import *
if int(nuke.NUKE_VERSION_STRING.split(".")[0])<11:
    import PySide.QtGui as QtGui
else:
    import PySide2.QtGui as QtGui
from inspect import currentframe, getframeinfo

library = os.path.basename(inspect.getfile(inspect.currentframe())).split(".")[0]

menubar = nuke.menu("Nuke")
menu_hub = menubar.addMenu("&_hub")

try:
    import CmdLineRender
    menu_hub.addCommand('CL Render', 'CmdLineRender.CLrender(nuke.selectedNodes())')
except Exception:
    print("CmdLineRender can't be imported")

try:
    import backdrop_hub
except Exception:
    print("backdrop_hub can't be imported")

try:
    from jad_pipe.utils.ovmApiForComp import OvmApiForComp
except:
    print("ovmApiForComp can't be imported")

def warningOnOutsideConnectedNodes():
    outside_connected_nodes = []
    for group in nuke.allNodes("Group"):
        if "CatchError" not in group.name():
            with group:
                for node in nuke.allNodes():
                    if node.input(0)!=None:
                        if node.input(0).fullName().split(".")[0]!=group.name():
                            outside_connected_nodes.append(node.fullName())
    if outside_connected_nodes!=[]:
        message = "Those nodes have connections made outside their groups.\n You MUST correct them otherwise it will make your file corrupted.\n Like the lovely blank error message next time you open your comp.\nThey have been opened in your properties panel.\n\n"
        for node_name in outside_connected_nodes:
            nuke.show(nuke.toNode(node_name))
            message+=node_name+"\n"
        print(message)
        nuke.message( "<font size=4 color=\'red\'>"+message+"</font>" )

def disconnectInputsOutsideGroups():
    '''Node can be connected outside a group,
    that connection is shown in the group as a infinite connection,
    and makes the comp bug (blank error), so this function is meant to avoid that'''
    for Group in nuke.allNodes("Group"):
        with Group:
            all_nodes = nuke.allNodes()
            for node in all_nodes:
                for Input in node.dependencies(nuke.INPUTS | nuke.HIDDEN_INPUTS):
                    if Input not in all_nodes:
                        for input_number in range(node.inputs()):
                            node_input = node.input(input_number)
                            if node_input!=None:
                                print(node.input(input_number).name())
                                if node_input.name() == Input.name():
                                    message = node.name() + " nested in the " + Group.name() + " group, has his input number " + str(input_number) + ", an infinite connection outside the group.\n As it makes 'blank error message', this connection have been removed"
                                    nuke.tprint( message )
                                    # nuke.message( message )
                                    node.setInput(input_number, None)

def checkConnectedLinks():
    link_not_connected_list = []
    link_reconnected_list = []
    links_list = nuke.allNodes("PostageStamp")
    links_list.extend( nuke.allNodes("NoOp") )
    for node in links_list:
        if "LNK_" in node.name():
            if ( node.input(0)==None or node.input(0).name().split("LBL_")[-1] not in node.name() ) and not "whole" in node.name() and not "teeth" in node.name() and not "windshield" in node.name() and not "eyelids" in node.name() and not "tyres_rubber" in node.name() and not "tongue" in node.name() and not "body_metal" in node.name() and not "wings_cloth" in node.name():  
                # above is a RKZ specific
                nukescripts.clear_selection_recursive()
                node.setSelected(True)
                success = reconnectSelected(_silent=True)
                if success:
                    link_reconnected_list.append( node.name() )
                else:
                    if node.dependent()!=[]:
                        link_not_connected_list.append( node.name() )
    if link_reconnected_list!=[]:
        nuke.message( repr(link_reconnected_list) + " have been reconnected.")
    if link_not_connected_list!=[]:
        nuke.message( repr(link_not_connected_list) + " cannot be reconnected, please fix it.\nThose links have been opened in the property bin")
 
def checkPSDlayersCount():
    psd_layers_count = 0
    for psd in nuke.allNodes("Read"):
        if ".psd" in psd["file"].value():
            psd_layers_count += len(nuke.layers(psd))
    if psd_layers_count>40:
        nuke.message("Warning !\nYou've got PSD files in your comp that add "+str(psd_layers_count*4)+ " channels.\nRemember that nuke cannot handle more than 1023 channels (341 layers)")


def fetchGeoMeshSelection():
    for ReadGeo in nuke.allNodes(group=nuke.root(),recurseGroups=True):
        if ReadGeo.Class()=="ReadGeo2":
            if "scene_view" in ReadGeo.knobs() and "shapesSel" in ReadGeo.knobs():
                print(ReadGeo.name(), ReadGeo["shapesSel"].value())
                ReadGeo["scene_view"].setSelectedItems( ReadGeo["shapesSel"].value().split("\n") )

def keepGeoMeshSelection():
    for ReadGeo in nuke.allNodes(group=nuke.root(),recurseGroups=True):
        if ReadGeo.Class()=="ReadGeo2":
            if "scene_view" in ReadGeo.knobs():
                if "shapesSel" not in ReadGeo.knobs():
                    shapesSel_knob = nuke.Multiline_Eval_String_Knob("shapesSel", "shapesSel")
                    ReadGeo.addKnob( shapesSel_knob )
                ReadGeo["shapesSel"].setValue( "\n".join(ReadGeo["scene_view"].getSelectedItems()) )

def warnBadWrites():
    if "compo_" in nuke.root().name():
        for Write in nuke.allNodes("Write"):
            if not Write["disable"].value() and ".%0" not in Write["file"].value() and "#" not in Write["file"].value() and ".mov" not in Write["file"].value() and ".avi" not in Write["file"].value():
                nuke.show(Write)
                nuke.message(Write.name()+" doesn't have padding, so it will block your render.\nPlease disable it or delete it.)")

def fixLNKnames():
    for NoOp in nuke.allNodes(group=nuke.root(),recurseGroups=True):
        if NoOp.Class()=="NoOp":
            if "LNK_" in NoOp.name():
                if NoOp.name()[-1]!="_" and not NoOp.name()[-1].isdigit():
                    NoOp.setName( NoOp.name()+"_" )
                cara_after_underscore = NoOp.name().split("_")[-1]
                if cara_after_underscore!="" and not cara_after_underscore.isdigit():  # so it's not well named
                    if not cara_after_underscore.isdigit():
                        for i in range(3):
                            NoOp.setName( NoOp.name()[:-1] )
                            if not NoOp.name()[-1].isdigit():
                                break
                    NoOp.setName( NoOp.name()+"_" )

def checkLBLconformity():
    for NoOp in nuke.allNodes(group=nuke.root(),recurseGroups=True):
        if NoOp.Class()=="NoOp":
            if "LBL_" in NoOp.name() and not NoOp.name().endswith("_"):
                nuke.show(NoOp)
                nuke.message("The node "+NoOp.name()+ " is really really BAAAD ! It must be a duplicated 'Label node' that is not meant to exist.\nIt's almost sure that you have to delete it and maybe nodes connected to.\nIf you don't understand this message ask Philippe or your comp sup.")

def checkShuffleLinkName():
    for node in nuke.allNodes(group=nuke.root(),recurseGroups=True):
        if node.name().startswith("Sh_") and node["tile_color"].value()==1041247999:  # if node is dark purple thus it is a shuffle link and have to be check. Is the name is ok according to the selected Layer ?
            if node["in"].value().split(".")[0] not in node.fullName():
                nuke.message(node.fullName() + " hasn't the layer selected ( "+ node["in"].value() +" ) according to his name.\n You should renamed it ! (it has been opened in the properties bin.)")
                nuke.show( node )

def OnScriptLoad():
    fetchGeoMeshSelection()
    checkLBLconformity()
    # nuke.addOnCreate(onViewerCreate, nodeClass="Viewer")
# nuke.addOnScriptLoad(OnScriptLoad)

def OnScriptSave():
    if "compo_template" in nuke.root().name():
        checkPSDlayersCount()
    disconnectInputsOutsideGroups()
    warnBadWrites()
    fixLNKnames()

    for write in nuke.allNodes("Write"):
        if write["file"].value()=="":
            nuke.message( write.name() + " write Node deleted because his 'file' field was empty !")
            nuke.delete(write)
    try:
        statinfo = os.stat(nuke.root().name())
        num = float(statinfo.st_size)/1024/1024
        comp_size_meg = "%3.1f" % (num)
        if num>16:
            nuke.message("Before saving, your comp weighs more than 16 Meg, resave it to check if that weight persist.\nIf so, it can comes from bad characters,\n so check it")
    except:
        pass  
    if nuke.root()['proxy'].value():
        bad = True
        for write in nuke.allNodes("Write"):
            if write['proxy'].value()!="":
                print(write['proxy'].value())
                bad = False
        if bad:
            nuke.message("Warning you're in PROXY mode and none of your Write Nodes have their proxy paths filled.\nThe Comp will throw an error at render time :-/")
nuke.addOnScriptSave(OnScriptSave)

def onViewerCreate():
    viewer = nuke.thisNode()
    if viewer != None and viewer.Class()=="Viewer":
        context = returnContextGroup()
        if context!="root":
            viewer.setName(context+"_viewer")


########################################################################################################################################################################
######################################################################                                  ################################################################
######################################################################   AUTO CONNECT NODES CALLBACKS   ################################################################
######################################################################                                  ################################################################
########################################################################################################################################################################

def ppmask_CB():
    # print("ppmask_callback"
    fullname = nuke.thisNode().fullName()
    if "." in fullname:
        context = fullname.split(".")[0]
    else:
        context = "root"
    # print("context ::: "+context)
    if nuke.thisKnob().name()=="QuickLayerLink":
        if os.getenv('TT_PROD_TRIG') in ["dew","fam"]:
            LBL_Input1_ = nuke.toNode("LBL_Input1_")
            if context!="root" and nuke.thisNode().input(0)==None and LBL_Input1_:
                # print("----------++"+nuke.thisNode().name())
                with nuke.toNode(context):
                    thisNode = nuke.toNode(context+"."+nuke.thisNode().name())
                    nukescripts.clear_selection_recursive()
                    link = createLinkContainer(LBL_Input1_, show=False)
                    link.setInput(0, LBL_Input1_)
                    link.setName( LBL_Input1_.name().replace("LBL_","LNK_") )
                    addLinkDressing(link)
                    link.setXYpos(thisNode.xpos(), thisNode.ypos()-50)
                    thisNode.setInput(0, nuke.toNode(context+"."+link.name()))
            if "Pw" in nuke.thisKnob().value():
                nuke.thisNode()["in"].setValue("tech_Pw")
            elif "pRef" in nuke.thisKnob().value():
                nuke.thisNode()["in"].setValue("tech_pRef")
        else:
            layer = nuke.thisNode()["QuickLayerLink"].value()
            if layer=="ANY":
                nuke.thisNode()["hide_input"].setValue(False)
            else:
                nuke.thisNode()["hide_input"].setValue(True)
                layer = layer.replace(" ","_")
                # label = context+"."+"LBL_"+layer.replace("pRef","pref")+"_"
                label = context+"."+"LBL_"+layer+"_"
                if not nuke.exists(label):
                    createInputAndLabelFromList([layer], context)
                nuke.thisNode().setInput(0,nuke.toNode(label))
            nuke.thisNode().setSelected(True)

def cryptoTT_CB(node_name="",layer=""):
    if layer!="" and node_name!="":
        knob_name = "Layer"
        thisNode = nuke.toNode(node_name)
    else:
        try:
            knob_name = nuke.thisKnob().name()
        except:
            knob_name = ""

    if knob_name=="Layer":
        if node_name=="":
            thisNode = nuke.thisNode()
        if thisNode.name()!="Root":
            thisNode["hide_input"].setValue(True)
            if layer=="":
                layer = thisNode["Layer"].value()
            if layer=="undefined":
                return
            if "." in node_name:
                context = node_name.split(".")[0]
            else:
                try:
                    context = returnContextGroupFromCB()
                except:
                    nuke.message("Warning, productivity_scripts_hub is not loaded, so automatic input add in group won't work")
                    context = "root"
            if context!="root":
                link_raw_names_list = returnCryptoNeededRawNames(context, [layer])
                createInputAndLabelFromList(link_raw_names_list, context)
                # cleanUnusedInputs(context)
            thisNode.setInput(0,nuke.toNode(context+".LBL_"+layer+"_cryptomatte_path_"))
            thisNode.setInput(1,nuke.toNode(context+".LBL_"+layer+"_cryptomatte_material_"))
            thisNode.setInput(2,nuke.toNode(context+".LBL_"+layer+"_cryptomatte_asset_"))
            thisNode.setInput(3,nuke.toNode(context+".LBL_"+layer+"_cryptomatte_shader_"))


def putOnChangedCB():
    if thisNode.name()!="Root":
        print("thisNode.name() : "+thisNode.name())
        print("thisNode.Class() : "+thisNode.Class())
        print("cryptoTT_CB ----")
        layer = nuke.thisNode()["Layer"].value()
        nuke.thisNode()["knobChanged"].setValue("productivity_scripts_hub.cryptoTT_CB()")

def copyToNetClipboard():
    try:
        net_clipboard = nuke.toNode("preferences")["net_clipboard"].value()
        nuke.nodeCopy(net_clipboard)
        print("Copied to :", net_clipboard)
    except:
        configureNetClipboard()
        # nuke.message("The path where to share clipboard with other users haven't been set\nPlease use the 'Configure Network Clipboard' command.")
        
def pasteFromNetClipboard():
    try:
        net_clipboard = nuke.toNode("preferences")["net_clipboard"].value()
        nuke.nodePaste(net_clipboard)
        print("Copied from :", net_clipboard)
    except:
        configureNetClipboard()

def configureNetClipboard():
    netboard = "//serveur/netboard.nk"
    try:
        print(nuke.toNode("preferences")['hubToolsTab'].value())
        print(nuke.toNode("preferences")['net_clipboard'].value())
    except:
        hubToolsKnob = nuke.Tab_Knob('hubToolsTab', 'hub Tools')
        nuke.toNode("preferences").addKnob(hubToolsKnob)
        netClipboardKnob = nuke.File_Knob('net_clipboard', 'Net Clipboard')
        nuke.toNode("preferences").addKnob(netClipboardKnob)
        nuke.toNode("preferences")['net_clipboard'].setValue(netboard)
    nuke.show(nuke.toNode("preferences"), "forceFloat")
    nuke.message("Go to the 'hub tools' tab to choose a path where to share the clipboard.\nClick 'Save Prefs' to keep the changes.")

menu_hub.addCommand("Network Clipboard/Copy to Network Clipboard", library+".copyToNetClipboard()","Alt+shift+c")
menu_hub.addCommand("Network Clipboard/Paste from Network Clipboard", library+".pasteFromNetClipboard()","Alt+shift+v")
menu_hub.addCommand("Network Clipboard/Configure Network Clipboard", library+".configureNetClipboard()")

    
# The "Channel" menu
toolbar = nuke.menu("Nodes")
m = toolbar.addMenu("Channel", "ToolbarChannel.png")
# m.addCommand("Shuffle", "nuke.createNode(\"Shuffle\")", icon="Shuffle.png")
m.addCommand("ShuffleCopy", "nuke.createNode(\"ShuffleCopy\")", "shift+k",  icon="ShuffleCopy.png")

# menu_hub = nuke.menu("Nodes").menu("ToolSets").addMenu("shortcuts")
def plusNode():
    sel = nuke.selectedNodes()
    if sel!=[]:
        if sel[0].Class()=="Merge2":
            sel[0]["operation"].setValue("plus")
            return
    nuke.createNode("Merge2", "operation plus", inpanel=False)
menu_hub.addCommand("Shortcuts/Plus", library+".plusNode()", "Shift+p")
def multiplyNode():
    sel = nuke.selectedNodes()
    if sel!=[]:
        if sel[0].Class()=="Merge2":
            sel[0]["operation"].setValue("multiply")
            return

    nuke.createNode("Merge2", "operation multiply", inpanel=False)
menu_hub.addCommand("Shortcuts/Multiply", library+".multiplyNode()", "Shift+m")
def stencilNode():
    sel = nuke.selectedNodes()
    if sel!=[]:
        if sel[0].Class()=="Merge2":
            sel[0]["operation"].setValue("stencil")
            return
    nuke.createNode("Merge2", "operation stencil", inpanel=False)
menu_hub.addCommand("Shortcuts/Stencil", library+".stencilNode()", "Ctrl+m")
def copyNode():
    sel = nuke.selectedNodes()
    if sel!=[]:
        if sel[0].Class()=="Merge2":
            sel[0]["operation"].setValue("copy")
            return
    nuke.createNode("Merge2", "operation copy", inpanel=False)
menu_hub.addCommand("Shortcuts/Copy", library+".copyNode()", "Ctrl+Shift+m")
def fromNode():
    sel = nuke.selectedNodes()
    if sel!=[]:
        if sel[0].Class()=="Merge2":
            sel[0]["operation"].setValue("from")
            return
    nuke.createNode("Merge2", "operation from", inpanel=False)
menu_hub.addCommand("Shortcuts/From", library+".fromNode()", "Ctrl+Shift+Alt+m")
def overNode():
    sel = nuke.selectedNodes()
    if sel!=[]:
        if sel[0].Class()=="Merge2":
            sel[0]["operation"].setValue("over")
            return
    nuke.createNode("Merge2", "operation over", inpanel=False)
menu_hub.addCommand("Shortcuts/Over", library+".overNode()", "Shift+Alt+m")

menu_hub.addCommand("Shortcuts/Reformat", "nuke.createNode(\"Reformat\", inpanel=True)","shift+r")
menu_hub.addCommand("Shortcuts/FrameHold", "nuke.createNode(\"FrameHold\", inpanel=True)","shift+h")
menu_hub.addCommand("Shortcuts/Tracker", "nuke.createNode(\"Tracker4\")","Shift+t")
menu_hub.addCommand("Shortcuts/ShuffleCopy", "nuke.createNode(\"ShuffleCopy\")","Shift+k")



# menu_hub.addCommand("AutoCrop", "nukescripts.autocrop()", icon="AutoCrop.png")

menu_hub.addMenu("Misc")

        
def CustomAutoCrop():
    """The CurveTool AutoCrop results are copied into a Crop
    node attached to each selected node.
    If script executed only on 1 frame, if it was previously executed it adds keyframe to previously created crop"""
    ask = nuke.ask("Process all frames ?")
    if ask:
        first = int(nuke.root()["first_frame"].value())
        last = int(nuke.root()["last_frame"].value())
    else:
        first = nuke.frame()
        last = nuke.frame()
    
    sel = nuke.selectedNodes()

    nukescripts.clear_selection_recursive()
    for node in sel:
        node.setSelected(True)
        autocropper = nuke.createNode("CurveTool",  '''operation 0 ROI {0 0 input.width input.height} Layer "rgba" label "Processing Crop..." selected true''', False)
        nuke.executeMultiple([autocropper,], ([first, last, 1],))
        autocropper.setSelected(True)

        exist = False
        if first==last:
            for child in autocropper.dependent():
                if "AutoCrop" in child['label'].value():
                    crop_node = child
                    exist = True
        if not exist:
            crop_node = nuke.createNode("Crop", "label AutoCrop", False)

        crop_knob = crop_node["box"]
        autocropbox = autocropper["autocropdata"]
        
        if first==last:
            crop_knob.setKeyAt( nuke.frame() )
            crop_knob.setValue( autocropbox.value() )
        else:
            crop_knob.copyAnimations(autocropbox.animations())

        crop_node.knob("indicators").setValue(1)
        nukescripts.clear_selection_recursive()
        autocropper.setSelected(True)
        nukescripts.node_delete()
        nukescripts.clear_selection_recursive()
        crop_node.setSelected(True)
        nuke.autoplace(crop_node)
        crop_node.setSelected(False)
        crop_node.showControlPanel()
        crop_node.setName("Crop_from_" + node.name() + "_")
    for node in sel:
        node.setSelected(True)
        
menu_hub.addCommand("Misc/Custom AutoCrop", library+".CustomAutoCrop()", icon="AutoCrop.png")


def setProjectBoundsFromRead():
    try:
        sel = nuke.selectedNode()
    except Exception:
        nuke.message("Please select a Read Node")
        return
    if sel.Class()=="Read":
        nuke.root()['first_frame'].setValue( sel['first'].value() )
        nuke.root()['last_frame'].setValue( sel['last'].value() )
        nuke.root()['format'].setValue( sel['format'].value() )
    else:
        nuke.message("Please select a Read Node")
menu_hub.addCommand("Misc/set ProjectBounds From Read", library+".setProjectBoundsFromRead()", "ctrl+alt+shift+p")
        
def setReadBoundsFromProject():
    try:
        selNodes = nuke.selectedNodes()
    except Exception:
        nuke.message("Please select one or mutliple Read Nodes")
        return
    for sel in selNodes():
        if sel.Class()=="Read":
            sel['first'].setValue( int(nuke.root()['first_frame'].value()) )
            sel['last'].setValue( int(nuke.root()['first_frame'].value()) )
        else:
            nuke.message("Please select one or mutliple Read Nodes")
menu_hub.addCommand("Misc/set Selected ReadBounds From Project", library+".setReadBoundsFromProject()")

def staticFrameToMiddleFrame():
    first = int(nuke.knob("first_frame"))
    last = int(nuke.knob("last_frame"))
    for n in nuke.allNodes(group=nuke.root(),recurseGroups=True):
        if n.Class()=="Read":
            n['postage_stamp_frame'].setValue((last-first)/2+first)
#menu_hub.addCommand("Misc/staticFrameToMiddleFrame", library+".staticFrameToMiddleFrame()", "ctrl+alt+shift+f")

def connectMaskNgetName(_nodesList):
    if len(_nodesList) != 2:
        nuke.message("Must have exactly 2 nodes selected")
    else:
        node = _nodesList[1]
        mask = _nodesList[0]
        node.setInput(1, mask)
        # mask_name = mask['label'].evaluate()
        mask_name = None
        if mask_name == None:
            try:
                mask_name = ("_").join( mask['name'].value().split('_')[1:] )   # remove first part before "_"
                if mask_name=="":
                    mask_name = mask['name'].value()
            except Exception:
                mask_name = mask['name'].value()
        node.setName( node['name'].value().split('_')[0] + '_' + mask_name )
menu_hub.addCommand("Misc/connectMaskNgetName", library+".connectMaskNgetName(nuke.selectedNodes())", "alt+shift+y")

def toggleGUI(_nodes=[]):
    if _nodes!=[]:
        for node in _nodes:
            if node['disable'].hasExpression():
                if node['disable'].toScript()=='{"\$gui"}':
                    node['disable'].clearAnimated()
                    node['disable'].setValue(False)
                    node['note_font_color'].setValue(0)
                else:
                    nuke.message("You already have an expression on this knob, but not related to $gui.\n If you really want to delete it, do it yourself !")
            else:
                node['disable'].setExpression("$gui")
                node['note_font_color'].setValue(7405567)
    else:
        for node in nuke.allNodes("VectorBlur"):
            if node["disable"].toScript()== '{"\$gui"}':
                node['disable'].clearAnimated()
                node['disable'].setValue(False)
            elif node["disable"].toScript()== "false":
                node["disable"].fromScript('{"\$gui"}')
menu_hub.addCommand("Misc/toggleGUI", library+".toggleGUI(nuke.selectedNodes())", "ctrl+alt+shift+g")



def displayGUInodes():
    list = []
    for node in nuke.allNodes(group=nuke.root(),recurseGroups=True):
        for key in node.knobs():
            if "$gui" in node[key].toScript():
                list.append(node.name())
    print("Nodes which have '$gui' expression : " + repr(list))
    if len(list)>10:
        nuke.toNode("preferences")["maxPanels"].setValue(len(list))
    for node_name in list:
        nuke.show( nuke.toNode(node_name) )
    nuke.message("Nodes which have '$gui' expression : \n" + repr(list) + "\nsee it also in script editor")
menu_hub.addCommand("Misc/displayGUInodes", library+".displayGUInodes()")

def ClosePropertiesButLast(n) :
    p = nuke.toNode("preferences")
    max = p['maxPanels'].value()
    p['maxPanels'].setValue(n)
    p['maxPanels'].setValue(max)
menu_hub.addCommand("Misc/ClosePropertiesButLast", library+".ClosePropertiesButLast(1)","Alt+z")
menu_hub.addCommand("Misc/ClosePropertiesBut2Last", library+".ClosePropertiesButLast(2)","Alt+Shift+z")

def openLabeledNodes():
    class openLabeledNodesDIALOG(nukescripts.PythonPanel):
            def __init__(self):
                nukescripts.PythonPanel.__init__(self, ' Open Specified Labeled Nodes')
                self.SpecifiedLabeledKnob = nuke.String_Knob('SpecifiedLabeled', 'Specified Labeled')
                self.addKnob(self.SpecifiedLabeledKnob)
                # self.tutoKnob = nuke.Text_Knob("Tuto", "Move cursor over line to have more info")
                # self.addKnob(self.tutoKnob)
                self.SpecifiedLabeledKnob.setTooltip("(Open each of these nodes,\nallow to navigate through them using the top left circle button\nIt's also useful in conjonction with the 'set as retake' tool)")
                
    p = openLabeledNodesDIALOG()
    p.SpecifiedLabeledKnob.setValue( "retake" )
    result = p.showModalDialog()
    if not result: return
    specifiedLabeled = p.SpecifiedLabeledKnob.value()
    for node in nuke.allNodes(group=nuke.root(),recurseGroups=True):
        if specifiedLabeled in node['label'].value():
            nuke.show(node)
menu_hub.addCommand("Misc/Open Specified Labeled Nodes", library+".openLabeledNodes()","Ctrl+Shift+Alt+/")

def goToMiddleFrame():
    first = nuke.root()["first_frame"].value()
    last = nuke.root()["last_frame"].value()
    if last%2==0:
        nuke.frame( (last-first)/2+1 )
    else:
        nuke.frame( (last-first)/2+1 )
menu_hub.addCommand("Misc/Go To Middle Frame", library+".goToMiddleFrame()", "Ctrl+Shift+Alt+Y")

def checkBboxSize():
    sel = nuke.selectedNodes()
    too_big_ratio = 2
    # nuke.getInput()
    if sel==[]:
        sel = nuke.allNodes()
        # sel = nuke.allNodes(group=nuke.root(),recurseGroups=True)
    too_big_bbox_list = []
    for node in sel:
        if node.Class()!="BackdropNode":
            if -node.bbox().x()>node.width() or node.bbox().w()>2*node.width() or node.bbox().h()>2*node.height() or -node.bbox().y()>node.height():
                too_big_bbox_list.append(node)
    node_to_remove_bbox_list = []
    for node in too_big_bbox_list:
            if node.input(0) in too_big_bbox_list:
                node_to_remove_bbox_list.append( node )
    for node in node_to_remove_bbox_list:
        too_big_bbox_list.remove( node )
    for node in too_big_bbox_list:
        nuke.show(node)
    if len(too_big_bbox_list)>0:
        message = "Those opened nodes have their bbox doubled at least one direction from the node's rez : \n"+repr(too_big_bbox_list)
        print(message)
        nuke.message( message )

menu_hub.addCommand("Misc/Check Bbox Size of Selected Nodes", library+".checkBboxSize()", "Ctrl+Shift+Alt+B")

def toogle_RGBA_RGB():
    for node in nuke.selectedNodes():
        for knob in node.knobs():
            if node[knob].value()=="rgba":
                node[knob].setValue("rgb")
            elif node[knob].value()=="rgb":
                node[knob].setValue("rgba")
menu_hub.addCommand("Misc/toggle between knobs in RGBA and RGB", library+".toogle_RGBA_RGB()","Ctrl+Alt+Shift+A")

def fitBboxsSizeToNodeRez():
    for n in nuke.allNodes():
        for k in n.knobs():
            if nuke.knob(n[k].fullyQualifiedName(), type = True)==15:  # check if knob is an array_knob
                if n[k].value()==(0.0, 0.0, 1920.0, 1080.0) and n.width()!=1920 and n.height()!=1080:
                    n[k].setValue( (0.0, 0.0, n.width(), n.height()) )
menu_hub.addCommand("Misc/Fit BboxsSize to Node Rez (ex Crops for 4K comps)", library+".fitBboxsSizeToNodeRez()")

def recoverNkFileFromTooManyBadCharacters():
    filepath = r"\\pjm_server\projets\PYJAMASQUES\PJM_COMPO\334\334-161\work\pjm_compo_334_161_001.nk"
    filepath = nuke.getInput("Enter filepath you want to heal :", filepath)
    bad_char = nuke.getInput("Enter the one bad character you want the entire line to be stripped :", "Æ")
    file_src = open(filepath, 'r')
    file_dst = open(filepath.replace(".nk","_rescue2.nk"), 'w')
    i = 0
    for line in file_src.readlines():
        i+=1
        if bad_char in line:
            print(i)
        else:
            file_dst.write(line)
    file_src.close()
    file_dst.close()
menu_hub.addCommand("Misc/Recover Nuke File from Too Many Bad Characters", library+".recoverNkFileFromTooManyBadCharacters()")

global main
global prev

def togglePreviousNode():
    global main
    global prev
    av = nuke.activeViewer()
    if not av:
        av = nuke.allNodes("Viewer")[0]
    try :
        ai = av.activeInput()
        avn = av.node()
        curr = avn.input(ai)
        try :
            if main :
                if not(curr==main or curr==prev):
                    del main
        except :
            main = avn.input(ai)
        if main == curr :
            prev = curr.input(0)
            nuke.connectViewer( ai, prev )
        else :
            nuke.connectViewer( ai, main )
            prev = main.input(0)
            del main
    except :
        print('no active viewer')
def navDown():
    '''
    av = nuke.activeViewer()
    if av:
        ai = av.activeInput()
        avn = av.node()
        curr = avn.input(ai)
        nextlist = curr.dependent()
        next = nextlist[0]
        nuke.connectViewer( ai, next )
    '''
    try:
        nuke.zoom( 1, [ current.xpos(), current.ypos() ])
    except:
        pass

def navUp():
    '''
    sel = nuke.selectedNodes()
    if len(sel)==1 and "LNK_" in sel[0].name():
        prev = sel[0].input(0)
        nuke.zoom( 1, [ prev.xpos(), prev.ypos() ])
        sel[0].showControlPanel()
    else:
        av = nuke.activeViewer()
        if av:
            ai = av.activeInput()
            avn = av.node()
            curr = avn.input(ai)
            prev = curr.input(0)
            nuke.connectViewer( ai, prev )
    '''
    global current
    current = nuke.selectedNode()
    prev = nuke.selectedNode().input(0)
    nuke.zoom( 1, [ prev.xpos(), prev.ypos() ])
    current.showControlPanel()
    prev["selected"].setValue(True)

def goToActiveNode():
    av = nuke.activeViewer()
    if av:
        ai = av.activeInput()
        avn = av.node().input(ai)
        nuke.zoom( 1, [ avn.xpos(), avn.ypos() ] )
def goToActiveNthNode(nth):
    av = nuke.activeViewer()
    if av:
        if nth-1<0:
            avn = av.node().input(9)   
        else: 
            avn = av.node().input(nth-1)
        nuke.zoom( 1, [ avn.xpos(), avn.ypos() ] )
def whichBuffer():
	av = nuke.activeViewer()
	try :
		ai = int(av.activeInput()) + 1
		if ai == 10:
			ai = 0
		nuke.message( "Current Buffer : "+str(ai) )
	except Exception:
		pass

def goToLinkedExpressionNodes():
    sel = nuke.selectedNodes()[0]
    for node in sel.dependent(nuke.EXPRESSIONS):
        nuke.show( node )
    linked_nodes = []
    for knob in sel.knobs():
        if sel[knob].hasExpression():
            expr = sel[knob].toScript()
            # for node in nuke.allNodes(group=nuke.root(),recurseGroups=True):
            for node in nuke.allNodes():
                if node.name() in expr:
                    if node not in linked_nodes:
                        linked_nodes.append(node)
    if len(linked_nodes)!=0:
        for node in linked_nodes:
            nuke.show( node )
        # if len(linked_nodes)==1:
            # nuke.zoom( 1,[linked_nodes[0].xpos(), linked_nodes[0].ypos() ] )
	
mnn =menu_hub.addMenu("Node Navigation")
# mnn.addCommand("Go to 0th buffer node", library+".goToActiveNthNode(0)", "Ctrl+0")
# mnn.addCommand("Go to 1th buffer node", library+".goToActiveNthNode(1)", "Ctrl+1")
# mnn.addCommand("Go to 2th buffer node", library+".goToActiveNthNode(2)", "Ctrl+2")
# mnn.addCommand("Go to 3th buffer node", library+".goToActiveNthNode(3)", "Ctrl+3")
# mnn.addCommand("Go to 4th buffer node", library+".goToActiveNthNode(4)", "Ctrl+4")
# mnn.addCommand("Go to 5th buffer node", library+".goToActiveNthNode(5)", "Ctrl+5")
# mnn.addCommand("Go to 6th buffer node", library+".goToActiveNthNode(6)", "Ctrl+6")
# mnn.addCommand("Go to 7th buffer node", library+".goToActiveNthNode(7)", "Ctrl+7")
# mnn.addCommand("Go to 8th buffer node", library+".goToActiveNthNode(8)", "Ctrl+8")
# mnn.addCommand("Go to 9th buffer node", library+".goToActiveNthNode(9)", "Ctrl+9")
    
def backToDAGrootTab():
    if int(nuke.NUKE_VERSION_STRING.split(".")[0])<11:
        nuke_app = QtGui.QApplication.instance()
    else:
        nuke_app = QtGui.QGuiApplication.instance()
    all_widgets = nuke_app.allWidgets()
    node_graph_widget = None
    for w in all_widgets:
        name =  w.objectName()
        if not len(name) == 0:
         if name == 'DAG.1':
             node_graph_widget = w
    if node_graph_widget:
        parent = node_graph_widget.parent()
        parent.setCurrentIndex(0)

def switchBackToRGBAlayer():
    global previous_layer
    try:
        print(previous_layer)
    except:
        previous_layer = "depth"
    if nuke.activeViewer().node()['channels'].value()=="rgba":
        nuke.activeViewer().node()['channels'].setValue(previous_layer)
    else:
        previous_layer = nuke.activeViewer().node()['channels'].value()
        nuke.activeViewer().node()['channels'].setValue("rgba")
    
mnn.addCommand("togglePreviousNode", library+".togglePreviousNode()",'*')
mnn.addCommand("navUp", library+".navUp()","Shift+Up")
mnn.addCommand("navDown", library+".navDown()","Shift+Down")
mnn.addCommand("goToActiveNode", library+".goToActiveNode()","Ctrl+home")
mnn.addCommand("whichBuffer", library+".whichBuffer()","Ctrl+Shift+home")
mnn.addCommand("back to DAG RootTab", library+".backToDAGrootTab()",'Ctrl+Shift+Q')

mnn.addCommand("Go To Linked Expression Nodes", library+".goToLinkedExpressionNodes()","Alt+Shift+E")
mnn.addCommand("Switch Back to RGBA Layer",library+".switchBackToRGBAlayer()","ctrl+end")


menu_hub.addMenu("Node Dressing")

def changeNodeFontSize(_multiplier):
    bd = []
    nodes = nuke.selectedNodes()
    for node in nodes:
        if node.Class()=="BackdropNode" or node.Class()=="StickyNote":
            bd.append(node)
    if bd!=[]:
        nodes = bd
    for node in nodes:
        node['note_font_size'].setValue(node['note_font_size'].value()+1*_multiplier)
        print(_multiplier/abs(_multiplier))
        node.setXYpos(node.xpos(), node.ypos()-2*_multiplier/abs(_multiplier))
menu_hub.addCommand("Node Dressing/increase node font size", library+".changeNodeFontSize(4)","Shift+Alt+*")
menu_hub.addCommand("Node Dressing/decrease node font size", library+".changeNodeFontSize(-4)","Shift+Alt+/")

def scaleSelNodes(amount):
    sel = nuke.selectedNodes()
    sel.sort(key=lambda a: a.xpos())
    dist = sel[1].xpos()-sel[0].xpos()
    if dist>0:
        for i in range(len(sel)-1):
            sel[i+1].setXYpos( int(sel[i+1].xpos()+amount*(i+1)), sel[i+1].ypos() )
    sel.sort(key=lambda a: a.ypos())
    dist = sel[1].ypos()-sel[0].ypos()
    if dist>0:
        for i in range(len(sel)-1):
            sel[i+1].setXYpos( sel[i+1].xpos(), int(sel[i+1].ypos()+amount*(i+1)) )
menu_hub.addCommand("Node Dressing/decrease nodes spaces", library+".scaleSelNodes(-10)","Shift+Ctrl+-")
menu_hub.addCommand("Node Dressing/increase nodes spaces", library+".scaleSelNodes(10)","Shift+Ctrl++")

menu_hub.addCommand("Node Dressing/decrease nodes spaces", library+".scaleSelNodes(-10)","Shift+Ctrl+-")
menu_hub.addCommand("Node Dressing/increase nodes spaces", library+".scaleSelNodes(10)","Shift+Ctrl++")

def toggleAlignHorizVertiInOrder():
    sel_h = nuke.selectedNodes()
    sel_v = nuke.selectedNodes()
    sel_h.sort(key=lambda a: a.xpos())
    average_h = 0
    for i in range(len(sel_h)-1):
        average_h += sel_h[i+1].xpos()-sel_h[i].xpos()
    average_h = average_h/len(sel_h)
    sel_v.sort(key=lambda a: a.ypos())
    average_v = 0
    for i in range(len(sel_v)-1):
        average_v += sel_v [i+1].ypos()-sel_v [i].ypos()
    average_v = average_v/len(sel_v)
    if average_h<average_v:
        for i in range(len(sel_v)-1):
            sel_v[i+1].setXYpos( int(sel_v[0].xpos()+100*(i+1)), sel_v[0].ypos() )
    else:
        for i in range(len(sel_h)-1):
            sel_h[i+1].setXYpos( sel_h[0].xpos(), int(sel_h[0].ypos()+50*(i+1)) )
menu_hub.addCommand("Node Dressing/Toggle Align Horizontally or Vertically and keep order", library+".toggleAlignHorizVertiInOrder()","Shift+Ctrl+*")

def SetAsRetake():
    for n in nuke.selectedNodes():
        label = n['label'].value()
        if "retake" in label:
            label = label.replace("\nretake", "").replace("retake", "")
            n['note_font_color'].setValue(0)
        else:
            if label != "":
                label = label+"\n"
            label += "retake"
            n['note_font_color'].setValue(2600468735)
        n['label'].setValue(label)
menu_hub.addCommand("Node Dressing/Set As Retake", library+".SetAsRetake()", 'Alt+Shift+R')

def SetToExport():
    context = returnContextGroup()
    with nuke.toNode(context):
        for n in nuke.selectedNodes():
            label = n['label'].value()
            if "to_export" in label:
                label = label.replace("\nto_export", "").replace("to_export", "")
            else:
                if label != "":
                    label = label+"\n"
                label += "to_export"
            n['label'].setValue(label)
menu_hub.addCommand("Node Dressing/Set to Export", library+".SetToExport()", 'Ctrl+Alt+Shift+X')

def toggleColorOfNonMasterRezNodes():
    orange = 3846308095
    state = "black"
    for node in nuke.allNodes(group=nuke.root(),recurseGroups=True):
        if node['note_font_color'].value()==orange:
            state = "orange"
            break
    for node in nuke.allNodes(group=nuke.root(),recurseGroups=True):
        if node.format().name()!=nuke.root()['format'].value().name():
            # if node['note_font_color'].value()==0 and node.name().split("_")[0]!="LNK":
            if node['note_font_color'].value()==0:
                node['note_font_color'].setValue(orange)
        if state=="orange":
            if node['note_font_color'].value()==orange:
                node['note_font_color'].setValue(0)

menu_hub.addCommand("Node Dressing/Toggle Color of Non-MasterRez-Nodes", library+".toggleColorOfNonMasterRezNodes()")

def textToWhite():
    for n in nuke.selectedNodes():
        n['note_font_color'].setValue(4294967295)
def textToBlack():
    for n in nuke.selectedNodes():
        n['note_font_color'].setValue(0)
menu_hub.addCommand("Node Dressing/textToWhite", library+".textToWhite()", 'Shift+w')
menu_hub.addCommand("Node Dressing/textToBlack", library+".textToBlack()", 'Shift+b')

def __NodeHasKnobWithName(node, name):
  try:
    node[name]
  except NameError:
    return False
  else:
    return True

def __NodeHasFileKnob(node):
  return __NodeHasKnobWithName(node, 'file')

def __NodeHasProxyKnob(node):
  return __NodeHasKnobWithName(node, 'proxy')
  
def __NodeHasLabelKnob(node):
  return __NodeHasKnobWithName(node, 'label')
  
def __NodeHasNameKnob(node):
  return __NodeHasKnobWithName(node, 'name')

def __ReplaceKnobValue(searchstr, replacestr, knob):
  v = knob.value()
  if v:
    repl = v.replace(searchstr, replacestr)
    # repl = re.sub(searchstr, replacestr, v)
    knob.setValue(repl)

def search_replace():
    """ Search/Replace in Reads and Writes. """
    p = nuke.Panel("Search/Replace in Reads and Writes")
    p.addSingleLineInput("Search for:", "")
    p.addSingleLineInput("Replace with:", "")
    p.addEnumerationPulldown('Copy Mode', 'ASCIIcopy NukeCopy NoCopy')
    p.addBooleanCheckBox("Files and Proxies ?", True)
    p.addBooleanCheckBox("Names ?", True)
    p.addBooleanCheckBox("Labels ?", True)
    p.addBooleanCheckBox("Expressions ?", True)
    p.addBooleanCheckBox("Upper Case also ?", True)
    # p.addBooleanCheckBox("Duplicate Nodes ?", False)
    # p.addBooleanCheckBox("ASCII copy ?", False)
    success = p.show()
    if success == 1:
        searchstr = p.value("Search for:")
        replacestr = p.value("Replace with:")
    else:
        return
    context = returnContextGroup()
    new_context = context
    sel = ""
    # if p.value("ASCII copy ?"):
    if p.value("Copy Mode")=="ASCIIcopy":
        nuke.nodeCopy('%clipboard%')
        if int(nuke.NUKE_VERSION_STRING.split(".")[0])<11:
            node_paste = QtGui.QApplication.clipboard().text()
        else:
            node_paste = QtGui.QGuiApplication.clipboard().text()
        case_count = 1
        if p.value("Upper Case also ?"):
            case_count = 3
            searchstr = searchstr.lower()   # to ensure we start with a lowercase and then convert it well.
            replacestr = replacestr.lower()
        for j in range(case_count):
            node_paste = node_paste.replace(searchstr, replacestr)
            # double case handling
            if j==0:
                searchstr = searchstr.upper()  # capital case
                replacestr = replacestr.upper()
            elif j==1:
                searchstr = searchstr[0].upper()+searchstr.lower()[1:]     # camel case
                replacestr = replacestr[0].upper()+replacestr.lower()[1:]
            j+=1
        if int(nuke.NUKE_VERSION_STRING.split(".")[0])<11:
            QtGui.QApplication.clipboard().setText(node_paste)
        else:
            QtGui.QGuiApplication.clipboard().setText(node_paste)
        nukescripts.clear_selection_recursive()
        nuke.nodePaste('%clipboard%')
        sel = nuke.selectedNodes()

    else:
        if p.value("Copy Mode")=="NukeCopy":
            nuke.nodeCopy(nukescripts.cut_paste_file())
            group = nuke.createNode("Group")
            group.setName("TMP")
            new_context = context+"."+group.name()

        with nuke.toNode(new_context):
            if p.value("Copy Mode")=="NukeCopy":
                nuke.nodePaste(nukescripts.cut_paste_file())
                for n in nuke.allNodes():
                    n.setSelected(True)
            case_count = 1
            if p.value("Upper Case also ?"):
                case_count = 3
                searchstr = searchstr.lower()   # to ensure we start with a lowercase and then convert it well.
                replacestr = replacestr.lower()
            for j in range(case_count):
                if p.value("Files and Proxies ?"):
                    fileKnobNodes = [i for i in nuke.selectedNodes() if __NodeHasFileKnob(i)]
                    proxyKnobNodes = [i for i in nuke.selectedNodes() if __NodeHasProxyKnob(i)]
                    for i in fileKnobNodes: __ReplaceKnobValue(searchstr, replacestr, i['file'])
                    for i in proxyKnobNodes: __ReplaceKnobValue(searchstr, replacestr, i['proxy'])
                if p.value("Names ?"):
                    nameKnobNodes = [i for i in nuke.selectedNodes() if __NodeHasNameKnob(i)]
                    # for i in nameKnobNodes: __ReplaceKnobValue(searchstr, replacestr, i['name'])
                    for n in nuke.selectedNodes():
                        old_name = n.name()
                        if searchstr in old_name:
                            new_name = old_name.replace(searchstr, replacestr)
                            new_name_long = context+"."+new_name
                            if nuke.exists(new_name_long):
                                ask = nuke.ask(new_name_long + " already exists. Do you want to increment the name ?\nOtherwise it will not rename it")
                                if ask:
                                    while nuke.toNode(new_name):
                                        new_name += "0"
                            n['name'].setValue(new_name)
                    # for i in nameKnobNodes: i.setName( i.name().replace(searchstr, replacestr) )
                if p.value("Labels ?"):
                    labelKnobNodes = [i for i in nuke.selectedNodes() if __NodeHasLabelKnob(i)]
                    for i in labelKnobNodes: __ReplaceKnobValue(searchstr, replacestr, i['label'])        
                if p.value("Expressions ?"):
                    for node in nuke.selectedNodes():
                        for knob in node.knobs():
                            if knob!="Link_hub":
                                if node[knob].hasExpression():
                                    if searchstr in node[knob].toScript():
                                        node[knob].fromScript( node[knob].toScript().replace(searchstr, replacestr) )
                # double case handling
                if j==0:
                    searchstr = searchstr.upper()  # capital case
                    replacestr = replacestr.upper()
                elif j==1:
                    return
                    searchstr = searchstr[0].upper()+searchstr.lower()[1:]     # camel case
                    replacestr = replacestr[0].upper()+replacestr.lower()[1:]
                j+=1

    if p.value("Copy Mode")=="NukeCopy":
        with nuke.toNode(context):
            group.expand()
menu_hub.addCommand("Node Dressing/SearchAndReplace in Names and Labels", library+".search_replace()", 'Ctrl+Shift+/')

def colorizeLightAOVbackdrops(sel=""):
    context = returnContextGroup()
    with nuke.toNode(context):
        if sel=="":
            sel = nuke.selectedNodes()
    color_dico = {}
    layer = ""
    # bd_scheme_name = nuke.getInput('In which backdrop do we get the color scheme', 'BD_CHARS_LightGroups_AOVs')
    bd_scheme_name = "BD_CHARS_LightGroups_AOVs"
    bd_scheme_context = nuke.toNode(context)
    if not nuke.exists(context+"."+bd_scheme_name):
        bd_scheme_context = nuke.root()
    with bd_scheme_context:
        for bd in backdrop_hub.BackDropContentSelected(nuke.toNode(bd_scheme_name)):
            if bd.Class()=="BackdropNode":
                color = bd["tile_color"].value()
                aov_name = bd["label"].value().split("_")[-1].split("0")[0]
                color_dico[aov_name]=color
    with nuke.toNode(context):
        for node in sel:
            if node.Class()=="BackdropNode" or node.Class()=="StickyNote":
                for key in color_dico.keys():
                    if key in node["label"].value().upper():
                        node["tile_color"].setValue( color_dico[key] )
menu_hub.addCommand("Node Dressing/Colorize LightAOV backdrops", library +".colorizeLightAOVbackdrops()")

def nodeNamerAccordingToReadName():
    for sel in nuke.selectedNodes():
        name = sel.name()
        for i in range(2):
            if sel.name()[-1].isdigit():
                name = name[:-1]
        sel.setName( name.split("_")[0] + "_" + nuke.tcl("value [topnode %s].name" % sel.name()).split("read_")[-1] )
menu_hub.addCommand("Node Dressing/Node Namer according to Read Name", library +".nodeNamerAccordingToReadName()","Ctrl+Alt+Shift+Q")

def toogleDAGgrid():
    if nuke.toNode("preferences")["show_grid"].value():
        nuke.toNode("preferences")["show_grid"].setValue(False)
        nuke.toNode("preferences")["SnapToGrid"].setValue(False)
    else:
        nuke.toNode("preferences")["show_grid"].setValue(True)
        nuke.toNode("preferences")["SnapToGrid"].setValue(True)

menubar = nuke.menu("Nuke")
menu_hub = menubar.addMenu("&_hub")
menu_hub.addCommand("Node Dressing/Toggle DAG grid", library +".toogleDAGgrid()", "alt+ctrl+h" )


mrw = menu_hub.addMenu("ReadWrite Tools")

def createContribsReconstruction(sel):
    # if sel.Class()=="Read":
    #     read = sel
    # else:
    #     nuke.message("Use this function on a EXR multichannel.")
    crypto_CopyBBox = False
    # filepath = read["file"].evaluate()
    filepath = sel.metadata("input/filename")
    aov = filepath.split("_all_")[-1].split(".")[0]
    crypto_filepath = filepath.replace(aov,"crypto_asset").replace("%03d","001").replace("###","001")
    if os.path.exists(crypto_filepath):
        sel.selectOnly()
        crypto_CopyBBox = nuke.createNode("CopyBBox")
        nukescripts.clear_selection_recursive()
        crypto_read = nuke.createNode("Read")
        crypto_read.setXYpos(sel.xpos()+150, sel.ypos()+50)
        crypto_read["file"].setValue(crypto_filepath)
        crypto_CopyBBox.setInput(1,crypto_read)
        crypto_CopyBBox.setXYpos(sel.xpos(), crypto_read.ypos())
        crypto_CopyBBox.selectOnly()

    shuffles_list = []
    shuffles_dico = {}
    contribs_list_raw = ["directDiffuse", "directSpecular","indirectDiffuse", "indirectSpecular","subsurface","transmissiveGlassLobe"]
    contribs_list = []
    contrib_exist = False
    for contrib in contribs_list_raw:
        for layer in nuke.layers(sel):
            if contrib in layer:
                contribs_list.append(contrib)
                shuffles_dico[contrib]=[]
                break
    for contrib in contribs_list:
        for layer in nuke.layers(sel):
            if layer.startswith(contrib) and layer not in contribs_list and contrib in layer and not "shadow" in layer and not "occluded" in layer.lower():
                sh = nuke.createNode("Shuffle")
                sh["in"].setValue(layer)
                sh.setName("sh_"+layer)
                shuffles_dico[contrib].append(sh.name())
        merge = nuke.createNode("Merge2")
        merge["operation"].setValue("plus")
        merge.setName("Merge_"+contrib)
    
    for contrib in contribs_list:
        i=0
        for sh_name in shuffles_dico[contrib]:
            nuke.toNode("Merge_"+contrib).setInput(i,nuke.toNode(sh_name))
            if i==1:
                i+=2
            else:
                i+=1
    merge_global = nuke.createNode("Merge2")
    merge_global.setName("Merge_Global")
    merge_global["operation"].setValue("plus")
    merge_global.setXYpos(merge_global.xpos()+100,merge_global.ypos())
    i = 0
    for contrib in contribs_list:
        merge_global.setInput(i, nuke.toNode("Merge_"+contrib))
        if i==1:
            i+=2
        else:
            i+=1
    ShuffleCopy = nuke.createNode("ShuffleCopy")
    ShuffleCopy.setName("FetchAlpha")
    ShuffleCopy.setXYpos( merge_global.xpos()+100,merge_global.ypos() )
    if crypto_CopyBBox:
        ShuffleCopy.setInput(1,crypto_CopyBBox)
    else:
        ShuffleCopy.setInput(1,sel)
mrw.addCommand("Create Contribs Reconstruction Tree", library+".createContribsReconstruction(nuke.selectedNode())")

def reloadRead(_node):
    if _node.Class()=="Read":
        _node['reload'].execute()
    else:
        for child in _node.dependencies():
            reloadRead(child)
mrw.addCommand("Reload all connected Reads", library+".reloadRead(nuke.selectedNode())","Ctrl+Shift+R")

def selectRead(_node):
    if _node.Class()=="Read":
        _node['selected'].setValue(True)
    else:
        for child in _node.dependencies():
            selectRead(child)
mrw.addCommand("Select all connected Reads", library+".selectRead(nuke.selectedNode())","Ctrl+Shift+Alt+S")
            
def createCopyFromAOVs(node_list,ask=False):
    if ask:
        shuffle_or_copy = nuke.ask("Do you want a shuffle (or rather a copy node) ?")
    else:
        shuffle_or_copy = True
    shuffles_list = []
    for n in node_list:
        first = True
        lkg = False
        if "LKG" in n.name():
            lkg = True
        if first:
            nukescripts.clear_selection_recursive()
        else:
            n.selectOnly()
        i = 0
        for l in nuke.layers(n):
            if l not in ["rgba", "rgb", "alpha", "depth", "motion", "forward", "backward"]:
                if not lkg or n["label"].value().split("\n")[0] in l.lower():
                    i+=1
                    if shuffle_or_copy:
                        sh = nuke.createNode("Shuffle")
                        sh.setName("sh__"+l)
                        sh['in'].setValue(l)
                        if l+".alpha" not in n.channels():   # if there is no alpha, no need to fuck it up
                            sh["out"].setValue("rgb")
                    else:
                        sh = nuke.createNode("Copy")
                        # sh.setInput(1,n)
                        sh.setName("sc__"+l)
                        sh['from0'].setValue(l+".red")
                        sh['from1'].setValue(l+".green")
                        sh['from2'].setValue(l+".blue")
                        sh['to0'].setValue("rgba.red")
                        sh['to1'].setValue("rgba.green")
                        sh['to2'].setValue("rgba.blue")
                    sh['note_font_color'].setValue(4294967295) #dark purple
                    shuffles_list.append(sh)
                    sh.setInput(0,n)
                    sh.setXYpos(n.xpos()+00, n.ypos()+50*i)
    for sh in shuffles_list:
        sh.setSelected(True)
    return shuffles_list
mrw.addCommand("Create CopyNode from AOVs", library +".createCopyFromAOVs(nuke.selectedNodes(),True)","Alt+Shift+A")

def selReadNameFromFile():
    for read in nuke.selectedNodes():
        if read.Class()=="Read":
            read.setName( "R_" + read['file'].value().split("/")[-1].split(".")[0] )
mrw.addCommand("Selected Read Name From Filename", library+".selReadNameFromFile()","Alt+Shift+Ctrl+R")
	
def readFromWrite():
    read_list = []
    ask = False
    x = 0
    same_type_list = []
    sel_list = nuke.selectedNodes()
    for sel in sel_list:
        if sel.Class() in ['Write', 'Read', 'WriteGeo2', 'ReadGeo2', 'WriteGeo', 'ReadGeo',]:
            filepath =  sel['file'].evaluate()
            filenamebase =  filepath.split('/')[-1].split('.')[0]
            try:
                read_name = "_".join( filenamebase.split("_")[-3:] )
            except:
                read_name = filenamebase
            ext = filepath.split('.')[-1]
            dirpath = op.dirname( filepath )
            elts = nuke.getFileNameList( dirpath )
            for elt in elts:
                if elt.split('.')[-1].split(' ')[0] == ext:
                    same_type_list.append(elt)
            if len(same_type_list)>1:
                ask = nuke.ask("There are multiples elements of the same format in the folder.\nDo you want to load just the specified one in the file knob ?\n (Otherwise it will load all of them)")
            if ask:
                for elt in same_type_list:
                    if filenamebase==elt.split(".")[0]:
                        if sel.Class() in ["ReadGeo", "WriteGeo"]:
                            read = nuke.createNode("ReadGeo2")
                        elif sel.Class() in ["DeepRead", "DeepWrite"]:
                            read = nuke.createNode("DeepRead")
                        else:
                            read = nuke.createNode("Read")
                        read['file'].fromUserText( dirpath + "/" + elt )
                        read.setXYpos(sel.xpos(),sel.ypos()+60)
                        read_name = read_name.replace("-","_")
                        read.setName("_"+read_name)
            else:
                for elt in same_type_list:
                    if elt.split('.')[-1].split(' ')[0] == ext:
                        if sel.Class() in ["Read", "Write"]:
                            read = nuke.createNode('Read')
                        elif sel.Class() in ["DeepRead", "DeepWrite"]:
                            read = nuke.createNode("DeepRead")
                        else:
                            read = nuke.createNode('ReadGeo2')
                        read['file'].fromUserText( dirpath + '/' + elt )
                        read.setXYpos(sel.xpos()+x,sel.ypos()+60)
                        x += 50
                        read_name = read_name.replace("-","_")
                        read.setName("_"+read_name)
                        read_list.append(read)      
    for read in read_list:
        read.setSelected(True)
mrw.addCommand("Read from Write", library+".readFromWrite()","Ctrl+Alt+R")

def writeFromRead():
    description = nuke.getInput('add description to unify your files\n(it will add it also to a new directory)', 'draft')
    if description:
        description = "_" + description
        for read in nuke.selectedNodes():
            read.selectOnly()
            filepath = read['file'].value()
            dirpath = os.path.dirname(filepath)
            filename = os.path.basename(filepath)
            if read.Class()=="Read":
                padding = filename.split(".")[-2]
                write = nuke.createNode("Write")
                # write['beforeRender'].setValue( "beforeRenderActions()" )
                write.setName("Write_from_" + read.name())
                write['file'].setValue( dirpath + description + "/" + filename.replace("."+padding, description+"."+padding))
mrw.addCommand("Write from Read", library+".writeFromRead()")

def openSelInExplorer():
    try:
        sel = nuke.selectedNode()
        if sel.Class() in ['Read','Write','DeepRead','DeepWrite','ReadGeo','WriteGeo','Axis','Camera','ReadGeo2','WriteGeo2','Axis2','Camera2','Precomp']:
            file = sel['file'].evaluate()
            (path, name) = os.path.split(file)
            localize_path = nuke.toNode("preferences")["localCachePath"].evaluate()+ os.path.dirname( nuke.selectedNode()["file"].evaluate().replace("//","/__") )
            if os.path.exists( localize_path ):
                ask = nuke.ask("A localised version of this read exists, do you want to open the network version ?")
                if not ask:
                    path = localize_path
                # os.startfile(os.path.dirname(path).replace("/","\\"))
        else:
            print(sel.Class() + sel["help"].value())
            if sel.Class() in ['Group'] and "//" in sel["help"].value():
                path = os.path.dirname(sel["help"].value())
    except Exception:
        path = nuke.tcl("return [file dirname [value root.name]]")
    try:
        print(path)
    except Exception:
        path = os.path.dirname( nuke.env['ExecutablePath'] ) + "/"
    remapL = nuke.toNode("preferences")['platformPathRemaps'].toScript().split(";")
    if os.name == "posix":
        if remapL!=['']:
            path = path.replace(remapL[0],remapL[2])
            print("converted path from remap : "+path)
        os.system('xdg-open "%s"' % path)
    elif os.name == "nt":
        if remapL!=['']:
            path = path.replace(remapL[2],remapL[0])
            print("converted path from remap : "+ path)
        try:
            os.startfile(path.replace("/","\\"))
        except:
            nuke.message(path+"\ndoesn't exist, let's try to open 3 times upper from this folder")
            os.startfile(os.path.dirname(os.path.dirname(os.path.dirname(path.replace("/","\\")))))

mrw.addCommand("Open Selection in Explorer", library+".openSelInExplorer()","Alt+ctrl+o")

def bakeFileExpression():
    for Read in nuke.selectedNodes():
        if "file" in Read.knobs() and ("%03d" in Read["file"].value() or "###" in Read["file"].value()):
            Read["file"].setValue( Read["file"].evaluate().replace( str(nuke.frame()).zfill(3),"%03d" ) )
mrw.addCommand("Bake FileExpression for selected Nodes ", library+".bakeFileExpression()","alt+B")

def copySelToLocal():
    for node in nuke.selectedNodes():
        filepath = node["file"].evaluate()
        local_root = "e:/temp/nuke/"
        if local_root in filepath:
            dirpath_local = os.path.dirname(filepath)+"/"
            if not os.path.exists(dirpath_local):
                os.makedirs(dirpath_local)
            dirpath_net = dirpath_local.replace(local_root, "//")
            for file in os.listdir(dirpath_net):
                print(dirpath_local+file)
                shutil.copy(dirpath_net+file, dirpath_local+file)
mrw.addCommand("Copy Selected Reads to Local ttStorage", library+".copySelToLocal()")


def AutoNameReads():
    class READNAMER( nukescripts.PythonPanel ):
        def __init__( self, sel ):
            nukescripts.PythonPanel.__init__(self, 'Generate Name')
            self.node = sel[0]
            self.fromNum = nuke.Enumeration_Knob("fromNum","from",["0", "1", "2", "3", "4", "5", "6", "7", "8"])
            self.addKnob(self.fromNum)
            self.toNum = nuke.Enumeration_Knob("toNum","to",["1", "2", "3", "4", "5", "6", "7", "8", "9"])
            self.addKnob(self.toNum)
            self.toNum.clearFlag(nuke.STARTLINE)
            self.filename = self.retFilename(self.node)
            self.label = nuke.String_Knob("name","name", self.filename)
            if len(sel)>1:
                self.label.setEnabled( False )
                multiSel = nuke.Text_Knob("MultipleSelection", "Multiple Selection", " prevents editing as it is batch generated ")
                self.addKnob(multiSel)
                multiSel.setEnabled( False )
            self.addKnob(self.label)
            self.setMinimumSize(500, 200)

        def knobChanged(self,knob):
            if nuke.thisKnob().name() == "fromNum" or nuke.thisKnob().name() == "toNum":
                self.label.setValue( self.retFilename(self.node) )

        def retFilename(self, _node):
            _filename = _node['file'].evaluate().split("/")[-1].split(".")[0].replace("-","_")   # evaluate() instead of value() to handle TCL driven paths
            return "_".join(_filename.split("_")[int(self.fromNum.value()):int(self.toNum.value())+1])    # keep only Layer and AOV part

    sel = nuke.selectedNodes()
    if sel!=[]:
        namer = READNAMER(sel)
        result = namer.showModalDialog()
        if result:
            for read in sel:
                if read.Class()=="Read":
                    if len(sel)>1:
                        name = namer.retFilename(read)
                    else:
                        name = namer.label.value()
                    read.setName(name)
mrw.addCommand("AutoNameReads", library+".AutoNameReads()")

def createDirForSelectedWrites():
    for sel in nuke.selectedNodes():
        if sel.Class()=="Write" or sel.Class()=="WriteGeo" or sel.Class()=="WriteGeo2" or sel.Class()=="DeepWrite":
            dirpath = os.path.dirname( sel['file'].evaluate() ) + '/'
            if not os.path.exists(dirpath):
                ask = nuke.ask("Create this path ? \n" + dirpath)
                if ask:
                    os.makedirs(dirpath)
            else:
                nuke.message("Path already exists")
        else:
            nuke.message("Create path ONLY for Write nodes")
mrw.addCommand("Create Folder for Selected Write Nodes", library+".createDirForSelectedWrites()")

def displayMissingFramesSelection():
    missing_frames_str = "None"
    empty_frames_str = "None"
    class MINSIZECHOOSE(nukescripts.PythonPanel):
        def __init__( self ):
            nukescripts.PythonPanel.__init__( self, 'MinSizeChooser', 'MinSizeChooser')
            self.size = nuke.Int_Knob("MinSize","Min Valid Size (Ko)")
            # self.size.setValue( 40)
            self.addKnob(self.size)
    dialog = MINSIZECHOOSE()
    dialog.size.setValue(40)
    result = dialog.showModalDialog()
    if not result:return
    size =  dialog.size.value()
    log = "See more in Script Editor\n\n"
    for sel in nuke.selectedNodes():
        if (sel.Class()=="Read" or sel.Class()=="Write"):
            if not "%0" in sel['file'].value() or "#" in sel['file'].value():
                print("It must contains an image sequence, not a single image file")
                return
            path = os.path.dirname( sel['file'].value() )
            fileseq = sel['file'].value().split("/")[-1]
            seq_pattern = fileseq.split(".")[0]
            padding = fileseq.split(".")[1]
            if not "%" in padding:   #thus it's a # based padding
                padding = "%0"+str(len(fileseq.split(".")[1]))+"d"
            extension = fileseq.split(".")[-1]
            seq_files = []
            try:
                listdir = os.listdir(path)
            except Exception:
                break
            for file in listdir:
                if seq_pattern in file and file.split(".")[-1]==extension:
                    seq_files.append(file)
            seq_files.sort()
            first_frame = int( seq_files[0].split(".")[1] )
            last_frame = int( seq_files[-1].split(".")[1] )

            missing_frames = []
            empty_frames = []
            for i in range(last_frame-first_frame+1):
                current_frame = first_frame + i
                if not( seq_pattern+"."+(padding %current_frame)+"."+extension ) in seq_files:
                    missing_frames.append(current_frame)
                else:
                    if os.path.getsize( path + "/" + seq_pattern+"."+(padding %current_frame)+"."+extension )<size*1000:
                        empty_frames.append(current_frame)
            missing_frames_str = ""
            for fr in missing_frames:
                missing_frames_str += str(fr) + " "
            empty_frames_str = ""
            for fr in empty_frames:
                empty_frames_str += str(fr) + " "
            if missing_frames_str=="":
                missing_frames_str = "None"
            if empty_frames_str=="":
                empty_frames_str = "None"
        if empty_frames_str!="None" or missing_frames_str!="None":
            log = log + seq_pattern + " ("+ path + ")" + " :\n" + "Missing Frames : " + missing_frames_str.rstrip(" ") + "\n" + "Empty Frames (<"+str(size)+"Ko): " + empty_frames_str.rstrip(" ") + "\n\n"
            nuke.message(log)
            print(log)
mrw.addCommand("Display Missing Frames for Selected Reads", library+".displayMissingFramesSelection()", "Alt+Shift+F")

def cacheLocalSelected():
    for n in nuke.selectedNodes():
        try:
            n['localizationPolicy'].setValue('on demand')
        except Exception:
            pass
mrw.addCommand("Set Cache Local to 'on demand' for Selection", library+".cacheLocalSelected()")

import metaCamEXR_hub

mcam = menu_hub.addMenu("Camera Tools")
mcam.addCommand('Create MetaCam from EXR', 'metaCamEXR_hub.createMetaCam()', 'Ctrl+Alt+Shift+e', icon='exrCam.jpg')


def CameraBlender():
    sel = nuke.selectedNodes()
    nukescripts.clear_selection_recursive()
    try:
        cam1, cam2 = sel[1], sel[0]
    except Exception:
        nuke.message("You must select 2 cameras ! ")
        return   
    cam1.setSelected(True)
    if not "Camera" in cam1.Class() or not "Camera" in cam2.Class():
    # if cam1.Class()!="Camera2" or cam2.Class()!="Camera2" or cam1.Class()!="Camera" or cam2.Class()!="Camera":
        nuke.message("You must select 2 cameras")
        return
    nuke.nodeCopy(nukescripts.cut_paste_file())
    nukescripts.clear_selection_recursive()
    blendcam = nuke.nodePaste(nukescripts.cut_paste_file())
    blendcam.setName("blendcam")
    blendcam["label"].setValue("from "+cam1.name()+" to "+cam2.name())
    blendKnob = nuke.Double_Knob("blend","blend")
    blendcam.addKnob(blendKnob)
    for knob in ['translate', 'rotate', 'scaling', 'skew', 'pivot', 'focal', 'haperture', 'vaperture', 'win_translate', 'win_scale']:
        try:
            blendcam[knob].setExpression("parent."+cam1.name()+"."+knob+"*blend" + "+parent."+cam2.name()+"."+knob+"*(1-blend)")
        except Exception:
            pass
    nuke.message("Please adjust and animate to your needs the blend parameter in the user tab of the freshly created camera")
mcam.addCommand("Camera Dissolver", library+".CameraBlender()")

def CameraInverter():
    cam = nuke.selectedNode()
    '''
    if cam.Class()!="Camera2":
        nuke.message("You must select 1 camera")
        return
    '''
    nuke.nodeCopy(nukescripts.cut_paste_file())
    nukescripts.clear_selection_recursive()
    inverted_cam = nuke.nodePaste(nukescripts.cut_paste_file())
    inverted_cam.setName("INVERTED_cam")
    inverted_cam["label"].setValue("from "+cam.name()+"\nref frame : [value reference_frame]")
    refKnob = nuke.Double_Knob("reference_frame","reference_frame")
    inverted_cam.addKnob(refKnob)
    for knob in ['translate', 'rotate', 'scaling', 'skew', 'pivot', 'focal', 'haperture', 'vaperture', 'win_translate', 'win_scale']:
        try:
            inverted_cam[knob].setExpression("-parent."+cam.name()+"."+knob+"+2*parent."+cam.name()+"."+knob+"(reference_frame)" )
        except Exception:
            pass
    nuke.message("Please set the reference frame in the user tab of the freshly created camera")
mcam.addCommand("Camera Inverter", library+".CameraInverter()")

def copyKeepInputs(node_list):
    dst_list = []
    for src in node_list:
        xpos = src.xpos()
        ypos = src.ypos()
        src.selectOnly()
        nuke.nodeCopy(nukescripts.cut_paste_file())
        nukescripts.clear_selection_recursive()
        dst = nuke.nodePaste(nukescripts.cut_paste_file())
        for input in range(src.inputs()):
            dst.setInput(input,src.input(input))                
        dst.setXYpos(xpos-50, ypos-30)
        dst_list.append(dst)
    nukescripts.clear_selection_recursive()
    for dst in dst_list:
        dst.setSelected(True)
        nuke.show(dst)


########################################################################################################################################################################
########################################################################################################################################################################
##########################################################################          ####################################################################################
##########################################################################  LINKS   ####################################################################################
##########################################################################          ####################################################################################
########################################################################################################################################################################
########################################################################################################################################################################



def createLinkContainer(sel, name="", show=True):
    if nuke.thisNode().name()!="Root" and ".nk" not in nuke.thisNode().name() and "." not in nuke.thisNode().name():
        sel = nuke.thisNode()
    if "rkz" in nuke.root().name():
        link = nuke.createNode("PostageStamp", inpanel=False)  # RKZ needs PostageStamp to return error when not connected and thus disable the node connected to it
        link["postage_stamp"].setValue(False)
    else:
        link = nuke.createNode("NoOp", inpanel=False)  # NoOp rather than PostageStamp because, according to N11 ProfileTool it seems RAM heavier even if not enabled.
    link.setInput(0,sel)
    if link.input(0)==None and name=="":      # so connection failed, the selection is a 3d node and postageStamp can't connect
        nukescripts.node_delete(popupOnError=True)
        link = nuke.createNode("NoOp")     # NoOp can connect to 3d nodes
        link['tile_color'].setValue(520093951) # dark red to indicate relation to 3D node
        link.setInput(0,sel)
    else:
        # link['postage_stamp'].setValue(False)
        link['tile_color'].setValue(255)
    link['note_font_size'].setValue(12)
    if name!="":
        link.setName(name)
        reconnectSelected( _silent=True)
    if show:
        nuke.show(link)
    return link
    
def addLinkDressing(_link):
    _link['tile_color'].setValue(520093951) # dark red to indicate relation to 3D node
    if len(_link.name())<20:
        _link['note_font_size'].setValue(11)
    else:
        _link['note_font_size'].setValue(10)
    _link['hide_input'].setValue(True)

def renameByFamily(_thisNode, _lnklbl):
    ''' _lnklblh has two possible values : "LNK_" or "LBL_" to know which type of node run the script '''
    oldname = _thisNode.name().split(_lnklbl)[-1] + "0" # little hack to avoid no number at the end
    # num = re.search('\d+', oldname).group(0)
    # oldname = oldname.split(num)[0]
    oldname = ("_").join(oldname.split("_")[:-1])   # rip the last characters after "_"
    newname = nuke.getInput("New Name", oldname) +"_"
    family = []
    link_class = []
    for ps in nuke.allNodes("PostageStamp"):
        link_class.append(ps)
    for ps in nuke.allNodes("NoOp"):
        link_class.append(ps)        
    for ps in link_class:
        psname = ps.name().split("LNK_")[-1] + "0"
        # num = re.search('\d+', psname).group(0)
        # psname = psname.split(num)[0]
        psname = ("_").join(psname.split("_")[:-1])   # rip the last characters after "_"
        if psname == oldname:
            family.append(ps)
    for link in family:
        link.setName("LNK_"+newname)
    if _lnklbl=="LNK_":
        _thisNode.input(0).setName("LBL_"+newname)
    else:
        _thisNode.setName("LBL_"+newname)

def selectByFamily(_thisNode, _lnklbl):
    ''' _lnklblh has two possible values : "LNK_" or "LBL_" to know which type of node runs the script
        kept only for retrocompatibility '''
    family_name = _thisNode.name().split(_lnklbl)[-1] + "0" # little hack to avoid zero number for the regex
    num = re.search('\d+', family_name).group(0)
    family_name = family_name.split(num)[0]
    family = []
    link_class = []
    nukescripts.clear_selection_recursive()
    for ps in nuke.allNodes("PostageStamp"):
        link_class.append(ps)
    for ps in nuke.allNodes("NoOp"):
        link_class.append(ps)
    for ps in link_class:
        psname = ps.name().split("LNK_")[-1] + "0"
        num = re.search('\d+', psname).group(0)
        psname = psname.split(num)[0]
        if psname == family_name:
            family.append(ps)
    for link in family:
        link.setSelected(True)
    if _lnklbl=="LNK_":
        _thisNode.input(0).setSelected(True)
    else:
        _thisNode.setSelected(True)
        
def selectOrOpenByFamily(_thisNode, _lnklbl, _mode):
    ''' _lnklbl has two possible values : "LNK_" or "LBL_" to know which type of node runs the script '''
    # family_name = _thisNode.name().split(_lnklbl)[-1] + "0" # little hack to avoid zero number for the regex
    family_name = "_".join( _thisNode.name().split("_")[1:-1] )
    # num = re.search('\d+', family_name.split(_lnklbl)[-1]).group(0)
    # family_name = family_name.split(num)[0]
    family = []
    link_class = []
    nukescripts.clear_selection_recursive()
    for ps in nuke.allNodes("PostageStamp"):
        link_class.append(ps)
    for ps in nuke.allNodes("NoOp"):
        link_class.append(ps)
    for ps in link_class:
        # psname = ps.name().split("LNK_")[-1] + "0"
        # num = re.search('\d+', psname.split(_lnklbl)[-1]).group(0)
        # psname = psname.split(num)[0]
        psname = "_".join( ps.name().split("_")[1:-1] )
        if psname == family_name:
            family.append(ps)
    for link in family:
        if _mode == "select":
            link.setSelected(True)
        elif _mode == "open":
            if _thisNode!=link:
                nuke.show(link, "forceFloat")
    if _lnklbl=="LNK_":
        if _mode == "select":
            _thisNode.input(0).setSelected(True)
        elif _mode == "open":
            nuke.show(_thisNode.input(0), "forceFloat")
    else:
        if _mode == "select":
            _thisNode.setSelected(True)
        
def reconnectSelected(_silent=False, context=None):
    if context==None:
        context = returnContextGroup()
    with nuke.toNode(context):
        not_reconnec_list = []
        bad_connec_list = []
        label_nodes_list = []
        postage_nodes_list = [label for label in nuke.allNodes("PostageStamp")]
        postage_nodes_list.extend([label for label in nuke.allNodes("NoOp")])
        i = 0
        for lbl in postage_nodes_list:
            if "LBL_" in lbl.name():
                label_nodes_list.append(lbl)
        ask = False
        for node in nuke.selectedNodes():
            reconnect = False
            if node.Class() in ["PostageStamp","NoOp"] and "LNK_" in node.name():
                lnk_name = ("_").join(node.name().split("_")[1:-1]).rstrip("_")
                try:
                    node.input(0).name()            # it has a connection so no need to reconnect
                    already_connec = True
                except Exception:
                    already_connec = False
                if already_connec:
                    if lnk_name!= ("_").join(node.input(0).name().split("_")[1:-1]).rstrip("_"):
                        bad_connec_list.append(node.name())
                        break
                for lbl in label_nodes_list:
                    lbl_name = ("_").join(lbl.name().split("_")[1:-1]).rstrip("_")

                    if lnk_name==lbl_name:  # check that link finishes with _digit and minus this, is equal to label
                        if not already_connec:      # it has no connection so let's reconnect it
                            node.setInput(0,lbl)
                            reconnect = True
                            break
                if not reconnect and not already_connec:
                    not_reconnec_list.append(node.name())
                    nuke.show( node )
                    if not "NOT CONNECTED" in node['label'].value():
                        node['label'].setValue( node['label'].value() + "\nNOT CONNECTED", "")
                if reconnect:
                    if "NOT CONNECTED" in node['label'].value():
                        node['label'].setValue( node['label'].value().replace("\nNOT CONNECTED", "") )
        if not_reconnec_list!=[] and not _silent:
            not_reconnec_list_str = ""
            for n in not_reconnec_list:
                not_reconnec_list_str += n + ", "  
            print("Warning ! Some Links haven't been reconnected succesfully.\nThey have been labeled 'NOT CONNECTED' to help you searching them.\nBut FYOI it's\n " + not_reconnec_list_str)
            if not _silent:
                nuke.message("Warning ! Some Links haven't been reconnected succesfully.\nThey have been labeled 'NOT CONNECTED' to help you searching them.\nThey are also listed in the script editor")
        if bad_connec_list!=[] and not _silent:
            bad_connec_list_str = ""
            for n in bad_connec_list:
                bad_connec_list_str += n + ", "  
            print("Warning ! Some Links are wrongly connected.\nYou should check for it.\nThose links are\n" + bad_connec_list_str)
            if not _silent:
                ask = nuke.ask("Warning ! Some Links are wrongly connected.\nYou should check for it in the script editor.\n" + "\nDo you want to disconnect them and reconnect them automatically ?")
        if _silent:
            ask = True
        if ask:
            for node in bad_connec_list:
                nuke.toNode(node).setInput(0, None)
                reconnectSelected(_silent=True)
        if not_reconnec_list==[]:
            # print("Reconnection succesfull")
            return True
        else:
            print(repr(not_reconnec_list)+repr(bad_connec_list))
        
def openReadProperties():
    prev = nuke.thisNode()
    while prev.inputs()>0:
        prev = prev.input(0)
    prev.showControlPanel()
        
def addLabelOptions(_label):
    _label['note_font_color'].setValue(4294902015)
    _label['note_font_size'].setValue(11)
    pybut = nuke.PyScript_Knob("create_link", "Create Link (Ctrl+L)")
    pybut.clearFlag(nuke.STARTLINE)
    library = os.path.basename(inspect.getfile(inspect.currentframe())).split(".")[0]
    pybut.setCommand( '''nukescripts.clear_selection_recursive()
link = '''+library+ '''.createLinkContainer('',nuke.thisNode().name().replace("LBL_","LNK_"))
link.setInput(0,nuke.thisNode())
link.setXYpos(nuke.thisNode().xpos()+70,nuke.thisNode().ypos()+70)
link.setName(nuke.thisNode().name().replace("LBL","LNK"))
'''+library+".addLinkOptions(link)\n"+library + ".addLinkDressing(link)\n")
    _label.addKnob(pybut)
    pybut = nuke.PyScript_Knob("RenameAllSame", "Rename by family")
    pybut.setFlag(nuke.STARTLINE)
    pybut.setCommand(library + ".renameByFamily(nuke.thisNode(), 'LBL_')")
    _label.addKnob(pybut)
    
    pybut = nuke.PyScript_Knob("selectByFamily", "Select by family")
    pybut.setCommand(library + ".selectOrOpenByFamily(nuke.thisNode(), 'LBL_', 'select')")
    _label.addKnob(pybut)
    
    pybut = nuke.PyScript_Knob("openByFamily", "Open by family")
    pybut.setCommand(library + ".selectOrOpenByFamily(nuke.thisNode(), 'LBL_', 'open')")
    _label.addKnob(pybut)
        
def addLinkOptions(_link):
    _link['hide_input'].setValue(True)
    pybut = nuke.PyScript_Knob("duplicate", "DUPLICATE (alt+c)\nwith same input")
    library = os.path.basename(inspect.getfile(inspect.currentframe())).split(".")[0]
    pybut.setCommand( library + ".copyKeepInputs([nuke.thisNode()])" )
    _link.addKnob(pybut)

    pybut = nuke.PyScript_Knob("ReconnectSelected", "Reconnect Sel (ctrl+alt+shift+R)\nand check connections")
    pybut.setCommand( library + ".reconnectSelected()")
    pybut.clearFlag(nuke.STARTLINE)
    _link.addKnob(pybut)
    
    pybut = nuke.PyScript_Knob("RenameAllSame", "Rename by family")
    pybut.setCommand(library + ".renameByFamily(nuke.thisNode(), 'LNK_')")
    pybut.setFlag(nuke.STARTLINE)
    _link.addKnob(pybut)
    pybut = nuke.PyScript_Knob("selectByFamily", "Select by family")
    pybut.setCommand(library + ".selectOrOpenByFamily(nuke.thisNode(), 'LNK_', 'select')")
    _link.addKnob(pybut)
    
    pybut = nuke.PyScript_Knob("openByFamily", "Open by family")
    pybut.setCommand(library + ".selectOrOpenByFamily(nuke.thisNode(), 'LNK_', 'open')")
    _link.addKnob(pybut)
    
    pybut = nuke.PyScript_Knob("openReadProperties", "Open Read Properties")
    pybut.setCommand(library + ".openReadProperties()")
    pybut.setFlag(nuke.STARTLINE)
    _link.addKnob(pybut)

    pybut = nuke.PyScript_Knob("go_to_input", "go to INPUT (shift+up)")
    pybut.setCommand('''prev = nuke.thisNode().input(0)
nuke.zoom( 1, [ prev.xpos(), prev.ypos() ])''')
    _link.addKnob(pybut)
    pybut = nuke.PyScript_Knob("go_to_root", "go to ROOT")
    pybut.setCommand('''prev = nuke.thisNode()
while prev.inputs()>0:
    prev = prev.input(0)
nuke.zoom( 1, [ prev.xpos(), prev.ypos() ])''')
    _link.addKnob(pybut)

    pybut = nuke.PyScript_Knob("infos", "infos")
    pybut.setCommand('''import webbrowser
webbrowser.open("http://www.nukepedia.com/gizmos/other/link_hub/")''')
    pybut.setFlag(nuke.STARTLINE)
    _link.addKnob(pybut)
    #_link.setXYpos( src.xpos(), src.ypos()+100 )
    #_link.autoplace()
    try:
        _link['User'].setName("Link_hub")
    except:
        pass
    return _link
global last_label_chosen
last_label_chosen = ""
def linkTools():
    global last_label_chosen
    class NAMER( nukescripts.PythonPanel ):
        def __init__( self, sel ):
            self.node = sel[0]
            nukescripts.PythonPanel.__init__( self, 'Namer', 'Namer')
            self.pulldown = nuke.Enumeration_Knob("GetFrom","GetFrom",["InHouseLayerPass", "name", "filename", "label", "shuffle layer"])
            self.addKnob(self.pulldown)
            self.shortName = nuke.Boolean_Knob("shortName", "shortName", True)
            self.addKnob(self.shortName)
            self.shortName.clearFlag(nuke.STARTLINE)
            self.shortName.setTooltip( "Shorten the AOV names.\nFor example, it replaces Beauty by BTY")
            self.shortName.setVisible( False )
            self.filename = self.retFilename(self.node)
            self.fromNum = nuke.Int_Knob("fromNum","Keep the last n elements : ")
            self.addKnob(self.fromNum)
            self.fromNum.setValue( 2 )
            self.fromNum.setVisible( False )
            self.inHouseHowTo = nuke.Text_Knob("inHouseHowTo", "", " to match LAYER and PASS")
            self.addKnob(self.inHouseHowTo)
            self.inHouseHowTo .clearFlag(nuke.STARTLINE)
            self.inHouseHowTo.setEnabled( False )
            self.inHouseHowTo.setVisible( False )
            if self.node.Class()=="Read":
                self.label = nuke.String_Knob("name","name", self.filename)
                self.inHouseHowTo.setEnabled( True )
                self.inHouseHowTo.setVisible( True )
                self.fromNum.setVisible( True )
                self.shortName.setVisible( True )
            else:
                self.label = nuke.String_Knob("name","name",self.node.name())
                self.label.setEnabled( True )
                self.pulldown.setValue( "name" )
                # if self.node.Class()=="Group" and "SAMEid_picker" in self.node["label"].value():
                    # if self.node["Layer"].value()=="SETS":
                        # self.label = nuke.String_Knob("name","name","msksets_" + self.node.name())
            if len(sel)>1:
                self.label.setEnabled( False )
                multiSel = nuke.Text_Knob("MultipleSelection", "Multiple Selection", " prevents editing as it is batch generated ")
                self.addKnob(multiSel)
                multiSel.setEnabled( False )

            self.addKnob(self.label)

            self.setMinimumSize(500, 200)
            if self.node.Class()=="Read" or self.node.Class()=="Copy" or self.node.Class()=="Shuffle":
                self.pulldown.setValue( "InHouseLayerPass" )
                self.label.setValue( self.retNameFromMode(self.node) )
                 
            if "Cryptomatte_" in self.node.Class():
                self.infoMask = nuke.Text_Knob("infoMask"," (+) TAG <font size=4 color=\'white\'>'"+nuke.selectedNodes()[0]["Layer"].value()+"_mask'</font> will be created in the Label")
                self.addKnob(self.infoMask)
            elif "PP_Mask_hub" in self.node.Class():
                self.infoMask = nuke.Text_Knob("infoMask"," (+) TAG <font size=4 color=\'white\'>'"+nuke.selectedNodes()[0]["QuickLayerLink"].value().split(" ")[0]+"_mask'</font> will be created in the Label")
                self.addKnob(self.infoMask)

            context = returnContextGroup()
            self.prefixe = ""
            if context!="root" and "LKG" in context:
                if nuke.toNode(context)['asset_type'].value() in ["char", "prop"]:
                    asset_name = nuke.toNode(context)['asset_name'].value().replace("-","_")
                    if self.node["label"].evaluate():
                        if " ASSET " not in self.node["label"].evaluate():
                            if asset_name!="" and asset_name!="None" and asset_name!="none":
                                self.prefixe = asset_name+"__"
                                self.label.setLabel( "name (prefixed by <font size=4 color=\'white\'>"+self.prefixe+"</font>)" )
                
            self.separator = nuke.Text_Knob("separator","")
            self.addKnob(self.separator)
            labels_list = []
            links = nuke.allNodes("PostageStamp")
            links.extend(nuke.allNodes("NoOp"))
            for ps in links:
                if "LBL_" in ps.name():
                    realname = ps.name().split("LBL_")[-1]
                    node_labelfield_list = ps["label"].value().split("\n")
                    prefixe = adaptPrefixForLinksDisplayInMenu(realname, node_labelfield_list)
                    if "msk_" in realname:
                        labels_list.append(prefixe+"/"+realname.split("_")[1]+"/"+realname)
                    else:
                        labels_list.append(prefixe+"/"+realname)
            labels_list.sort()
            self.already_created_pulldown = nuke.CascadingEnumeration_Knob("labelchooser","(already created labels)", labels_list)
            self.addKnob(self.already_created_pulldown)
        def knobChanged(self,knob):
            if nuke.thisKnob().name() == "GetFrom" or nuke.thisKnob().name() == "fromNum" or nuke.thisKnob().name()=="shortName":
                self.label.setValue( self.retNameFromMode(self.node) )
                if nuke.thisKnob().value() == "InHouseLayerPass" or nuke.thisKnob().name() == "fromNum" or nuke.thisKnob().name() == "shortName":
                    self.fromNum.setVisible( True )
                    self.inHouseHowTo.setVisible( True )
                    self.shortName.setVisible( True )
                else:
                    self.label.setEnabled( True )
                    self.fromNum.setVisible( False )
                    self.inHouseHowTo.setVisible( False )
                    self.shortName.setVisible( False )

        def retFilename(self, _node):
            parent = _node
            try:     # to avoid error when selected node is connected to nothing
                while parent.Class()!="Read" or parent.input(0):
                    parent = parent.input(0)
                return parent['file'].evaluate().split("/")[-1].split(".")[0].replace("-","_")   # evaluate() instead of value() to handle TCL driven paths
            except Exception:
                return ""
                        
        def retNameFromMode(self, _node):
            if self.pulldown.value()=="name":
                return _node.name()
            elif self.pulldown.value()=="filename":
                if self.filename:
                    return self.retFilename(_node)
                else:
                    return ""
            elif self.pulldown.value()=="label":
                return _node['label'].evaluate()
            elif self.pulldown.value()=="InHouseLayerPass":
                if self.filename:
                    return self.InHouseLayerPass(_node)
                else:
                    return ""

        def InHouseLayerPass(self, _node):
            _filename = self.retFilename(_node).lower()
            _filename = _filename.replace("setstranspa","setsTranspa").replace("charstranspa","charsTranspa").replace("setsextra","setsExtra").replace("charsextra","charsExtra")
            if len(nuke.layers())>5:
                layer = _filename.split("layer")[-1].split("all")[0]
                if _node.Class()=="Shuffle":
                    _filename = _filename.split("layer")[0] + "layer" + layer
                    _filename = _filename.split("layer")[0] + "layer" + layer
                    _filename =  _filename+_node['in'].value().split(".")[0].lstrip("_")
                elif _node.Class()=="Copy":
                    _filename = _filename.split("layer")[0] + "layer" + layer
                    _filename = _filename.split("layer")[0] + "layer" + layer
                    _filename = _filename+_node['from0'].value().split(".")[0]
            # _filename = "_".join(_filename.split("_")[5:])    # keep only Layer and AOV part
            if self.shortName.value():
                if len(_filename.split("layer_")[-1].split("_"))==1:
                    _filename = _filename + "_BTY"
                if "masterLayer" in _filename: 
                    _filename = _filename.replace("masterLayer", "Master")
                '''
                if _filename.split("chars_all")[-1] == "": 
                    _filename = _filename.replace("chars_all", "chars_beauty")
                else:
                    _filename = _filename.replace("chars_all", "chars") 
                    
                if _filename.split("sets_all")[-1] == "": 
                    _filename = _filename.replace("sets_all", "sets_beauty")
                else:
                    _filename = _filename.replace("sets_all", "sets") 
                '''
                if _filename.split("_all")[-1] == "": 
                    _filename = _filename.replace("_all", "_beauty")
                else:
                    _filename = _filename.replace("_all", "") 
                    
                if "_0" in _filename:
                    _filename = _filename.replace("_0", "0")                    
                if "_groupeddiffuse_" in _filename:
                    _filename = _filename.replace("_groupeddiffuse_", "_DIFFUSE")
                    layer_aov_parts = _filename.split("_Diff")
                    layer_aov_parts = [layer_aov_parts[0], "".join(layer_aov_parts[-1].split("_"))]
                    _filename = layer_aov_parts[0]+"_DIFF"+layer_aov_parts[1]
                if "_groupedspecular_" in _filename: 
                    _filename = _filename.replace("_groupedspecular_", "_SPECULAR")
                    layer_aov_parts = _filename.split("_Spec")
                    layer_aov_parts = [layer_aov_parts[0], "".join(layer_aov_parts[-1].split("_"))]
                    _filename = layer_aov_parts[0]+"_SPEC"+layer_aov_parts[1]
                if "subsurface" in _filename: 
                    _filename = _filename.replace("subsurface", "SSS")
                if "motionvector" in _filename: 
                    _filename = _filename.replace("motionvector", "MV")
                if "beauty" in _filename: 
                    _filename = _filename.replace("beauty", "BTY")
                # if "specular" in _filename: 
                #     _filename = _filename.replace("specular", "SPEC")   # to be able to match AOV name when rename by ascii method
                # if "diffuse" in _filename: 
                #     _filename = _filename.replace("diffuse", "DIFF")    # to be able to match AOV name when rename by ascii method
                # if "indirect" in _filename: 
                #     _filename = _filename.replace("indirect", "ind")
                if "direct" in _filename and not "indirect" in _filename: 
                    _filename = _filename.replace("direct", "")
                    # _filename = _filename.replace("direct", "dir")
                if "reflection" in _filename: 
                    _filename = _filename.replace("reflection", "REFL")
                if "refraction" in _filename: 
                    _filename = _filename.replace("refraction", "REFR")
                if "shadow" in _filename: 
                    _filename = _filename.replace("shadow", "shad")
                if "Pworld" in _filename: 
                    _filename = _filename.replace("Pworld", "wp")
                if "Nworld" in _filename: 
                    _filename = _filename.replace("Nworld", "nW")
                if "albedo" in _filename: 
                    _filename = _filename.replace("albedo", "ALBEDO")
                # if "n" in _filename: 
                    # _filename = _filename.replace("n", "N")
            # new_filename = "_".join(_filename.split("_")[-int(self.fromNum.value()):])    # keep only Layer and AOV part
            new_filename = _filename.split("layer_")[-1].replace("___","_")
            # if "chars" not in new_filename and "sets" not in new_filename:
            #     new_filename = "_".join(_filename.split("_")[-int(self.fromNum.value())-1:])    # keep only Layer and AOV part
            return new_filename

    class LABELCHOOSER( nukescripts.PythonPanel):
        def __init__( self ):
            nukescripts.PythonPanel.__init__( self, 'labelchooser', 'labelchooser')
            context = returnContextGroup()
            self.whichSource = "root"  # can be group or root, to know which menu is used for link
            if context=="root":
                labels_list = self.returnLabelsListFromContext("root")
                self.labelchooser_root = nuke.CascadingEnumeration_Knob("labelchooser","Choose a Label", labels_list)
                self.addKnob(self.labelchooser_root)
            else:
                labels_list = self.returnLabelsListFromContext(context)
                self.labelchooser_root = nuke.CascadingEnumeration_Knob("labelchooser_root","Choose a Label from those in group", labels_list)
                self.addKnob(self.labelchooser_root)
                labels_list = self.returnLabelsListFromContext("root", context)
                self.labelchooser_group = nuke.CascadingEnumeration_Knob("labelchooser_group","Choose a Label from ALL available", labels_list)
                self.addKnob(self.labelchooser_group)

        def knobChanged(self,knob):
            if nuke.thisKnob().name() == "labelchooser_root":
                self.whichSource="root" 
            elif nuke.thisKnob().name() == "labelchooser_group":
                self.whichSource="group" 

        def returnLabelsListFromContext(self, main_context, stream_context=""):
            labels_list = []
            with nuke.toNode(main_context):
                links = nuke.allNodes("PostageStamp")
                links.extend(nuke.allNodes("NoOp"))
                for ps in links:
                    if "LBL_" in ps.name():
                        realname = ps.name().split("LBL_")[-1]
                        node_labelfield_list = ps["label"].value().split("\n")
                        prefixe = adaptPrefixForLinksDisplayInMenu(realname, node_labelfield_list)
                        rank = ""
                        for text in node_labelfield_list:
                            if text.isdigit():
                                rank = text + "_"
                                labels_list.append( "ALL_FAVORITES/"+rank+realname )
                        labels_list.append(prefixe+"/"+rank+realname)
                if stream_context!="" and "asset_name" in nuke.toNode(stream_context).knobs():
                    if nuke.toNode(stream_context)["asset_name"].value()=="":   # we show the masks of other assets ONLY if this LKG isn't for a specific asset.
                        with nuke.toNode(stream_context):
                            if nuke.exists("Input1"):
                                for layer in nuke.layers(nuke.toNode("Input1")):
                                    if layer.startswith("msk"):
                                        realname = layer.split("LBL_")[-1]
                                        [shuffle_name, label_knob_name] = returnRawNameAndLabelFromLayerMskName(layer)
                                        prefixe = adaptPrefixForLinksDisplayInMenu(layer)
                                        labels_list.append(prefixe+"/"+shuffle_name)
            labels_list.sort()
            return labels_list
    sel = nuke.selectedNodes()
    if sel==[]:                # if nothing is selected create a link from all labels available
        label_chooser = LABELCHOOSER()
        global last_label_chosen
        if last_label_chosen!="":
            label_chooser.labelchooser_root.setValue(last_label_chosen)
        result = label_chooser.showModalDialog()
        if result:
            context = returnContextGroup()
            with nuke.toNode(context):
                #nukescripts.clear_selection_recursive()
                #nuke.toNode( "LBL_" + label_chooser.pulldown.value().split("/")[-1] ).setSelected(True)
                if label_chooser.whichSource=="root":
                    name = label_chooser.labelchooser_root.value().split("/")[-1]
                else:
                    name = label_chooser.labelchooser_group.value().split("/")[-1]
                if name.split("_")[0].isdigit():
                    name = "_".join(name.split("_")[1:])
                last_label_chosen = name
                name = "LNK_" + name
                link = createLinkContainer(nuke.toNode("LBL_" + name), name, show=False)
                addLinkDressing(link)
                '''
                for ps in nuke.allNodes("PostageStamp"):
                    if ps.name().split("LBL_")[-1] in link.name().split("LNK_")[-1]:
                        link.setInput(0,ps)
                        break
                '''
                addLinkOptions(link)
                if context!="root":   # part to handle links inside groups. Thus creating InputNode and LabelNode
                    group = nuke.toNode(context)
                    nukescripts.clear_selection_recursive()
                    raw_name = returnRawNameFromLNKorLBL(link.name())
                    if not nuke.exists(context+".LBL_"+raw_name+"_"):
                        Input, label = createInputAndLabelFromList([raw_name], context)
                    if link.input(0)==None:
                        link.setSelected(True)
                        link.setInput(0,label)
                        link["label"].setValue("")
                        # if Input!=None:
                        #     label.setInput(0,Input)
                        #     link.setSelected(True)
                        #     with nuke.toNode(context):
                        #         reconnectSelected()
                        #     with nuke.root():
                        #         group.setInput( group.inputs(), nuke.toNode(label.name()))  # to access outside label and not the one inside.
    else:
        if sel[0].name().split("_")[0]=="LBL":
            nukescripts.clear_selection_recursive()
            name = sel[0].name().replace("LBL","LNK")
            link = createLinkContainer(sel[0], name)
            # link.setInput(0,sel[0]) # no need since it's implemented in createContainer
            link.setXYpos(sel[0].xpos()+70,sel[0].ypos()+70)
            addLinkOptions(link)
            addLinkDressing(link)
        else:
            namer = NAMER(sel)
            namer.setMinimumSize(800, 200)
            result = namer.showModalDialog()
            if result:
                for src in sel:
                    src.selectOnly()
                    label = createLinkContainer(src)
                    # label.hideControlPanel()
                    label.setXYpos(src.xpos(),src.ypos()+100)
                    label.setInput(0, src)
                    if len(sel)>1:
                        name = namer.retNameFromMode(src)
                    else:
                        name = namer.prefixe + namer.label.value()

                    name = name.replace("sh__", "").replace("sc__", "").lstrip("_")
                    print("'sh__' and 'sc__' generated by 'createCopyNodeFromAOVs' are deleted to match LBL name convention for LKG exports")

                    link = createLinkContainer(label)
                    link.setInput(0, label)
                    addLabelOptions(label)
                    link.setXYpos(label.xpos()+0,label.ypos()+120)
                    label.setName( "LBL_" + name + "_")
                    link.setName( "LNK_" + name + "_")
                    addLinkDressing(link)
                    addLinkOptions(link)
                    label.hideControlPanel()
                    # label.setSelected(True)
                    if "Cryptomatte_" in str(src.Class()):
                        label["label"].setValue(src["Layer"].value()+"_mask")
                    if "PP_Mask_hub" in str(src.Class()):
                        label["label"].setValue(src["QuickLayerLink"].value().split(" ")[0]+"_mask")
                    if "SAMEid_picker" in src["label"].value():
                        label["label"].setValue(src["Layer"].value().lower()+"_mask")

                    # if src.Class()=="Group" and "SAMEid_picker" in src["label"].value():
                    #     label.setXYpos(src.xpos()+180,src.ypos()+4)
                    #     link.setXYpos(label.xpos()+240,label.ypos()+8)
                    #     if src["Layer"].value()=="sets":
                    #         label["label"].setValue("sets_mask")
                    #     elif src["Layer"].value()=="chars":
                    #         label["label"].setValue("chars_mask")
                    #     elif src["Layer"].value()=="SETSTRANSPA":
                    #         label["label"].setValue("setstranspa_mask")
                    #     elif src["Layer"].value()=="CHARSTRANSPA":
                    #         label["label"].setValue("charstranspa_mask")
                    # if "Cryptomatte" in str(src.Class()):
                    #     if src["Layer"].value()=="SETS":
                    #         label["label"].setValue("sets_mask")
                    #     elif src["Layer"].value()=="CHARS":
                    #         label["label"].setValue("chars_mask")
                    if src.Class()=="Read":
                        if "pjm_server" in src["file"].value().lower():
                            label.setXYpos(src.xpos(),src.ypos()-70)
                            nuke.delete( link ) 
                link.setSelected(True)
                label.setSelected(True)
      
def adaptPrefixForLinksDisplayInMenu(realname, node_labelfield_list=[]):
    if realname.startswith("msk"):      # so it's a layer mask name
        realname = realname.split("_")[0].split("msk")[-1]
        node_labelfield_list = [realname+"_mask"]
    if "_" in realname:
        prefixe = realname.split("_")[0].lower()
    else:
        prefixe = realname.lower()
    if prefixe.startswith("charsextra"):
        prefixe = "charsextra/"+prefixe.split("charsextra")[-1]
    elif prefixe.startswith("vehicules"):
        prefixe = "VEHICULES/VEHICULES"+prefixe.split("vehicules")[-1]
    elif prefixe.startswith("chars"):
        prefixe = "CHARS/CHARS"+prefixe.split("chars")[-1]
    elif prefixe.startswith("setsextra"):
        prefixe = "setsextra/"+prefixe.split("setsextra")[-1]
    elif prefixe.startswith("sets"):
        prefixe = "SETS/SETS"+prefixe.split("sets")[-1]
    elif prefixe.startswith("propsextra"):
        prefixe = "propsextra/"+prefixe.split("propsextra")[-1]
    elif prefixe.startswith("PROPS"):
        prefixe = "props/"+prefixe.split("props")[-1]
    # elif prefixe.startswith("msk"):
        # if prefixe.startswith("mskset"):
            # prefixe = "__MASKS/"+prefixe.split("msk")[-1]
        # else:
            # prefixe = "__MASKS/chars"
    if "sets_mask" in node_labelfield_list:
        prefixe = "SETS/masks"
        # labels_list.append("__MASKS/sets/"+realname.split("_")[1]+"/"+realname)
    elif "chars_mask" in node_labelfield_list:
        prefixe = "CHARS/masks"
        # labels_list.append("__MASKS/chars/"+realname.split("_")[1]+"/"+realname)
    elif "vehicules_mask" in node_labelfield_list:
        prefixe = "VEHICULES/masks"
    elif "setstranspa_mask" in node_labelfield_list:
        prefixe = "SETS/masks"
    elif "charstranspa_mask" in node_labelfield_list:
        prefixe = "CHARS/masks"
    else:
        pass
    if "DIFF" in realname:
        prefixe = prefixe+"/DIFF"
    elif "SPEC" in realname: 
        prefixe = prefixe+"/SPEC"
    return prefixe

def selectLinksFromSelectionLabels():
    sel = nuke.selectedNodes()
    nukescripts.clear_selection_recursive()
    for lbl in sel:
            if "LBL" in lbl.name():
                for dep in lbl.dependent():
                    dep.setSelected(True)

def returnRawNameFromLNKorLBL(link_name):
    # handle numbers at the end of LNK
    raw_name = "_".join( link_name.split("_")[1:])
    if raw_name.split("_")[-1].isdigit():
        raw_name = "_".join( raw_name.split("_")[:-1])
    return raw_name.rstrip("_")
    
menu_hub.addCommand("Link hub/Create Link", library+".linkTools()","Ctrl+l")
menu_hub.addCommand("Link hub/Reconnect Selected Links", library+".reconnectSelected()","Ctrl+Shift+Alt+R")
menu_hub.addCommand("Link hub/Select Links from Selection Labels", library+".selectLinksFromSelectionLabels()", "Ctrl+Shift+Alt+L")


def findNodeInAnyGroup(node):
    group_name = node.fullName().split(".")[0]
    nuke.toNode(group_name).setSelected(True)
    # nuke.menu("Nuke").menu("Edit").menu("Node").menu("Group").findItem("Open Group Node Graph").invoke()
    nuke.showDag(nuke.toNode(group_name))
    # nuke.zoom(1,[node.xpos(),node.ypos()])
    # nuke.message("The node is inside "+group_name+" 's group")
nuke.menu( 'Animation' ).addCommand( 'Find Node in any Group', library+".findNodeInAnyGroup(nuke.thisNode())" )
# nuke.menu( 'Properties' ).addCommand( 'Find Node in any Group', library+".findNodeInAnyGroup(nuke.thisNode())" )

def zoomToGroupInRoot():
    sel = nuke.selectedNodes()
    nuke.allNodes()[0].setSelected(True)
    group_name = returnContextGroup()
    nukescripts.clear_selection_recursive()
    group = nuke.toNode(group_name)
    if group_name!="root":
        with nuke.root():
            group.setSelected(True)
            nuke.show(group)
            nuke.showDag(nuke.root())
            nuke.zoom(1, [group.xpos(),group.ypos()])
    with group:
        for n in sel:
            n.setSelected(True)
nuke.menu( 'Node Graph' ).addCommand( 'Zoom to Group in Root', library+".zoomToGroupInRoot()" )

def openGroupProperties():
    group_name = returnContextGroup()
    group = nuke.toNode(group_name)
    if group_name!="root":
        with nuke.root():
            group.setSelected(True)
            nuke.show(group)
nuke.menu( 'Node Graph' ).addCommand( 'Open Group Properties', library+".openGroupProperties()" ) 
"""
def goToParent():
    nuke.showDag(nuke.root())
    nuke.showDag(nuke.toNode( nuke.thisNode().fullName().split(".")[0] ))
nuke.menu( 'Node Graph' ).addCommand( 'Go To Parent', library+".goToParent()" ) 
"""
import glob, time

### Example that implements a rolling autosave using the autoSaveFilter callbacks
###
## autosaves roll from 0-20 eg myfile.autosave, myfile.autosave1, myfile.autosave2...
#
## To use just add 'import nukescripts.autosave' in your init.py


def onAutoSave(filename):

  ## ignore untiled autosave
  if nuke.root().name() == 'Root':
    return filename

  fileNo = 0
  files = getAutoSaveFiles(filename)

  if len(files) > 0 :
    lastFile = files[-1]
    # get the last file number

    if len(lastFile) > 0:
      try:
        fileNo = int(lastFile[-1:])
      except:
        pass

      fileNo = fileNo + 1

  if ( fileNo > 9 ):
    fileNo = 0

  if ( fileNo != 0 ):
    filename = filename + str(fileNo)

  return filename


def onAutoSaveRestore(filename):

  files = getAutoSaveFiles(filename)

  if len(files) > 0:
    filename = files[-1]

  return filename

def onAutoSaveDelete(filename):

  ## only delete untiled autosave
  if nuke.root().name() == 'Root':
    return filename

  # return None here to not delete auto save file
  return None

  
def getAutoSaveFiles(filename):
  date_file_list = []
  files = glob.glob(filename + '[1-9]')
  files.extend( glob.glob(filename) )

  for file in files:
      # retrieves the stats for the current file as a tuple
      # (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime)
      # the tuple element mtime at index 8 is the last-modified-date
      stats = os.stat(file)
      # create tuple (year yyyy, month(1-12), day(1-31), hour(0-23), minute(0-59), second(0-59),
      # weekday(0-6, 0 is monday), Julian day(1-366), daylight flag(-1,0 or 1)) from seconds since epoch
      # note:  this tuple can be sorted properly by date and time
      lastmod_date = time.localtime(stats[8])
      # create list of tuples ready for sorting by date
      date_file_tuple = lastmod_date, file
      date_file_list.append(date_file_tuple)
   
  date_file_list.sort()
  return [ filename for _, filename in date_file_list ]


nuke.addAutoSaveFilter( onAutoSave )
nuke.addAutoSaveRestoreFilter( onAutoSaveRestore )
nuke.addAutoSaveDeleteFilter( onAutoSaveDelete )



def createShuffleFromSelectedLayer():
    class LAYERSELECTOR( nukescripts.PythonPanel ):
        def __init__( self, sel ):
            self.node = sel
            nukescripts.PythonPanel.__init__( self, 'Namer', 'Namer')
            self.pulldown = nuke.Enumeration_Knob("Layers","Layers",layers_list)
            self.addKnob(self.pulldown)
            # self.pulldown2 = nuke.Enumeration_Knob("OneMore","One More",layers_list)
            # self.addKnob(self.pulldown2)
    sel = nuke.selectedNodes()
    context = returnContextGroup()
    if sel==[]: 
        if nuke.exists(context+".Input1"):
            if not nuke.exists(context+".LBL_Input1_"):
                with nuke.toNode(context):
                    Input1 = nuke.toNode(context+".Input1")
                    label = createLinkContainer(Input1, "LBL_Input1_", show=False)
                    label.setInput(0,Input1)
                    label.setXYpos(Input1.xpos(), Input1.ypos()+28)
                    addLinkDressing(label)
                    addLabelOptions(label)
                    nukescripts.clear_selection_recursive()
            with nuke.toNode(context):
                link = createLinkContainer(nuke.toNode(context+".LBL_Input1_"), "LNK_Input1_", show=False)
                addLinkDressing(link)
                addLinkOptions(link)
                sel = [link]
    with nuke.toNode(context):
        if sel!=[]:
            sel = sel[0]
            # layers_list = nuke.layers(sel) # bugs on nuke13
            layers_list = []
            for layer in nuke.channels(nuke.selectedNode()):
                if layer.split(".")[0] not in layers_list:
                    layers_list.append(layer.split(".")[0])
            unwanted_layers = ["rgba", "rgb", "alpha", "motion", "forward", "backward",'disparity', 'disparityL', 'disparityR', 'rotopaint_mask', 'mask_planartrack', 'mask_splinewarp', 'deep','identifier_name00', 'identifier_name01', 'identifier_name02', 'identifier_name03']
            for layer in unwanted_layers:
                if layer in layers_list:
                    layers_list.remove(layer)
            for layer in layers_list:
                if "___" in layer:  # for cryptomattes
                    layers_list.remove(layer)
            layers_list.sort()
            layer_selector = LAYERSELECTOR(sel)
            viewer_layer = nuke.activeViewer().node()['channels'].value()
            if viewer_layer not in unwanted_layers:
                layer_selector.pulldown.setValue( viewer_layer )
            layer_selector.pulldown.setValue( viewer_layer )

            result = layer_selector.showModalDialog()
            if result:
                xpos = sel.xpos()
                ypos = sel.ypos()
                nukescripts.clear_selection_recursive()
                if int(nuke.NUKE_VERSION_STRING.split(".")[0])<13:
                    if os.getenv('TT_PROD_TRIG')=="jad":
                        Shuffle = nuke.createNode("Shuffle_hub_v1p6") 
                    elif os.getenv('TT_PROD_TRIG')=="crc":
                        Shuffle = nuke.createNode("Shuffle_hub_v1p5") 
                    else:
                        Shuffle = nuke.createNode("Shuffle_hub_v1p8") 
                else:
                        Shuffle = nuke.createNode("Shuffle_hub_v1p9") 

                layer_name = layer_selector.pulldown.value()
                Shuffle["in"].setValue( layer_name )
                Shuffle.setInput(0,sel)
                Shuffle["DivideByAlbedo"].setValue(False)
                if "tech_alpha_ref" in layers_list:
                    Shuffle["FetchAlpha"].setValue(True)
                    Shuffle["in_2"].setValue("tech_alpha_ref")
                elif "alpha_raw" in layers_list:
                    Shuffle["FetchAlpha"].setValue(True)
                    Shuffle["in_2"].setValue("alpha_raw")
                else:
                    Shuffle["FetchAlpha"].setValue(False)
                if sel.Class() in ["Shuffle_hub", "Shuffle_hub_v1p2", "Shuffle_hub_v1p4", "Shuffle_hub_v1p5", "Shuffle_hub_v1p6", "Shuffle_hub_v1p7", "Shuffle_hub_v1p8" "NoOp", "PostageStamp"]:
                    Shuffle.setXYpos( xpos, ypos+28 )
                else:
                    Shuffle.setXYpos( xpos, ypos+50 )
                if "mask" in layer_name.lower() or "msk" in layer_name.lower() or "shadow_" in layer_name.lower() or "depth" in layer_name.lower() or "Z" in layer_name.lower():  # 'mask' only has got an alpha channel, but has it is alpha, we want to have it also in the alpha channel.
                    Shuffle["CopyRedChannelToAlpha"].setValue(True)  #  version v1
                    Shuffle["FetchAlpha"].setValue(False)
                    # Shuffle["from0"].setValue("rgba.alpha")    # new version 1p1
                else:
                    Shuffle["CopyRedChannelToAlpha"].setValue(False)
                if ("diffuse" in layer_name.lower() or "specular" in layer_name.lower()) and "shadow" not in layer_name.lower() and "crc" in nuke.root()["name"].value():
                    Shuffle["DivideByAlbedo"].setValue(True)
                    Shuffle["CopyRedChannelToAlpha"].setValue(False)     #  version v1
                # if ("diffuse" in layer_name.lower() or "specular" in layer_name.lower()) and "shadow" not in layer_name.lower() and "jad" in nuke.root()["name"].value():
                #     Shuffle["DivideByAlbedo"].setValue(True)
                #     Shuffle["WhiteLights"].setValue(True)    
                if "albedo" in layer_name.lower() or "tech_" in layer_name.lower():
                    Shuffle["CopyRedChannelToAlpha"].setValue(False)    #  version v1

menu_hub.addCommand("Shuffle hub/Create Shuffle from Selected Layer", library+".createShuffleFromSelectedLayer()", "Ctrl+Alt+K")

def createReinjectAOVfromShuffleHub():
    sel = nuke.selectedNode()
    if sel.Class() in ["Shuffle_hub","Shuffle_hub_v1p2", "Shuffle_hub_v1p4", "Shuffle_hub_v1p5", "Shuffle_hub_v1p6", "Shuffle_hub_v1p7", "Shuffle_hub_v1p8"]:
        layer = sel["in"].value()
        nukescripts.clear_selection_recursive()
        Copy = nuke.createNode("ShuffleCopy")
        Copy.setName("SC_ReinjectFrom_"+layer+"_")
        Copy['note_font_color'].setValue(4294967295) #white
        Copy["out"].setValue(layer)
        Copy["red"].setValue("red")
        Copy["green"].setValue("green")
        Copy["blue"].setValue("blue")
menu_hub.addCommand("Shuffle hub/Create ReinjectAOV from Shuffle_hub", library+".createReinjectAOVfromShuffleHub()", "Ctrl+Alt+Shift+K")

menu_hub.addCommand("Copy Nodes and Keep inputs", library+".copyKeepInputs(nuke.selectedNodes())", "Alt+v")


try:
    create_menu = nuke.menu("Nuke").menu("Edit").menu("Node").addMenu("Create")
    create_menu.addCommand('foo','nuke.nodes.NoOp().setName("ThisNameMustBeUnique")')
except:
    pass
def returnContextGroupFromCB():
    if "." not in nuke.thisNode().fullName():
        context = "root"
    else:
        context = '.'.join(nuke.thisNode().fullName().split('.')[:-1])
    if context!=None:
        pass
        return context
    else:
        context = returnContextGroup()
        print("contextRegular :"+context)
        return context
def returnContextGroup():
    # sel = nuke.selectedNodes()
    try:
        nuke.menu("Nuke").menu("Edit").menu("Node").menu("Create").findItem("foo").invoke()
    except:
        pass
    context = "root"
    if nuke.exists("root.ThisNameMustBeUnique"):
        nuke.delete(nuke.toNode("root.ThisNameMustBeUnique"))
        context = "root"
    else:
        for node in nuke.allNodes(group=nuke.root(),recurseGroups=True):
            if node.name()=="ThisNameMustBeUnique":
                group_name = ".".join( node.fullName().split(".")[:-1] )
                # nukescripts.clear_selection_recursive()
                # node.setSelected(True)
                # nukescripts.node_delete(popupOnError=True)
                nuke.delete(node)
                context = group_name
    # for n in nuke.allNodes("NoOp"):
    #     if "ThisNameMustBeUnique" in n.name():
    #         nuke.delete(n)
    # print("function : context : "+context)
    # nukescripts.clear_selection_recursive()
    # for n in sel:
    #     n.setSelected(True)
    return context
menu_hub.addCommand("returnContextGroup", library+".returnContextGroup()")
'''
from nukescripts import panels
from PySide.QtGui import *
from PySide.QtCore import *
from PySide.QtWebKit import *

class WebBrowserWidget(QWidget):
  def changeLocation(self):
    url = self.locationEdit.text()
    if not url.startswith( 'http://' ):
      url = 'http://' + url
    self.webView.load( QUrl(url) )

  def urlChanged(self, url):
    self.locationEdit.setText( url.toString() )

  def __init__(self):
    QWidget.__init__(self)
    self.webView = QWebView()
   
    self.setLayout( QVBoxLayout() )  
    
    self.x = QLineEdit( 'http://www.google.com' )
    self.locationEdit.setSizePolicy( QSizePolicy.Expanding, self.locationEdit.sizePolicy().verticalPolicy() )
    
    QObject.connect( self.locationEdit, SIGNAL('returnPressed()'),  self.changeLocation )
    QObject.connect( self.webView,   SIGNAL('urlChanged(QUrl)'),     self.urlChanged )

    self.layout().addWidget( self.locationEdit )
  
    bar = QToolBar()
    bar.addAction( self.webView.pageAction(QWebPage.Back))
    bar.addAction( self.webView.pageAction(QWebPage.Forward))
    bar.addAction( self.webView.pageAction(QWebPage.Stop))
    bar.addAction( self.webView.pageAction(QWebPage.Reload))
    bar.addSeparator()
    
    self.layout().addWidget( bar )
    self.layout().addWidget( self.webView )

    url = 'http://tractor-engine/tv/#' 
    self.webView.load( QUrl( url ) )
    self.locationEdit.setText( url ) 
    self.setSizePolicy( QSizePolicy( QSizePolicy.Expanding,  QSizePolicy.Expanding))

## make this work in a .py file and in 'copy and paste' into the script editor
moduleName = __name__
if moduleName == '__main__':
  moduleName = ''
else:
  moduleName = moduleName + '.'

def showTractor():
    pane = nuke.getPaneFor('Viewer.1')
    panels.registerWidgetAsPanel( moduleName + 'WebBrowserWidget', 'Web Browser','uk.co.thefoundry.WebBrowserWidget', True).addToPane(pane)
'''
# menu_hub.addCommand("Tractor", library+".showTractor()", "alt+t")


'''
import subprocess

def playInRV():
    try:
        sel = nuke.selectedNode()
        if (sel.Class() == 'Read') or (sel.Class() == 'Write'):
            file = sel['file'].evaluate()
            (path, name) = os.path.split(file)
    except Exception:
        return
    try:
    except Exception:
        path = os.path.dirname( nuke.env['ExecutablePath'] ) + "/"
    remapL = nuke.toNode("preferences")['platformPathRemaps'].toScript().split(";")
    if os.name == "posix":
        if remapL!=['']:
            path = path.replace(remapL[0],remapL[2])
        #os.system('rv "%s" &' % path)
        subprocess.Popen(["/s/apps/lin/rv/rv",path])
    elif os.name == "nt":
        if remapL!=['']:
            path = path.replace(remapL[2],remapL[0])
        subprocess.Popen(["D:/32/rv/bin/rv.exe",path+"/"+name])
menu_hub.addCommand("play in RV", library+".playInRV()","Alt+ctrl+p")
'''

# import numpy


def infos():
    webbrowser.open("http://www.nukepedia.com/python/nodegraph/productivity_scripts_hub")
    # pane = nuke.getPaneFor('Viewer.1')
    # from nukescripts import panels
    # panels.registerWidgetAsPanel( moduleName + 'WebBrowserWidget', 'Web Browser','uk.co.thefoundry.WebBrowserWidget', True).addToPane(pane)
    # gui = panels.customKnob.getObject().widget
    # gui.urlChanged("http://www.nukepedia.com/python/nodegraph/productivity_scripts_hub")
    # gui.changeLocation()
menu_hub.addCommand("infos", library+".infos()")



