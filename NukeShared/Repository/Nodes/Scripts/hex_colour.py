presetColor = (0.819, 0.286, 0.329)
r = int(presetColor[0]*255)
g = int(presetColor[1]*255)
b = int(presetColor[2]*255)
hexColour = ('%02x%02x%02x%02x' % (r,g,b,1), 16)

print (hexColour)