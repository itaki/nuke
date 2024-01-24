import os
import threading
import getpass
import datetime
import json
import re
import nuke
import time

CURRENT_USER = getpass.getuser()
# TESTING_FILE = '/Volumes/Dettifoss/nuke_dev/shotclock/shot_clock_v01.nk'
# LOG_IN_PROJECT_DIR = True
LOG_IN_USER_LOGS = False
USER_LOGS = '/Volumes/panda/Dropbox (Personal)/_Library/nuke/_logs/'
TIMER = 60
IDLE_TIME = 180
USE_VIEWER_NODE = False

GAME = True

THEME = 'animals' # "animals", "objects", "all"
ACHIEVEMENT_SCORE = [0,1,2,5,10,15,30,60,120,240,480,600,720,960,1440,2880,5760,7200,10080,13440,20160,40320]
if THEME == 'animals':
    ACHIEVEMENTS = ['🐣','🐥','🐸','🐷','🐮','🐹','🐰','🐶','🐨','🐵','🐼','🐻','🦊','🐙','🦉','💀','👹','👿','👽','🦁','🐯','🐲']
elif THEME == 'objects':
    ACHIEVEMENTS = ['🍼','🎈','🔫','🏓','🌮','🌈','🍯','🌊','🌋','🍺','🍩','🎁','🎩','🍷','☕','☔','🦄','🎥','🦖','🧘','🧟','👑']
elif THEME == 'all':
    ACHIEVEMENTS = 127752 # where the emojis start


class Timekeeper():
    def __init__(self):
        self.start_thread()
    
    def start_thread(self):
        Timekeeper.thread = threading.Timer(TIMER, self.this_loop)
        Timekeeper.thread.setDaemon(True)
        Timekeeper.thread.start()

    def this_loop(self):
        logger.update_session()
        self.start_thread()

class viewer_updater():
    def __init__(self):
        pass
