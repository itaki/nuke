################

"""
	sb_autoRender
	Simon Bjork
	April 2014
	Version 1.5 (June 2015)
	bjork.simon@gmail.com

	Synopsis: Automatically setup write paths when rendering. Customizable to fit most pipelines.
	OS: Windows/OSX/Linux

	To install the script:
	- Add the script to your Nuke pluginPath.
	- Add the following to your init.py/menu.py:

	#init.py	
	import sb_autoRender
	nuke.addBeforeRender(sb_autoRender.sb_autoRender)

	#menu.py (default setup)
	import sb_autoRender
	sb_tools = nuke.toolbar("Nodes").addMenu( "sb_Tools", icon = "sb_tools.png" )
	sb_tools.addCommand('Python/sb AutoRender', 'sb_autoRender.sb_autoRender()', "shift+w")

	--------------------------

	You also have the option to set default values to most of the knobs depending on your pipeline.
	The syntax for adding a custom version of sb_autoWrite:
	<menu-bar>.addCommand("<name in menu>", 'sb_autoRender.sb_autoRenderNode(<root folder method>, <user input (search word/environment variables)>, <custom path>, <render name>, <custom name>, <add subfolder>, <render type>, <prefix>, <suffix>, <add colorspace to filename>, <use OCIO for color conversions>, <channels>, <colorspace>, <file extension>, <main render folder>, <precomp render folder>, <proxy render folder>, <framepadding separator (._-)>, <framepadding (#)> )', '')
	Note that the environment variable USE_OCIO (set to "1") will override the useOCIO argument.
	Most of the string knobs (exluding the rootFolderUserInput knob) can be written as TCL expressions and evaluated at rendertime. For example you could add _[value channels] to write the channels as a suffix.

	To make the custom setup more readable, I recommend using something like the following in your menu.py::

	import sb_autoRender
	sb_tools = nuke.toolbar("Nodes").addMenu( "sb_Tools", icon = "sb_tools.png" )

	sb_tools.addCommand("Python/sb AutoRender", '''sb_autoRender.sb_autoRenderNode(
		rootFolderMethod="search word",
		rootFolderUserInput="comp", 
		customRenderPath="",
		renderType="main render",
		renderName="script name",
		customName="",
		prefix="",
		suffix="",
		addSubfolder=True,
		addColorspaceSubfolder=False,
		addFileExtensionSubfolder=False,
		addColorToFileName=True,
		useOCIO=True,
		channels="rgb",
		colorspace="Cineon",
		fileType="dpx",
		mainRenderFolder="publish/comp",
		precompRenderFolder="publish/precomp",
		proxyRenderFolder="publish/proxy",
		framePaddingSep=".",
		framePadding="####"
		)''', "shift+w")

"""
################

import os
import nuke
import re
import PyOpenColorIO as OCIO

################

def sb_autoRender_Data():
	data = {}
	data["scriptName"] = "sb AutoRender"
	data["scriptVersion"] = "1.5"
	return data

def sb_autoRenderCreateRenderDirs(path):
	dirname = os.path.dirname(path)
	if not os.path.exists(dirname):
		try:
			os.makedirs(dirname)
		except OSError:
			pass

def getNodeInput(node, input, ignoreNode='Dot'):
	''' 
	Get input from node, ignoring a specific node.
	print getNodeInput(nuke.selectedNode(), 0)
	'''    
	found = False     
	while not found:
		# Get input.        
		currInput = node.input(input)        
		# If no input is found, return False.
		if currInput == "" or currInput == None:
			return False
		if currInput.Class() == ignoreNode:
			# If not found, keep looking.
			return getNodeInput( currInput, 0, ignoreNode ) 
		else: 
			found = True 
			return currInput

def replaceEnvsInsideBrackets(str):
	'''
	Replace envrionment variables within brackets
	myStr = "My temp dir is: [TEMP]
	print replaceEnvsInsideBrackets(myStr)
	>> My temp dir is: C:/Users/Simon/AppData/Local/Temp
	'''
	foundEnvs = re.findall(r'\[([^]]*)\]', str)	
	for i in foundEnvs:
		env = i
		val = os.getenv(env.replace("'", "").replace('"', ''))
		if not val:
			raise Exception ("Could not find environment variable: {0}".format(env))
		str = str.replace("[{0}]".format(env), val.replace("\\", "/"))
	return str

