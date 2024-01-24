import nuke

toolbar = nuke.toolbar("Nodes")

m = toolbar.addMenu("Particles/Birds3D", icon="Birds3D_Icon.png")

m_birds = m.addMenu("Birds")
m_templates = m.addMenu("Templates")

m_birds.addCommand("Wood Pigeon", "nuke.createNode(\"Bird3D_WoodPigeon\")")
m_birds.addCommand("Crow", "nuke.createNode(\"Bird3D_Crow\")")
m_birds.addCommand("Seagull", "nuke.createNode(\"Bird3D_Seagull\")")
m_birds.addCommand("Scarlet Macaw", "nuke.createNode(\"Bird3D_ScarletMacaw\")")
m_birds.addCommand("Blue Gold Macaw", "nuke.createNode(\"Bird3D_BlueGoldMacaw\")")


m_templates.addCommand("Large Random Flock", "nuke.nodePaste(birds3d_templates_path+\"/Birds3D_Template_LargeRandom.nk\")")
m_templates.addCommand("Murmuration", "nuke.nodePaste(birds3d_templates_path+\"/Birds3D_Template_Murmuration.nk\")")
m_templates.addCommand("Circling", "nuke.nodePaste(birds3d_templates_path+\"/Birds3D_Template_Circling.nk\")")