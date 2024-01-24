#--coding: utf-8 --
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
import nuke
import sys
import os

class Settings(QWidget):
    def __init__(self):
        super(Settings, self).__init__()
        self.setWindowTitle("AOV Selector Settings")
        
        description_label = QLabel("Edit the following 4 (comma seperated) key word lists to modify how AOV Selector sorts your layers into groups.<br>The layers are sorted into the following categories in the order that they are listed below.<br>")

        custom_label = QLabel("Choose a node to be created when you ctrl+click on a layer, and have one of its knobs set to that layer.<br>Enter the node Class and the name of the knob. (e.g. GradeAOV, pMatte, Remove)<br> ")
        
        auto_close_label = QLabel("With Auto close checked, AOV Selector will automatically close after creating a shuffle, contact sheet or custom node.<BR>If this is not checked you will be able to make multiple nodes at once.<br>In order to close the AOV Selector: click Close, click on Nuke, or press ESC.<br>")

        light_label = QLabel("Lighting AOV's:")
        util_label = QLabel("Utility AOV's:")
        shad_label = QLabel("Shadow AOV's:")
        plo_label = QLabel("PLO's:")
        node_label = QLabel("Custom Node:")
        knob_label = QLabel("Custom Knob:")
        
        self.light = QLineEdit()
        self.light.setToolTip("Keywords to identfy lighting passes")
        self.util = QLineEdit()
        self.util.setToolTip("Keywords to identfy Utility passes")
        self.shad = QLineEdit()
        self.shad.setToolTip("Keywords to identfy Shadow passes")
        self.plo = QLineEdit()
        self.plo.setToolTip("Keywords to identfy light passes")
        self.node = QLineEdit()
        self.node.setToolTip("Class name of the node to use when creating a 'custom node'")
        self.knob = QLineEdit()
        self.knob.setToolTip("Knob name of the 'custom node' to set to the selected AOV")
        
        self.auto_close = QCheckBox("Auto close")
        self.auto_close.setToolTip("With this checked, AOV Selector will automatically close after creating a shuffle, contact sheet or custom node.<BR>If this is not checked you will be able to make multiple nodes at once. In order to close the AOV Selector: click Close, click on Nuke, or press ESC.")
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine);
        line.setFrameShadow(QFrame.Sunken);
        
        line2 = QFrame()
        line2.setFrameShape(QFrame.HLine);
        line2.setFrameShadow(QFrame.Sunken);
        
        line3 = QFrame()
        line3.setFrameShape(QFrame.HLine);
        line3.setFrameShadow(QFrame.Sunken);
        
        reset = QPushButton("Reset Defaults")
        reset.clicked.connect(self.Sreset)
        
        cancel = QPushButton("Cancel")
        cancel.setFixedWidth(90)
        cancel.clicked.connect(self.Scancel)
        
        save = QPushButton("Save")
        save.setFixedWidth(90)
        save.clicked.connect(self.Ssave)

        sv_buttons_layout = QHBoxLayout()
        sv_layout = QGridLayout()
        
        sv_buttons_layout.addWidget(reset)
        sv_buttons_layout.addWidget(save)
        sv_buttons_layout.addWidget(cancel)
        
        sv_layout.addWidget(description_label, 0, 1,1,3)
        
        sv_layout.addWidget(plo_label, 1, 0, Qt.AlignRight)
        sv_layout.addWidget(self.plo, 1, 1,1,3)
        
        sv_layout.addWidget(shad_label, 2, 0, Qt.AlignRight)
        sv_layout.addWidget(self.shad, 2, 1,1,3)
        
        sv_layout.addWidget(light_label, 3, 0, Qt.AlignRight)
        sv_layout.addWidget(self.light, 3, 1,1 ,3)
        
        sv_layout.addWidget(util_label, 4 , 0, Qt.AlignRight)
        sv_layout.addWidget(self.util, 4, 1,1,3)
        

    
        sv_layout.addWidget(line, 5, 0, 1, 4)
        
        sv_layout.addWidget(custom_label, 6, 1,1,3)
      
        sv_layout.addWidget(node_label, 7, 0)
        sv_layout.addWidget(self.node, 7, 1, 1, 1)
        
        sv_layout.addWidget(knob_label, 7, 2)
        sv_layout.addWidget(self.knob, 7, 3)
        
        sv_layout.addWidget(line2, 8, 0, 1, 4)
        
        sv_layout.addWidget(auto_close_label, 9, 1, 1, 3)
        
        sv_layout.addWidget(self.auto_close, 10, 1, 1, 1)
        
        sv_layout.addWidget(line3, 11, 0, 1, 4)
        sv_layout.addLayout(sv_buttons_layout, 12, 3)
        
        sv_layout.setHorizontalSpacing(25)
        
        
        ################## Load data  ######################
        
        self.settings_file =  os.path.expanduser('~') + '/.nuke/' + 'AOV_settings.txt'
        
        if os.path.isfile(self.settings_file):
            with open(self.settings_file, 'r') as f:
                data = f.readlines()
                f.close
            
            self.light.setText(data[0][:-1])
            self.util.setText(data[1][:-1])
            self.shad.setText(data[2][:-1])
            self.plo.setText(data[3][:-1])
            self.node.setText(data[4][:-1].replace(" ", ""))
            self.knob.setText(data[5][:-1].replace(" ", ""))
            if data[6][:-1] == "0":
                self.auto_close.setCheckState(Qt.Unchecked)
            else:
                self.auto_close.setCheckState(Qt.Checked)

        else:

            self.light.setText("spec,diffuse,refl,refr,light,illum,ambient,sss,bounce,emissive,lgt,fill,rim,scatter")
            self.util.setText("normal,depth,position,pref,restp,vector,motion,ward,deep,mask,id,noise,dirt,fresnel,facing,ratio,world")
            self.shad.setText("shad,occ,cast")
            self.plo.setText("ls,lss,plo")
            self.node.setText("")
            self.knob.setText("")
            self.auto_close.setCheckState(Qt.Checked)

        
        
        
        
        
        
        
        
        
        self.setLayout(sv_layout)
            
            
