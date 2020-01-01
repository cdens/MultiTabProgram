# =============================================================================
#     Code: mainprogram.py
#     Author: Casey R. Densmore, 25JUN2019
#     
#     Purpose: Creates QMainWindow class with basic functions for a GUI with
#        	multiple tabs. Requires PyQt5 module (pip instal PyQt5) 
#
#   General functions within main.py "RunProgram" class of QMainWindow:
#       o __init__: Calls functions to initialize GUI
#       o initUI: Builds GUI window
#		o makenewtab: Creates a new tab window (make all widgets/buttons here)
#       o whatTab: gets identifier for open tab
#       o renametab: renames open tab
#       o setnewtabcolor: sets the background color pattern for new tabs
#       o closecurrenttab: closes open tab
#       o savedataincurtab: saves data in open tab (saved file types depend on tab type and user preferences)
#       o postwarning: posts a warning box specified message
#       o posterror: posts an error box with a specified message
#       o postwarning_option: posts a warning box with Okay/Cancel options
#       o closeEvent: pre-existing function that closes the GUI- function modified to prompt user with an "are you sure" box
#
# =============================================================================


# =============================================================================
#   CALL NECESSARY MODULES HERE
# =============================================================================
from sys import argv, exit
from platform import system as cursys
from struct import calcsize
from os import remove, path, listdir
from traceback import print_exc as trace_error

if cursys() == 'Windows':
    from ctypes import windll

from shutil import copy as shcopy

from PyQt5.QtWidgets import (QMainWindow, QAction, QApplication, QMenu, QLineEdit, QLabel, QSpinBox, QCheckBox,
    QPushButton, QMessageBox, QWidget, QFileDialog, QComboBox, QTextEdit, QTabWidget, QVBoxLayout, QInputDialog, 
    QGridLayout, QDoubleSpinBox, QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar, QDesktopWidget, 
    QStyle, QStyleOptionTitleBar)
from PyQt5.QtCore import QObjectCleanupHandler, Qt, pyqtSlot
from PyQt5.QtGui import QIcon, QColor, QPalette, QBrush, QLinearGradient, QFont
from PyQt5.Qt import QThreadPool


#   DEFINE CLASS FOR PROGRAM (TO BE CALLED IN MAIN)
class RunProgram(QMainWindow):
    
    
# =============================================================================
#   INITIALIZE WINDOW, INTERFACE
# =============================================================================
    def __init__(self):
        super().__init__()
        
        try:
            self.initUI() #creates GUI window
            self.buildmenu() #Creates interactive menu, options to create tabs and start autoQC
            self.makenewtab() #Opens first tab

        except Exception:
            trace_error()
            self.posterror("Failed to initialize the program.")
        
    def initUI(self):

        #setting window size
        cursize = QDesktopWidget().availableGeometry(self).size()
        titleBarHeight = self.style().pixelMetric(QStyle.PM_TitleBarHeight, QStyleOptionTitleBar(), self)
        self.resize(cursize.width(), cursize.height()-titleBarHeight)

        # setting title/icon, background color
        self.setWindowTitle('Blank Multitab GUI Window')
        #self.setWindowIcon(QIcon('pathway_to_icon_here.png'))
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(255,255,255)) #white background
        self.setPalette(p)

        #sets app ID to ensure that any additional windows appear under the same tab
        if cursys() == 'Windows':
            myappid = 'APP_ID'  # arbitrary string
            windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        #changing font size
        font = QFont()
        font.setPointSize(11)
        font.setFamily("Arial")
        self.setFont(font)

        # prepping to include tabs
        mainWidget = QWidget()
        self.setCentralWidget(mainWidget)
        mainLayout = QVBoxLayout()
        mainWidget.setLayout(mainLayout)
        self.tabWidget = QTabWidget()
        mainLayout.addWidget(self.tabWidget)
        self.myBoxLayout = QVBoxLayout()
        self.tabWidget.setLayout(self.myBoxLayout)
        self.show()

        #setting slash dependent on OS- for file naming and handling
        global slash
        if cursys() == 'Windows':
            slash = '\\'
        else:
            slash = '/'

        #setting up dictionary to store data for each tab
        global alltabdata
        alltabdata = {}

        #tab tracking
        self.totaltabs = 0
        self.tabnumbers = []
        
        
