import nuke
import os
import getpass
import json
import datetime
import re
import time

CURRENT_USER = getpass.getuser()
TESTING_FILE = '/Volumes/Dettifoss/nuke_dev/shotclock/shot_clock_v01.nk'


class Log_Manager():
    '''this class does things like check for files, create files, save files
    it can also get datestamps of files'''

    def __init__(self, log_in_project_dir=True, log_in_user_logs=False, user_log_dir='~/nuke/logs'):
        self.log_in_project_dir = log_in_project_dir
        self.log_in_user_logs = log_in_user_logs
        self.user_log_dir = user_log_dir
        self.project_path = self.get_project_path()
        self.extract_data_from_path()
        self.user = getpass.getuser()
        self.log_name = self.generate_log_name()

    def check_for_log(self):
        if os.path.isfile(self.log_path):
            return True
        else:
            print(f"no log found at {self.log_path}")
            return False
        
    def load_log(self):
        with open(self.log_path, 'r') as _log:
            self.log_data = json.load(_log)
        return self.log_data

    def save_log(self, log):
        self.log_data = log
        if self.log_in_project_dir:
            with open(self.log_path, 'w+') as _log:
                json.dump(self.log_data, _log, indent=4 )
        if self.log_in_user_logs:
            with open(self.user_log_dir+self.log_name, 'w+') as _log:
                json.dump(self.log_data, _log, indent=4 )


    def get_project_path(self):
        return nuke.root()['name'].value()

    def extract_data_from_path(self):
        if self.comp_name == 'Untitled.nk':
            print("Comp not saved yet so not recording time")
            return False 
        else:
            # the comp name and the project path
            self.project_path, self.comp_name = os.path.split(self.script_file)
            #normalize the project path then split it out
            split_path = os.path.normpath(self.script_file).split(os.path.sep)
            #print (split_path)
            self.shot_name = split_path[-3] # Change this setting to change where it gets shot name from
            self.project_name = split_path[-4] # Change this setting to change where it gets project name from
            self.log_name = f'{self.project_name}_{self.shot_name}_log.json'
            self.log_path = os.path.join(self.project_path, self.log_name)
            return True
        

    def get_file_timestamp(self, path):
        modification_time = (os.stat(f'{self.script_file}.autosave').st_mtime)