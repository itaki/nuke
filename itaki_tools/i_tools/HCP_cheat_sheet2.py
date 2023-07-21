m = nuke.thisNode()
kc = nuke.thisKnob()

if kc.name() in ["iterations"]:
    i = nuke.toNode('Merge1')
    i2 = nuke.toNode('Invert1')
    o = nuke.toNode('Transform3')
    
    for n in nuke.allNodes():
      if "static" not in n['label'].getValue():
          ###print "i would delete" + n['name'].value()
          nuke.delete(n)
    
    
    slices = int(m['iterations'].value())
    step = int(1)
    for x in range(1,slices+step,step):

      b1 = nuke.nodes.Blur()
      b1.setInput(0, i)
      b1['size'].setSingleValue(False)
      b1['size'].setExpression("parent.size.w", 0)
      b1['size'].setExpression("parent.size.h", 1)

      b2 = nuke.nodes.Blur()
      b2.setInput(0, i2)
      b2['size'].setSingleValue(False)
      b2['size'].setExpression("parent.size.w", 0)
      b2['size'].setExpression("parent.size.h", 1)

      g1 = nuke.nodes.Grade()
      g1.setInput(0, b2)
      g1['channels'].setValue('rgba')
      g1['blackpoint'].setValue(-0.0001)
      g1['disable'].setExpression("parent.softEdges ? 0 : 1")

      m1 = nuke.nodes.Merge()
      m1.setInput(1, b1)
      m1.setInput(0, g1)
      m1['operation'].setValue("divide")
      
      if x < slices:
         m2 = nuke.nodes.Merge()
         m2.setInput(1, b2)
         m2.setInput(0, g1)
         m2['operation'].setValue("divide")
    
      i = m1
      i2 = m2
    
    o.setInput(0, i)