# =============================================================================
#    BUILD MENU, GENERAL SETTINGS
# =============================================================================

    #builds file menu for GUI
    def buildmenu(self):
        #setting up primary menu bar
        menubar = self.menuBar()
        FileMenu = menubar.addMenu('Options')
        
        #File>New Profile Editor Tab
        newptab = QAction('&New Tab',self)
        newptab.setShortcut('Ctrl+N')
        newptab.triggered.connect(self.makenewtab)
        FileMenu.addAction(newptab)
        
        #File>Rename Current Tab
        renametab = QAction('&Rename Current Tab',self)
        renametab.setShortcut('Ctrl+R')
        renametab.triggered.connect(self.renametab)
        FileMenu.addAction(renametab)
        
        #File>Close Current Tab
        closetab = QAction('&Close Current Tab',self)
        closetab.setShortcut('Ctrl+X')
        closetab.triggered.connect(self.closecurrenttab)
        FileMenu.addAction(closetab)
        
        #File>Save Files
        savedataintab = QAction('&Save',self)
        savedataintab.setShortcut('Ctrl+S')
        savedataintab.triggered.connect(self.savedataincurtab)
        FileMenu.addAction(savedataintab)
        


# =============================================================================
#     SIGNAL PROCESSOR TAB AND INPUTS HERE
# =============================================================================
    def makenewtab(self):     
        try:

            newtabnum,curtabstr = self.addnewtab()
    
            #creates dictionary entry for current tab- you can add additional key/value combinations for the opened tab at any point after the dictionary has been initialized
            alltabdata[curtabstr] = {"tab":QWidget(),"tablayout":QGridLayout(),
                      "tabtype":"newtab","testvariable":False}

            self.setnewtabcolor(alltabdata[curtabstr]["tab"])
            
            alltabdata[curtabstr]["tablayout"].setSpacing(10)
    
            #creating new tab, assigning basic info
            self.tabWidget.addTab(alltabdata[curtabstr]["tab"],'New Tab') 
            self.tabWidget.setCurrentIndex(newtabnum)
            self.tabWidget.setTabText(newtabnum, "New Tab #" + str(self.totaltabs))
            alltabdata[curtabstr]["tabnum"] = self.totaltabs #assigning unique, unchanging number to current tab
            alltabdata[curtabstr]["tablayout"].setSpacing(10)
            
            
            #and add new buttons and other widgets
            alltabdata[curtabstr]["tabwidgets"] = {}

            #making widgets
            alltabdata[curtabstr]["tabwidgets"]["sourcetitle"] = QLabel(' Source:') #1
            alltabdata[curtabstr]["tabwidgets"]["refresh"] = QPushButton('Refresh')  # 2
            alltabdata[curtabstr]["tabwidgets"]["options"] = QComboBox() #3
            alltabdata[curtabstr]["tabwidgets"]["options"].addItem('Item A')
            alltabdata[curtabstr]["tabwidgets"]["options"].addItem('Item B')
            alltabdata[curtabstr]["currentoption"] = alltabdata[curtabstr]["tabwidgets"]["options"].currentText()
            
            alltabdata[curtabstr]["tabwidgets"]["sb1title"] = QLabel('Spinbox 1:') #4
            alltabdata[curtabstr]["tabwidgets"]["sb2title"] = QLabel('Spinbox 2:') #5
            
            alltabdata[curtabstr]["tabwidgets"]["sb1"] = QSpinBox() #6
            alltabdata[curtabstr]["tabwidgets"]["sb1"].setRange(1,99)
            alltabdata[curtabstr]["tabwidgets"]["sb1"].setSingleStep(1)
            alltabdata[curtabstr]["tabwidgets"]["sb1"].setValue(12)
            
            alltabdata[curtabstr]["tabwidgets"]["sb2"] = QDoubleSpinBox() #7
            alltabdata[curtabstr]["tabwidgets"]["sb2"].setRange(20, 30)
            alltabdata[curtabstr]["tabwidgets"]["sb2"].setSingleStep(0.25)
            alltabdata[curtabstr]["tabwidgets"]["sb2"].setDecimals(2)
            alltabdata[curtabstr]["tabwidgets"]["sb2"].setValue(23.5)
            
            #run function every time spinbox value is changed
            #alltabdata[curtabstr]["tabwidgets"]["sb2"].valueChanged.connect(self.callbackfunction) 
            
            alltabdata[curtabstr]["tabwidgets"]["b1"] = QPushButton('Button 1') #8
            alltabdata[curtabstr]["tabwidgets"]["b2"] = QPushButton('Button 2') #9
            alltabdata[curtabstr]["tabwidgets"]["b3"] = QPushButton('Button 3') #10
            
            alltabdata[curtabstr]["tabwidgets"]["t1t"] = QLabel('Entry 1:') #11
            alltabdata[curtabstr]["tabwidgets"]["t1"] = QLineEdit('E1 example') #12
            alltabdata[curtabstr]["tabwidgets"]["t2t"] = QLabel('Entry 2: ') #13
            alltabdata[curtabstr]["tabwidgets"]["t2"] = QLineEdit('E2 example') #14
            alltabdata[curtabstr]["tabwidgets"]["t3t"] = QLabel('Entry 3: ') #15
            alltabdata[curtabstr]["tabwidgets"]["t3"] = QLineEdit('E3 example') #16
            alltabdata[curtabstr]["tabwidgets"]["t4t"] = QLabel('Entry 4: ') #17
            alltabdata[curtabstr]["tabwidgets"]["t4"] = QLineEdit('E4 example') #18
            alltabdata[curtabstr]["tabwidgets"]["t5t"] = QLabel('Entry 5: ') #19
            alltabdata[curtabstr]["tabwidgets"]["t5"] = QLineEdit('E5 example') #20
            
            #formatting widgets
            alltabdata[curtabstr]["tabwidgets"]["sb1title"].setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            alltabdata[curtabstr]["tabwidgets"]["sb2title"].setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            alltabdata[curtabstr]["tabwidgets"]["t1t"].setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            alltabdata[curtabstr]["tabwidgets"]["t2t"].setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            alltabdata[curtabstr]["tabwidgets"]["t3t"].setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            alltabdata[curtabstr]["tabwidgets"]["t4t"].setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            alltabdata[curtabstr]["tabwidgets"]["t5t"].setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            #should be 19 entries 
            widgetorder = ["sourcetitle","refresh","options","sb1title","sb2title","sb1","sb2",
            "b1","b2","b3","t1t","t1","t2t","t2","t3t","t3",
            "t4t","t4","t5t","t5"]
            wrows     = [1,1,2,3,4,3,4,5,5,6,1,1,2,2,3,3,4,4,5,5]
            wcols     = [2,3,2,2,2,3,3,2,3,3,4,5,4,5,4,5,4,5,4,5]
            wrext     = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
            wcolext   = [1,1,2,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1]
    
            #adding user inputs
            for i,r,c,re,ce in zip(widgetorder,wrows,wcols,wrext,wcolext):
                alltabdata[curtabstr]["tablayout"].addWidget(alltabdata[curtabstr]["tabwidgets"][i],r,c,re,ce)
                    
            #adjusting stretch factors for all rows/columns
            colstretch = [5,1,1,1,1,1,1]
            for col,cstr in zip(range(0,len(colstretch)),colstretch):
                alltabdata[curtabstr]["tablayout"].setColumnStretch(col,cstr)
            rowstretch = [1,1,1,1,1,1,1,1,10]
            for row,rstr in zip(range(0,len(rowstretch)),rowstretch):
                alltabdata[curtabstr]["tablayout"].setRowStretch(row,rstr)

            #making the current layout for the tab
            alltabdata[curtabstr]["tab"].setLayout(alltabdata[curtabstr]["tablayout"])

        except Exception: #if something breaks
            trace_error()
            self.posterror("Failed to build new tab")
        
        
        
