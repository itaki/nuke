import nuke
# Replace nukes icons with higher rez versions
# This doesn't actually work. I think it's because the icons are loaded after this script is run.
nuke.menu('Nodes').addMenu("Image", icon="icon_toolbar_image_HighRes.png")
nuke.menu('Nodes').addMenu("Draw", icon="icon_toolbar_draw_HighRes.png")
nuke.menu('Nodes').addMenu("Time", icon="icon_toolbar_time_HighRes.png")
nuke.menu('Nodes').addMenu("Channel", icon="icon_toolbar_channel_HighRes.png")
nuke.menu('Nodes').addMenu("Color", icon="icon_toolbar_color_HighRes.png")
nuke.menu('Nodes').addMenu("Filter", icon="icon_toolbar_filter_HighRes.png")
nuke.menu('Nodes').addMenu("Keyer", icon="icon_toolbar_keyer_HighRes.png")
nuke.menu('Nodes').addMenu("Merge", icon="icon_toolbar_merge_HighRes.png")
nuke.menu('Nodes').addMenu("Transform", icon="icon_toolbar_transform_HighRes.png")
nuke.menu('Nodes').addMenu("3D", icon="icon_toolbar_3d_HighRes.png")
nuke.menu('Nodes').addMenu("Particles", icon="icon_toolbar_particles_HighRes.png")
nuke.menu('Nodes').addMenu("Deep", icon="icon_toolbar_deep_HighRes.png")
nuke.menu('Nodes').addMenu("Views", icon="icon_toolbar_views_HighRes.png")
nuke.menu('Nodes').addMenu("MetaData", icon="icon_toolbar_metadata_HighRes.png")
nuke.menu('Nodes').addMenu("ToolSets", icon="icon_toolbar_toolsets_HighRes.png")
nuke.menu('Nodes').addMenu("Other", icon="icon_toolbar_other_HighRes.png")
nuke.menu('Nodes').addMenu("FurnaceCore", icon="icon_toolbar_furnace_HighRes.png")
nuke.menu('Nodes').addMenu("AIR", icon="icon_toolbar_AIR_HighRes.png")
nuke.menu('Nodes').addMenu("CaraVR", icon="icon_toolbar_CaraVR_HighRes.png")

# Add my own icons
nuke.menu('Nodes').addMenu("Tools", icon="toolbox_icon.png")
nuke.menu('Nodes').addMenu("Scripts", icon="scripts.png")
nuke.menu('Nodes').addMenu("RG Magic Bullet", icon="maxon.png")