############ Reset  ###########
    def Sreset(self):
        self.light.setText("spec,diffuse,refl,refr,light,illum,ambient,sss,bounce,emissive,lgt,fill,rim,scatter")
        self.util.setText("normal,depth,position,pref,restp,vector,motion,ward,deep,mask,id,noise,dirt,fresnel,facing,ratio,world")
        self.shad.setText("shad,occ,cast")
        self.plo.setText("ls,lss,plo")
        self.node.setText("")
        self.knob.setText("")
        self.auto_close.setCheckState(Qt.Checked)



############ Cancel  ###########
    def Scancel(self):
        AOVsettings.settings.close()

############ Save  ###########
    def Ssave(self):
        
        with open(self.settings_file, 'w') as f:
            f.write(self.light.text().replace(" ", ""))
            f.write('\n')
            f.write(self.util.text().replace(" ", ""))
            f.write('\n')
            f.write(self.shad.text().replace(" ", ""))
            f.write('\n')
            f.write(self.plo.text().replace(" ", ""))
            f.write('\n')
            
            if self.node.text() == "":
                f.write(" ")
            else:
                f.write(self.node.text())
            f.write('\n')
            
            if self.knob.text() == "":
                f.write(" ")
            else:
                f.write(self.knob.text())

            f.write('\n')
            
            if self.auto_close.isChecked():
                f.write("1")
            else:
                f.write("0")
            f.write('\n')
            
            f.close()
        
        
        
        AOVsettings.settings.close()





########################################################
###=============   AOV Selector  ====================###
########################################################


