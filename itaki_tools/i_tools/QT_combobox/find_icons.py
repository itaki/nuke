import nuke
import os


stock_plugins_path = nuke.pluginPath()[-1]
icons_path = os.path.join(stock_plugins_path, 'icons')
stock_icons = os.listdir(icons_path)

print (stock_icons)