################

"""
	sb_globalToolset
	Simon Bjork
	March 2014
	Version 2.0 (April 2015)
	bjork.simon@gmail.com

	To install the script:

	- Add the script to your Nuke pluginPath.
	- Add the following to your menu.py:

	import sb_globalToolset
	sb_tools = nuke.toolbar("Nodes").addMenu( "sb_Tools", icon = "sb_tools.png" )
	sb_tools.addCommand("Python/sb GlobalToolset", 'sb_globalToolset.sb_globalToolset("D:/tools/Toolsets")', '')

"""

################

import nuke
import nukescripts
import bisect
import os

################

def sb_globalToolset_Data():

	data = {}
	data["scriptName"] = "sb GlobalToolset"
	data["scriptVersion"] = "2.0"
	return data

def insertToolset(menu_name, path):
	'''
	Insert a toolset in the Toolset menu.
	'''
	m = nuke.menu("Nodes").findItem("ToolSets")
	items = m.items()
	names = []
	for i in range(0, len(items)-2):
		name = items[i].name()
		if items[i+2].name() == "Delete":
			break
		names.append(name)
	name_split = menu_name.split("/")
	bisect.insort(names, name_split[0])
	mi = names.index(name_split[0])
	if len(name_split) > 1:
		me = m.addMenu("/".join(name_split[:-1]), index=mi)
		me.addCommand(name_split[-1], 'nuke.loadToolset("%s")' % path, "")
	else:
		m.addCommand(name_split[-1], 'nuke.loadToolset("%s")' % path, "", index=mi)

class sb_globalToolset_Panel(nukescripts.PythonPanel):

	def __init__(self, path, subfolder):
		scriptData = sb_globalToolset_Data()
		nukescripts.PythonPanel.__init__(self, '{0} v{1}'.format(scriptData["scriptName"], scriptData["scriptVersion"]))
		self.path = nuke.File_Knob("path", "path")
		self.sub = nuke.String_Knob("subfolder", "subfolder")
		self.div1 = nuke.Text_Knob("divider1", "")
		self.name = nuke.String_Knob("name", "name")
		self.div2 = nuke.Text_Knob("divider2", "")
		self.save = nuke.PyScript_Knob("save", "save toolset")
		for i in [self.path, self.sub, self.div1, self.name, self.div2, self.save]:
			self.addKnob(i)

		# Set knobs.
		self.path.setValue(path)
		self.sub.setValue(subfolder)

	# Set knobChanged commands.
	def knobChanged(self, knob):
		if knob is self.save:
			self.globalToolset()

	# Main function.
	def globalToolset(self):

		path = self.path.value()
		sub = self.sub.value()
		name = self.name.value()

		# Error checking.
		if len(nuke.selectedNodes()) == 0:
			nuke.message("No nodes selected.")
			return

		if not path:
			nuke.message("Specify a folder path.")
			return

		if not name:
			nuke.message("Specify a name.")
			return
		
		if path.endswith("/"):
			path = path[:-1]

		if not "ToolSets" in path.split("/"):
			path = "{0}/ToolSets".format(path)

		if sub:
			path = "{0}/{1}".format(path, sub)

		# Check if the base is in the pluginPath.
		base, subs = path.split("ToolSets")
		plug_paths = [i.replace("\\", "/") for i in nuke.pluginPath()]
		if not base[:-1] in plug_paths:
			ask = nuke.ask("ERROR: Can't find '{0}' in the pluginPath. This is required for Nuke to be able to load the Toolset. Are you sure you want to continue?".format(base[:-1]))
			if not ask:
				return

		# Create folders if needed.
		if not os.path.isdir(path):
			try:
				os.makedirs(path)
			except:
				nuke.message("ERROR: Can't create folders at path:\n\n'{0}'".format(path))
				return

		# Create the file.
		namefix = name.replace(" ", "_")
		toolset = "{0}/{1}.nk".format(path, namefix)
		nuke.nodeCopy(toolset)

		# Add the toolset to a menu.
		if subs:
			menu_name = "{0}/{1}".format(subs[1:], namefix)
		else:
			menu_name = namefix
		insertToolset(menu_name, toolset)

		nuke.message("{0}.nk was successfully exported as a ToolSet.".format(namefix))

# Run main script.
def sb_globalToolSet(path="", subfolder=""):
	p = sb_globalToolset_Panel(path, subfolder)
	p.show()