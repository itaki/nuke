import os

import node_graph_utils

ICONS_ROOT = os.path.join(os.path.dirname(__file__), 'icons')
node_graph_utils.install_menus(icons_root=ICONS_ROOT, install_experimental_menus=True)


import Dots

m=nuke.menu('Nuke')

n=m.addMenu('coolDotFromInternet/NodeGraph',icon='NodeGrapf.png')

n.addCommand ('Dots', 'Dots.Dots()', 'alt+,')
