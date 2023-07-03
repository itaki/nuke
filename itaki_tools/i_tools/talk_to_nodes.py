#import nuke
import threading
TESTING = False

'''
https://learn.foundry.com/nuke/developers/63/pythondevguide/basics.html
showControlPanel()
nuke.createNode( "Blur" )
nuke.knobDefault("Blur.size", "20")
nuke.selectedNode().addKnob(nuke.PyCustom_Knob("name", "label", "some_code()"))

'''

class Threadtester():
    def __init__(self):
        self.count = 0

    def update_thread(self):
        self.update_session()
        print("I got here")
        self.start_thread()

    def update_session(self):
        print(f"I am updating {self.count}")
        self.count +=1
        
    def start_thread(self):
        Threadtester.thread = threading.Timer(4, self.update_thread)
        if not TESTING:
            Threadtester.thread.setDaemon(True)
        Threadtester.thread.start()

def question_loop():
    inp = input('enter')
    if inp == "1":
        print("I got a number 1 entered")
        tt.update_session()
        question_loop()

    else:
        quit()


if __name__ == '__main__':
    tt = Threadtester()
    tt.start_thread()
    question_loop()
