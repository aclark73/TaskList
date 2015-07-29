#!/usr/bin/env pythonw

import Tkinter as tk
import ttk
import sys
import requests
import subprocess
from task_timer import TaskTimer
from task_picker import TaskPicker
from logging import getLogger
from models import TaskLog

class TaskListSettings(object):
    GEOMETRY = None
SETTINGS = TaskListSettings()
    
LOGGER = getLogger(__name__)

class TaskList(tk.Frame):

    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.initUI()
        if SETTINGS.GEOMETRY:
            self.setGeometry(SETTINGS.GEOMETRY.toRect())
        
    def initUI(self):
        self.timerWidget = TaskTimer(self)
        self.pickerWidget = TaskPicker(self)

        f = tk.Frame(self)
        self.startButton = ttk.Button(f, text='Start', command=self.timerWidget.start)
        self.stopButton = ttk.Button(f, text='Stop', command=self.timerWidget.stop)
        self.loadPicksButton = ttk.Button(f, text='Load Tasks', command=self.pickerWidget.fetchTasks)
        self.startButton.pack(side=tk.LEFT)
        self.stopButton.pack(side=tk.LEFT)
        self.loadPicksButton.pack(side=tk.LEFT)

        self.timerWidget.pack()
        self.pickerWidget.pack()
        f.pack()

        self.pickerWidget.picked_event.add(self.onTaskPicked)
        self.timerWidget.stopped_event.add(self.onTaskStopped)

        self.timerWidget.updateUI()
        
    def showPicker(self):
        # self.pickerWidget.show()
        pass
    
    def onTaskPicked(self, task=None):
        self.timerWidget.setTask(task)

    def onTaskStopped(self, task=None, startTime=None, endTime=None):
        log = TaskLog.log(task, startTime, endTime)
        print(log)

    def closeEvent(self, *args, **kwargs):
        SETTINGS.GEOMETRY = self.geometry()
        super(TaskList, self).closeEvent(*args, **kwargs)


def run():
    root = tk.Tk()
    t = TaskList(root)
    t.pack()
    root.mainloop()

if __name__ == '__main__':
    run()

