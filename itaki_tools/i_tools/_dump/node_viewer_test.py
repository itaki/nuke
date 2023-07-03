import nuke
import threading

TIMER = 2


class Viewer_Updater():
    def __init__(self):
        self.i = 0

    def start_thread(self):
        # Viewer_Updater.thread = threading.Timer(TIMER, self.this_loop)
        # Viewer_Updater.thread.setDaemon(True)
        # Viewer_Updater.thread.start()
        self.this_loop

    def this_loop(self):
        print("threading is working")
        m.modify(2)
        self.start_thread()

class Node_Modify_Test():
    def __init__(self):
        self.blurry = nuke.nodes.Blur(name = 'Big_Blur')
        self.blurry.showControlPanel()

    def modify(self, amount=0):
        self.amount = self.amount + amount
        print("function is being called")
        value = self.blurry.knob('size').getValue()
        print(f"{value}")
        # self.blurry.knob('size').setValue(self.amount)

m = Node_Modify_Test()
vu = Viewer_Updater()
vu.start_thread()