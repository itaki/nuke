import os
import threading
import getpass
import datetime
import json
import re
import nuke
import time

CURRENT_USER = getpass.getuser() # gets the current user
LOG_IN_CONSOIDATED_LOGS = False # log in another log directory
CONSOIDATED_LOGS = '~/Dropbox (Personal)/_Library/nuke/_logs/' # this could also be a network drive
TIMER = 5 # this uprdates every x seconds
IDLE_TIME = 30 # starts idling afert x seconds
TESTING = False
USE_VIEWER = False
GAME = True


THEME = 'animals' # "animals", "objects", "all"
ACHIEVEMENT_SCORE = [0,1,2,5,10,15,30,60,120,240,480,600,720,960,1440,2880,5760,7200,10080,13440,20160,40320]
if THEME == 'animals':
    ACHIEVEMENTS = ['🐣','🐥','🐸','🐷','🐮','🐹','🐰','🐶','🐨','🐵','🐼','🐻','🦊','🐙','🦉','💀','👹','👿','👽','🦁','🐯','🐲']
elif THEME == 'objects':
    ACHIEVEMENTS = ['🍼','🎈','🔫','🏓','🌮','🌈','🍯','🌊','🌋','🍺','🍩','🎁','🎩','🍷','☕','☔','🦄','🎥','🦖','🧘','🧟','👑']
elif THEME == 'all':
    ACHIEVEMENTS = 127752 # where the emojis start


class Timelogger():
    def __init__(self):
        '''
        self.startup_time
        self.script_file
        self.project_path
        self.comp_name
        self.shot_name
        self.log_name
        self.log_path
        self.log_data : json dump of log file
        self.id : unqiue session id = to start time
        self.all_sessions : how many sessions
        self.all_work : minutes of work
        self.all_idle : minutes idling
        self.idling : boolean
        '''
        #print("timelogger loaded")
        self.startup_time = self.now()
        self.id = self.startup_time
        self.log_data = None
        self.all_sessions = 0
        self.all_work = 0
        self.all_idle = 0
        self.idling = False
        self.recently_saved = True
        self.started = False
        

    def now(self):
        return (datetime.datetime.now().isoformat())
    
    def save_session(self):
        if self.log_data == None: # on first run do all the stuff
            if self.get_nk_path():
                self.extract_data_from_path()

                self.get_log_data()
                if not self.check_for_session():
                    self.create_new_session()
                if USE_VIEWER:
                    self.lv = Log_Viewer()
        if self.log_data != None:
            #self.recently_saved = True
            self.update_session()

    def get_log_data(self):
        '''Load the log file into self.log_data
        if no log exists self.create_log'''
        if os.path.exists(self.log_path):
            try:
                with open(self.log_path, 'r') as _log:
                    self.log_data = json.load(_log)
                    # self.sessions = self.log_data['sessions']
            except:
                print(f"Can't load log at {self.log_path}. Are there special characters in the path?") 
        else:
            self.create_log()

    def create_log(self):

        if not os.path.exists(self.log_path):
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
            self.save_log()

    def check_for_session(self):
        for session in range(len(self.log_data['sessions'])):
            if self.log_data['sessions'][session]['start_time'] == self.id:
                return True
        return False
    
    def create_new_session(self):
        #print("creating new session")
        new_session = {
            "filename" : str(self.comp_name),
            "artist" : CURRENT_USER,
            "start_time" : self.id,
            "notes" : [],
            "idle_time" : 0,
            "end_time" :  self.now(),
            "status" : "unsaved"
            }
        #print (new_session)
        self.log_data['sessions'].append(new_session)
        self.save_log()
        return new_session

    def update_thread(self):
        self.save_session()
        self.start_thread()

    def update_session(self): 
        print("starting update")
        self.get_log_data()
        current_session = self.get_session()
        # I need it to actually update the session first and then calculate everything
        # Then send it onnn
        self.log_data['sessions'][current_session]['end_time'] = self.now()
        if self.recently_saved == True:
            self.log_data['sessions'][current_session]['status'] = 'saved'
            self.recently_saved = False
        else:
            self.log_data['sessions'][current_session]['status'] = 'unsaved'

        if self.calculate_idle_time() > IDLE_TIME:
            self.log_data['sessions'][current_session]['idle_time'] += TIMER
            self.idling = True
        else:
            self.idling = False

        print("calculated idle time")
        self.calculate_stats()
        self.log_data['header']['shot_clock'] = str(datetime.timedelta(seconds=self.all_sessions))      
        self.log_data['header']['work_time'] = str(datetime.timedelta(seconds=self.all_work))
        self.log_data['header']['idle_time'] = str(datetime.timedelta(seconds=self.all_idle))
        print (f"work {self.all_work}   : all_sessions {self.all_sessions}   : idle {self.all_idle}")

        self.save_log()
        print("sending off data to update node")
        if USE_VIEWER:
            self.update_node()
        

    def save_log(self): 
        #print("saving time log")
        try:
            with open(self.log_path, 'w+') as _log:
                json.dump(self.log_data, _log, indent=4 )
        except:
            print(f"Can't save log at {self.log_path}. Are there special characters in the path?") 
        try:
            if LOG_IN_CONSOIDATED_LOGS:
                with open(self.consolidated_path, 'w+') as _log:
                    json.dump(self.log_data, _log, indent=4 )
        except:
            print(f"Can't save log at {self.consolidated_path}. Is your path correct?")

    def get_session(self):
        for session in range(len(self.log_data['sessions'])):
            if self.log_data['sessions'][session]['start_time'] == self.id:
                return session

    def get_nk_path(self): 
            '''Checks to see if the path to nk file exists '''
            self.script_file = nuke.root()['name'].value()
            if self.script_file != '': # get value from nuke
                return True
            else:
                return False

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
        self.consolidated_path = os.path.join(CONSOIDATED_LOGS, self.log_name)

        if self.comp_name == 'Untitled.nk':
            print("Comp not saved yet so not recording time")
            return False 
        return True

    def calculate_idle_time(self):
        now = time.time()
        print("started the idle time calculator")
        # if there is an autosave and it's from over the idle time ago, start idling
        if os.path.isfile(f'{self.script_file}.autosave'):
            modification_time = (os.stat(f'{self.script_file}.autosave').st_mtime)
            _all_idle = now - modification_time + 1
            #print (f"there is an autosave at {modification_time} and idle has been {_all_idle}")
        
        # if no autosave but file modified then user has modified it means user just saved it
        elif nuke.modified():
            if not os.path.isfile(f'{self.script_file}.autosave'):
                _all_idle = 0
        
        # if no autosave file and nuke is not modified, 
        # compare current time to the last file save time and the 
        # start time of the current session to make sure someone hasn't just opened the project and it could think
        # it's been idling for days.
        elif not nuke.modified():
            i = self.get_session()
            start_session_timestamp = int(datetime.datetime.timestamp(datetime.datetime.fromisoformat(self.log_data['sessions'][i]['start_time'])))
            if  start_session_timestamp >= int(os.stat(self.script_file).st_mtime):
                modification_time = start_session_timestamp
            else:
                modification_time = int(os.stat(self.script_file).st_mtime)
            _all_idle = now - modification_time
            #print (f"no autosave and last saved at {modification_time} and idle has been {_all_idle}")

        #print (_all_idle)
        print("finished calculating idle time")
        return _all_idle

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

    def start_thread(self):
        if self.started:
            self.save_session()
        else:
            # set this to be at the class level and not the instance level
            # so that it doesn't spin up a zillion threads

            Timelogger.thread = threading.Timer(TIMER, self.update_thread)
            Timelogger.thread.setDaemon(True)
            # if not TESTING:
            #     Timelogger.thread.setDaemon(True)
            print("starting thread")
            self.started = True
            Timelogger.thread.start()

    def update_node(self):
        self.lv.update_node(self.all_work, self.all_sessions, self.all_idle, self.idling, self.number_of_sessions)



