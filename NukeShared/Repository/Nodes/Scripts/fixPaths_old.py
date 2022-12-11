def fixPaths():
    import os, nuke

    inputPath = nuke.getFilename("input")
    inputDir = os.path.dirname(inputPath)

    projFolder = os.path.basename(inputDir)

    for n in nuke.allNodes():
        if n.Class() == "Read" or n.Class() == "ReadGeo":
            oldPath = nuke.filename(n)
        if not os.path.exists(oldPath):
            pathTuple = oldPath.partition(projFolder)

        fileKnob = n.knob("file")
        fileKnob.setValue(inputDir + pathTuple[2])
fixPaths()