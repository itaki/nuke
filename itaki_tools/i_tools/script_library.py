import nuke
import os

def test(text="the test ran but didn't receive the variable"):
    print (f"{text} : this was printed using the script_library")

def find_file_return_path(filename):
    '''Finds the path of a specified file in 
    the array nuke.pluginPath()
    takes : filename
    returns : path_to_file
    if file is not found
    returns : None
    '''
    nukepaths = nuke.pluginPath()
    path_to_file = None
    for path in nukepaths:
        candidate_path = os.path.join(path, filename)
        #print(f"looking in {candidate_path}")
        if os.path.exists(candidate_path):
            path_to_file = candidate_path
            nuke.tprint("File Found: " + candidate_path)
            break
    return path_to_file


def get_mouse_position():
    '''returns the position of the mouse
    returns : list with [x, y] coordinates'''
    n = nuke.createNode("NoOp")
    position = [n.xpos(), n.ypos()]
    nuke.delete(n)
    return position

def get_script_directory():
    path, this_file = os.path.split(os.path.realpath(__file__))
    return path


    

def get_position_size_of_node_selection(nodes = None):
    '''normally some like nuke.selectedNodes would be sent
    but this could figure out another grouping
    takes : node or selectedNodes
    returns : ['x_pos' : #, 'y_pos' : #, 'width' : #, 'height' : #]'''
    if nodes is None:
        nodes = nuke.selectedNodes() # if no nodes are sent just grab the selected ones
    if len(nodes) == 0:
        print("No nodes selected!")
        return None

    # Calculate bounds for the backdrop node.
    x = min([node.xpos() for node in nodes])
    y = min([node.ypos() for node in nodes])
    w = (max([node.xpos() + node.screenWidth() for node in nodes])) - x
    h = (max([node.ypos() + node.screenHeight() for node in nodes])) - y
    position_and_size = {
                        'x_pos' : x,
                        'y_pos' : y, 
                        'width' : w,
                        'height' : h
                        }
    return position_and_size


class StockIcons():
    '''creates a list or dictionary of nuke icons
    returns an object with
    stock_icons
    html_icon_list | "<img src='path/to/icons/icon.png'> icon.png"
    html_icon_dict | "icon.png" : "<img src='path/to/icons/icon.png'>" '''
    def __init__(self):
        self.html_icon_list = []
        # the first path nuke loads is the stock plugin repository which is last in the list
        self.stock_icons_path = os.path.join(nuke.pluginPath()[-1], 'icons') 
        # add the icons directory to the path
        self.stock_icons = os.listdir(self.stock_icons_path)
        self.stock_icons.sort()
        self.html_icon_list = self.make_html_icon_list()
        self.html_icon_dict = self.make_html_icon_dict()
    
    def make_html_icon_list(self):
        html_icon_list = []
        for icon in self.stock_icons:
            html_icon_list.append(f"<img src='{self.stock_icons_path}/{icon}'> {icon}")
        return html_icon_list

    def make_html_icon_dict(self):
        html_icon_dict = {}
        for icon in self.stock_icons:
            # html_icon_dict[icon] = f"<img src='{self.stock_icons_path}/{icon}'>"
            html_icon_dict[icon] = print(f"<img src='{self.stock_icons_path}/{icon}'>")
        return html_icon_dict
    

def write_degrain_mov():
    pass