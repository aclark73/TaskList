#!/usr/bin/env pythonw

from PyQt4 import QtGui, QtCore
import sys
import requests
import subprocess
from timer_widget import TimerWidget
from task_picker import TaskPicker
from settings import AppSettings
from logging import getLogger
from models import TaskLog

class TaskListSettings(AppSettings):
    GEOMETRY = None
SETTINGS = TaskListSettings()
    
LOGGER = getLogger(__name__)

class TaskList(QtGui.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(TaskList, self).__init__(*args, **kwargs)
        self.initUI()
        if SETTINGS.GEOMETRY:
            self.setGeometry(SETTINGS.GEOMETRY.toRect())
        
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
        self.timerWidget.updateUI()
        
    def showPicker(self):
        self.pickerWidget.show()
    
    def onTaskPicked(self, task):
        self.timerWidget.setTask(task)

    def onTaskStopped(self, task, startTime, endTime):
        log = TaskLog.log(task, startTime, endTime)
        print(log)

    def closeEvent(self, *args, **kwargs):
        SETTINGS.GEOMETRY = self.geometry()
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