class Panel(QWidget):
    def __init__(self):
        super(Panel, self).__init__()
        self.setWindowTitle("AOV Selector")

        self.channels=[]
        
        


        self.parent = nuke.root()
        
        ###### Viewer Exists  ######

        if nuke.activeViewer() != None:
            self.viewer = nuke.activeViewer().node()
            
        
            if "." in self.viewer.fullName():
                self.parent = nuke.toNode(self.viewer.fullName().rsplit('.', 1)[0])
            
            if nuke.activeViewer().activeInput() == None:

                self.parent.begin()
        
                try:
                    self.mainnode = nuke.selectedNode()
                except ValueError:
                    nuke.message("Please select and view a node to see channels.")
                    
                    self.parent.end()

                    return



                self.viewer.setInput(0, self.mainnode)
                self.parent.end()
                nuke.root().begin()
                nuke.root().end()


            self.vinput = nuke.activeViewer().activeInput()
            
            
            try:
                self.mainnode = nuke.selectedNode()
            except ValueError:
                self.mainnode = self.viewer.input(self.vinput)

            self.mainnode.setSelected(True)
        
        
        ###### No Viewer  ######
   
        else:
            
            try:
                self.mainnode = nuke.selectedNode()
            except ValueError:
                nuke.message("no viewer, cant set selected to mainnode")
                return
            
            self.viewer = nuke.createNode('Viewer')
            self.viewer.setSelected(False)
            self.mainnode.setSelected(True)
            self.vinput = 0
        
        
        
        
        self.vchannels = self.viewer['channels'].value()
        self.vnode = self.viewer.input(self.vinput)
        


        for i in self.mainnode.channels():
                if i.split(".", 1)[0] not in self.channels:
                    self.channels.append(i.split(".", 1)[0])




        self.close_check = QCheckBox("Auto close")
        self.close_check.setToolTip("With this checked, AOV Selector will automatically close after creating a shuffle, contact sheet or custom node.<BR>If this is not checked you will be able to make multiple nodes at once, but will have to close the AOV Selector by clicking Close, clicking on Nuke, or pressing ESC.")
        
        
    
    ############    READING SETTINGS FROM DISK   ########
    
    
        self.settings_file =  os.path.expanduser('~') + '/.nuke/' + 'AOV_settings.txt'

        if os.path.isfile(self.settings_file):
            with open(self.settings_file, 'r') as f:
                data = f.readlines()
                f.close

            aovl = data[0][:-1].split(',')
            aovu = data[1][:-1].split(',')
            aovshad = data[2][:-1].split(',')
            aovplo = data[3][:-1].split(',')
            self.customNode = data[4][:-1]
            self.customKnob = data[5][:-1]
            if data[6][:-1] == "0":
                self.close_check.setCheckState(Qt.Unchecked)
            else:
                self.close_check.setCheckState(Qt.Checked)
        else:
            
            aovl = ['spec', 'diffuse', 'refl', 'refr', 'light', 'illum', 'ambient', 'sss', 'bounce', 'emissive', 'lgt', 'fill', 'rim', 'scatter']
            aovu = ['normal', 'depth', 'position', 'pref', 'restp', 'vector', 'motion', 'ward', 'deep', 'mask', 'id', 'noise', 'dirt', 'fresnel', 'facing', 'ratio', 'world']
            aovshad = ['shad', 'occ', 'cast']
            aovplo = ['ls', 'lss', 'plo']
            self.customNode = " "
            self.customKnob = " "
            self.close_check.setCheckState(Qt.Checked)
            
            
            with open(self.settings_file, 'w') as f:
                f.write("spec,diffuse,refl,refr,light,illum,ambient,sss,bounce,emissive,lgt,fill,rim,scatter")
                f.write('\n')
                f.write("normal,depth,position,pref,restp,vector,motion,ward,deep,mask,id,noise,dirt,fresnel,facing,ratio,world")
                f.write('\n')
                f.write("shad,occ,cast")
                f.write('\n')
                f.write("ls,lss,plo")
                f.write('\n')
                f.write(" ")
                f.write('\n')
                f.write(" ")
                f.write('\n')
                f.write("1")
                f.write('\n')
                f.close()
    






        self.lighting = []
        self.util = []
        self.shad = []
        self.plo = []

##### sort PLO's #####
        for i in self.channels:
            for a in aovplo:
                if i.lower().find(a) == 0:
                    self.plo.append(i)

        for i in self.plo:
            if i in self.channels:
                self.channels.remove(i)
        

##### sort shads #####
        for i in self.channels:
            for a in aovshad:
                if i.lower().find(a) >= 0:
                    self.shad.append(i)

        for i in self.shad:
            if i in self.channels:
                self.channels.remove(i)


##### sort Lighting #####
        for i in self.channels:
            for a in aovl:
                if i.lower().find(a) >= 0:
                    self.lighting.append(i)
            if i.lower() == "gi" or i.lower() == "rawgi":
                self.lighting.append(i)

        for i in self.lighting:
            if i in self.channels:
                self.channels.remove(i)


