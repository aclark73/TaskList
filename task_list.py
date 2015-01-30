#!/usr/bin/env pythonw

from PyQt4 import QtGui, QtCore
import sys
import requests
import subprocess
from timer_widget import TimerWidget
from task_picker import TaskPicker
from settings import Settings
from logging import getLogger

REDMINE_HOME = 'http://dmscode.iris.washington.edu'
# REDMINE_HOME = 'http://localhost:8181'
REDMINE_USER = 'adam'
ISSUES_URL = '%s/issues.json?assigned_to=%s&sort=updated_on:desc&status_id=open' % (REDMINE_HOME, REDMINE_USER)
ISSUE_URL = REDMINE_HOME + '/issues/%s'
POMODORO_SCRIPT = """
set theDuration to 29
set theBreak to 1

tell application "Pomodoro"
    start "%s" duration theDuration break theBreak
end tell
"""

LOGGER = getLogger(__name__)

class TaskList(QtGui.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(TaskList, self).__init__(*args, **kwargs)
        self.initUI()
        with Settings(__name__) as settings:
            if settings.contains('geometry'):
                self.setGeometry(settings.value('geometry').toRect())
        settings.endGroup()        
        
    def initUI(self):
        self.timerWidget = TimerWidget()
        self.timerWidget.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.pickerWidget = TaskPicker(self.timerWidget)
        self.pickerWidget.setModal(True)
        
        self.timerWidget.taskNeeded.connect(self.showPicker)
        self.pickerWidget.picked.connect(self.onTaskPicked)

        self.timerWidget.stopped.connect(self.onTaskStopped)

        self.setCentralWidget(self.timerWidget)
        self.timerWidget.toolbar.setMovable(False)
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.timerWidget.toolbar)
        
    def showPicker(self):
        self.pickerWidget.show()
    
    def onTaskPicked(self, task):
        self.timerWidget.setTask(task)

    def onTaskStopped(self, task, startTime, endTime):
        print("%s,%s,%s" % (task, startTime, endTime))

    def closeEvent(self, *args, **kwargs):
        with Settings(__name__) as settings:
            settings.setValue('geometry', self.geometry())
        super(TaskList, self).closeEvent(*args, **kwargs)


def run():
    app = QtGui.QApplication(sys.argv)

    menu = QtGui.QMenu('test')
    font = menu.font()
    icon = QtGui.QIcon(QtGui.QPixmap(10,20))
    trayicon = QtGui.QSystemTrayIcon(icon)
    trayicon.setContextMenu(menu)
    trayicon.show()

    print trayicon.geometry()

    pm = QtGui.QPixmap(trayicon.geometry().size())
    painter = QtGui.QPainter()
    painter.begin(pm)
    font.setPixelSize(pm.height())
    painter.setFont(font)
    
    print painter.font()
    painter.fillRect(0,0,pm.width(),pm.height(),QtCore.Qt.red)
    painter.drawText(0, pm.height(), "Test")
    painter.end()
    trayicon.setIcon(QtGui.QIcon(pm))

    task_list = TaskList()
    task_list.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    task_list.menuBar().addMenu(menu)
    
#     trayicon.showMessage('test', 'test message')
    #w = TaskList()
#     w = QtGui.QWidget()
    #w.show()
    task_list.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    run()

