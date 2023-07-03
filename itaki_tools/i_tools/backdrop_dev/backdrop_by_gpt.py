import nuke
import json
from PySide2.QtGui import QColor, QPainter, QBrush
from PySide2.QtCore import QRectF
from nukescripts import PythonPanel

# Define the path to the JSON file as a global variable
BACKDROP_STYLES_JSON = '/Volumes/panda/Dropbox (Personal)/_Library/nuke/itaki_tools/i_tools/backdrops.json'


class BackdropStylePanel(PythonPanel):
    def __init__(self):
        PythonPanel.__init__(self, 'Backdrop Styles')

        # Create the dropdown menu to select the style
        self.style_dropdown = nuke.Enumeration_Knob('style', 'Style', [])
        self.addKnob(self.style_dropdown)

        # Create the button to create the backdrop
        self.create_button = nuke.PyScript_Knob('create', 'Create Backdrop')
        self.addKnob(self.create_button)

        # Load the JSON data for the backdrop styles
        with open(BACKDROP_STYLES_JSON, 'r') as f:
            data = json.load(f)

        # Populate the dropdown menu with the style names and preview rectangles
        for style in data['styles']:
            color = style.get('color', 'FFFFFF')
            self.style_dropdown.setValues(self.style_dropdown.values() + [style['name']])

            # Create a rectangle for the preview
            self.addKnob(nuke.Text_Knob('', ''))
            preview_knob = self.knob(len(self) - 1)
            preview_knob.setFlag(nuke.STARTLINE)
            preview_knob.clearFlag(nuke.NO_RERENDER)
            preview_knob.clearFlag(nuke.NO_ANIMATION)
            preview_knob.setValue('color: {0};'.format(color))

    def knobChanged(self, knob):
        if knob == self.create_button:
            # Get the selected style
            selected_style = self.style_dropdown.value()

            # Load the JSON data for the selected style
            with open(BACKDROP_STYLES_JSON, 'r') as f:
                data = json.load(f)
            style_data = next((style for style in data['styles'] if style['name'] == selected_style), None)

            # Create the backdrop node based on the style data
            bd = nuke.createNode('BackdropNode')
            bd.setName(selected_style)

            # Set the backdrop color based on the style data
            color = style_data.get('color', 'FFFFFF')
            bd['tile_color'].setValue(int(color, 16))

            # Set the backdrop label based on the style data
            bd['label'].setValue(style_data['label'])

            # Set the backdrop font based on the style data
            bd['note_font'].setValue(style_data['font'])
            bd['note_font_size'].setValue(18)
            bd['note_font_color'].setValue(16777215)
            bd['note_font'].setValue(style_data['font'])

            # Deselect the nodes
            nuke.selectAll()
            nuke.invertSelection()

    def createBackdrop(nodes, label, note, font, icon=None):
        bd = nuke.nodes.BackdropNode(label=label, note=note, tile_color=hexToFloatColor(backdropStyles[font]['tile_color']))
        bd['bdheight'].setValue(len(nodes)/2)
        bd['note_font_size'].setValue(30)
        bd['label'].setValue(label)
        bd['note_font'].setValue(font)
        bd['icon'].setValue(icon) # Set the backdrop icon

        x = min([node.xpos() for node in nodes])
        y = min([node.ypos() for node in nodes])
        bd.setXpos(x-bd.screenWidth()/2)
        bd.setYpos(y-bd.screenHeight()/2)

        for node in nodes:
            node.setInput(0, bd)

        return bd


# Show the panel
BackdropStylePanel().show()