##### sort Util's #####
        for i in self.channels:
           for a in aovu:
                if i.lower().find(a) >= 0 :
                    self.util.append(i)
           if i.lower() == "n" or i.lower() == "p":
                self.util.append(i)

        for i in self.util:
            if i in self.channels:
                self.channels.remove(i)




        self.lighting = set(self.lighting)
        self.lighting = sorted(list(self.lighting))

        self.util = set(self.util)
        self.util = sorted(list(self.util))

        self.shad = set(self.shad)
        self.shad = sorted(list(self.shad))

        self.plo = set(self.plo)
        self.plo = sorted(list(self.plo))

        self.channels = sorted(self.channels)
        

#######   Title font
        self.Titlefont = QFont()
        self.Titlefont.setPointSize(38)
        self.Titlefont.setBold(True)
        
#######   top Button font
        self.topbuttonfont = QFont()
        self.topbuttonfont.setPointSize(18)
        self.topbuttonfont.setBold(False)

#######   Button font
        self.font = QFont()
        self.font.setPointSize(10)
        self.font.setBold(True)
        
#######   no search font
        self.hiddenfont = QFont()
        self.hiddenfont.setPointSize(10)
        self.hiddenfont.setBold(False)
        
#######   Label font
        self.hfont = QFont()
        self.hfont.setPointSize(20)
        self.hfont.setBold(True)

#######     Layouts


        v_layout = QVBoxLayout()
        h_layout = QHBoxLayout()
        help_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        light_layout = QVBoxLayout()
        util_layout = QVBoxLayout()
        shad_layout = QVBoxLayout()
        plo_layout = QVBoxLayout()
        extra_layout = QVBoxLayout()
        bottom_layout = QHBoxLayout()
        
        self.title = QLabel(" AOV selector")
        self.title.setFont(self.Titlefont)
        self.settings = QPushButton(u'⚙')
        self.settings.clicked.connect(self.edit_settings)
        self.settings.setFont(self.topbuttonfont)
        self.settings.setFlat(True)
        self.settings.setFixedWidth(40)
        self.help = QPushButton("?")
        self.help.clicked.connect(self.help_popup)
        self.help.setFont(self.topbuttonfont)
        self.help.setFlat(True)
        self.help.setFixedWidth(40)
        self.help.setToolTip("<h2>AOV selector v1.0</h2><b>Darren MacKay, April 2017</b><br> <table width='400'><tr><td>click</td><td>shuffle out AOV</td></tr>      <tr><td>shift+click</td><td>view AOV</td></tr>           <tr><td>ctrl+click</td><td>create custom node</td></tr>          <tr><td>click on heading    </td><td>create contact sheet of current group</td></tr>  </table> <br><br>click on the gear to control how AOV's are sorted and to define your 'custom node'.\n")

        

        
        
        line = QFrame()
        line.setGeometry(QRect(320, 150, 118, 3));
        line.setFrameShape(QFrame.HLine);
        line.setFrameShadow(QFrame.Sunken);
        
        cancel = QPushButton("Close")
        cancel.setFixedWidth(90)
        cancel.clicked.connect(self.cancel)


        light_layout.setAlignment(Qt.AlignTop)
        util_layout.setAlignment(Qt.AlignTop)
        shad_layout.setAlignment(Qt.AlignTop)
        plo_layout.setAlignment(Qt.AlignTop)
        extra_layout.setAlignment(Qt.AlignTop)
        

        h_layout.addSpacing(25)
        h_layout.addLayout(light_layout)
        h_layout.addLayout(util_layout)
        h_layout.addLayout(shad_layout)
        h_layout.addLayout(plo_layout)
        h_layout.addLayout(extra_layout)
        h_layout.addSpacing(25)
        
