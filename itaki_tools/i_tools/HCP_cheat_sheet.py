kc = nuke.thisKnob()

if kc.name() in ["iterations"]:
    i = nuke.toNode('In')
    #p = nuke.toNode('Premult')
    m = nuke.toNode('Merge')
    b = nuke.toNode('Blur')
    #u = nuke.toNode('Unpremult')
    e = nuke.toNode('Expression')
    o = nuke.toNode('Keymix')
    #eb = p

    for n in nuke.allNodes():
        if "static" not in n['label'].getValue():

            nuke.delete(n)
            o.setInput(0,m)
        
    slices = int(node['iterations'].getValue())
        
    if slices > 1:  
        for x in range(1,slices):  
            p1 = nuke.nodes.Premult()
            p1.setInput(0,e)
            
            b1 = nuke.nodes.Blur()
            b1.setInput(0,p1)
            b1['size'].setExpression('%s.size*mult'%b.name())
            b1['channels'].setValue('rgba')
            
            u1 = nuke.nodes.Unpremult()
            u1.setInput(0,b1)
            
            e1 = nuke.nodes.Expression()
            e1['expr0'].setValue('r*(a/a?a>0.001:r)')
            e1['expr1'].setValue('g*(a/a?a>0.001:g)')
            e1['expr2'].setValue('b*(a/a?a>0.001:b)')
            e1['expr3'].setValue('a/a?a>0.001:0')
            e1.setInput(0,u1)
            
            eb1 = nuke.nodes.EdgeBlur()
            eb1['size'].setExpression('%s.size*softness'%b.name())
            eb1.setInput(0,m)
            
            
            m1 = nuke.nodes.Merge()
            m1.setInput(0,e1)
            m1.setInput(1,eb1)
                        
            b = b1
            e = e1
            m = m1
            
            o.setInput(1,i)
            o.setInput(0,m)
            
if node.input(2):
    if node['maskChannel'].value() == 'none':
        node['maskChannel'].setValue("rgba.alpha")
    else:
        pass
else:
    node['maskChannel'].setValue("none")
    
if node.input(1):

    nuke.toNode('CopyGEE')['disable'].setValue(0)
else:

    nuke.toNode('CopyGEE')['disable'].setValue(1)
    pass      
        
if node['in'].getValue() == 0:
    node['out'].setEnabled(False)
    node['out'].setValue(0)
else:
    node['out'].setEnabled(True)  
    
if node['onThreshold'].getValue() == 0:
    node['threshold'].setEnabled(False)
else:
    node['threshold'].setEnabled(True)
                 