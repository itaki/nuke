#fixpaths v0.1 ~ Michael McReynolds itaki.com

import os
import nuke



def get_current_path():
    '''gets the path value of the current node,
    asks if that's the path you want change.
    if not, will ask for the path you change '''
    if not nuke.nodesSelected():
        nuke.error("READ node not selected") 
        return False
    if nuke.selectedNodes() == 'Read':
        print("selected node is read")
        current_path = nuke.getReadFileKnob()

        return current_path
        

def fixpaths():
        nuke.error("made it to fixpaths")
    

    getErrorPath = nuke.getInput('Old Path', 'Past your old Path')
    getNewPath = nuke.getInput('New Path', 'Past Your New Path')

    for node in nuke.allNodes('Read'):
        readPath = node['file'].value()

        if getErrorPath in readPath:
            newPath = readPath.replace(getErrorPath, getNewPath)
            node['file'].setValue(newPath)

current_path = get_current_path()  
if current_path != False:

    fixpaths()

else:
    exit()

