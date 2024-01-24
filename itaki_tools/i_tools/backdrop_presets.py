# Preset Backdrop 1.3
# Copyright (c) 2011 Victor Perez.  All Rights Reserved. Updated by Michael McReynolds
# Create your own theme http://colrd.com/palette/

### Add to menu.py ###
#import presetBackdrop
#VictorMenu = nuke.menu('Nuke').addMenu('V!ctor')
#VictorMenu.addCommand('Preset Backdrop', 'presetBackdrop.presetBackdrop()', 'ctrl+alt+b')
###

import nuke, colorsys, operator, json
import script_library

script_library.test('oh my god it worked')


#notes fix cg_motion_vectors, fix despill effects
# Make json file
### Preset Backdrop
## beauty
## keyer in
## keyer out
# Hole Fill
# tracking stabilze matchmove
# test viewer
# VIEWER INPUT
# slate
# master output
# review output
# 


def backdrop_presets():
    customPreset = None
    sep = '"'
    presets = ['Input', 'Reference', 'DISABLED',
                'Grain',
                'Element',
                'Retime',
                'Transformations', 'Tracker', 'Mocha',
                'Keyer', 'Additive_Key', 'Edge_Fixes', 'Despill',
                'Effects', 'Defocus', 'Glow', 'Lens_Flare', 'Godrays', 'Light_Wrap',
                'Roto','Matte',
                'Cleanup','Rig_Removal',
                'CG', 'CG:Beauty', 'CG:Diffuse', 'CG:Reflection', 'CG:Refraction', 'CG:Shadow', 'CG:Specular', 'CG:Motion_Vectors', 'CG:Z-Depth', 'CG:Matte',
                'Shuffle',
                '3D', 'Camera_Tracker', 'Camera_Rig', 'Projection', '3D_Elements',
                'Set_Extension',
                'Particles',
                'Color_Correction',
                'Deep',
                'Controllers',
                'Write',
                'Previous_Versions',
                'Temp'
    ]
                
 
    '''
    '''
    p = nuke.Panel('Preset Backdrop')
    p.addEnumerationPulldown('Preset',' '.join(presets))
    p.addSingleLineInput('Custom Label','')
    if p.show():
        customPreset = p.value('Preset')
        customLabel = p.value('Custom Label')
    
    # Backdrop presets
    if customPreset == 'Input':
        presetLabel = 'Input'
        presetIcon = 'Read.png'
        presetColor = (0.156,0.011,0.212)

    if customPreset == 'Reference':
        presetLabel = 'Reference'
        presetIcon = 'SideBySide.png'
        presetColor = colorsys.hsv_to_rgb(0.682, 0, 0.298)

    if customPreset == 'DISABLED':
        presetLabel = 'DISABLED'
        presetIcon = '🚫'
        presetColor = colorsys.hsv_to_rgb(0, 0, 0)

    if customPreset == 'Grain':
        presetLabel = 'Grain'
        presetIcon = 'Grain.png'
        presetColor = colorsys.hsv_to_rgb(0, 0, 0.3)

    if customPreset == 'Element':
        presetLabel = 'Element'
        presetIcon = 'Read.png'
        presetColor = colorsys.hsv_to_rgb(0.125, 1, 0.5)

    if customPreset == 'Retime':
        presetLabel = 'Retime'
        presetIcon = 'Retime.png'
        presetColor = colorsys.hsv_to_rgb(0.152, 0, 0.5)

    if customPreset == 'Transformations':
        presetLabel = 'Transformations'
        presetIcon = '2D.png'
        presetColor = colorsys.hsv_to_rgb(0.819, 0.286, 0.329)

    if customPreset == 'Tracker':
        presetLabel = 'Tracker'
        presetIcon = 'Tracker.png'
        presetColor = colorsys.hsv_to_rgb(0.2, 1, 0.5)

    if customPreset == 'Mocha':
        presetLabel = 'Mocha'
        presetIcon = 'Tracker.png'
        presetColor = colorsys.hsv_to_rgb(0.2, 1, 0.5)

    if customPreset == 'Keyer':
        presetLabel = 'Keyer'
        presetIcon = 'Keyer.png'
        presetColor = colorsys.hsv_to_rgb(0.333, 1, 0.5)
    
    if customPreset == 'Additive_Key':
        presetLabel = 'Additive Key'
        presetIcon = 'Keyer.png'
        presetColor = colorsys.hsv_to_rgb(0.333, 1, 0.5)

    if customPreset == 'Edge_Fixes':
        presetLabel = 'Edge Fixes'
        presetIcon = 'EdgeDetect.png'
        presetColor = colorsys.hsv_to_rgb(0.256, 0.354, 0.5)

    if customPreset == 'Despill':
        presetLabel = 'Despill'
        presetIcon = 'HueCorrect.png'
        presetColor = colorsys.hsv_to_rgb(0.682, 0.528, 0.5)

    if customPreset == 'Effects':
        presetLabel = 'FX'
        presetIcon = ':qrc/images/ToolbarFilter.png'
        presetColor = colorsys.hsv_to_rgb(0.812, 1, 0.5)

    if customPreset == 'Defocus':
        presetLabel = 'Defocus'
        presetIcon = 'LightWrap.png'
        presetColor = colorsys.hsv_to_rgb(0.41, 0.62, 0.5)

    if customPreset == 'Glow':
        presetLabel = 'Glow'
        presetIcon = 'Glow.png'
        presetColor = colorsys.hsv_to_rgb(0.5, 1, 0.5)

    if customPreset == 'Lens_Flare':
        presetLabel = 'Lens Flare'
        presetIcon = 'Flare.png'
        presetColor = colorsys.hsv_to_rgb(0.152, 0.354, 0.5)
    
    if customPreset == 'Godrays':
        presetLabel = 'Godrays'
        presetIcon = 'GodRays.png'
        presetColor = colorsys.hsv_to_rgb(0.152, 0.354, 0.5)

    if customPreset == 'Light_Wrap':
        presetLabel = 'Light Wrap'
        presetIcon = 'LightWrap.png'
        presetColor = colorsys.hsv_to_rgb(0.91, 0.62, 0.5)

    if customPreset == 'Roto':
        presetLabel = 'Roto'
        presetIcon = 'Roto.png'
        presetColor = colorsys.hsv_to_rgb(0.333, 0.430, 0.384)

    if customPreset == 'Matte':
        presetLabel = 'Matte'
        presetIcon = 'Radial.png'
        presetColor = colorsys.hsv_to_rgb(0.5, 1, 0.1)

    if customPreset == 'Cleanup':
        presetLabel = 'Cleanup'
        presetIcon = 'DustBust.png'
        presetColor = colorsys.hsv_to_rgb(0.450, 0.44, 0.384)

    if customPreset == 'Rig_Removal':
        presetLabel = 'Rig Removal'
        presetIcon = 'MarkerRemoval.png'
        presetColor = colorsys.hsv_to_rgb(0, 0.443, 0.38)

    if customPreset == 'CG':
        presetLabel = 'CG'
        presetIcon = 'Shader.png'
        presetColor = (0.141, 0.047, 0)

    if customPreset == 'CG:Beauty':
        presetLabel = 'CG: Beauty'
        presetIcon = 'Shader.png'
        presetColor = (0.204, 0.133, 0.062)

    if customPreset == 'CG:Beauty_Denoised':
        presetLabel = 'CG: Beautry Denoised'
        presetIcon = 'Shader.png'
        presetColor = (0.204, 0.133, 0.062)
        
    if customPreset == 'CG:Diffuse':
        presetLabel = 'CG: Diffuse'
        presetIcon = 'Shader.png'
        presetColor = (0.204, 0.133, 0.062)
        
    if customPreset == 'CG:Reflection':
        presetLabel = 'CG: Reflection'
        presetIcon = 'Shader.png'
        presetColor = (0.204, 0.133, 0.062)
        
    if customPreset == 'CG:Refraction':
        presetLabel = 'CG: Refraction'
        presetIcon = 'Shader.png'
        presetColor = (0.204, 0.133, 0.062)
        
    if customPreset == 'CG:Shadow':
        presetLabel = 'CG: Shadow'
        presetIcon = 'Shader.png'
        presetColor = (0.204, 0.133, 0.062)
        
    if customPreset == 'CG:Specular':
        presetLabel = 'CG: Specular'
        presetIcon = 'Shader.png'
        presetColor = (0.204, 0.133, 0.062)

    if customPreset == 'CG:Motion_Vectors':
        presetLabel = 'CG: Motion Vectors'
        presetIcon = 'VectorToMotion.png'
        presetColor = colorsys.hsv_to_rgb(0.062, 1, 0.5)

    if customPreset == 'CG:Z-Depth':
        presetLabel = 'CG: Z-Depth'
        presetIcon = 'ZMerge.png'
        presetColor = colorsys.hsv_to_rgb(0.062, 1, 0.5)

    if customPreset == 'CG:Matte':
        presetLabel = 'CG: Matteh'
        presetIcon = 'Cryptomatte.png'
        presetColor = colorsys.hsv_to_rgb(0.062, 1, 0.5)
    
    if customPreset == 'Shuffle':
        presetLabel = 'Shuffle'
        presetIcon = 'Shuffle.png'
        presetColor = colorsys.hsv_to_rgb(0.682, 0.528, 0.5)
    
    if customPreset == '3D':
        presetLabel = '3D'
        presetIcon = 'Shader.png'
        presetColor = colorsys.hsv_to_rgb(0.152, 0, 0.5)

    if customPreset == 'Camera_Tracker':
        presetLabel = 'Camera Tracker'
        presetIcon = 'CameraTracker.png'
        presetColor = (0xF9,0x26,0x72)

    if customPreset == 'Camera_Rig':
        presetLabel = 'Camera Rig'
        presetIcon = 'Camera.png'
        presetColor = colorsys.hsv_to_rgb(0.682, 0, 0.298)

    if customPreset == 'Projection':
        presetLabel = 'Projection'
        presetIcon = 'Project3D_3D@2x.png'
        presetColor = colorsys.hsv_to_rgb(0.333, 1, 0.5)

    if customPreset == '3D_Elements':
        presetLabel = '3D_Element'
        presetIcon = 'GeoImport_3D@2x.png'
        presetColor = colorsys.hsv_to_rgb(1, .5, 0.1)

    if customPreset == 'Set_Extension':
        presetLabel = 'Set Extension'
        presetIcon = 'Reformat.png'
        presetColor = colorsys.hsv_to_rgb(0.2, 1, 0.5)

    if customPreset == 'Particles':
        presetLabel = 'Particles'
        presetIcon = 'ParticleEmitter.png'
        presetColor = colorsys.hsv_to_rgb(0.256, 0.354, 0.5)
    
    if customPreset == 'Color_Correction':
        presetLabel = 'Color Correction'
        presetIcon = 'ColorLookup.png'
        presetColor = colorsys.hsv_to_rgb(0.607, 0.528, 0.5)

    if customPreset == 'Deep':
        presetLabel = 'Deep'
        presetIcon = 'DeepRead.png'
        presetColor = colorsys.hsv_to_rgb(0.5, .1, 1)
        
    if customPreset == 'Controllers':
        presetLabel = 'Controllers'
        presetIcon = 'LevelSet.png'
        presetColor = colorsys.hsv_to_rgb(0.805, 1, 0.3)
    
    if customPreset == 'Write':
        presetLabel = 'Write'
        presetIcon = 'Write.png'
        presetColor = colorsys.hsv_to_rgb(0.167, 1, 0.373) 
    
    if customPreset == 'Previous_Versions':
        presetLabel = 'Previous Versions'
        presetIcon = 'Viewer.png'
        presetColor = colorsys.hsv_to_rgb(0.125, 0, 0.3)

    if customPreset == 'Temp':
        presetLabel = 'Temp'
        presetIcon = 'CheckerBoard.png'
        presetColor = colorsys.hsv_to_rgb(0, 1, 1)

           
