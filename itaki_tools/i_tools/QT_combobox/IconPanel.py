# QUICK AND DIRTY HACK TO SEE AVAILABLE ICONS IN NUKE AND THEIR SYNTAX FOR US IN LABELS
# PUT THIS INTO YOUR MENU.PY:

#def addIconPanel():
#    global iconPanel
#    iconPanel = OhuPanels.IconPanel()
#    return iconPanel.addToPane()
#paneMenu.addCommand( 'Universal Icons', addIconPanel )
#nukescripts.registerPanel('com.ohufx.iconPanel', addIconPanel)
import os
import nuke
import nukescripts
from PyQt4 import QtCore

class IconPanel( nukescripts.PythonPanel ):
    def __init__( self ):
        nukescripts.PythonPanel.__init__( self, 'Universal Icons', 'com.ohufx.IconPanel')
        icons = ('NukeApp.png', 'frame.png', 'SliderThumb.png', 'Eyedropper.png', 'ArrowWhiteLeft.png', 'ArrowWhiteRight.png', 'arrow_left.png', 'arrow_right.png', 'arrow_up.png', 'arrow_down.png', 'next.png', 'previous.png', 'undo.png', 'redo.png', 'revert.png', 'Add.png', 'Remove.png', 'TCStart.png', 'TCEnd.png', 'TCFrameBackward.png', 'TCFrameForward.png', 'TCKeyBackward.png', 'TCKeyForward.png', 'TCPlayBackward.png', 'TCPlayForward.png', 'TCStop.png', 'TCIntervalBackward.png', 'TCIntervalForward.png', 'RangeBackward.png', 'RangeForward.png', 'GroupShow.png', 'Disable.png', 'Cached.png', 'HideInput.png', 'PostageStamp.png', 'Help.png', 'Bold.png', 'Italic.png', 'File_Knob.png', 'Color_Knob.png', 'MultiView.png', 'SingleView.png', 'Curve_Button.png', 'Color_Knob.png', 'SVG/VisibleCurrentFrame.svg', 'SVG/MoveUpOne.svg', 'SVG/Reveal.svg', 'ShowStructure.png', 'select.png', 'AxisIcon.png', 'FolderIcon.png', 'GeoSelect_Nodes_16x16.png', 'GeoSelect_Vertices_16x16.png', 'GeoSelect_OcclusionTest_16x16.png', 'show_points.png', 'show_point_num.png', 'show_point_info.png', 'show_point_normals.png', 'show_point_uvs.png', 'show_vertex_num.png', 'show_vertex_normals.png', 'show_vertex_uvs.png', 'show_prim_num.png', 'show_prim_normals.png', 'show_prim_bbox.png', 'grid_display.png', 'View.png', 'Lock.png', 'Unlock.png', 'Camera.png', 'Refresh.png', 'ROI.png', 'Proxy.png', 'Pause.png', 'IP.png', 'zebra.png', 'FrameRangeLock.png', 'FrameRangeUnlock.png', 'MonitorOut.png', 'Toggle3DToolbar_16x16.png', 'Loop.png', 'Bounce.png', 'StopPlay.png', 'Plugin.png', 'ToolbarImage.png', 'ToolbarDraw.png', 'ToolbarTime.png', 'ToolbarChannel.png', 'ToolbarColor.png', 'Toolbar3DLUT.png', 'ToolbarFilter.png', 'ToolbarKeyer.png', 'ToolbarMerge.png', 'ToolbarTransform.png', 'Toolbar3D.png', 'Toolbar3DLights.png', 'ToolbarViews.png', 'ToolbarStereo.png', 'ToolbarOther.png', 'ToolbarOFX.png', 'AllPlugins.png', 'SVG/Eraser.svg', 'SVG/Selection.svg', 'SVG/MoveToTop.svg', 'SVG/Paint.svg', 'CenterThisNode12p.png', 'QuestionMark12p.png', 'SVG/VisibleSpecificRange.svg', 'SVG/Clone.svg', 'SVG/MoveDownOne.svg', 'SVG/VisibleFromNowOn.svg', 'SVG/Key.svg', 'SVG/UnlimitedLife.svg', 'SVG/MoveToBottom.svg', 'SVG/VisibleUpTillNow.svg', 'ScriptEditor/clearHistory.png', 'ScriptEditor/source.png', 'ScriptEditor/load.png', 'ScriptEditor/save.png', 'ScriptEditor/run.png', 'ScriptEditor/inputOn.png', 'ScriptEditor/inputOff.png', 'ScriptEditor/outputOn.png', 'ScriptEditor/outputOff.png', 'ScriptEditor/bothOn.png', 'ScriptEditor/bothOff.png', 'ScriptEditor/clearOutput.png', 'ControlPanelBin/clear.png', 'ControlPanelBin/lock.png', 'ControlPanelBin/unlock.png', 'CursorTranslate.png', 'CursorRotateNW.png', 'CursorRotateNE.png', 'CursorRotateSW.png', 'CursorRotateSE.png', 'CursorSizeAll.png', 'CursorSkew.png', 'CursorMovePoint.png', 'CursorAddPoint.png', 'CursorRemovePoint.png', 'CursorClosePath.png', 'CursorFeatherPoint.png', 'CursorRemoveFeatherPoint.png', 'CursorSmoothPoint.png', 'CursorCuspPoint.png', 'KeyLeft.png', 'KeyRight.png', 'KeyPlus.png', 'KeyMinus.png', 'Brush.png', 'Roto/Curve.png', 'Roto/Shape.png', 'Roto/Layer.png', 'Roto/BlendUnion.png', 'Roto/BlendIntersect.png', 'Roto/BlendOver.png', 'Roto/BlendDarken.png', 'Roto/BlendMultiply.png', 'Roto/BlendColorBurn.png', 'Roto/BlendLighten.png', 'Roto/BlendScreen.png', 'Roto/BlendColorDodge.png', 'Roto/BlendAdd.png', 'Roto/BlendOverlay.png', 'Roto/BlendSoftLight.png', 'Roto/BlendHardLight.png', 'Roto/BlendDifference.png', 'Roto/BlendExclusion.png', 'Roto/BlendFrom.png', 'Roto/BlendMinus.png', 'Roto/InvertOn.png', 'Roto/InvertOff.png', 'Roto/MotionBlurOn.png', 'Roto/MotionBlurOff.png', 'Roto/Visible.png', 'Roto/Invisible.png', 'Roto/Color.png', 'Roto/OverlayColor.png', 'Roto/OverlayColor.png', 'Roto/SelectAllTool.png', 'Roto/SelectCurvesTool.png', 'Roto/SelectPointsTool.png', 'Roto/SelectFeatherPointsTool.png', 'Roto/BezierTool.png', 'Roto/BSplineTool.png', 'Roto/EllipseTool.png', 'Roto/RectangleTool.png', 'Roto/AddPointsTool.png', 'Roto/RemovePointsTool.png', 'Roto/CuspPointsTool.png', 'Roto/CurvePointsTool.png', 'Roto/RemoveFeatherTool.png', 'Roto/CloseCurveTool.png', 'Roto/BrushTool.png', 'Roto/PencilTool.png', 'Roto/EraserTool.png', 'Roto/CloneTool.png', 'Roto/RevealTool.png', 'Roto/BlurTool.png', 'Roto/SharpenTool.png', 'Roto/SmearTool.png', 'Roto/DodgeTool.png', 'Roto/BurnTool.png', 'Roto/LinkedFeather.png', 'Roto/UnlinkedFeather.png', 'Roto/SingleKeyframe.png', 'Roto/RippleKeyframe.png', 'Roto/ShowCurvesOnDrag.png', 'Roto/ShowPointsOnDrag.png', 'Roto/ShowAllOnDrag.png', 'Roto/CurvePriority.png', 'Roto/PointPriority.png', 'Roto/ShowTransformNone.png', 'Roto/ShowTransformJack.png', 'Roto/ShowTransformBBox.png', 'Roto/ShowTransformBoth.png', 'Roto/ShowPointNumbers.png', 'Roto/UnlimitedLife.png', 'Roto/VisibleFromNowOn.png', 'Roto/VisibleCurrentFrame.png', 'Roto/VisibleUpTillNow.png', 'Roto/VisibleSpecificRange.png', 'Roto/CloneToolbar.png')
        batch = 30
        for index, icon in enumerate(icons):
            counter = index%batch
            if counter == 0:
                tab = nuke.Tab_Knob( str(index), str(index) )
                self.addKnob( tab )
            name = os.path.splitext( icon.split('/')[-1] )[0]
            iconString = '%s <img src=":qrc/images/%s">' % ( name, icon )
            k = nuke.String_Knob(icon, iconString)
            k.setValue( iconString )
            self.addKnob( k )

class QT_Icon_Panel():
    def __init__(self):
        nukescripts.PythonPanel.__init__( self, 'Universal Icons', 'com.itaki.IconPanel')
        icons = QtCore.QResource(':qrc/images').children()
        for icon in icons:
            name = os.path.splitext(icon.split('/')[-1] )[0]
            iconString = '%s <img src=":qrc/images/%s">' % (name, icon)