def getOCIOConfig():
	'''
	Get the current OCIO config.
	If the $OCIO environment variable is not set, create a new config from the nuke-default that ships with Nuke.
	'''
	if os.getenv("OCIO"):
		return OCIO.GetCurrentConfig()
	else:
		nukeDir = os.path.dirname(nuke.env['ExecutablePath'])
		nuke_default_config = OCIO.Config.CreateFromFile("{0}/plugins/OCIOConfigs/configs/nuke-default/config.ocio".format(nukeDir))
		return nuke_default_config

def getOCIOColorSpaces():	
	'''
	Get all OCIO colorspaces
	If a family name exist, return <family name>/<name>, otherwise return <name>.
	'''
	colorSpaces = []
	for i in getOCIOConfig().getColorSpaces():
		name = i.getName()
		familyName = i.getFamily()
		if familyName:
			colorSpaces.append("{0}/{1}".format(familyName, name))
		else:
			colorSpaces.append(name)
	return colorSpaces

def getOCIOFamilyAndName(colorSpaceName):
	'''
	Return colorspace family/name.
	If no family name, return name.
	If not found, return False
	'''
	colorFamily = False
	colorSpace = False
	for i in getOCIOConfig().getColorSpaces():
		if i.getName().lower() == colorSpaceName.lower():
			colorSpace = i.getName()
			colorFamily = i.getFamily()
			break
	if colorFamily:
		colorSpace = "{0}/{1}".format(colorFamily, colorSpace)
	return colorSpace

def colorspaceNameFix(colorspace):
	'''
	Fixes Nuke's default colorspace name.
	default (Cineon) >> Cineon.
	'''
	colorNameFix = re.findall(r'\(([^]]*)\)', colorspace)
	if colorNameFix:
		return colorNameFix[0]
	else:
		return colorspace

def rootFolderHelp():

	helpText = """

	<b>Root folder method</b> 

	The root folder works as the base for the full render path. This is the key parameter in having the script automatically work out where you want your renders located.
	 
	<b>-Search word:</b>
	Search for a specific word in the file path of the current Nuke script. The root folder will then be set one level up from the search word. For example, let's say we have a script saved at D:/show/shot01/nuke/shot01_v001.nk, and we use 'nuke' as search word. The root folder will then be set to D:/projects/show/shot01/.

	<b>- Environment variables:</b>
	Evaluate environment variables to build the root folder. Use [<name>] syntax for environment variables. For example: D:/projects/[SHOW]/[SEQ]/[SHOT]/.

	<b>- Custom path:</b>
	Manually set the root folder.

	"""
	return helpText

