#!/usr/bin/env pythonw

from PyQt4 import QtGui, QtCore
import sys
import requests
import json
from models import Task, NO_TASK
from settings import AppSettings
from socket import gethostname

class TaskPickerSettings(AppSettings):
    if 'honu' in gethostname():
        BASE_URL = 'http://dmscode.iris.washington.edu/'
    else:
        BASE_URL = 'http://localhost/'
    USER = 3
    ISSUES_URL =  '%s/issues.json?assigned_to_id=%s&sort=updated_on:desc&status_id=open&limit=200'
    ISSUE_URL =  '%s/issues/%s'
    GEOMETRY = None
    
SETTINGS = TaskPickerSettings()

class BasePickerItem(QtGui.QTreeWidgetItem):
    itemType = QtGui.QTreeWidgetItem.UserType
    source = ''
    task = None
    def __init__(self, *args, **kwargs):
        for k in kwargs.keys():
            if hasattr(self, k) and getattr(self, k) is None:
                setattr(self, k, kwargs.pop(k))
        kwargs['type'] = self.itemType
        super(BasePickerItem, self).__init__(*args, **kwargs)
        self.init()
    def init(self):
        pass
    def get_task(self):
        if not self.task:
            kwargs = self.get_task_kwargs()
            self.task = Task.get_or_create(**kwargs)
        return self.task
    def get_task_kwargs(self):
        raise NotImplementedError

class ProjectItem(BasePickerItem):
    itemType = BasePickerItem.itemType + 1
    name = None
    def init(self):
        self.setFirstColumnSpanned(True)
        self.setText(0, self.name)
    def get_task_kwargs(self):
        return dict(
            project=self.name,
            name='',
            source=self.source
        )

class IssueItem(BasePickerItem):
    itemType = ProjectItem.itemType + 1
    title = None
    project = None
    link_label = None
    link_url = None
    
    def init(self):
        assert(self.title)
        assert(self.project)
        if self.link_label:
            self.setText(0, self.link_label)
            if self.link_url:
                self.setData(0, QtCore.Qt.ToolTipRole, self.link_url)
        self.setText(1, self.title)

    def get_task_kwargs(self):
        return dict(
            project=self.project, 
            name=self.title,
            source=self.source,
        )

class LocalProjectItem(ProjectItem):
    def init(self):
        assert(self.task)
        self.name = self.task.project
        super(LocalProjectItem, self).init()

class RedmineProjectItem(ProjectItem):
    pass

class LocalIssueItem(IssueItem):
    def init(self):
        assert(self.task)
        self.title = self.task.name
        self.project = self.task.project
        super(LocalIssueItem, self).init()

class RedmineIssueItem(IssueItem):
    source = 'redmine'
    issue = None
    def init(self):
        assert(self.issue)
        issue_id = self.issue.get('id')
        self.link_label = "#%s" % issue_id
        link = SETTINGS.ISSUE_URL % (SETTINGS.BASE_URL, issue_id)
        self.link_url = QtCore.QUrl(link)
        self.title = self.issue.get('subject')
        self.project = self.issue.get('project').get('name')
        super(RedmineIssueItem, self).init()
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
    
    pickedTask = NO_TASK
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
        self.fetchLocalTasks()
        self.fetchRedmineTasks()
        for column in range(self.list.columnCount()):
            self.list.resizeColumnToContents(column)
        self.list.setSortingEnabled(True)

    def addProject(self, project):
        self.projects[project.name] = project
        self.list.addTopLevelItem(project)
        return project
    
    def addItem(self, item):
        project_item = self.projects.get(item.project)
        if not project_item:
            project_item = self.addProject(ProjectItem(name=item.project))
        project_item.addChild(item)
        
    def fetchLocalTasks(self):
        tasks = Task.query().filter_by(source=LocalIssueItem.source).all()
        for task in tasks:
            if not task.name:
                if task.project not in self.projects:
                    self.addProject(LocalProjectItem(task=task))
            else:
                self.addItem(LocalIssueItem(task=task))
    
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
            self.addItem(RedmineIssueItem(issue=issue))
    
        
    def onItemClick(self, item, column):
        self.pickedTask = item.get_task()
    
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

