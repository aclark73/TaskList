#!/usr/bin/env pythonw

from PyQt4 import QtGui, QtCore
import sys
import requests
import json
from models import Task, NO_TASK
# from settings import AppSettings
from socket import gethostname

from task_source.local import LocalSource
from task_source.redmine import RedmineSource

SOURCES = [LocalSource(), RedmineSource()]

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

class PickerItem(QtGui.QTreeWidgetItem):
    itemType = QtGui.QTreeWidgetItem.UserType
    task = None
    def __init__(self, task):
        assert(task)
        super(PickerItem, self).__init__()
        self.task = task
        self.setText(0, self.task.get_label())
    def get_uid(self):
        return self.task.get_uid()
    def __str__(self):
        return str(self.task)
    

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
        for source in SOURCES:
            for task in source.fetch():
                self.addTask(task)

    def addTask(self, task):
        print 'Adding task "%s"' % task.get_uid()
        item = PickerItem(task)
        self.uids[task.get_uid()] = item
        if task.is_project():
            self.projects[task.project] = item
            self.treeWidget.addTopLevelItem(item)
        else:
            project = self.getOrCreateProject(task.project, source=task.source)
            project.addChild(item)
        return item

    def getOrCreateProject(self, project, **kwargs):
        if project in self.projects:
            return self.projects[project]
        else:
            (task, _) = Task.get_or_create(
                project=project, title=None, defaults=kwargs)
            return self.addTask(task)

    def selectTask(self, task_uid):
        # print "Looking for %s in [%s]" % (task_uid, ','.join(self.uids.keys()))
        task_uid = str(task_uid)
        current_item = self.treeWidget.currentItem()
        if current_item:
            current_uid = str(current_item.task.get_uid())
        else:
            current_uid = ''
        # print "Looking for %s, current task is %s" % (task_uid, current_uid)
        if task_uid != current_uid:
            item = self.uids.get(task_uid)
            if item:
                # print "Found item"
                self.treeWidget.setCurrentItem(item)
                self.picked.emit(item.task)

    def onItemClick(self, item):
        # self.pickedTask = self.uids[self.list.focus()].task
        self.pickedTask = item.task
        self.picked.emit(self.pickedTask)


def run():
    root = tk.Tk()
    w = TaskPicker(root)
    w.pack()
    w.fetchTasks()
    root.mainloop()

if __name__ == '__main__':
    run()