def sb_autoRenderNode(rootFolderMethod="search word", rootFolderUserInput="scripts", customRenderPath="", renderType="main render", renderName="script name", customName="", prefix="", suffix="", addSubfolder=True, addColorspaceSubfolder=False, addFileExtensionSubfolder=False, addColorToFileName=True, useOCIO=True, channels="rgb", colorspace="linear", fileType="exr", mainRenderFolder="renders/main", precompRenderFolder="render/precomp", proxyRenderFolder="render/proxy", framePaddingSep=".", framePadding="#####"):

	# Environment variable that override the argument.
	# The USE_OCIO env is also used by sb_createRead.py.
	if os.getenv("USE_OCIO") in ["1", "True"]:
		useOCIO = True

	# Get the OCIO config.
	# If the $OCIO env is not set, it will return the internal Nuke config.
	OCIOColorSpaces = getOCIOColorSpaces()

	if useOCIO:
		o = nuke.createNode("OCIOColorSpace", inpanel=False)

		# Get full name of OCIO (<family>/<name>).
		ocioFamilyAndName = getOCIOFamilyAndName(colorspace)

		# Setup the OCIO node.
		o["out_colorspace"].setEnabled(False)		
		o["tile_color"].setValue(8847615)
		
		n = nuke.createNode("Write", inpanel=False)
		n.setInput(0, o)
		n["xpos"].setValue(o["xpos"].value())
		n["ypos"].setValue(o["ypos"].value()+75)
		n["raw"].setValue(True)

		o["selected"].setValue(True)
		n["selected"].setValue(True)
	else:
		n = nuke.createNode("Write", inpanel=False)

	# Setup Write node.
	n["tile_color"].setValue(4289462527)
	script_info = sb_autoRender_Data()
	n["label"].setValue("{0} ({1})".format(script_info["scriptName"], script_info["scriptVersion"]))
	# name = n["name"].value()

	# Add main tab.
	mainTab = nuke.Tab_Knob("sb_autoRender", "sb AutoRender")

	hiddenEvalKnob = nuke.File_Knob("hiddenEvalKnob", "hiddenEvalKnob")

	rootFolderMethodKnob = nuke.Enumeration_Knob("rootFolderMethod", "root folder method", ["search word", "environment variables", "custom path"])
	rootFolderHelpKnob = nuke.PyScript_Knob("rootFolderHelpKnob", "?", "")
	rootFolderHelpKnob.clearFlag(nuke.STARTLINE)
	rootFolderUserInputKnob = nuke.String_Knob("rootFolderUserInput", "user input")
	customRootFolderKnob = nuke.File_Knob("customRootFolderPath", "custom path")
	div1 = nuke.Text_Knob("divider1", "")

	renderTypeKnob = nuke.Enumeration_Knob("renderType", "render type", ["main render", "precomp render", "proxy render", "none"])
	div2 = nuke.Text_Knob("divider2", "")

	renderNameKnob = nuke.Enumeration_Knob("renderName", "render name", ["script name", "custom name"])
	customNameKnob = nuke.String_Knob("customName", "custom name")
	div3 = nuke.Text_Knob("divider3", "")

	prefixKnob = nuke.String_Knob("prefix", "prefix")
	suffixKnob = nuke.String_Knob("suffix", "suffix")
	div4 = nuke.Text_Knob("divider4", "")

	addSubfolderKnob = nuke.Boolean_Knob('addSubfolder', "add filename subfolder")
	addSubfolderKnob.setFlag(nuke.STARTLINE)
	addColorspaceSubfolderKnob = nuke.Boolean_Knob('addColorspaceSubfolder', "add colorspace subfolder")
	addColorspaceSubfolderKnob.setFlag(nuke.STARTLINE)
	addFileExtensionSubfolderKnob = nuke.Boolean_Knob('addFileExtensionSubfolder', "add file extension subfolder")
	addFileExtensionSubfolderKnob.setFlag(nuke.STARTLINE)
	addColorNameKnob = nuke.Boolean_Knob('addColorSpaceName', "add colorspace to filename")
	addColorNameKnob.setFlag(nuke.STARTLINE)
	useOCIOKnob = nuke.Boolean_Knob("use_ocio", "use OCIO for color conversions")
	useOCIOKnob.setFlag(nuke.STARTLINE)
	div5 = nuke.Text_Knob("divider5", "")
	
	channelsKnob = nuke.Link_Knob("c", "channels")
	OCIOColorSpaceKnob = nuke.CascadingEnumeration_Knob("OCIOColorSpace", "colorspace", OCIOColorSpaces)
	colorspaceKnob = nuke.Link_Knob("cs", "colorspace")
	rawKnob = nuke.Link_Knob("raw_color", "raw")
	rawKnob.clearFlag(nuke.STARTLINE)
	fileTypeKnob = nuke.Link_Knob("ft", "file type")
	dataTypeKnob = nuke.Link_Knob("datatype2", "datatype")
	compressionKnob = nuke.Link_Knob("compression2", "compression")
	qualityKnob = nuke.Link_Knob("_jpeg_quality2", "quality")
	subSamplingKnob = nuke.Link_Knob("_jpeg_sub_sampling2", "subsampling")
	div6 = nuke.Text_Knob("divider6", "")
	renderKnob = nuke.PyScript_Knob("rl", '<b><font color="green"><size><font size="6">render</font size></font></b>', "nukescripts.render_panel((nuke.thisNode(),), False)")
	div7 = nuke.Text_Knob("divider7", "")

	# Add knobs.
	for i in [mainTab, hiddenEvalKnob, rootFolderMethodKnob, rootFolderHelpKnob, rootFolderUserInputKnob, customRootFolderKnob, div1, renderTypeKnob, div2, renderNameKnob, customNameKnob, div3, prefixKnob, suffixKnob, div4, addSubfolderKnob, addColorspaceSubfolderKnob, addFileExtensionSubfolderKnob, addColorNameKnob, useOCIOKnob, div5, channelsKnob, OCIOColorSpaceKnob, colorspaceKnob, rawKnob, fileTypeKnob, dataTypeKnob, compressionKnob, qualityKnob, subSamplingKnob, div6, renderKnob, div7]:
		n.addKnob(i)

	# Link knobs.
	channelsKnob.setLink("channels")
	colorspaceKnob.setLink("colorspace")
	rawKnob.setLink("raw")
	fileTypeKnob.setLink("file_type")

	dataTypeKnob.setLink("datatype")
	compressionKnob.setLink("compression")
	qualityKnob.setLink("_jpeg_quality")
	subSamplingKnob.setLink("_jpeg_sub_sampling")

	# Set default values.
	rootFolderMethodKnob.setValue(rootFolderMethod)
	rootFolderUserInputKnob.setValue(rootFolderUserInput)
	customRootFolderKnob.setValue(customRenderPath)
	rootFolderHelpKnob.setValue( 'nuke.message("""{0}""")'.format(rootFolderHelp()) )
	renderTypeKnob.setValue(renderType)
	renderNameKnob.setValue(renderName)
	customNameKnob.setValue(customName)
	prefixKnob.setValue(prefix)
	suffixKnob.setValue(suffix)
	addSubfolderKnob.setValue(addSubfolder)
	addColorspaceSubfolderKnob.setValue(addColorspaceSubfolder)
	addFileExtensionSubfolderKnob.setValue(addFileExtensionSubfolder)
	addColorNameKnob.setValue(addColorToFileName)
	useOCIOKnob.setValue(useOCIO)
	n["channels"].setValue(channels)
	n["file_type"].setValue(fileType)

	# Hide/Show knobs.
	if useOCIOKnob.value():
		n.knobs()["cs"].setVisible(False)
		n.knobs()["raw_color"].setVisible(False)
		try:
			n["OCIOColorSpace"].setValue(ocioFamilyAndName)
		except Exception as e:
			# nuke.message(str(e))
			pass
	else:
		n["OCIOColorSpace"].setVisible(False)
		n["colorspace"].setValue(colorspace)

	if fileType == "exr":
		n.knobs()["datatype2"].setVisible(True)
		n.knobs()["compression2"].setVisible(True)
		n.knobs()["_jpeg_quality2"].setVisible(False)
		n.knobs()["_jpeg_sub_sampling2"].setVisible(False)
	elif fileType == "dpx":
		n.knobs()["datatype2"].setVisible(True)
		n.knobs()["compression2"].setVisible(False)
		n.knobs()["_jpeg_quality2"].setVisible(False)
		n.knobs()["_jpeg_sub_sampling2"].setVisible(False)
	elif fileType in ["tif", "tiff"]:
		n.knobs()["datatype2"].setVisible(True)
		n.knobs()["compression2"].setVisible(True)
		n.knobs()["_jpeg_quality2"].setVisible(False)
		n.knobs()["_jpeg_sub_sampling2"].setVisible(False)
	elif fileType == "png":
		n.knobs()["datatype2"].setVisible(True)
		n.knobs()["compression2"].setVisible(False)
		n.knobs()["_jpeg_quality2"].setVisible(False)
		n.knobs()["_jpeg_sub_sampling2"].setVisible(False)
	elif fileType in ["jpg", "jpeg"]:
		n.knobs()["datatype2"].setVisible(False)
		n.knobs()["compression2"].setVisible(False)
		n.knobs()["_jpeg_quality2"].setVisible(True)
		n.knobs()["_jpeg_sub_sampling2"].setVisible(True)

	hiddenEvalKnob.setVisible(False)

	if rootFolderMethodKnob.value() == "search word":
		rootFolderUserInputKnob.setVisible(True)
		rootFolderUserInputKnob.setLabel("search word")
		customRootFolderKnob.setVisible(False)
	elif rootFolderMethodKnob.value() == "environment variables":
		rootFolderUserInputKnob.setVisible(True)
		rootFolderUserInputKnob.setLabel("env variables/path")
		customRootFolderKnob.setVisible(False)
	elif rootFolderMethodKnob.value() == "custom path":
		rootFolderUserInputKnob.setVisible(False)
		customRootFolderKnob.setVisible(True)

	if renderNameKnob.value() == "custom name":
		customNameKnob.setVisible(True)
	else:
		customNameKnob.setVisible(False)

	# Add settings tab.
	settingsTab = nuke.Tab_Knob("sb_autoRenderSettings", "Settings")
	mainRenderFolderKnob = nuke.String_Knob("mainRenderFolder", "main render")
	precompRenderFolderKnob = nuke.String_Knob("precompRenderFolder", "precomp render")
	proxyRenderFolderKnob = nuke.String_Knob("proxyRenderFolder", "proxy render")
	framePaddingSepKnob = nuke.String_Knob("framePaddingSep", "frame padding separator")
	framePaddingKnob = nuke.String_Knob("framePadding", "frame padding")
	div8 = nuke.Text_Knob("divider8", "")
	noRenderKnob = nuke.Boolean_Knob("no_render", "no render (debugging)")

	for i in [settingsTab, mainRenderFolderKnob, precompRenderFolderKnob, proxyRenderFolderKnob, framePaddingSepKnob, framePaddingKnob, div8, noRenderKnob]:
		n.addKnob(i)

	mainRenderFolderKnob.setValue(mainRenderFolder)
	precompRenderFolderKnob.setValue(precompRenderFolder)
	proxyRenderFolderKnob.setValue(proxyRenderFolder)
	framePaddingSepKnob.setValue(framePaddingSep)
	framePaddingKnob.setValue(framePadding)

	# Focus on main tab.
	n.showControlPanel()
	rootFolderMethodKnob.setFlag(0)

