import nuke
import nukescripts
import os

# This one works. Don't modify it.
class GetIcons():
    def __init__(self):
        self.stock_icons_path = os.path.join(nuke.pluginPath()[-1], 'icons') 
        self.stock_icons = self.get_stock_icons()
        self.stock_icons_dict = self.make_icon_dict()

        
    def get_stock_icons(self):
        stock_icons = os.listdir(self.stock_icons_path) # get a list of all the icons in the dir
        stock_icons.sort() # sort them
        # create a dictionary with the icon name as the key and path as the value
        return stock_icons

    def make_icon_dict(self):
        stock_icons_dict = {}
        for icon in self.stock_icons:
            stock_icons_dict[icon] = f"{os.path.join(self.stock_icons_path, icon)}" 
        return stock_icons_dict


    
    # def make_html_icon_list(self):
    #     html_icon_list = []
    #     for icon in self.stock_icons:
    #         html_icon_list.append(f"<img src='{self.stock_icons_path}/{icon}'> {icon}")
    #     return html_icon_list

class IconSelectorPanel(nukescripts.PythonPanel):
    def __init__(self):
        self.wrapped_icons = []
        nukescripts.PythonPanel.__init__(self, "Icon Selector")

        self.icon_dict = GetIcons().stock_icons_dict
        self.icon_names_list = list(self.icon_dict.keys())
        self.icon_menu = nuke.Enumeration_Knob("icon", "Icon", self.icon_names_list)
        self.addKnob(self.icon_menu)

        # Add a label to display the selected icon
        self.icon_label = nuke.Text_Knob("icon_label", "Selected Icon", "")
        self.addKnob(self.icon_label)
        
    def knobChanged(self, knob):
        if knob is self.icon_menu:
            print("i got here")
            # Update the icon label when the user selects a new icon
            selected_icon = self.icon_menu.value()
            wrapped_icon = self.html_wrap_up(self.icon_dict[selected_icon])
           
            self.icon_label.setValue(wrapped_icon)

    def html_wrap_up(self, icon):
        wrapped_icon = f"<img src='{icon}'>"
        return wrapped_icon
        
    

       
# Create an instance of the panel and show it
icon_selector_panel = IconSelectorPanel()
icon_selector_panel.show()