#!/usr/bin/env pythonw

from PyQt4 import QtGui, QtCore
import sys
import requests
import subprocess
import json
import timer_widget
from timer_widget import Task

REDMINE_URL = 'http://localhost/'
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

class TaskPicker(QtGui.QDialog):

    picked = QtCore.pyqtSignal(Task)
    
    pickedTask = timer_widget.NO_TASK
    savedGeometry = None

    def __init__(self, *args, **kwargs):
        super(TaskPicker, self).__init__(*args, **kwargs)
        self.initWidgets()
        if self.savedGeometry:
            self.setGeometry(self.savedGeometry)

    def initWidgets(self):
#         main_widget = QtGui.QWidget(self)
#         self.map = BasemapWidget(main_widget)
#         self.waveforms = MPLWidget(main_widget)
        self.list = QtGui.QTreeWidget(self)
        self.list.setHeaderLabels([ 'Id', 'Project', 'Title' ])
        self.list.itemClicked.connect(self.onItemClick)
        self.list.doubleClicked.connect(self.onPicked)

        self.fetchButton = QtGui.QPushButton('Fetch')
        self.fetchButton.clicked.connect(self.fetchTasks)
        self.okButton = QtGui.QPushButton('Ok')
        self.okButton.clicked.connect(self.onPicked)
        

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.list)
        button_layout = QtGui.QHBoxLayout()
        button_layout.addWidget(self.fetchButton)
        button_layout.addWidget(self.okButton)
        layout.addLayout(button_layout)
        self.setLayout(layout)

        # self.fetchTasks()
#         self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
#         self.show()

    def fetchTasks(self):
        if 'localhost' in REDMINE_URL:
            with open('issues.json') as f:
                j = json.load(f)
        else:
            r = requests.get(ISSUES_URL)
            if r.ok:
                j = r.json()
        self.list.clear()
        for issue in j.get('issues'):
            link = ISSUE_URL % issue.get('id')
            item = QtGui.QTreeWidgetItem(self.list, [ "#%s" % issue.get('id'), issue.get('project').get('name'), issue.get('subject') ])
            item.setData(0, QtCore.Qt.ToolTipRole, QtCore.QUrl(link))
        for column in range(self.list.columnCount()):
            self.list.resizeColumnToContents(column)
        if not self.savedGeometry:
            self.adjustSize()
    
    def onItemClick(self, item, column):
        self.pickedTask = Task("%s | %s" % (item.text(1), item.text(2)))
        if column == 0:
            url = item.data(0, QtCore.Qt.ToolTipRole)
            QtGui.QDesktopServices.openUrl(url)
    
    def onPicked(self):
        self.picked.emit(self.pickedTask)
        self.close()
    
    def closeEvent(self, *args, **kwargs):
        self.savedGeometry = self.geometry()
        super(TaskPicker, self).closeEvent(*args, **kwargs)
        

def run():
    app = QtGui.QApplication(sys.argv)

#     trayicon.showMessage('test', 'test message')
    w = TaskPicker()
    
    def on_ok(label):
        print(label)
    w.picked.connect(on_ok)
#     w = QtGui.QWidget()
    w.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    run()