def sb_autoRender():

	n = nuke.thisNode()

	# If not a sb_autoRender node, return.
	try:
		n["sb_autoRender"]
	except:
		return

	# Make sure we're using an up to date version, including new knobs.
	new_knobs = ["addSubfolder", "addColorspaceSubfolder", "addFileExtensionSubfolder"]
	not_existing = [x for x in new_knobs if x not in n.knobs()]
	if len(not_existing):
		raise Exception ("An old version of the sb AutoRender write node is currently used. Update with a new node. Missing knobs:\n\n{0}".format("\n".join(not_existing)))

	# Make sure user variables work.
	mainRenderFolder = n["mainRenderFolder"].value()
	precompRenderFolder = n["precompRenderFolder"].value()
	proxyRenderFolder = n["proxyRenderFolder"].value()
	framePaddingSep = n["framePaddingSep"].value()
	framePadding = n["framePadding"].value()

	for i in [mainRenderFolder, precompRenderFolder, proxyRenderFolder, framePaddingSep, framePadding]:
		if not i:
			raise Exception ("Set a value to the {0} knob (Settings tab)".format( i.name() ))

	# Script path.
	script_path = nuke.root()["name"].value()

	# Hidden evaluation knob. Use this as a containter to evaluate string knobs (to enble the use of expressions).
	evalKnob = n["hiddenEvalKnob"]

	# Get the root folder path.
	rootFolderMethod = n["rootFolderMethod"].value()	

	if rootFolderMethod in ["search word", "environment variables"]:
		rootFolderUserInput = n["rootFolderUserInput"].value()
		if not rootFolderUserInput:
			raise Exception ("User input knob is not set.")

		if rootFolderMethod == "search word":
			split_path = script_path.split("/")
			rootFolderPath = ""
			for i in reversed(range(len(split_path))):
				if split_path[i] == rootFolderUserInput:
					rootFolderPath = "/".join(split_path[0:i])
					break
			if not rootFolderPath:
				noSwMatchMsg = "Can't find '{0}' in the current script's filepath.".format(rootFolderUserInput)
				raise Exception (noSwMatchMsg)
		elif rootFolderMethod == "environment variables":
			rootFolderPath = replaceEnvsInsideBrackets(rootFolderUserInput)
	else:
		rootFolderPath = n["customRootFolderPath"].evaluate()
		if not rootFolderPath:
			raise Exception ("Custom render path knob is not set.")

	if not rootFolderPath.endswith("/"):
		rootFolderPath = "{0}/".format(rootFolderPath)

	# Get render type (main, pre, proxy).
	renderType = n["renderType"].value()

	if renderType == "main render":
		renderFolder = mainRenderFolder
	elif renderType == "precomp render":
		renderFolder = precompRenderFolder
	elif renderType == "proxy render":
		renderFolder = proxyRenderFolder
	elif renderType == "none":
		renderFolder = ""
		rootFolderPath = rootFolderPath[:-1]

	if renderFolder:
		evalKnob.setValue(renderFolder)
		renderFolder = evalKnob.evaluate()

	# Suffix/Prefix.
	prefix = n["prefix"].value()
	if prefix:
		evalKnob.setValue(prefix)
		prefix = evalKnob.evaluate()

	suffix = n["suffix"].value()
	if suffix:
		evalKnob.setValue(suffix)
		suffix = evalKnob.evaluate()

	# Colorspace.
	if n["use_ocio"].value():
		OCIONode = getNodeInput(n, 0)
		if OCIONode.Class() != "OCIOColorSpace":
			raise Exception ("Add a OCIOColorSpace node before the write node.\n\nIf you don't want to use OCIO, uncheck the 'Use OCIO for color conversions' checkbox.")
		if OCIONode["disable"].value():
			raise Exception("Enable the OCIOColorSpace node or uncheck the 'Use OCIO for color conversions' checkbox.")
		# Make sure the OCIO node has the same value as the Write.
		if OCIONode["out_colorspace"].value() != n["OCIOColorSpace"].value():
			OCIONode["out_colorspace"].setValue(n["OCIOColorSpace"].value())
		colorSpaceName = n["OCIOColorSpace"].value().split("/")[-1]
	else:
		colorSpaceName = n["colorspace"].value()

	# Build the folder path for the render.
	renderName = n["renderName"].value()
	if renderName == "script name":
		scriptName = os.path.splitext(script_path.split("/")[-1])[0]
		if not scriptName:
			raise Exception ("Can't find scriptname as the script isn't saved. Save script.")
		fullFileName = "{0}{1}{2}".format(prefix, scriptName, suffix)
	
	elif renderName == "custom name":
		evalKnob.setValue(n["customName"].value())
		customRenderName = evalKnob.evaluate()
		if not customRenderName:
			raise Exception ("Custom render name knob is empty.")
		fullFileName = "{0}{1}{2}".format(prefix, customRenderName, suffix)

	# Colorspace
	colorspaceFix = colorspaceNameFix(colorSpaceName)

	# Colorspace in filename.
	if n["addColorSpaceName"].value():
		# Don't add colorspace if OCIO is not used and the raw checkbox is checked.
		if not n["raw"].value() and not n["use_ocio"].value():
			colorspaceFix = colorspaceNameFix(colorSpaceName)
			fullFileName = "{0}_{1}".format(fullFileName, colorspaceFix)

	# Render path base.
	renderPathBase = "{0}{1}".format(rootFolderPath, renderFolder)

	# Subfolders.
	if n["addSubfolder"].value():
		renderPathBase = "{0}/{1}".format(renderPathBase, fullFileName)

	if n["addColorspaceSubfolder"].value():
		renderPathBase = "{0}/{1}".format(renderPathBase, colorspaceFix)

	ext = n["file_type"].value()
	if n["addFileExtensionSubfolder"].value():
		renderPathBase = "{0}/{1}".format(renderPathBase, ext)

	# Build full path.
	if ext.lower() in ["mov", "yuv"]:
		# Skip frame-padding if rendering a movie file.
		renderPath = "{0}/{1}.{2}".format(renderPathBase, fullFileName, ext)
	else:
		renderPath = "{0}/{1}{2}{3}.{4}".format(renderPathBase, fullFileName, framePaddingSep, framePadding, ext)

	if n["no_render"].value():
		raise Exception ("Render path: {0}".format(renderPath))

	# Set path, create folders and continue with render.
	if nuke.root()["proxy"].value():
		n["proxy"].setValue(renderPath)
	else:
		n["file"].setValue(renderPath)
	
	sb_autoRenderCreateRenderDirs(renderPath)
	sb_autoRenderMsg = "sb AutoRender ({0}): {1}".format(n["name"].value(), renderPath)
	nuke.tprint(sb_autoRenderMsg)

