#fixpaths v0.1 ~ Michael McReynolds itaki.com

import os
import nuke

def get_current_path():
    '''gets the path value of the current node if it is a read node.
    If not it will grab all the nodes and 
    will ask for the path you change
    -> current_path or False if there are no paths '''
    current_path = str
    
    if nuke.nodesSelected("Read"): # if there is a read node selected
        currentReadNode = nuke.selectedNode()
        current_path = currentReadNode["file"].value()
        return current_path
    else:
        print("no READ nodes are selected")
        readNodes = nuke.allNodes('Read')
        print(readNodes[0])
        if readNodes: # if there is a read node in the script, grab the first one
            current_path == readNodes[0]["file"].value()
            return current_path
        else:
            nuke.error("There are no READ nodes")
        return False

def get_new_path(): 
    '''presents the current path and allows the user to 
    set a new project directory'''


def fixpaths():
    nuke.error("made it to fixpaths")
    getErrorPath = nuke.getInput('Old Path', 'Past your old Path')
    if not getErrorPath:
        return

    else:
        getNewPath = nuke.getInput('New Path', 'Past Your New Path')

        for node in nuke.allNodes('Read'):
            readPath = node['file'].value()

            if getErrorPath in readPath:
                newPath = readPath.replace(getErrorPath, getNewPath)
                node['file'].setValue(newPath)

current_path = get_current_path()  
print(current_path)
if current_path != False:

    fixpaths()

else:
    pass

