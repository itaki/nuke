import nuke

file_type = 'exr' # exr, mov, dpx, png, tiff
colorspace = 'sRGB' # sRGB, rec709, linear
channels = 'rgba' # rgba, rgb

nuke.knobDefault('Write.file_type', file_type)
nuke.knobDefault('Write.colorspoce', colorspace)
nuke.knobDefault('Write.channels', channels)
nuke.knobDefault('Write.create_directories', '1')

# ----------
# ❓ EXR SETTINGS
nuke.knobDefault('Write.exr.write_ACES_compliant_EXR','1')
nuke.knobDefault('Write.exr.autocrop','1')
# 16 bit half is FOR BEAUTY and rough AOVs. Fine AOVs should be 32bit float.
nuke.knobDefault('Write.exr.datatype','16 bit half')
# 32 bit float is FOR AOVs at the highest quality.
#nuke.knobDefault('Write.exr.datatype','32 bit float')
#### DWA compression is the best for EXRs. It's lossy compression but the AOVs are zip compressed.
'''
Lossy Channel names:
R, G, B, Y, RY, BY (capital channel names are required)

RLE compressed:
A

Zip compressed - All other channel names not fitting the above:
Red, red, r, Green, green, g, Blue, blue, b, x, y, z, U, u, V, v, etc... Be careful with x,y,z as if it's named Y it will be lossy.
'''
#nuke.knobDefault('Write.exr.compression','DWAA') # DWAB is smaller but slower to read
#nuke.knobDefault('Write.exr.dw_compression_level','1') # almost lossless - note: 0 is larger than piz or zip
#nuke.knobDefault('Write.exr.dw_compression_level','10') # good balance. Highest you'd want to go for green screen is 25
#nuke.knobDefault('Write.exr.dw_compression_level','45') # standard but too lossy for green screen
#nuke.knobDefault('Write.exr.dw_compression_level','150') # lossy
#nuke.knobDefault('Write.exr.dw_compression_level','500') # proxy
# For lossless beauty, better for grain and slower to read. 32 scanlines
#nuke.knobDefault('Write.exr.compression','PIZ')
# For lossless beauty, better for CGI and faster to read. 1 or 16 scanlines
#nuke.knobDefault('Write.exr.compression','Zip (1 scanline)')
#nuke.knobDefault('Write.exr.compression','Zip (16 scanlines)')
# For lossless beauty, best for network
nuke.knobDefault('Write.exr.compression','PIZ Wavelet (32 scanlines)')

######## MOTION VECTORS
# The next 5 lines are For motion vectors. These settings are the same as smart vector node 'Export Write'
# nuke.knobDefault('Write.colorspace','linear')
# nuke.knobDefault('Write.exr.compression','Zip (1 scanline)')
# nuke.knobDefault('Write.exr.metadata','all metadata except input/*')
# nuke.knobDefault('Write.exr.interleave','channels')
# nuke.knobDefault('Write.exr.write_full_layer_names','True')

# ----------
# ❗MOV settings 
#nuke.knobDefault('Write.mov.channels','rgb') # if you use one that's not 4444 it doesn't give you an alpha anyway
# nuke.knobDefault('Write.mov.channels','rgba')
# ❓MOV codec settings and compressionn 
# FOR PRORES
# ❓Select either of these two options.
nuke.knobDefault('Write.mov.mov_prores_codec_profile','ProRes 4444 XQ 12-bit') # All channels Extreme Quality
#nuke.knobDefault('Write.mov.mov_prores_codec_profile','ProRes 4:2:2 Proxy 10-bit') # 1/10 the size of 4444, no alpha
# FOR H.264
#nuke.knobDefault('Write.mov.mov64_codec','H.264')




# ----------
# DPX settings
# Write > Default for DPX files: 10bit Log, No Compression
nuke.knobDefault('Write.dpx.datatype','10 bit')
#nuke.knobDefault('Write.dpx.datatype','12 bit')

# ----------
# PNG settings
# Write > Default for PNG files: 16bit, No Compression
#nuke.knobDefault('Write.png.datatype','16 bit')
nuke.knobDefault('Write.png.datatype','8 bit') # mocha requires 8 bit grayscale pngs as mask inputs


# ----------
# TIFF settings
# Write > Default for TIFF files: 16bit, No Compression
nuke.knobDefault('Write.tiff.datatype','16 bit')