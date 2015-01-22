#!/usr/bin/env pythonw

from PyQt4 import QtGui, QtCore
import sys
import requests
import subprocess
import json
from task_picker import TaskPicker
from timer_widget import TimerWidget

REDMINE_URL = ''
# REDMINE_URL = 'http://dmscode.iris.washington.edu/'
REDMINE_USER = 'adam'
ISSUES_URL =  REDMINE_URL + '/issues.json?assigned_to=%s&sort=updated_on:desc&status_id=open' % (REDMINE_USER,)
ISSUE_URL =  REDMINE_URL + '/issues/%s'
POMODORO_SCRIPT = """
set theDuration to 29
set theBreak to 1

tell application "Pomodoro"
    start "%s" duration theDuration break theBreak
end tell
"""

class TaskList(QtGui.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(TaskList, self).__init__(*args, **kwargs)
        self.initWindow()
        self.initWidgets()

    def initWindow(self):
        self.setWindowTitle('TaskList')

        self.file_menu = QtGui.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QtGui.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)
    
    def initWidgets(self):
        mainWidget = QtGui.QWidget(self)
        self.setCentralWidget(mainWidget)
        
        #taskPickerLayout = QtGui.QVBoxLayout()
        self.taskPicker = TaskPicker(self)
        #self.taskPicker.taskPicked.connect(self.taskPickerDone)
        #self.taskPicker.cancel.connect(self.taskPickerDone)
        #taskPickerLayout.addWidget(self.taskPicker)
        #self.taskPickerDialog.setLayout(taskPickerLayout)

        self.timerWidget = TimerWidget(mainWidget)
        self.timerWidget.needsPick.connect(self.pickTask)
        
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.addWidget(self.timerWidget)

        mainWidget.setLayout(self.mainLayout)
        
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.show()
 
    def pickTask(self):
        result = self.taskPicker.exec_()
        if result:
            self.timerWidget.setTask(self.taskPicker.pickedTask)
 
    def fileQuit(self):
        self.close()
    
    def asrun(self, ascript):
        "Run the given AppleScript and return the standard output and error."
        osa = subprocess.Popen(['osascript', '-'],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE)
        return osa.communicate(ascript)[0]

    def about(self):
        QtGui.QMessageBox.about(self, "About",
"""embedding_in_qt4.py example
Copyright 2005 Florent Rougon, 2006 Darren Dale

This program is a simple example of a Qt4 application embedding matplotlib
canvases.

It may be used and modified with no restriction; raw copies as well as
modified versions may be distributed without limitation."""
)


def run():
    app = QtGui.QApplication(sys.argv)

    icon = QtGui.QIcon(QtGui.QPixmap(10,20))
    trayicon = QtGui.QSystemTrayIcon(icon)
#     trayicon.setContextMenu(menu)
    trayicon.show()

    print trayicon.geometry()

    menu = QtGui.QMenu('test')
    pm = QtGui.QPixmap(trayicon.geometry().size())
    painter = QtGui.QPainter()
    painter.begin(pm)
    font = menu.font()
    font.setPixelSize(pm.height())
    painter.setFont(font)
    
    print painter.font()
    painter.fillRect(0,0,pm.width(),pm.height(),QtCore.Qt.red)
    painter.drawText(0, pm.height(), "Test")
    painter.end()
    trayicon.setIcon(QtGui.QIcon(pm))

#     trayicon.showMessage('test', 'test message')
    w = TaskList()
#     w = QtGui.QWidget()
    w.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    run()

