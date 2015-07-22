#!/usr/bin/env pythonw

import Tkinter as tk
import ttk
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

class BasePickerItem(object):
    source = ''
    task = None
    def __init__(self, *args, **kwargs):
        for k in kwargs.keys():
            if hasattr(self, k) and getattr(self, k) is None:
                setattr(self, k, kwargs.pop(k))
        self.init()
    def init(self):
        pass
    def get_task(self):
        if not self.task:
            kwargs = self.get_task_kwargs()
            (self.task, _) = Task.get_or_create(**kwargs)
        return self.task
    def get_task_kwargs(self):
        raise NotImplementedError
    def get_label(self):
        raise NotImplementedError
    def get_iid(self):
        raise NotImplementedError

class ProjectItem(BasePickerItem):
    name = None
    def get_task_kwargs(self):
        return dict(
            project=self.name,
            name='',
            source=self.source
        )
    def get_label(self):
        return self.name
    def get_iid(self):
        return "P.%s.%s" % (self.source, self.name)

class IssueItem(BasePickerItem):
    title = None
    project = None
    issue_id = None
    link_url = None

    def init(self):
        assert(self.title)
        assert(self.project)

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

    def get_iid(self):
        return "I.%s.%s.%s.%s" % (self.source, self.project, self.issue_id, self.title)

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


class TaskPicker(tk.Frame):

    picked_event = '<<picked>>'

    pickedTask = NO_TASK
    savedGeometry = None
    projects = None
    iids = None
    list = None

    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.initWidgets()

    def initWidgets(self):
#         main_widget = QtGui.QWidget(self)
#         self.map = BasemapWidget(main_widget)
#         self.waveforms = MPLWidget(main_widget)
        self.list = ttk.Treeview(self)
        self.list.pack()
        self.list.heading('#0', text='Task')
        # self.list.setHeaderItem(QtGui.QTreeWidgetItem([ 'Id', 'Project', 'Title' ]))
        # self.list.setHeaderLabels([ 'Id', 'Title' ])
        self.list.bind('<<TreeviewSelect>>', self.onItemSelected)
        self.list.bind('<Double-Button>', self.onItemPicked)
        #self.list.itemClicked.connect(self.onItemClick)
        #self.list.doubleClicked.connect(self.onPicked)

    def fetchTasks(self):
        if self.iids:
            self.list.delete(self.iids.keys())
        self.projects = {}
        self.iids = {}
        self.fetchLocalTasks()
        self.fetchRedmineTasks()

    def addProject(self, project):
        self.projects[project.name] = project
        self.iids[project.get_iid()] = project
        self.list.insert('', 'end', iid=project.get_iid(), text=project.get_label())
        return project

    def addItem(self, item):
        project = self.projects.get(item.project)
        if not project:
            project = self.addProject(ProjectItem(name=item.project))
        self.iids[item.get_iid()] = item
        self.list.insert(project.get_iid(), 'end', iid=item.get_iid(), text=item.get_label())

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


    def onItemSelected(self, ev):
        self.pickedTask = self.iids[self.list.focus()]
        # self.pickedTask = item.get_task()

    def onItemPicked(self, ev):
        self.event_generate(self.picked_event)
        # self.close()


def run():
    root = tk.Tk()
    w = TaskPicker(root)
    w.pack()
    w.fetchTasks()
    root.mainloop()

if __name__ == '__main__':
    run()