def sb_autoRenderKnobChanged():

	n = nuke.thisNode()
	k = nuke.thisKnob()

	if k.name() in ["xpos", "ypos", "selected", "onCreate", "onDestroy"]:
		return

	# If not a sb_autoRender node, return.
	try:
		n["sb_autoRender"]
	except:
		return

	if k.name() == "rootFolderMethod":		
		rfui = n["rootFolderUserInput"]
		crfp = n["customRootFolderPath"]
		
		if n["rootFolderMethod"].value() == "search word":
			rfui.setVisible(True)
			rfui.setLabel("search word")
			crfp.setVisible(False)
		elif n["rootFolderMethod"].value() == "environment variables":
			rfui.setVisible(True)
			rfui.setLabel("env variables/path")
			crfp.setVisible(False)
		elif n["rootFolderMethod"].value() == "custom path":
			rfui.setVisible(False)
			crfp.setVisible(True)

	if k.name() == "renderName":
		if n["renderName"].value() == "custom name":
			n["customName"].setVisible(True)
		else:
			n["customName"].setVisible(False)

	if k.name() == "use_ocio":
		if n["use_ocio"].value():
			n.knobs()["cs"].setVisible(False)
			n["colorspace"].setEnabled(False)
			n.knobs()["raw_color"].setVisible(False)
			n["raw"].setValue(True)
			n["OCIOColorSpace"].setVisible(True)
		else:
			n.knobs()["raw_color"].setVisible(True)
			n["raw"].setValue(False)
			n.knobs()["cs"].setVisible(True)
			n["colorspace"].setEnabled(True)
			n["OCIOColorSpace"].setVisible(False)

	if k.name() == "file_type":
		if n["ft"].value() == "exr":
			n.knobs()["datatype2"].setVisible(True)
			n.knobs()["compression2"].setVisible(True)
			n.knobs()["_jpeg_quality2"].setVisible(False)
			n.knobs()["_jpeg_sub_sampling2"].setVisible(False)
		elif n["ft"].value() == "dpx":
			n.knobs()["datatype2"].setVisible(True)
			n.knobs()["compression2"].setVisible(False)
			n.knobs()["_jpeg_quality2"].setVisible(False)
			n.knobs()["_jpeg_sub_sampling2"].setVisible(False)
		elif n["ft"].value() in ["tif", "tiff"]:
			n.knobs()["datatype2"].setVisible(True)
			n.knobs()["compression2"].setVisible(True)
			n.knobs()["_jpeg_quality2"].setVisible(False)
			n.knobs()["_jpeg_sub_sampling2"].setVisible(False)
		elif n["ft"].value() == "png":
			n.knobs()["datatype2"].setVisible(True)
			n.knobs()["compression2"].setVisible(False)
			n.knobs()["_jpeg_quality2"].setVisible(False)
			n.knobs()["_jpeg_sub_sampling2"].setVisible(False)
		elif n["ft"].value() in ["jpg", "jpeg"]:
			n.knobs()["datatype2"].setVisible(False)
			n.knobs()["compression2"].setVisible(False)
			n.knobs()["_jpeg_quality2"].setVisible(True)
			n.knobs()["_jpeg_sub_sampling2"].setVisible(True)
		else:
			n.knobs()["datatype2"].setVisible(False)
			n.knobs()["compression2"].setVisible(False)
			n.knobs()["_jpeg_quality2"].setVisible(False)
			n.knobs()["_jpeg_sub_sampling2"].setVisible(False)

	if k.name() == "OCIOColorSpace":
		if n["use_ocio"].value():
			OCIONode = getNodeInput(n, 0)
			if not OCIONode or OCIONode.Class() != "OCIOColorSpace":
				nuke.message("No OCIOColorSpace node attached to Write node.")
				return

		OCIONode["out_colorspace"].setValue(n["OCIOColorSpace"].value())
		OCIONode["out_colorspace"].setEnabled(False)
		OCIONode["tile_color"].setValue(8847615)

	if k.name() == "inputChange":
		if n["use_ocio"].value():
			OCIONode = getNodeInput(n, 0)
			if OCIONode and OCIONode.Class() == "OCIOColorSpace":
				OCIONode["out_colorspace"].setValue(n["OCIOColorSpace"].value())
				OCIONode["out_colorspace"].setEnabled(False)
				OCIONode["tile_color"].setValue(8847615)

nuke.addKnobChanged(sb_autoRenderKnobChanged, nodeClass="Write")