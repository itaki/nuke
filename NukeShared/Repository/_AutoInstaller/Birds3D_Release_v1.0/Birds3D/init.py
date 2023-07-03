#Birds3D Tools
nuke.pluginAddPath('./assets')
nuke.pluginAddPath('./icons')
nuke.pluginAddPath('./templates')
nuke.pluginAddPath('./tools')

#Assign Birds3D assets path variable for read nodes in bird nodes
pluginpath = nuke.pluginPath()
birds3d_assets_path = [x for x in pluginpath if "Birds3D/assets" in x][0]
birds3d_templates_path = [x for x in pluginpath if "Birds3D/templates" in x][0]