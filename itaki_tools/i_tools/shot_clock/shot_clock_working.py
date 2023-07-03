import os
import threading
import getpass
import datetime
import json
import re
import nuke
import time

CURRENT_USER = getpass.getuser()
TESTING_FILE = '/Volumes/Dettifoss/nuke_dev/shotclock/shot_clock_v01.nk'
LOG_IN_PROJECT_DIR = True
LOG_IN_USER_LOGS = False
USER_LOGS = '/Volumes/panda/Dropbox (Personal)/_Library/nuke/_logs/'
TIMER = 60
IDLE_TIME = 300
TESTING = False


class Timelogger():
    def __init__(self):
        print("timelogger loaded")
        pass
    
    def start_session(self):
        #print("starting session")
        if self.get_path():
            if self.extract_data_from_path():
                if self.check_for_log():
                    # if there is a log check it
                    self.check_last_session()
                #otherwise just create a new session

                self.create_new_session()
                #print("calling threading function")
                self.start_thread()
        
    def save_session(self):
        self.get_path()
        self.extract_data_from_path()
        self.check_for_log()
        self.log_data['sessions'][-1]['status'] = "Saved"
        self.log_data['sessions'][-1]['end_time'] = self.now()
        #print("saved session")
        #self.create_new_session()
        self.save_log()
      

    # def close_session(self):
    #     print("closing")
    #     self.get_path()
    #     self.extract_data_from_path()
    #     self.check_for_log()
    #     self.log_data['sessions'][-1]['status'] = "Closed"
    #     self.log_data['sessions'][-1]['end_time'] = self.now()
    #     self.create_new_session()
    
    def start_thread(self):
        Timelogger.thread = threading.Timer(TIMER, self.update_session)
        if not TESTING:
            Timelogger.thread.setDaemon(True)
        Timelogger.thread.start()

    
    def now(self):
        return (datetime.datetime.now().isoformat())

    def load_log(self):
        if LOG_IN_PROJECT_DIR:
            with open(self.log_path, 'r') as _log:
                self.log_data = json.load(_log)
        elif LOG_IN_USER_LOGS:
            with open(USER_LOGS+self.log_name, 'r') as _log:
                self.log_data = json.load(_log)
        else:
            print("Stopping time logger - no log path")

    
    def save_log(self):
        #print("saving time log")
        if LOG_IN_PROJECT_DIR:
            with open(self.log_path, 'w+') as _log:
                json.dump(self.log_data, _log, indent=4 )
        if LOG_IN_USER_LOGS:
            with open(USER_LOGS+self.log_name, 'w+') as _log:
                json.dump(self.log_data, _log, indent=4 )

    def check_last_session(self):
        if self.log_data['sessions'][-1]['status'] == '':
            self.log_data['sessions'][-1]['status'] = "CRASHED"
            self.save_log()

    def get_path(self): 
        '''Checks to see if the path to nk file exists '''
        if TESTING:
            self.script_file = TESTING_FILE
        else:
            self.script_file = nuke.root()['name'].value() # get value from nuke
        # this checks to make sure the path is valid. it should always work
        # if not os.path.exists(self.script_file): 
        #     print( f"Trying to find {self.script_file}")
        #     print( "Invalid Path! Can't write timer to log file")
        #     return False

        #print(f"Got script path! {self.script_file}")
        return True

    def extract_data_from_path(self):
        # the comp name and the project path
        self.project_path, self.comp_name = os.path.split(self.script_file)
        #normalize the project path then split it out
        split_path = os.path.normpath(self.script_file).split(os.path.sep)
        #print (split_path)
        self.shot_name = split_path[-3] # Change this setting to change where it gets shot name from
        self.project_name = split_path[-4] # Change this setting to change where it gets project name from
        self.log_name = f'{self.project_name}_{self.shot_name}_log.json'
        self.log_path = os.path.join(self.project_path, self.log_name)

        if self.comp_name == 'Untitled.nk':
            print("Comp not saved yet so not recording time")
            return False 
        return True

    def check_for_log(self):
        if not os.path.exists(self.log_path):
            #print("creating new log file")
            self.create_log()
            return False
        else:
            self.load_log()
        return True
        
    def create_log(self):
        # if it has to create the log then start the session
        header = { 
                "header" : {
                    "project_name" : str(self.project_name),
                    "shot" : str(self.shot_name),
                    "directory" : str(self.project_path) 
                    },
                "sessions" :[]
                }

        self.log_data = header
        return

    def create_new_session(self):
        #print("creating new session")
        new_session = {
            "filename" : str(self.comp_name),
            "artist" : CURRENT_USER,
            "start_time" : self.now(),
            "notes" : [],
            "idle_time" : 0,
            "end_time" :  self.now(),
            "status" : ""
            }
        #print (new_session)
        self.log_data['sessions'].append(new_session)
        self.save_log()

    def update_session(self): 
        self.load_log()
        if self.log_data['sessions'][-1]['status'] != '':
            self.create_new_session()
        self.log_data['sessions'][-1]['end_time'] = self.now()
        #if were idling subtract the time
        if self.idle_time() > IDLE_TIME:
            self.log_data['sessions'][-1]['idle_time'] += TIMER
    
        self.save_log()
        #print("starting thread again")
        self.start_thread()


    def idle_time(self):
        now = time.time()

        # if there is an autosave and it's from over the idle time ago, start idling
        if os.path.isfile(f'{self.script_file}.autosave'):
            modification_time = (os.stat(f'{self.script_file}.autosave').st_mtime)
            _idle_time = now - modification_time + 1
            #print (f"there is an autosave at {modification_time} and idle has been {_idle_time}")
        
        # if no autosave but file modified then user has modified it means user just saved it
        elif nuke.modified():
            if not os.path.isfile(f'{self.script_file}.autosave'):
                _idle_time = 0
        
        # if no autosave file and nuke is not modified, 
        # compare current time to the last file save time and the 
        # start time of the current session to make sure someone hasn't just opened the project and it could think
        # it's been idling for days.
        elif not nuke.modified():
            start_session_timestamp = int(datetime.datetime.timestamp(datetime.datetime.fromisoformat(self.log_data['sessions'][-1]['start_time'])))
            if  start_session_timestamp >= int(os.stat(self.script_file).st_mtime):
                modification_time = start_session_timestamp
            else:
                modification_time = int(os.stat(self.script_file).st_mtime)
            _idle_time = now - modification_time
            #print (f"no autosave and last saved at {modification_time} and idle has been {_idle_time}")

        #print (_idle_time)
        return _idle_time


if __name__ == '__main__':
    TESTING = True
    logger = Timelogger()
    logger.start_session()
