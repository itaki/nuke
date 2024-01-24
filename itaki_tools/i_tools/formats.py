import nuke



working_format = 'UHD_4K_sRGB'
# examples are 'UHD_4K_sRGB', 'Regions', 'Horizon'
# Set default formats. Note this expects an empty formats.tcl in the NUKE_PATH to clear the existing default formats.
custom_formats = [
    '1560 1560 1 square_1.5K',
    '4448 3096 1 Regions',
    '3072 1620 1 C3-Nemours',
    '4312 2274 1 Horizon',

]

project_settings = {
    'UHD_4K_sRGB': {'format':'UHD_4K', 'fps':'23.976', 'first_frame':'1', 'colorspace':'sRGB'},
    'Regions': {'format':'Regions', 'fps':'23.976', 'first_frame':'1', 'colorspace':'Log3G12'},
    'Horizon': {'format':'Horizon', 'fps':'24', 'first_frame':'1001', 'colorspace':'linear'},
}


def add_formats(custom_formats):
    '''Adds formats from the custom_formats list to the format list in Nuke'''
    for f in custom_formats:
        nuke.addFormat(f)

def set_project(settings='UHD_4K'):
    print(settings)
    '''When given a format, will set the startup and format settings'''
    nuke.knobDefault('Root.format', settings['format'])
    nuke.knobDefault('Read.frame_mode', 'start at')
    nuke.knobDefault('Read.frame',settings['first_frame'])
    nuke.knobDefault('Read.colorspace', settings['colorspace'])
    nuke.knobDefault('Root.fps', settings['fps']) 

# Start the script
add_formats(custom_formats)
set_project(settings=project_settings[working_format])

''' these are just notes for now'''
# SET DEFAULT FORMAT
#nuke.knobDefault('Root.format', 'HD_1080') # 1920x1080
#nuke.knobDefault('Root.format', 'UHD_4K') # 3840x2160
#nuke.knobDefault('Root.format', '4K_DCP') # 4096x2160
# nuke.knobDefault('Root.format', 'Horizon') # 4312x2274
# nuke.knobDefault('Read.frame_mode', 'start at')
# nuke.knobDefault('Read.frame','1001')
# nuke.knobDefault('Read.colorspace','linear') #
#nuke.knobDefault('Root.format', 'TL') # 4448x3096 

#nuke.knobDefault('Root.proxy_format', 'SD_540p')

# SET FRAME RATE
#nuke.knobDefault("Root.fps", "23.976") 
# nuke.knobDefault("Root.fps", "24") 
#nuke.knobDefault("Root.fps", "29.976") 


'''default_formats = [
    '854 480 1 SD_480p', 
    '960 540 1 SD_540p', 
    '1280 720 1 HD_720p', 
    '1920 1080 1 HD_1080p', 
    '2560 1440 1 UHD_1440p', 
    '3840 2160 1 UHD_4k', 
    '2048 1556 1 2K_Super_35_full-ap', 
    '1828 1556 2 2K_Cinemascope', 
    '2048 1080 1 2K_DCP', 
    '4096 3112 1 4K_Super_35_full-ap', 
    '3656 3112 2 4K_Cinemascope', 
    '4096 2160 1 4K_DCP', 
    '256 256 1 square_256', 
    '512 512 1 square_512', 
    '1024 1024 1 square_1K', 
    '2048 2048 1 square_2K', 
    '4096 4096 1 square_4K', 
    '1024 512 1 latlong_1k', 
    '2048 1024 1 latlong_2k', 
    '4096 2048 1 latlong_4k', 
    '8192 4096 1 latlong_8k', 
    '10240 5120 1 latlong_10k', 
    '12288 6144 1 latlong_12k', 
    '16384 8192 1 latlong_16k', 
]'''