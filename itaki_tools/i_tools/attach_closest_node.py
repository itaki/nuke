import nuke, math
def get_closest_node(node):
    # Return the closest node to node
    distances = {}
    for n in nuke.allNodes():
        if n.name() == node.name():
            continue
        distance = math.sqrt( 
            math.pow( (node.xpos() - n.xpos()), 2 ) + math.pow( (node.ypos() - n.ypos()), 2 )
        )
        distances[n.name()] = distance
    return nuke.toNode(min(distances, key=distances.get))
        

def connect_to_closest(direction=0):
    # Connect next available input of all selected nodes to the closest node
    print("CONNECTING TO CLOSEST")
    for node in nuke.selectedNodes():
        closest = get_closest_node(node)
        if direction:
            closest.setInput(0, node)
        else:
            node.connectInput(0, closest)