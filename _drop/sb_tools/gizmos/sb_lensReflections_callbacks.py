# Add following to menu.py:
# import sb_lensReflections_callbacks

import nuke

def sb_lensReflections_callbacks():

	n = nuke.thisNode()
	k = nuke.thisKnob()

	if k.name() in ["selected", "xpos", "ypos"]:
		return

	if k.name() == "method":
		noiseKnobs = ["noise_controls_text", "random_seed", "aspect_ratio", "mix", "noise_controls"]
		plateKnobs = ["dirtPlate_text", "blackpoint_1", "whitepoint_1", "gamma_5", "saturation_1"]

		if n["method"].value() == "generated noise":
			for i in noiseKnobs:
				n.knobs()[i].setVisible(True)
			for i in plateKnobs:
				n.knobs()[i].setVisible(False)

		elif n["method"].value() == "dirt plate":
			for i in noiseKnobs:
				n.knobs()[i].setVisible(False)
			for i in plateKnobs:
				n.knobs()[i].setVisible(True)

nuke.addKnobChanged(sb_lensReflections_callbacks, nodeClass="sb_lensReflections")