#########   Headings
        
        Tlight = QPushButton("Component")
        Tlight.setFocusPolicy(Qt.NoFocus)
        Tlight.clicked.connect(self.make_contact_sheets)
        Tlight.setFlat(True)
        Tlight.setFont(self.hfont)
        if len(self.lighting) > 0:
            light_layout.addWidget(Tlight)
        
        Tutil = QPushButton("Utility")
        Tutil.clicked.connect(self.make_contact_sheets)
        Tutil.setFlat(True)
        Tutil.setFont(self.hfont)
        if len(self.util) > 0:
            util_layout.addWidget(Tutil)
                
                
        Tshad = QPushButton("Shadow")
        Tshad.clicked.connect(self.make_contact_sheets)
        Tshad.setFont(self.hfont)
        Tshad.setFlat(True)
        if len(self.shad) > 0:
            shad_layout.addWidget(Tshad)
        
        
        Tplo = QPushButton("Light")
        Tplo.clicked.connect(self.make_contact_sheets)
        Tplo.setFont(self.hfont)
        Tplo.setFlat(True)
        if len(self.plo) > 0:
            plo_layout.addWidget(Tplo)

        
        Tother = QPushButton("Other")
        Tother.clicked.connect(self.make_contact_sheets)
        Tother.setFont(self.hfont)
        Tother.setFlat(True)
        if len(self.channels) > 0:
            extra_layout.addWidget(Tother)
                
        
        self.lightinglist = QGridLayout()
        self.lightinglist.setAlignment(Qt.AlignTop)
        light_layout.addLayout(self.lightinglist)

        self.utillist = QGridLayout()
        self.utillist.setAlignment(Qt.AlignTop)
        util_layout.addLayout(self.utillist)

        self.shadlist = QGridLayout()
        self.shadlist.setAlignment(Qt.AlignTop)
        shad_layout.addLayout(self.shadlist)
        
        self.plolist = QGridLayout()
        self.plolist.setAlignment(Qt.AlignTop)
        plo_layout.addLayout(self.plolist)

        self.extralist = QGridLayout()
        self.extralist.setAlignment(Qt.AlignTop)
        extra_layout.addLayout(self.extralist)
        
        
        self.close_check.stateChanged.connect(self.save_autoclose)
        

        row = 0
        col = 0
        for i in self.lighting:
            p = QPushButton(i)
            #p.setFixedHeight(50)
            p.setFont(self.font)
            p.clicked.connect(self.who_got_clicked)
            self.lightinglist.addWidget(p, row, col)
            if row == 19:
                row = 0
                col += 1
            else:
                row += 1



        row = 0
        col = 0
        for i in self.util:
            p = QPushButton(i)
            #p.setFixedHeight(50)
            p.setFont(self.font)
            p.clicked.connect(self.who_got_clicked)
            self.utillist.addWidget(p, row, col)
            if row == 19:
                row = 0
                col += 1
            else:
                row += 1



        row = 0
        col = 0
        for i in self.shad:
            p = QPushButton(i)
            #p.setFixedHeight(50)
            p.setFont(self.font)
            p.clicked.connect(self.who_got_clicked)
            shad_layout.addWidget(p)
            self.shadlist.addWidget(p, row, col)
            if row == 19:
                row = 0
                col += 1
            else:
                row += 1


        row = 0
        col = 0
        for i in self.plo:
            p = QPushButton(i)
            #p.setFixedHeight(50)
            p.setFont(self.font)
            p.clicked.connect(self.who_got_clicked)
            self.plolist.addWidget(p, row, col)
            if row == 19:
                row = 0
                col += 1
            else:
                row += 1

        row = 0
        col = 0
        for i in self.channels:
            p = QPushButton(i)
            #p.setFixedHeight(50)
            p.setFont(self.font)
            p.clicked.connect(self.who_got_clicked)
            self.extralist.addWidget(p, row, col)
            if row == 19:
                row = 0
                col += 1
            else:
                row += 1




        self.search = QLineEdit()
        self.search.setPlaceholderText("Search")
        self.search.textChanged.connect(self.search_update)
        
        
        
        help_layout.addWidget(self.help)
        help_layout.addWidget(self.settings)
        
        top_layout.addWidget(self.title)
        top_layout.addLayout(help_layout)
        
        bottom_layout.addSpacing(25)
        bottom_layout.addWidget(self.close_check, 0 , Qt.AlignLeft)
        bottom_layout.addWidget(cancel, 0 , Qt.AlignRight)
        
        
        v_layout.addLayout(top_layout)
        
        
        v_layout.addWidget(self.search)
        v_layout.addLayout(h_layout)
        v_layout.addWidget(line)
        v_layout.addLayout(bottom_layout)


        self.setLayout(v_layout)
        self.move(QCursor().pos().x()-200, 120)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        self.search.setFocus()


