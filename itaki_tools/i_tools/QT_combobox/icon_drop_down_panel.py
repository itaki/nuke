import nuke
import nukescripts
import os
from PySide2 import QtCore, QtGui, QtWidgets


''' this icon selector works but it only shows the QT resource icons'''

class IconSelectorPanel(nukescripts.PythonPanel):
    def __init__(self):
        nukescripts.PythonPanel.__init__(self, "Icon Selector")
        self.all_icons = []

        
        # Create a drop down menu with all the available icons in Nuke
        self.get_stock_icons()
        # icon_paths = self.get_icon_paths()
        self.icon_menu = nuke.Enumeration_Knob("icon", "Icon", self.all_icons)
        self.addKnob(self.icon_menu)

        # Add a label to display the selected icon
        self.icon_label = nuke.Text_Knob("icon_label", "Selected Icon", "")
        self.addKnob(self.icon_label)
        
    def knobChanged(self, knob):
        if knob is self.icon_menu:
            # Update the icon label when the user selects a new icon
            selected_icon = self.icon_menu.value()
            self.icon_label.setValue(selected_icon)
    
    def get_stock_icons(self):

        self.stock_icons = QtCore.QResource(':qrc/images').children()
        for icon in self.stock_icons:
            name = os.path.splitext(icon.split('/')[-1] )[0]
            icon_string = '%s <html><img src=":qrc/images/%s"></html>' % ( name, icon )
            # icon_string = f"{name} <img src=':qrc/images/{icon}'"
            self.all_icons.append(icon_string)
        self.all_icons.sort()



    def get_icon_paths(self):
        # Get the path to the Nuke plugins directory
        plugins_path = nuke.pluginPath()[0]
        icons_path = os.path.join(plugins_path, "icons")

        # Get a list of all files in the icons directory
        files = os.listdir(icons_path)

        # Filter the list to only include image files
        image_files = [f for f in files if f.endswith(".png") or f.endswith(".jpg") or f.endswith(".tif")]

        # Create a list of the full file paths for the images
        icon_paths = [os.path.join(icons_path, f) for f in image_files]

        return icon_paths
        
# Create an instance of the panel and show it
icon_selector_panel = IconSelectorPanel()
icon_selector_panel.show()