#Extras from here down

    if customPreset == 'Light_Setup':
        presetLabel = 'Light Setup'
        presetIcon = 'SpotLight.png'
        presetColor = colorsys.hsv_to_rgb(0.152, 0, 0.5)
        
    if customPreset == 'Relight':
        presetLabel = 'Relight'
        presetIcon = 'ReLight.png'
        presetColor = colorsys.hsv_to_rgb(0.938, 1, 0.5)
        
    if customPreset == 'Resources':
        presetLabel = 'Resources'
        presetIcon = 'Merge.png'
        presetColor = colorsys.hsv_to_rgb(0.682, 0, 0.298)
          
    if customPreset == 'Stereo_Fixes':
        presetLabel = 'Stereo Fixes'
        presetIcon = 'Anaglyph.png'
        presetColor = colorsys.hsv_to_rgb(0.5, 1, 0.267)
        
    if customPreset == 'Temp':
        presetLabel = 'Temp'
        presetIcon = 'CheckerBoard.png'
        presetColor = colorsys.hsv_to_rgb(0, 1, 1)
        
    if customPreset == 'Test':
        presetLabel = 'Test'
        presetIcon = 'ClipTest.png'
        presetColor = colorsys.hsv_to_rgb(0, 0, 0.3)
        
##
        
    
        
        
    ### Backdrop creation based on presets
    if customPreset is not None:
        # RGB to HEX
        r = presetColor[0]
        g = presetColor[1]
        b = presetColor[2]
        hexColour = int("{0:02x}{1:02x}{2:02x}{3:02x}".format(int (r*255), int(g*255),int(b*255),1),16)

        
        if presetIcon == '':
            icon = ''
        else:
            icon = '<img src='+sep+presetIcon+sep+'> '
            
        selNodes = nuke.selectedNodes()
        if not selNodes:
            if customLabel == '':
                return nuke.nodes.BackdropNode(label = '<center>'+icon+presetLabel, tile_color = hexColour, note_font_size = 30)
            else:
                return nuke.nodes.BackdropNode(label = '<center>'+icon+customLabel, tile_color = hexColour, note_font_size = 30)
    
       
        # Find Min. and Max. of Positions
        positions = [(i.xpos(), i.ypos()) for i in selNodes]
        xPos = sorted(positions, key = operator.itemgetter(0))
        yPos = sorted(positions, key = operator.itemgetter(1))
        xMinMaxPos = (xPos[0][0], xPos[-1:][0][0])
        yMinMaxPos = (yPos[0][1], yPos[-1:][0][1])
        
        if customLabel == '':
            n = nuke.nodes.BackdropNode(xpos = xMinMaxPos[0]-10, bdwidth = xMinMaxPos[1]-xMinMaxPos[0]+110, ypos = yMinMaxPos[0]-85, bdheight = yMinMaxPos[1]-yMinMaxPos[0]+160, label = '<center>'+icon+presetLabel, tile_color = hexColour, note_font_size = 30)
        else:
            n = nuke.nodes.BackdropNode(xpos = xMinMaxPos[0]-10, bdwidth = xMinMaxPos[1]-xMinMaxPos[0]+110, ypos = yMinMaxPos[0]-85, bdheight = yMinMaxPos[1]-yMinMaxPos[0]+160, label = '<center>'+icon+customLabel, tile_color = hexColour, note_font_size = 30)
            
        n['selected'].setValue(False)
       
        # Revert to Previous Selection
        [i['selected'].setValue(True) for i in selNodes]
        
        return n
    else:
        pass

if __name__ == "__main__":
    f = open('theme.json', 'r')
    theme = json.load(f)
    f.close()

    backdrop_presets()