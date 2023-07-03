import json
import nuke
import os
import colorsys
import operator
import random
import nukescripts
import colorsys

import script_library
from script_library import StockIcons
testing = False

# If no presets file is given, I will look for this file
preset_database = 'backdrops.json'
padding = { "left" : 70,
            "top" : 140,
            "right" : 70,
            "bottom" : 70
            }

class Backdrop:
    def __init__(self, label='Backdrop', icon='Backdrop.png', color=(20,20,20), font='Verdana', style=('reg','un'), size=30, label_color=(0,0,0) ):
        self.label = label
        self.icon = icon
        self.color = color
        self.font = font
        self.style = style
        self.size = size
        self.label_color = label_color


class BackdropManager:
    def __init__(self):
        self.preset_list = []
        if self.get_presets_local() == False:
            print ("Backdrop manager not loaded")
        else:
            '''Continue the entire build of the backdrop manager here'''
            print ("Backdrop manager start build")
            self.create_list_of_presets()
            print(self.preset_list)


    def get_presets_local(self, file=preset_database):
        # backdrop_presets = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),'backdrops.json')
        presets_dir = script_library.get_script_directory()
        backdrop_presets_file = os.path.join(presets_dir, file)
        if backdrop_presets_file != None:
            with open(backdrop_presets_file, 'r') as f:
                self.presets = json.load(f)['styles']
            return True
        else:
            print("Backdrop presets file not found. Download one at github.com/itaki/nuke")
            return False

    def get_presets(self, file=preset_database):
        path_to_presets_file = script_library.find_file_return_path(file)
        if path_to_presets_file != None:
            with open(path_to_presets_file, 'r') as file:
                self.presets = json.load(file)['styles']
            return True
        else:
            print("Backdrop presets file not found. Download one at github.com/itaki/nuke")
            return False

    def create_list_of_presets(self):
        for preset in self.presets:
            self.preset_list.append(preset['label'])
        
    def create_popup_menu(self):
        selected_preset = None
        p = nuke.Panel('Preset Backdrop')
        p.addEnumerationPulldown('Preset',' '.join(self.preset_list))
        p.addSingleLineInput('Custom Label','')
        if p.show():
            selected_preset = p.value('Preset')
            custom_label = p.value('Custom Label')

        if selected_preset != None:
            self.build_backdrop(selected_preset, custom_label)
        else:
            return
        
    def build_backdrop(self, selected_preset, custom_label):
        # search through the backdrops to find the one I want
        for preset in self.presets:
            if preset['label'] == selected_preset:
                self.create_backdrop(preset, custom_label)
                break
    

    
    def create_backdrop(self, preset, custom_label):
        
        # set label
        if custom_label == '':
            custom_label = preset['label']
        # set color
        r = float(preset['color'][0])
        g = float(preset['color'][1])
        b = float(preset['color'][2])
        # all colors need to be delivered to knobs as HEX
        tile_color = int("{0:02x}{1:02x}{2:02x}{3:02x}".format(int (r*255), int(g*255),int(b*255),1),16)

        # set label color
        r = float(preset['label_color'][0])
        g = float(preset['label_color'][1])
        b = float(preset['label_color'][2])
        note_color = int("{0:02x}{1:02x}{2:02x}{3:02x}".format(int (r*255), int(g*255),int(b*255),1),16)

        # set icon
        if preset['icon'] == '':
            icon = ''
        else:
            sep = '"'
            icon = '<img src='+sep+preset['icon']+sep+'> '

        # get position and size of node selection    
        selected_nodes = nuke.selectedNodes()
        if selected_nodes != None and len(selected_nodes) != 0:
            position_and_size = script_library.get_position_size_of_node_selection(selected_nodes)
        else:
            position_and_size={}
            mouse_position = script_library.get_mouse_position()
            position_and_size['x_pos'] = mouse_position[0]
            position_and_size['y_pos'] = mouse_position[1]
            position_and_size['width'] = 0
            position_and_size['height'] = 0

        # calculate the paddings
        x_pos = position_and_size['x_pos'] - padding['left']
        y_pos = position_and_size['y_pos'] - padding['top']
        width = position_and_size['width'] + padding['right'] + padding['left']
        height = position_and_size['height'] + padding['bottom'] + padding['top']

        # calculate z order

        #min_z = mix(selected_nodes["z_order"])
        z = 0
        for node in selected_nodes:
            if node.Class() == 'BackdropNode':
                if float(node.knob('z_order').getValue()) < z:
                    z = float(node.knob('z_order').getValue())
        z -= 1
     
        n = nuke.nodes.BackdropNode(
            xpos = x_pos, 
            bdwidth = width, 
            ypos = y_pos, 
            bdheight = height, 
            label = f'<center> {icon} {custom_label}', 
            tile_color = tile_color, 
            note_font = preset['font'],
            note_font_size = preset['size'],
            note_font_color = note_color,
            appearance = preset['appearance'],
            z_order = z
            )

        # Set backdrop to not be selected    
        n['selected'].setValue(False)
    
        # Revert to Previous Selection
        [i['selected'].setValue(True) for i in selected_nodes]
        

        n.showControlPanel()

        # Buid all knobs for Backdrop
        tab = nuke.Tab_Knob('F_VFX', 'BackdropNode')
        text = nuke.Multiline_Eval_String_Knob('text', 'Text')
        position = nuke.Enumeration_Knob('position', '', ['Left', 'Center'])
        size = nuke.Double_Knob('font_size', 'Font Size') 
        size.setRange(10,100)
        space1 = nuke.Text_Knob('S01', ' ', ' ')
        space2 = nuke.Text_Knob('S02', ' ', ' ')

        grow = nuke.PyScript_Knob('grow', ' <img src="F_scalep.png">', "n=nuke.thisNode()\n\ndef grow(node=None,step=50):\n    try:\n        if not node:\n            n=nuke.selectedNode()\n        else:\n            n=node\n            n['xpos'].setValue(n['xpos'].getValue()-step)\n            n['ypos'].setValue(n['ypos'].getValue()-step)\n            n['bdwidth'].setValue(n['bdwidth'].getValue()+step*2)\n            n['bdheight'].setValue(n['bdheight'].getValue()+step*2)\n    except:\n        pass\ngrow(n,50)")
        shrink = nuke.PyScript_Knob('shrink', ' <img src="F_scalem.png">', "n=nuke.thisNode()\n\ndef shrink(node=None,step=50):\n    try:\n        if not node:\n            n=nuke.selectedNode()\n        else:\n            n=node\n            n['xpos'].setValue(n['xpos'].getValue()+step)\n            n['ypos'].setValue(n['ypos'].getValue()+step)\n            n['bdwidth'].setValue(n['bdwidth'].getValue()-step*2)\n            n['bdheight'].setValue(n['bdheight'].getValue()-step*2)\n    except:\n        pass\nshrink(n,50)")

        colorandom = nuke.PyScript_Knob('colorandom', ' <img src="ColorBars.png">', "import colorsys, random\nn=nuke.thisNode()\nR,G,B= colorsys.hsv_to_rgb(random.random(),.1+random.random()*.15,.15+random.random()*.15)\nR,G,B=int(R*255),int(G*255),int(B*255)\nn['tile_color'].setValue( int('%02x%02x%02x%02x' % (R,G,B,255), 16 ) )")

        red = nuke.PyScript_Knob('red', ' <img src="F_r.png">', "import colorsys\nn=nuke.thisNode()\nR,G,B= [0.0, 0.77, 0.8]\nR,G,B=colorsys.hsv_to_rgb(R,G,B)\nR,G,B=int(R*255),int(G*255),int(B*255)\nn['tile_color'].setValue( int('%02x%02x%02x%02x' % (R,G,B,255), 16 ))\n")
        orange = nuke.PyScript_Knob('orange', ' <img src="F_o.png">', "import colorsys\nn=nuke.thisNode()\nR,G,B= [0.1, 0.8, 0.8]\nR,G,B=colorsys.hsv_to_rgb(R,G,B)\nR,G,B=int(R*255),int(G*255),int(B*255)\nn['tile_color'].setValue( int('%02x%02x%02x%02x' % (R,G,B,255), 16 ))\n")
        yellow = nuke.PyScript_Knob('yellow', ' <img src="F_y.png">', "import colorsys\nn=nuke.thisNode()\nR,G,B= [0.16, 0.8, 0.8]\nR,G,B=colorsys.hsv_to_rgb(R,G,B)\nR,G,B=int(R*255),int(G*255),int(B*255)\nn['tile_color'].setValue( int('%02x%02x%02x%02x' % (R,G,B,255), 16 ))\n")
        green = nuke.PyScript_Knob('green', ' <img src="F_g.png">', "import colorsys\nn=nuke.thisNode()\nR,G,B= [0.33, 0.8, 0.7]\nR,G,B=colorsys.hsv_to_rgb(R,G,B)\nR,G,B=int(R*255),int(G*255),int(B*255)\nn['tile_color'].setValue( int('%02x%02x%02x%02x' % (R,G,B,255), 16 ))\n")
        cyan = nuke.PyScript_Knob('cyan', ' <img src="F_c.png">', "import colorsys\nn=nuke.thisNode()\nR,G,B= [0.46, 0.8, 0.7]\nR,G,B=colorsys.hsv_to_rgb(R,G,B)\nR,G,B=int(R*255),int(G*255),int(B*255)\nn['tile_color'].setValue( int('%02x%02x%02x%02x' % (R,G,B,255), 16 ))\n")
        blue = nuke.PyScript_Knob('blue', ' <img src="F_b.png">', "import colorsys\nn=nuke.thisNode()\nR,G,B= [0.6, 0.7, 0.76]\nR,G,B=colorsys.hsv_to_rgb(R,G,B)\nR,G,B=int(R*255),int(G*255),int(B*255)\nn['tile_color'].setValue( int('%02x%02x%02x%02x' % (R,G,B,255), 16 ))\n")
        darkblue = nuke.PyScript_Knob('darkblue', ' <img src="F_db.png">', "import colorsys\nn=nuke.thisNode()\nR,G,B= [0.67, 0.74, 0.6]\nR,G,B=colorsys.hsv_to_rgb(R,G,B)\nR,G,B=int(R*255),int(G*255),int(B*255)\nn['tile_color'].setValue( int('%02x%02x%02x%02x' % (R,G,B,255), 16 ))\n")
        magenta = nuke.PyScript_Knob('magenta', ' <img src="F_m.png">', "import colorsys\nn=nuke.thisNode()\nR,G,B= [0.8, 0.74, 0.65]\nR,G,B=colorsys.hsv_to_rgb(R,G,B)\nR,G,B=int(R*255),int(G*255),int(B*255)\nn['tile_color'].setValue( int('%02x%02x%02x%02x' % (R,G,B,255), 16 ))\n")
        pink = nuke.PyScript_Knob('pink', ' <img src="F_p.png">', "import colorsys\nn=nuke.thisNode()\nR,G,B= [0.92, 0.74, 0.8]\nR,G,B=colorsys.hsv_to_rgb(R,G,B)\nR,G,B=int(R*255),int(G*255),int(B*255)\nn['tile_color'].setValue( int('%02x%02x%02x%02x' % (R,G,B,255), 16 ))\n")
        
        icons = StockIcons().make_html_icon_dict()
        icon_selector = nuke.Pulldown_Knob("icon", "Icon", icons)
        icon_label = nuke.Text_Knob("icon_label", "Selected Icon", "")
        icon_label.setValue(icon_selector.getValue())
        copyright = nuke.Text_Knob("Ftools","","<font color=\"#1C1C1C\"> v1.2 - Franklin VFX - 2018")

        n.addKnob(tab)
        n['knobChanged'].setValue("try:\n    listenedKnobs = ['text', 'position', 'name']\n    node = nuke.thisNode()\n    name = node.knob('name').value()\n    text = node.knob('text').value()\n    position = node.knob('position').value()\n    position = \"<\" + position + \">\"\n    label = node.knob('label').value()\n    \n    if nuke.thisKnob().name() in listenedKnobs:\n        if text == \"\":\n            if node.knob('position').value() == \"left\":\n                node.knob('label').setValue()\n            else:\n                node.knob('label').setValue(position + name)\n        else:\n            if node.knob('position').value() == \"left\":\n                node.knob('label').setValue(text)\n            else:\n                node.knob('label').setValue(position + text)\n                \n    elif nuke.thisKnob().name() == 'font_size':\n        fontSize = node.knob('font_size').value()\n        node.knob('note_font_size').setValue(fontSize)\nexcept:\n    pass")
        n.addKnob(text)
        n['text'].setFlag(nuke.STARTLINE)
        n.addKnob(size)
        n['font_size'].setValue(50)
        n.addKnob(position)
        n['position'].clearFlag(nuke.STARTLINE)
        n.addKnob(space1)
        n.addKnob(grow)
        n.addKnob(shrink)
        n.addKnob(colorandom)
        n.addKnob(red)
        n.addKnob(orange)
        n.addKnob(yellow)
        n.addKnob(green)
        n.addKnob(cyan)
        n.addKnob(blue)
        n.addKnob(darkblue)
        n.addKnob(magenta)
        n.addKnob(pink)
        n.addKnob(space2)
        n.addKnob(copyright)
        n.addKnob(icon_selector)
        n.addKnob(icon_label)

        # revert to previous selection
        n['selected'].setValue(True)
        
        # Make the backdrop
        return n




if __name__ == '__main__':
    #testing = True
    bd = BackdropManager()
