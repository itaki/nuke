#reference and icon or image from anywhere
#Location of the icons
import os
my_path = os.path.dirname(__file__)
iconFolder = os.path.join(my_path, "path_from_this_file_to_the_image")

#to swap out new node with regular nuke node
nuke.menu( 'Nodes' ).addCommand( 'Image/Constant', "nuke.createNode( 'ConstantPro' )")


# to add unicode to a gizmo
'''<span style='font-size:45px;'>&#x1F334;</span>

<b><span style="font-size:49px">Color Picker</span><span style="font-size:18px"> by Lundy Hu</span></b>

'''
# Use HTML

#reload modules in nuke
import importlib
importlib.reload(myModule)


#this could get file in the same directory as the python file
PresetsFile = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),'presets/GradientPresets.cfg')

function render() { return}