import nuke

def sb_grain_callbacks():

	n = nuke.thisNode()
	k = nuke.thisKnob()

	if k.name() in ["selected", "xpos", "ypos"]:
		return

	if k.name() == "grain_method":

		syntheticKnobs = ["size_text", "red_size", "green_size", "blue_size", "irregularity_text", "red_i", "green_i", "blue_i", "intensity_text", "red_m", "green_m", "blue_m"]
		grainPlateKnobs = ["avg_grain_plate", "plate_intensity", "mix_1", "mix_2", "mix_3"]

		if n["grain_method"].value() == "generated noise":

			for i in syntheticKnobs:
				n.knobs()[i].setVisible(True)

			for i in grainPlateKnobs:
				n.knobs()[i].setVisible(False)

		else:

			for i in syntheticKnobs:
				n.knobs()[i].setVisible(False)

			for i in grainPlateKnobs:
				n.knobs()[i].setVisible(True)

nuke.addKnobChanged(sb_grain_callbacks, nodeClass="sb_grain")