# =============================================================================
#     TAB MANIPULATION OPTIONS, OTHER GENERAL FUNCTIONS
# =============================================================================

    #handles tab indexing
    def addnewtab(self):
        #creating numeric ID for newly opened tab
        self.totaltabs += 1
        self.tabnumbers.append(self.totaltabs)
        newtabnum = self.tabWidget.count()
        curtabstr = "Tab "+str(self.totaltabs) #pointable string for alltabdata dict
        return newtabnum,curtabstr

    #gets index of open tab in GUI
    def whatTab(self):
        return self.tabnumbers[self.tabWidget.currentIndex()]
    
    #renames tab (only user-visible name, not alltabdata dict key)
    def renametab(self):
        try:
            curtab = self.tabWidget.currentIndex()
            name, ok = QInputDialog.getText(self, 'Rename Current Tab', 'Enter new tab name:',QLineEdit.Normal,str(self.tabWidget.tabText(curtab)))
            if ok:
                self.tabWidget.setTabText(curtab,name)
        except Exception:
            trace_error()
            self.posterror("Failed to rename the current tab")
    
    #sets default color scheme for tabs
    def setnewtabcolor(self,tab):
        p = QPalette()
        gradient = QLinearGradient(0, 0, 0, 400)
        gradient.setColorAt(0.0, QColor(255,253,253))
        #gradient.setColorAt(1.0, QColor(248, 248, 255))
        gradient.setColorAt(1.0, QColor(255, 225, 225))
        p.setBrush(QPalette.Window, QBrush(gradient))
        tab.setAutoFillBackground(True)
        tab.setPalette(p)
            
    #closes a tab
    def closecurrenttab(self):
        try:
            reply = QMessageBox.question(self, 'Message',
                "Are you sure to close the current tab?", QMessageBox.Yes | 
                QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:

                #getting tab to close
                curtab = int(self.whatTab())
                curtabstr = "Tab " + str(curtab)
                indextoclose = self.tabWidget.currentIndex()
                
                #add any additional necessary commands (stop threads, prevent memory leaks, etc) here
                
                #closing tab
                self.tabWidget.removeTab(indextoclose)

                #removing current tab data from the alltabdata dict, correcting tabnumbers variable
                alltabdata.pop("Tab "+str(curtab))
                self.tabnumbers.pop(indextoclose)

        except Exception:
            trace_error()
            self.posterror("Failed to close the current tab")
                
    #save data in open tab        
    def savedataincurtab(self):
        try:
            #getting directory to save files from QFileDialog
            outdir = str(QFileDialog.getExistingDirectory(self, "Select Directory to Save File(s)"))
            if outdir == '':
                QApplication.restoreOverrideCursor()
                return False
        except:
            self.posterror("Error raised in directory selection")
            return

        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            
            #pulling all relevant data
            curtabstr = "Tab " + str(self.whatTab())
            
            #write code to save open files here
                
        except Exception:
            trace_error() #if something else in the file save code broke
            self.posterror("Filed to save files")
            QApplication.restoreOverrideCursor()
            return False
        finally:
            QApplication.restoreOverrideCursor()
            return True
        
    #warning message
    def postwarning(self,warningtext):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(warningtext)
        msg.setWindowTitle("Warning")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
        
    #error message
    def posterror(self,errortext):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(errortext)
        msg.setWindowTitle("Error")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
    
    #warning message with options (Okay or Cancel)
    def postwarning_option(self,warningtext):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText(warningtext)
        msg.setWindowTitle("Warning")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        outval = msg.exec_()
        option = 'unknown'
        if outval == 1024:
            option = 'okay'
        elif outval == 4194304:
            option = 'cancel'
        return option
    
    #add warning message before closing GUI
    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
            "Are you sure to close the application? \n All unsaved work will be lost!", QMessageBox.Yes | 
            QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:

            if self.preferencesopened:
                self.settingsthread.close()

            #explicitly closing figures to clean up memory (should be redundant here but just in case)
            for curtabstr in alltabdata:
                if alltabdata[curtabstr]["tabtype"] == "ProfileEditor":
                    plt.close(alltabdata[curtabstr]["ProfFig"])
                    plt.close(alltabdata[curtabstr]["LocFig"])

                elif alltabdata[curtabstr]["tabtype"] == 'SignalProcessor_incomplete' or alltabdata[curtabstr]["tabtype"] == 'SignalProcessor_completed':
                    plt.close(alltabdata[curtabstr]["ProcessorFig"])

                    #aborting all threads
                    if alltabdata[curtabstr]["isprocessing"]:
                        alltabdata[curtabstr]["processor"].abort()

            event.accept()
        else:
            event.ignore() 
    

    
# =============================================================================
# EXECUTE PROGRAM
# =============================================================================
if __name__ == '__main__':  
    app = QApplication(argv)
    ex = RunProgram()
    exit(app.exec_())
    
    