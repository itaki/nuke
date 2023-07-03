import os
import nuke

class DiskCache():
    '''
    NOTE: This script ONLY works on MacOS and possibly Linux

    This class assigns takes a list of potential disks to make Nukes cache drive.
    It checks them in order of preference and as soon as it finds one that is available
    and that it can write to, it sets the path.
    If it fails to find any usable drives it will try to create the temp directory in the users
    '.nuke' folder. If it still fails it gives up and lets Nuke select it's default temp directory

    TAKES: 
    PREFERRED_CACHE_DISKS = ['drive1','drive2','drive3']
    CACHE_DIR = 'location/to/cache/directory'

    SETS:
    os.environ['NUKE_TEMP_DIR'] = cache_location
    os.environ['NUKE_DISK_CACHE'] = cache_location

    NOTE: Nuke will still create all the directories in /var/tmp/nuke-u501/ViewerCache,
    and will print out the disk location being there if you run from the command line.
    However, if you print(os.environ['NUKE_TEMP_DIR']) it prints out the correct location.

    Add this to your init.py file
    ### SET TEMP DIRECTORY
    import set_cache_disk
    PREFERRED_CACHE_DISKS = ['drive1','drive2','drive3']
    CACHE_DIR = 'location/to/cache/directory'
    set_cache_disk.DiskCache(PREFERRED_CACHE_DISKS,CACHE_DIR).set_cache_location()

    Documentation: https://support.foundry.com/hc/en-us/articles/207271649-Q100048-Nuke-Directory-Locations

    '''


    def __init__(self, preferred_cache_disks, cache_dir):
        self.preferred_disks = preferred_cache_disks
        self.cache_dir = cache_dir

    def set_cache_location(self):
        '''This function sets the environment variables for 
        NUKE_TEMP_DIR
        NUKE_DISK_CACHE
        If it doesn't receive a suitable directory it quits and allows Nuke to set the directory'''
        cache_location = self.get_cache_location()
        if not cache_location:
            print(f"Unable to set custom cache location. Using default")
            return
        else:
            os.environ['NUKE_TEMP_DIR'] = cache_location
            os.environ['NUKE_DISK_CACHE'] = cache_location


    def get_cache_location(self):
        '''This function cycles throught the potential cache locations and
        returns the first valid one. If it fails to find any suitable locations
        it will NOT set a location'''
        for volume in self.preferred_disks:
            cache_path = self.check_if_volume_exists(volume)
            if cache_path != False:
                # Stop searching, I found one, move along from here.
                break
        if cache_path != False: # Send the directory I found home
            print(f"Cache directory set to {cache_path}")
            return cache_path
        else: # if no drive has be set, set local
            cache_path = os.path.join(os.path.expanduser( '~' ), self.cache_dir)
            if os.path.isdir(cache_path):
                print(f"Cache directory is using user's home folder {cache_path}")
                return cache_path
            else:
                try:
                    os.makedirs(cache_path)
                    print(f"Created new directory in home folder")
                    print(f"Cache directory is using user's home folder {cache_path}")
                    return cache_path
                except: # Couldn't make cache directory
                    return False

    
    def check_if_volume_exists(self, volume):
        '''Recieves volume name and checks to see if it exists
        If it does exist will check to see if the cache folder exists
        If it does exist it returns the cache folder path
        If it does not exist it tries to create the folder
        If it successfully creates the path it returns the path
        If it fails it returns false
        
        NOTE: This is the part that doesn't work on Windows
        '''
        short_path = os.path.join('/Volumes', volume)
        if os.path.isdir(short_path):
            full_path = os.path.join(short_path, self.cache_dir)
            if os.path.isdir(full_path):    
                return full_path
            else:
                try:
                    os.makedirs(full_path)
                    print(f"Created a new temp directory at {full_path}")
                    return full_path
                except:
                    print(f"Failed to create {full_path}")
                    print(f"Volume : {short_path} exists but is not writable!")
                    return False
                    
        else:
            print(f"Cache drive {volume} not accesable on this machine")
            return False
