# -*- coding: utf-8 -*-
def Support():
    def Pay():    
        try:
            from PySide2.QtCore import Qt
            from PySide2.QtGui import QPixmap
            from PySide2.QtWidgets import QApplication, QMainWindow,QLabel,QPushButton,QGridLayout,QWidget,QLineEdit,QComboBox
        except Exception as e:
            from PySide.QtCore import Qt
            from PySide.QtGui import QPixmap, QApplication, QMainWindow,QLabel,QPushButton,QGridLayout,QWidget,QLineEdit,QComboBox

        import time,sys,os

        def getNukeWindow():
            return QApplication.activeWindow()
            
        class testWindow(QMainWindow):
            def __init__(self,parent=getNukeWindow()):
                super(testWindow,self).__init__(parent)
                self.initUI()
             
            def initUI(self):

                self.setWindowTitle('Choose mode')
                self.setFixedSize(563,420)
                self.Widget = QWidget()
                self.Layout = QGridLayout()
                self.Widget.setLayout(self.Layout)

                self.wechat = QLabel()
                self.wechat.setText("")
                self.wechatMap = QPixmap('{0}/weixin.png'.format('/'.join(__file__.replace("\\","/").split('/')[0:-1]).replace("py","Icons")))
                self.wechat.setMaximumSize(300,411)
                self.wechat.setPixmap(self.wechatMap)
                self.wechat.setScaledContents(True)

                self.zhifubao = QLabel()
                self.zhifubao.setText("")
                self.zhifubaoMap = QPixmap('{0}/zhifubao.jpg'.format('/'.join(__file__.replace("\\","/").split('/')[0:-1]).replace("py","Icons")))
                self.zhifubao.setMaximumSize(263,411)
                self.zhifubao.setPixmap(self.zhifubaoMap)
                self.zhifubao.setScaledContents(True)
                
                self.tonight = QLabel("今夜，我就是你♂的了")
                self.today = QLabel("今天，你是我♀的了")
                self.tonight.setAlignment(Qt.AlignCenter)
                self.today.setAlignment(Qt.AlignCenter)

                self.closes = QPushButton("close")
                self.closes.clicked.connect(self.closeWindow)
            
                self.Layout.addWidget(self.wechat,0,0)
                self.Layout.addWidget(self.zhifubao,0,1)
                self.Layout.addWidget(self.tonight,1,0)
                self.Layout.addWidget(self.today,1,1)
                self.Layout.addWidget(self.closes,2,0,5,5)
                self.setCentralWidget(self.Widget)
            def closeWindow(self):
                self.close()
        #if __name__ == '__main__':

        if True:
            try:
                startTest.close()
                del (startTest)
            except:
                pass
        startTest = testWindow()
        startTest.show()
        
    import nuke
    thisNode = nuke.thisNode()
    counter = thisNode['integerAmount'].getValue()
    indexCode = thisNode['indexCode'].value()
    if counter == 0:
        k = thisNode.knobs()['sup']
        newText = '''<h3><font color = 'red'>You may wanna rethink about this?<br><br>再想想？</font></h3>'''
        newKnob = nuke.PyScript_Knob('sup1', newText, indexCode)
        thisNode.removeKnob(k)
        thisNode.addKnob(newKnob)
        thisNode['integerAmount'].setValue(1)
        
    if counter == 1:
        k = thisNode.knobs()['sup1']
        newText = '''<h3><font color = 'green'>Seriously?<br><br>真的真的？</font></h3>'''
        newKnob = nuke.PyScript_Knob('sup2', newText, indexCode)
        thisNode.removeKnob(k)
        thisNode.addKnob(newKnob)
        thisNode['integerAmount'].setValue(2)

    if counter == 2:
        k = thisNode.knobs()['sup2']
        newText = '''<h3><font color = 'blue'>My tears are coming if you hit again!<br><br>再点一下我就要哭惹！T^T</font></h3>'''
        newKnob = nuke.PyScript_Knob('sup3', newText, indexCode)
        thisNode.removeKnob(k)
        thisNode.addKnob(newKnob)
        thisNode['integerAmount'].setValue(3)

    if counter == 3:
        k = thisNode.knobs()['sup3']
        newText = '''<h3><font color = 'cyan'>My man! Hit this! <br><br>好兄弟(小姐姐)，来！点这♂里</font></h3>'''
        newKnob = nuke.PyScript_Knob('sup4', newText, indexCode)
        thisNode.removeKnob(k)
        thisNode.addKnob(newKnob)
        thisNode['integerAmount'].setValue(4)

    if counter == 4:
        k = thisNode.knobs()['sup4']
        newText = '''<h3><font color = 'cyan'>You really wanna support me?<br><br>你真的想支持我嘛？</font></h3>'''
        newKnob = nuke.PyScript_Knob('sup', newText, indexCode)
        thisNode.removeKnob(k)
        thisNode.addKnob(newKnob)
        thisNode['integerAmount'].setValue(0)
        Pay()