######   Search  ######
    def search_update(self):
        
        query =self.search.text().lower()
        
        
        index = self.lightinglist.count()
        for i in xrange(index):
            if self.lightinglist.itemAt(i).widget().text().lower().find(query) >= 0:
                self.lightinglist.itemAt(i).widget().setFont(self.font)
                self.lightinglist.itemAt(i).widget().setStyleSheet("color: #C8C8C8;")
            else:
                self.lightinglist.itemAt(i).widget().setFont(self.hiddenfont)
                self.lightinglist.itemAt(i).widget().setStyleSheet("color: #555555;")


        index = self.utillist.count()
        for i in xrange(index):
            if self.utillist.itemAt(i).widget().text().lower().find(query) >= 0:
                self.utillist.itemAt(i).widget().setFont(self.font)
                self.utillist.itemAt(i).widget().setStyleSheet("color: #C8C8C8;")
            else:
                self.utillist.itemAt(i).widget().setFont(self.hiddenfont)
                self.utillist.itemAt(i).widget().setStyleSheet("color: #555555;")


        index = self.shadlist.count()
        for i in xrange(index):
            if self.shadlist.itemAt(i).widget().text().lower().find(query) >= 0:
                self.shadlist.itemAt(i).widget().setFont(self.font)
                self.shadlist.itemAt(i).widget().setStyleSheet("color: #C8C8C8;")
            else:
                self.shadlist.itemAt(i).widget().setFont(self.hiddenfont)
                self.shadlist.itemAt(i).widget().setStyleSheet("color: #555555;")


        index = self.plolist.count()
        for i in xrange(index):
            if self.plolist.itemAt(i).widget().text().lower().find(query) >= 0:
                self.plolist.itemAt(i).widget().setFont(self.font)
                self.plolist.itemAt(i).widget().setStyleSheet("color: #C8C8C8;")
            else:
                self.plolist.itemAt(i).widget().setFont(self.hiddenfont)
                self.plolist.itemAt(i).widget().setStyleSheet("color: #555555;")


        index = self.extralist.count()
        for i in xrange(index):
            if self.extralist.itemAt(i).widget().text().lower().find(query) >= 0:
                self.extralist.itemAt(i).widget().setFont(self.font)
                self.extralist.itemAt(i).widget().setStyleSheet("color: #C8C8C8;")
            else:
                self.extralist.itemAt(i).widget().setFont(self.hiddenfont)
                self.extralist.itemAt(i).widget().setStyleSheet("color: #555555;")




#######   Save AutoClose   ######
    def save_autoclose(self):
        with open(self.settings_file, 'r') as f:
            data = f.readlines()
            f.close
            
            
        if self.close_check.isChecked():
            data[6] = "1\n"
        else:
            data[6] = "0\n"
            
            
        with open(self.settings_file, 'w') as f:
            f.writelines(data)
            
            f.close



######   Edit Settings  ######
    def edit_settings(self):

    
        AOVsettings()


######   Help Popup  ######
    def help_popup(self):
        nuke.message("<h2>AOV selector v1.0</h2><b>Darren MacKay, April 2017</b><br> <table width='400'><tr><td>click</td><td>shuffle out AOV</td></tr>      <tr><td>shift+click</td><td>view AOV</td></tr>           <tr><td>ctrl+click</td><td>create custom node</td></tr>          <tr><td>click on heading    </td><td>create contact sheet of current group</td></tr>  </table> <br><br>click on the gear to control how AOV's are sorted and to define your 'custom node'.\n")






######   Cancel  ######
    def cancel(self):
        AOVselector.panel.close()
    
    
    
