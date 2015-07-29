import Tkinter as tk
import ttk
import tkMessageBox
import sys
import datetime
import threading
from event_hook import EventHook
from logging import getLogger
# from settings import AppSettings
from models import Task, NO_TASK

LOGGER = getLogger(__name__)

class TimerSettings(object):
    TASK_TIME = 1
    TASK_EXTENSION = 10
    INACTIVE_TIME = 1
    BREAK_TIME = 1
    BREAK_EXTENSION = 20
SETTINGS = TimerSettings()


class TimerState():
    STOPPED = 0
    RUNNING = 1
    ON_BREAK = 2
    

class TaskTimer(tk.Frame):
    
    started_event = EventHook() # (Task)
    stopped_event = EventHook() # (Task, datetime.datetime, datetime.datetime)
    
    state = None
    timeToGo = None
    timeToGoVar = None
    
    breakPromptWidget = None
    breakDoneWidget = None
    
    canContinue = False
    needsBreak = False
    task = NO_TASK
    
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        self.initUI()
        self.initTimers()
        self.updateUI()
    
    def setTimeToGo(self, minutes):
        self.timeToGo = datetime.timedelta(minutes=minutes)
        self.progressBar['maximum'] = minutes*60
    
    def initTimers(self):
        self.setTimeToGo(SETTINGS.TASK_TIME)
        
        self.inactivityTimer = threading.Timer(SETTINGS.INACTIVE_TIME, self.inactiveUser)
    
    def promptForBreak(self):
        if tkMessageBox.askyesno('Break Time', 'Ready for a break?'):
            self.startBreak()
        else:
            self.extendTask()
    
    def promptForBreakDone(self):
        if not tkMessageBox.askyesno('Break Done', 'Ready for more work?'):
            self.extendBreak()    

    def initUI(self):
        self.taskLabelVar = tk.StringVar()
        self.taskLabel = tk.Label(self, textvariable=self.taskLabelVar)
        self.taskLabel.pack()
        self.timeLabelVar = tk.StringVar()
        self.timeLabel = tk.Label(self, textvariable=self.timeLabelVar)
        self.timeLabel.pack()
        self.progressBarVar = tk.IntVar()
        self.progressBar = ttk.Progressbar(self, variable=self.progressBarVar)
        self.progressBar.pack()

        #self.displayMessage = QtGui.QLabel("", self)
        #self.displayMessage.hide()
        #sublayout.addWidget(self.displayMessage)

    def updateUI(self):
        self.showTimeToGo()

    def isRunning(self):
        return self.state == TimerState.RUNNING

    def isOnBreak(self):
        return self.state == TimerState.ON_BREAK
    
    def isStopped(self):
        return self.state == TimerState.STOPPED
    
    def startBreak(self, extended=False):
        if extended:
            minutes = SETTINGS.BREAK_EXTENSION
        else:
            minutes = SETTINGS.BREAK_TIME
        self.stop()
        self.setState(TimerState.ON_BREAK)
        self.needsBreak = False
        self.taskLabel.text = "On break"
        self.setTimeToGo(minutes)
        self.endTime = datetime.datetime.now() + self.timeToGo
        self.tick()
    
    def extendBreak(self):
        self.startBreak(extended=True)
    
    def extendTask(self):
        """ Add additional task time """
        self.start(extended=True)
    
    def hasTask(self):
        return self.task != NO_TASK

    def setState(self, state):
        if state == self.state:
            return
        self.state = state
    
    def showTimeToGo(self):
        # When clock reaches 0, time may go negative
        if self.timeToGo.days < 0:
            seconds = 0
        else:
            seconds = self.timeToGo.seconds
        # Round up number of seconds
        if self.timeToGo.microseconds:
            seconds += 1
        self.progressBarVar.set(seconds)
        hours = seconds / 3600
        minutes = (seconds / 60) % 60
        seconds = seconds % 60
        if hours:
            display = "%d:%02d" % (hours, minutes)
        else:
            display = "%d" % minutes
        display += ":%02d" % seconds
        self.timeLabelVar.set(display)

    def tick(self):
        now = datetime.datetime.now()
        self.timeToGo = self.endTime - now
        self.showTimeToGo()
        if now > self.endTime:
            self.timeUp()
        else:
            self.after(100, self.tick)
    
    def setTask(self, task):
        if task == self.task:
            if not self.isRunning():
                self.start()
            return
        else:
            if self.isRunning():
                self.stop()
            self.task = task
            self.taskLabelVar.set(str(self.task))
            self.canContinue = False
            self.updateUI()
            self.start()

    def timeUp(self):
        if self.isRunning():
            LOGGER.info("Start break")
            self.promptForBreak()
            self.needsBreak = True
        elif self.isOnBreak():
            LOGGER.info("Break over")
            self.promptForBreakDone()
            self.needsBreak = False
        self.stop()
        
    def inactiveUser(self):
        LOGGER.info("Inactivity!")
        if self.isStopped():
            tkMessageBox.showinfo("Inactivity", "Still there?")
    
    def activity(self):
        LOGGER.info("Activity!")
        self.after_cancel(self.inactivityTimer)
        self.inactivityTimer = self.after(SETTINGS.INACTIVE_TIME, self.inactiveUser)

    def start(self, extended=False):
        self.activity()
        if self.isRunning():
            return
        self.startTime = datetime.datetime.now()
        if extended:
            self.setTimeToGo(SETTINGS.TASK_EXTENSION)
        else:
            self.setTimeToGo(SETTINGS.TASK_TIME)
        self.endTime = self.startTime + self.timeToGo
        self.setState(TimerState.RUNNING)
        self.taskLabelVar.set(str(self.task))
        self.started_event.fire(self.task)
        self.tick()
    
    def stop(self):
        self.activity()
        # self.timer.cancel()
        self.endTime = datetime.datetime.now()
        if self.isRunning():
            self.stopped_event.fire(self.task, self.startTime, self.endTime)
            self.canContinue = True
        self.setState(TimerState.STOPPED)
        self.updateUI()

def run():
    root = tk.Tk()
    t = TaskTimer(root)
    t.pack()
    t.setTimeToGo(30)
    t.start()
    # def onTaskNeeded():
    #     w.setTask(Task("Some task"))
    # w.taskNeeded.connect(onTaskNeeded)
    # def onStart(task):
    #     LOGGER.info("Started %s" % task)
    # w.started.connect(onStart)
    # def onStop(task):
    #     LOGGER.info("Stopped %s" % task)
    # w.stopped.connect(onStop)
    # w.show()
    
    root.mainloop()

if __name__ == '__main__':
    run()


        