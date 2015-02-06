#!/usr/bin/env pythonw

from PyQt4 import QtGui, QtCore
import sys
import requests
import subprocess
import json
import timer_widget
from timer_widget import Task
from settings import AppSettings

class TaskPickerSettings(AppSettings):
#    BASE_URL = 'http://dmscode.iris.washington.edu/'
    BASE_URL = 'http://localhost/'
    USER = 3
    ISSUES_URL =  '%s/issues.json?assigned_to=%s&sort=updated_on:desc&status_id=open&limit=100'
    ISSUE_URL =  '%s/issues/%s'
    GEOMETRY = None
    
SETTINGS = TaskPickerSettings()


class RedmineProjectItem(QtGui.QTreeWidgetItem):
    itemType = QtGui.QTreeWidgetItem.UserType + 1
    def __init__(self, project, *args, **kwargs):
        self.project = project
        kwargs['type'] = self.itemType
        super(RedmineProjectItem, self).__init__(*args, **kwargs)
        self.setFlags(QtCore.Qt.ItemIsEnabled)
        self.setFirstColumnSpanned(True)
        self.setText(0, self.project)


class RedmineIssueItem(QtGui.QTreeWidgetItem):
    itemType = RedmineProjectItem.itemType + 1
    def __init__(self, issue, *args, **kwargs):
        self.issue = issue
        kwargs['type'] = self.itemType
        super(RedmineIssueItem, self).__init__(*args, **kwargs)
        # self.setText(0, self.issue.get('project').get('name'))
        self.setText(0, "#%s" % self.issue.get('id'))
        self.setText(1, self.issue.get('subject'))
        self.setData(0, QtCore.Qt.ToolTipRole, self.getLink())

    def getLink(self):
        link = SETTINGS.ISSUE_URL % (SETTINGS.BASE_URL, self.issue.get('id'))
        return QtCore.QUrl(link)




class TaskPicker(QtGui.QDialog):

    picked = QtCore.pyqtSignal(Task)
    
    pickedTask = timer_widget.NO_TASK
    savedGeometry = None

    def __init__(self, *args, **kwargs):
        super(TaskPicker, self).__init__(*args, **kwargs)
        self.initWidgets()
        geometry = SETTINGS.GEOMETRY
        if geometry:
            self.setGeometry(geometry.toRect())

    def initWidgets(self):
#         main_widget = QtGui.QWidget(self)
#         self.map = BasemapWidget(main_widget)
#         self.waveforms = MPLWidget(main_widget)
        self.list = QtGui.QTreeWidget(self)
        # self.list.setHeaderItem(QtGui.QTreeWidgetItem([ 'Id', 'Project', 'Title' ]))
        self.list.setHeaderLabels([ 'Id', 'Title' ])
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
        if 'localhost' in SETTINGS.BASE_URL:
            with open('issues.json') as f:
                j = json.load(f)
        else:
            r = requests.get(SETTINGS.ISSUES_URL % (
                SETTINGS.BASE_URL, SETTINGS.USER
            ))
            if r.ok:
                j = r.json()
        self.list.clear()
        self.projects = {}
        self.list.setSortingEnabled(False)
        for issue in j.get('issues'):
            item = RedmineIssueItem(issue)
            project = issue.get('project').get('name')
            project_item = self.projects.get(project)
            if not project_item:
                self.projects[project] = project_item = RedmineProjectItem(project)
                self.list.addTopLevelItem(project_item)
            project_item.addChild(item)
        for column in range(self.list.columnCount()):
            self.list.resizeColumnToContents(column)
        self.list.setSortingEnabled(True)
    
    def onItemClick(self, item, column):
        if isinstance(item, RedmineIssueItem):
            self.pickedTask = Task("%s | %s | %s" % (item.text(0), item.text(1), item.text(2)))
            if column == 0:
                QtGui.QDesktopServices.openUrl(item.getLink())
    
    def onPicked(self):
        self.picked.emit(self.pickedTask)
        self.close()
    
    def closeEvent(self, *args, **kwargs):
        SETTINGS.GEOMETRY = self.geometry()
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