class Logger():
    '''this class does things like check for files, create files, save files
    it can also get datestamps of files'''

    def __init__(self):
        '''
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
        self.initialized = False
        self.startup_time = self.now()
        self.id = self.startup_time
        self.idling = False
        self.error_flagged = False
        # self.comp_name = ''
        # self.script_file = ''
        # self.log_in_project_dir = log_in_project_dir
        # self.log_in_user_logs = log_in_user_logs
        # self.user_log_dir = user_log_dir
        
    def blur_test(self):
        nuke.createNode("Blur")
        print("I created a blur")

    def now(self):
        return (datetime.datetime.now().isoformat())
    
    def logit(self):
        ''' This is the method that is called when a Nuke project is loaded'''
        # print("load method activated")
        self.project_path = self.get_project_path()
        self.extract_data_from_path()
        self.user = getpass.getuser()
        if not self.check_for_log():
            print(f"Timelog not found. creating one")
            self.create_log()
        else:
            self.load_log()
        if not self.get_session_index():
            self.create_new_session()
            self.get_session_index()
        self.initialized = True
        self.recently_saved = True
        self.update_session()
            
    def check_for_log(self):
        if os.path.isfile(self.log_path):
            # print("found log and loadin it")
            return True
        else:
            # print(f"no log found at {self.log_path}")
            return False
    
    def load_log(self):
        with open(self.log_path, 'r') as _log:
            self.log_data = json.load(_log)

    def save_log(self):
        try:
            with open(self.log_path, 'w+') as _log:
                json.dump(self.log_data, _log, indent=4 )
        except:
            print ("Timelog not saved")
        if LOG_IN_USER_LOGS:
            try:
                with open(USER_LOGS+self.log_name, 'w+') as _log:
                    json.dump(self.log_data, _log, indent=4 )
            except:
                print("User timelog not saved. Is your path correct?")
    
    def get_project_path(self):
        '''Checks to see if the path to nk file exists '''
        self.script_file = nuke.root()['name'].value() # get value from nuke
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
        return True
        
    def last_saved(self):
        modification_time = (os.stat(f'{self.script_file}.autosave').st_mtime)
        return modification_time

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
            "artist" : getpass.getuser(), # gets current user
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
        if self.initialized:
            if self.check_for_log():

                self.load_log()
                if self.recently_saved == True:
                    self.log_data['sessions'][self.session_index]['status'] = 'saved'
                    self.recently_saved = False
                else:
                    self.log_data['sessions'][self.session_index]['status'] = 'unsaved'
                self.log_data['sessions'][self.session_index]['end_time'] = self.now()
                if self.calculate_idle_time() > IDLE_TIME:
                    self.log_data['sessions'][self.session_index]['idle_time'] += TIMER
                    self.idling = True
                else:
                    self.idling = False
                self.calculate_stats()
                self.log_data['header']['shot_clock'] = str(datetime.timedelta(seconds=self.all_sessions))      
                self.log_data['header']['work_time'] = str(datetime.timedelta(seconds=self.all_work))
                self.log_data['header']['idle_time'] = str(datetime.timedelta(seconds=self.all_idle))
                self.save_log()

                return
            else:
                print("No log yet. Are you saved")
                return 
        else:
            if not self.error_flagged:
                #print("Project not loaded or saved so there is not log")
                pass

    def get_session_index(self):
        for session_index in range(len(self.log_data['sessions'])):
            # print (f"session index = {session_index}, is {self.log_data['sessions'][session_index]['start_time']} but id is {self.id}")
            if self.log_data['sessions'][session_index]['start_time'] == self.id:
                # print("I found a session")
                self.session_index = session_index
                return True
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


class Viewers():
    def __init__(self):
        self.node_created = False
        pass

    def update(self):
        if USE_VIEWER_NODE and logger.initialized:
            if not self.node_created:
                self.v = Viewer_Node()
                self.node_created = True
            self.v.update_node(logger.all_work, logger.all_sessions, logger.all_idle, logger.idling, logger.number_of_sessions)



class Viewer_Node():
    def __init__(self):
        if USE_VIEWER_NODE:
   
            self.achievement = ACHIEVEMENTS[0]
            self.achievements_accomplished = []

    def create_node(self):
        existing_nodes = nuke.allNodes("NoOp")
        existing_shot_clocks = [n for n in existing_nodes if n.name() == "Shot_Clock"]
        if existing_shot_clocks:
            # If a Shot Clock node already exists, update the message with the new version
            
            print(f"viewer node already exists")
            viewer_node = existing_shot_clocks[0]
        else:
            # If no Time_Keeper node exists, create a new one
            print(f"created viewer node")
            viewer_node = nuke.createNode("NoOp")
            viewer_node.setName("Shot_Clock")
            message_knob = nuke.Text_Knob('achievement','Achievement','')
            viewer_node.addKnob(message_knob)

    def update_node(self, all_work, all_sessions, all_idle, idling, number_of_sessions):
        '''updates the node with stats'''
        self.create_node() # creates a node if there isn't one 
        print(f"I'm updating the node at {(datetime.datetime.now().isoformat())}")
        
        # work_time = datetime.timedelta(seconds=all_work)
        # all_sessions = datetime.timedelta(seconds=all_sessions)
        # all_idle = datetime.timedelta(seconds=all_idle)
        # label = f"<p style='font-size:20px;  font-weight:bold; text-align:center'>{work_time}</p>"
        # message = f"<p style='font-size:30px; font-weight:bold; text-align:center'> Working Time {work_time}</p><p style='font-size:20px; text-align:center'>Idle Time {all_idle}</p><p style='font-size:20px; text-align:center'>Total Time {all_sessions}</p>"
        # if GAME:
        #     self.select_achievement(all_work)
        #     label = f"<p style='font-size:80px; text-align:center'>{self.achievement}</p>label"
        #     message = f"<p style='font-size:100px; text-align:center'>{self.achievement}</p>{message}"
        # if idling:
        #     label = f"{label}<p style='font-size:20px;  text-align:center'>IDLING</p>"
        #     message = f"{message}<p style='font-size:20px; color:red; text-align:center'>IDLING...</p>"
        # nuke.toNode('Shot_Clock').knob('label').setValue(label)
        # nuke.toNode('Shot_Clock').knob('achievement').setValue(message)
        # print(f"I'm done updating the node at {(datetime.datetime.now().isoformat())}")


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



  
# Create the logger instance
logger = Logger()
# Create the timekeep instance
tk = Timekeeper()
# Create the viewer node
viewers = Viewers() 



# if __name__ == '__main__':
#     TESTING = True
#     logger = Logger()
    