class Log_Viewer():

    def __init__(self):
        self.create_node()
        self.achievement = ACHIEVEMENTS[0]
        self.achievements_accomplished = []

    def create_node(self):
        existing_nodes = nuke.allNodes("NoOp")
        existing_shot_clocks = [n for n in existing_nodes if n.name() == "Shot_Clock"]
        if existing_shot_clocks:
            # If a Shot Clock node already exists, update the message with the new version
            viewer_node = existing_shot_clocks[0]
        else:
            # If no Time_Keeper node exists, create a new one
            viewer_node = nuke.createNode("NoOp")
            viewer_node.setName("Shot_Clock")
            message_knob = nuke.Text_Knob('achievement','Achievement','')
            viewer_node.addKnob(message_knob)

    def update_node(self, all_work, all_sessions, all_idle, idling, number_of_sessions):
        '''updates the node with stats'''
        print(f"I'm updating the node at {(datetime.datetime.now().isoformat())}")
        work_time = datetime.timedelta(seconds=all_work)
        all_sessions = datetime.timedelta(seconds=all_sessions)
        all_idle = datetime.timedelta(seconds=all_idle)
        label = f"<p style='font-size:20px;  font-weight:bold; text-align:center'>{work_time}</p>"
        message = f"<p style='font-size:30px; font-weight:bold; text-align:center'> Working Time {work_time}</p><p style='font-size:20px; text-align:center'>Idle Time {all_idle}</p><p style='font-size:20px; text-align:center'>Total Time {all_sessions}</p>"
        if GAME:
            self.select_achievement(all_work)
            label = f"<p style='font-size:80px; text-align:center'>{self.achievement}</p>label"
            message = f"<p style='font-size:100px; text-align:center'>{self.achievement}</p>{message}"
        if idling:
            label = f"{label}<p style='font-size:20px;  text-align:center'>IDLING</p>"
            message = f"{message}<p style='font-size:20px; color:red; text-align:center'>IDLING...</p>"
        nuke.toNode('Shot_Clock').knob('label').setValue(label)
        nuke.toNode('Shot_Clock').knob('achievement').setValue(message)
        print(f"I'm done updating the node at {(datetime.datetime.now().isoformat())}")

    def select_achievement(self, all_work):
        if ACHIEVEMENTS != int: # if achie
            for i in range(len(ACHIEVEMENT_SCORE)):
                if (all_work/60) > ACHIEVEMENT_SCORE[i]:
                    self.achievement = ACHIEVEMENTS[i]
                    self.next_achievement = ACHIEVEMENTS[i+1]
                else:
                    self.achievements_accomplished.append(ACHIEVEMENTS[i])
                    return
                    
        else:
            self.achievement = str(f"&#{ACHIEVEMENTS+all_work};")
            return

    