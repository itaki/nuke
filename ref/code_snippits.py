#reference and icon or image from anywhere
#Location of the icons
import os
my_path = os.path.dirname(__file__)
iconFolder = os.path.join(my_path, "path_from_this_file_to_the_image")

#to swap out new node with regular nuke node
nuke.menu( 'Nodes' ).addCommand( 'Image/Constant', "nuke.createNode( 'ConstantPro' )")