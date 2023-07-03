import nuke
import nukescripts
import os
# from PySide2 import QtCore, QtGui, QtWidgets

class StockIcons():
    # I moved this into the script library
    def __init__(self):
        self.html_icon_list = []
        # the first path nuke loads is the stock plugin repository which is last in the list
        self.stock_icons_path = os.path.join(nuke.pluginPath()[-1], 'icons') 
        # add the icons directory to the path
        self.stock_icons = os.listdir(self.stock_icons_path)
        self.stock_icons.sort()
        # self.html_icon_list = self.make_html_icon_list()
        # self.html_icon_dict = self.make_html_icon_dict()
    
    def make_html_icon_list(self):
        html_icon_list = []
        for icon in self.stock_icons:
            html_icon_list.append(f"<img src='{self.stock_icons_path}/{icon}'> {icon}")
        return html_icon_list

    def make_html_icon_dict(self):
        html_icon_dict = {}
        for icon in self.stock_icons:
            html_icon_dict[f"<img src='{self.stock_icons_path}/{icon}'> {icon}"] = icon
        return html_icon_dict

class IconSelectorPanel(nukescripts.PythonPanel):

    def __init__(self):
        nukescripts.PythonPanel.__init__(self, "Icon Selector")
        self.icon_list_manager = StockIcons()
        self.icon_menu = nuke.Pulldown_Knob("icon", "Icon", self.icon_list_manager.make_html_icon_dict())
        self.addKnob(self.icon_menu)

        # Add a label to display the selected icon
        self.icon_label = nuke.Text_Knob("icon_label", "Selected Icon", "")
        self.addKnob(self.icon_label)
        
    def knobChanged(self, knob):
        if knob is self.icon_menu:
            # Update the icon label when the user selects a new icon
            selected_icon = self.icon_menu.value()
            self.icon_label.setValue(selected_icon)
    

       
# Create an instance of the panel and show it
icon_selector_panel = IconSelectorPanel()
icon_selector_panel.show()

