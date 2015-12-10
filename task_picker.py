#!/usr/bin/env pythonw

from PyQt4 import QtGui, QtCore
import sys
import requests
import json
from models import Task, NO_TASK
# from settings import AppSettings
from socket import gethostname

class TaskPickerSettings(object):
    if 'honu' in gethostname().lower():
        BASE_URL = 'http://dmscode.iris.washington.edu/'
    else:
        BASE_URL = 'http://localhost/'
    USER = 3
    ISSUES_URL =  '%s/issues.json?key=fb0ace80aa4ed5d8c113d5ecba70d6509b318837&assigned_to_id=me&sort=updated_on:desc&status_id=open&limit=200'
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
        # kwargs['type'] = self.itemType
        super(BasePickerItem, self).__init__(*args, **kwargs)
        self.init()
    def init(self):
        self.setText(0, self.get_label())
    def get_task(self):
        if not self.task:
            kwargs = self.get_task_kwargs()
            (self.task, _) = Task.get_or_create(**kwargs)
        return self.task
    def get_task_kwargs(self):
        raise NotImplementedError
    def get_label(self):
        raise NotImplementedError
    def get_uid(self):
        return self.get_task().get_uid()
    def __str__(self):
        return str(self.get_task())
    

class ProjectItem(BasePickerItem):
    itemType = BasePickerItem.itemType + 1
    name = None
    def get_task_kwargs(self):
        return dict(
            project=self.name,
            name='',
            source=self.source
        )
    def get_label(self):
        return self.name


class IssueItem(BasePickerItem):
    itemType = ProjectItem.itemType + 1
    title = None
    project = None
    issue_id = None
    link_url = None

    def init(self):
        assert(self.title)
        assert(self.project)
        super(IssueItem, self).init()

    def get_label(self):
        if self.issue_id:
            return "#%s %s" % (self.issue_id, self.title)
        else:
            return self.title

    def get_task_kwargs(self):
        return dict(
            project=self.project,
            name=self.title,
            source=self.source,
            issue_id=self.issue_id
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
        self.issue_id = self.issue.get('id')
        # link = SETTINGS.ISSUE_URL % (SETTINGS.BASE_URL, self.issue_id)
        self.title = self.issue.get('subject')
        self.project = self.issue.get('project').get('name')
        super(RedmineIssueItem, self).init()


class TaskPicker(QtCore.QObject):

    picked = QtCore.pyqtSignal(Task)

    pickedTask = NO_TASK
    savedGeometry = None
    projects = None
    uids = None
    list = None

    def __init__(self, app, treeWidget):
        super(TaskPicker, self).__init__()
        self.app = app
        self.treeWidget = treeWidget
        self.initWidgets()

    def initWidgets(self):
#         main_widget = QtGui.QWidget(self)
#         self.map = BasemapWidget(main_widget)
#         self.waveforms = MPLWidget(main_widget)
        # self.list = ttk.Treeview(self)
        # self.list.pack()
        # self.list.heading('#0', text='Task')
        # self.list.setHeaderItem(QtGui.QTreeWidgetItem([ 'Id', 'Project', 'Title' ]))
        # self.treeWidget.setHeaderLabels([ 'Id', 'Title' ])
        #self.list.bind('<<TreeviewSelect>>', self.onItemSelected)
        #self.list.bind('<Double-Button>', self.onItemPicked)
        self.treeWidget.itemClicked.connect(self.onItemClick)
        # self.treeWidget.doubleClicked.connect(self.onPicked)

    def fetchTasks(self):
        self.treeWidget.clear()
        self.projects = {}
        self.uids = {}
        self.fetchLocalTasks()
        self.fetchRedmineTasks()

    def addProject(self, project):
        self.projects[project.name] = project
        self.uids[project.get_uid()] = project
        self.treeWidget.addTopLevelItem(project)
        # self.list.insert('', 'end', uid=project.get_uid(), text=project.get_label())
        return project

    def addItem(self, item):
        project = self.projects.get(item.project)
        if not project:
            project = self.addProject(ProjectItem(name=item.project))
        self.uids[item.get_uid()] = item
        project.addChild(item)
        # self.list.insert(project.get_uid(), 'end', uid=item.get_uid(), text=item.get_label())

    def fetchLocalTasks(self):
        tasks = Task.select().where(Task.source==LocalIssueItem.source)
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
            r = requests.get(SETTINGS.ISSUES_URL % SETTINGS.BASE_URL)
            if r.ok:
                j = r.json()
        for issue in j.get('issues'):
            self.addItem(RedmineIssueItem(issue=issue))

    def selectTask(self, task_uid):
        print "Looking for %s" % task_uid
        item = self.uids.get(task_uid)
        if item:
            print "Found item"
            self.treeWidget.setCurrentItem(item)
            self.picked.emit(item.get_task())

    def onItemClick(self, item):
        # self.pickedTask = self.uids[self.list.focus()].task
        self.picked.emit(item.get_task())


def run():
    root = tk.Tk()
    w = TaskPicker(root)
    w.pack()
    w.fetchTasks()
    root.mainloop()

if __name__ == '__main__':
    run()

