kc = nuke.thisKnob()
#b_frame_step= int(node['before_frame_step'].getValue())
if kc.name() in ['before_frames']:
    print('before_frames changed')
    i = nuke.toNode('Input')
    s = nuke.toNode('startdot')
    e = nuke.toNode('enddot')
    
    print (node['mbf'].getValue())

    for n in nuke.allNodes(): #
        if "static" not in n['label'].getValue():
            nuke.delete(n)
        e.setInput(0,s)
        
        
    print(node['before_frames'].getValue())

    before_frames = int(node['before_frames'].getValue())
    print(f'before frames {before_frames}')
    if before_frames > 0:
        for x in range(0,before_frames,1):
            print("adding TimeOffset")
            o = nuke.nodes.TimeOffset()
            o.setInput(0,s)

            m = nuke.nodes.Merge()
            m.setInput(0,o)
            m.setInput(1,s)

            s = m
