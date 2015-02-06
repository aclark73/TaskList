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
    BASE_URL = 'http://dmscode.iris.washington.edu/'
    # BASE_URL = 'http://localhost/'
    USER = 3
    ISSUES_URL =  '%s/issues.json?assigned_to_id=%s&sort=updated_on:desc&status_id=open&limit=200'
    ISSUE_URL =  '%s/issues/%s'
    GEOMETRY = None
    
SETTINGS = TaskPickerSettings()

class ProjectItem(QtGui.QTreeWidgetItem):
    itemType = QtGui.QTreeWidgetItem.UserType + 1
    def __init__(self, project, *args, **kwargs):
        self.project = project
        kwargs['type'] = self.itemType
        super(ProjectItem, self).__init__(*args, **kwargs)
        # self.setFlags(QtCore.Qt.ItemIsEnabled)
        self.setFirstColumnSpanned(True)
        self.setText(0, self.project)

class IssueItem(QtGui.QTreeWidgetItem):
    itemType = ProjectItem.itemType + 1
    def __init__(self, issue, *args, **kwargs):
        self.issue = issue
        kwargs['type'] = self.itemType
        super(IssueItem, self).__init__(*args, **kwargs)
        self.setText(0, "#%s" % self.getId())
        self.setData(0, QtCore.Qt.ToolTipRole, self.getLink())
        self.setText(1, self.getTitle())

    def getLink(self):
        raise NotImplementedError
    
    def getId(self):
        raise NotImplementedError

    def getTitle(self):
        raise NotImplementedError

    def getProjectName(self):
        raise NotImplementedError

class RedmineProjectItem(ProjectItem):
    pass

class RedmineIssueItem(IssueItem):

    def getId(self):
        return self.issue.get('id')

    def getTitle(self):
        return self.issue.get('subject')

    def getLink(self):
        link = SETTINGS.ISSUE_URL % (SETTINGS.BASE_URL, self.issue.get('id'))
        return QtCore.QUrl(link)

    def getProjectName(self):
        return self.issue.get('project').get('name')

    def __lt__(self, otherItem):
        column = self.treeWidget().sortColumn()
        if column == 0:
            try:
                return int(self.text(column)[1:]) < int(otherItem.text(column)[1:])
            except:
                pass
        return super(RedmineIssueItem, self).__lt__(otherItem)


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
        self.list.clear()
        self.projects = {}
        self.list.setSortingEnabled(False)
        self.fetchRedmineTasks()
        for column in range(self.list.columnCount()):
            self.list.resizeColumnToContents(column)
        self.list.setSortingEnabled(True)
    
    def addTask(self, item):
        project_name = item.getProjectName()
        project_item = self.projects.get(project_name)
        if not project_item:
            project_item = self.projects[project_name] = ProjectItem(project_name)
            self.list.addTopLevelItem(project_item)
        project_item.addChild(item)
        
    
    def fetchRedmineTasks(self):
        if 'localhost' in SETTINGS.BASE_URL:
            with open('issues.json') as f:
                j = json.load(f)
        else:
            r = requests.get(SETTINGS.ISSUES_URL % (
                SETTINGS.BASE_URL, SETTINGS.USER
            ))
            if r.ok:
                j = r.json()
        for issue in j.get('issues'):
            self.addTask(RedmineIssueItem(issue))
    
        
    def onItemClick(self, item, column):
        if isinstance(item, IssueItem):
            project_item = self.projects.get(item.getProject())
            if project_item:
                project_name = project_item.text(0)
            else:
                project_name = "?"
            self.pickedTask = Task("%s | %s | %s" % (project_name, item.text(0), item.text(1)))
            if column == 0:
                QtGui.QDesktopServices.openUrl(item.getLink())
        elif isinstance(item, ProjectItem):
            self.pickedTask = Task("%s" % item.text(0))
    
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

