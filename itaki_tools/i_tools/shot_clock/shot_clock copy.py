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
TIMER = 5
IDLE_TIME = 30
TESTING = False


class Timelogger():
    def __init__(self):
        self.startup_time = self.now()
        self.id = self.startup_time
        self.log_data = None
        self.all_sessions = 0
        self.all_work = 0
        self.all_idle = 0
        self.idling = False
        self.recently_saved = True
        self.started = False
    
    def start_session(self):
        #print("starting session")
        if self.get_path():
            if self.extract_data_from_path():
                if self.check_for_log():
                    print("found log")
                    # if there is a log check it
                    if not self.check_for_session():
                        print("create new session")
                        self.create_new_session()
                #print("calling threading function")
                self.recently_saved = True
                self.start_thread()
    
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

    def check_for_session(self):
        for session in range(len(self.log_data['sessions'])):
            if self.log_data['sessions'][session]['start_time'] == self.id:
                return True
        return False

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
                    "directory" : str(self.project_path),
                    "number_of_sessions" : 0,
                    "shot_clock" : 0,
                    "work_time" : 0,
                    "idle_time" : 0 
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
            "start_time" : self.id,
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
        current_session = self.get_session()
        print(f"got current session {current_session}")
        # if self.log_data['sessions'][current_session]['status'] != '':
        #     self.create_new_session()
        if self.recently_saved == True:
            self.log_data['sessions'][current_session]['status'] = 'saved'
            self.recently_saved = False
        else:
            self.log_data['sessions'][current_session]['status'] = 'unsaved'

        # need to set this sessions end time before calculating stats
        self.log_data['sessions'][current_session]['end_time'] = self.now()
        #if were idling subtract the time
        if self.calculate_idle_time() > IDLE_TIME:
            self.log_data['sessions'][current_session]['idle_time'] += TIMER

        self.calculate_stats()
        self.log_data['header']['shot_clock'] = str(datetime.timedelta(seconds=self.all_sessions))      
        self.log_data['header']['work_time'] = str(datetime.timedelta(seconds=self.all_work))
        self.log_data['header']['idle_time'] = str(datetime.timedelta(seconds=self.all_idle))
    
        self.save_log()
        #print("starting thread again")
        self.start_thread()

    def get_session(self):
        for session in range(len(self.log_data['sessions'])):
            if self.log_data['sessions'][session]['start_time'] == self.id:
                return session
        return False

    def calculate_stats(self):
        self.all_sessions = 0
        self.all_work = 0
        self.all_idle = 0
        self.number_of_sessions = 0
        for session in self.log_data['sessions']:
            start_time = datetime.datetime.timestamp(datetime.datetime.fromisoformat(session['start_time'])) # as timestamp
            end_time = datetime.datetime.timestamp(datetime.datetime.fromisoformat(session['end_time'])) # as timestamp
            idle_time = session['idle_time'] # as int

            session_time = end_time - start_time
            work_time = session_time - idle_time
            self.all_sessions += int(session_time)
            self.all_work += int(work_time)
            self.all_idle += int(idle_time)
        self.number_of_sessions = len(self.log_data['sessions'])

    def calculate_idle_time(self):
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
    