######   Make Contact Sheets  ######
    def make_contact_sheets(self):
        name = self.sender().text()
        
        self.parent.begin()
        base = nuke.selectedNodes()[len(nuke.selectedNodes())-1]
        for n in nuke.selectedNodes():
            n['selected'].setValue(False)
        
        
    
        sheet = []
        if name == "Component":
            sheet = self.lighting
        if name == "Utility":
            sheet = self.util
        if name == "Shadow":
            sheet = self.shad
        if name == "Light":
            sheet = self.plo
        if name == "Other":
            sheet = self.channels
            if 'rgb' in self.channels:
                sheet.remove('rgb')
            if 'rgba' in self.channels:
                sheet.remove('rgba')
    
    
        group = nuke.createNode('Group', inpanel = False)
        group.setInput(0, base)
        group['label'].setValue(name)
        group.setXpos(base.xpos()+150)
        
        group.begin()


        input = nuke.createNode('Input', inpanel = False)
        remove = nuke.createNode('Remove', inpanel = False)
   
        remove['operation'].setValue('keep')
        remove['channels'].setValue('rgba')

        
        for i in sheet:
            rgb = nuke.createNode('ShuffleCopy', inpanel = False)
            rgb.setInput(1, input)
        
            rgb['in'].setValue(i)
            rgb['in2'].setValue('none')
            rgb['out'].setValue(i)
        
            rgb['red'].setValue('r')
            rgb['green'].setValue('g')
            rgb['blue'].setValue('b')
            rgb['alpha'].setValue('a')







        nuke.createNode('LayerContactSheet', inpanel = False)
        nuke.createNode('Output', inpanel = False)


        group.end()
        self.parent.end()
        nuke.root().begin()
        nuke.root().end()
        
        group.setSelected(False)
        base.setSelected(True)


        if self.close_check.isChecked():
            AOVselector.panel.close()


######   Clicked  ######
    def who_got_clicked(self):
        name = self.sender().text()
        
        
        modifiers = QApplication.keyboardModifiers()
        if modifiers == Qt.ShiftModifier:
            ##############    Shift Click ##############
            
            self.viewer.setInput(self.vinput, self.mainnode)
            self.viewer['channels'].setValue(name)

        elif modifiers == Qt.ControlModifier:
            ##############    Control Click ##############
            
            self.parent.begin()
            
            if self.customNode != " " and self.customKnob != " ":
                base = nuke.selectedNodes()[len(nuke.selectedNodes())-1]
                for n in nuke.selectedNodes():
                    n['selected'].setValue(False)
    
            custom = nuke.createNode(self.customNode, inpanel=False)
            custom[self.customKnob].setValue(name)
            custom.setXpos(base.xpos()-150)
            custom.setSelected(False)
            self.mainnode.setSelected(True)

            self.parent.end()
            nuke.root().begin()
            nuke.root().end()

            if self.close_check.isChecked():
                AOVselector.panel.close()




        else:
            ##############  Make the Shuffle  ############
            self.parent.begin()

            base = nuke.selectedNodes()[len(nuke.selectedNodes())-1]
            for n in nuke.selectedNodes():
                n['selected'].setValue(False)
                
            count = 0
            for i in base.channels():
                if i.split(".", 1)[0] == name:
                    count += 1
                
                
            stamp = nuke.createNode('Shuffle', inpanel=False)
            stamp['in'].setValue(name)
            stamp['postage_stamp'].setValue(True)
            stamp['label'].setValue(name)
            stamp['note_font_size'].setValue(15)
            stamp['tile_color'].setValue(2138864895)
            stamp.setXpos(stamp.xpos()-150)
            stamp.setInput(0, base)
            stamp.setSelected(False)
            base.setSelected(True)
                
                
                
            if count == 2:
                stamp['blue'].setValue('black')
                stamp['alpha'].setValue('black')
            elif count == 3:
                stamp['alpha'].setValue('black')


            self.parent.end()
            nuke.root().begin()
            nuke.root().end()




            if self.close_check.isChecked():
                AOVselector.panel.close()


##########  override close to return viewer back to original channels
    def closeEvent(self, event):
        self.viewer.setInput(self.vinput, self.vnode)
        self.viewer['channels'].setValue(self.vchannels)
        event.accept()






def AOVselector():
    

    
    if nuke.activeViewer().activeInput() == None and nuke.selectedNodes() == []:
        nuke.message("Please select and view a node to see channels.")
        return
    else:
        if nuke.selectedNode().Class() != "Viewer":
            AOVselector.panel = Panel()
            AOVselector.panel.show()
        else:
            nuke.message("Please select and view a node to see channels.")



def AOVsettings():

    AOVsettings.settings = Settings()
    AOVsettings.settings.setMinimumWidth(800)
    AOVsettings.settings.show()

