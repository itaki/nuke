import nuke
import json
from nukescripts import PythonPanel

# Global variable for the path to the backdrop styles JSON file
BACKDROP_STYLES_FILE = "/Volumes/panda/Dropbox (Personal)/_Library/nuke/itaki_tools/i_tools/backdrops.json"


class BackdropStylePanel(PythonPanel):
    def __init__(self):
        PythonPanel.__init__(self, "Backdrop Styles")
        self.backdrop_style_knob = nuke.Enumeration_Knob('backdrop_style', 'Style', [])
        self.addKnob(self.backdrop_style_knob)
        self.backdrop_color_knob = nuke.ColorChip_Knob('backdrop_color', 'Color', (0, 0, 0))
        self.addKnob(self.backdrop_color_knob)
        self.backdrop_note_knob = nuke.String_Knob('backdrop_note', 'Note')
        self.addKnob(self.backdrop_note_knob)
        # self.backdrop_icon_knob = nuke.Icon_Knob('backdrop_icon', 'Icon')
        # self.addKnob(self.backdrop_icon_knob)
        self.backdrop_preview_knob = nuke.PyScript_Knob('backdrop_preview', 'Preview')
        self.addKnob(self.backdrop_preview_knob)

        self.backdrop_styles = self.load_backdrop_styles()
        self.populate_backdrop_style_menu()

    def load_backdrop_styles(self):
        with open(BACKDROP_STYLES_FILE) as f:
            backdrop_styles = json.load(f)
        return backdrop_styles

    def populate_backdrop_style_menu(self):
        styles = [(style["name"], style["name"]) for style in self.backdrop_styles]
        self.backdrop_style_knob.setValues(styles)

    def get_selected_backdrop_style(self):
        selected_style_name = self.backdrop_style_knob.value()
        for style in self.backdrop_styles:
            if style["name"] == selected_style_name:
                return style
        return None

    def set_color_from_style(self):
        style = self.get_selected_backdrop_style()
        if style is not None:
            color = nuke.Color(*style["color"])
            self.backdrop_color_knob.setValue(color)

    def set_note_from_style(self):
        style = self.get_selected_backdrop_style()
        if style is not None:
            note = style["note"]
            self.backdrop_note_knob.setValue(note)

    def set_icon_from_style(self):
        style = self.get_selected_backdrop_style()
        if style is not None:
            icon_path = style["icon"]
            self.backdrop_icon_knob.setValue(icon_path)

    def set_preview_from_style(self):
        style = self.get_selected_backdrop_style()
        if style is not None:
            self.backdrop_preview_knob.setCommand("nuke.createNode('BackdropNode')['tile_color'].setValue({})".format(style["color"]))

    def knobChanged(self, knob):
        if knob == self.backdrop_style_knob:
            self.set_color_from_style()
            self.set_note_from_style()
            self.set_icon_from_style()
            self.set_preview_from_style()


panel = BackdropStylePanel()
panel.showModalDialog()
