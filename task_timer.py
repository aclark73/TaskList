from PyQt4 import QtGui, QtCore
import sys
import datetime
from logging import getLogger
from settings import AppSettings
from models import Task, NO_TASK

LOGGER = getLogger(__name__)

class TimerSettings(AppSettings):
    TASK_TIME = 30
    TASK_EXTENSION = 10
    INACTIVE_TIME = 1
    BREAK_TIME = 1
    BREAK_EXTENSION = 20
SETTINGS = TimerSettings()


class TimerState():
    STOPPED = 0
    RUNNING = 1
    ON_BREAK = 2
    

class TaskTimer(QtCore.QObject):
    
    started = QtCore.pyqtSignal(Task)
    stopped = QtCore.pyqtSignal(Task, datetime.datetime, datetime.datetime)
    taskNeeded = QtCore.pyqtSignal()
    
    state = None
    
    breakPromptWidget = None
    breakDoneWidget = None
    
    canContinue = False
    needsBreak = False
    task = NO_TASK
    
    def __init__(self, app, timeLabel, progressBar):
        super(TaskTimer, self).__init__()
        self.app = app
        self.initUI(timeLabel, progressBar)
        self.initTimers()
        self.updateUI()
    
    def setTimeToGo(self, minutes):
        self.timeToGo = datetime.timedelta(minutes=minutes)
        self.progressBar.setMaximum(minutes*60)
    
    def initTimers(self):
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.tick)
        self.setTimeToGo(SETTINGS.TASK_TIME)
        
        self.inactivityTimer = QtCore.QTimer()
        self.inactivityTimer.setInterval(SETTINGS.INACTIVE_TIME*60*1000)
        self.inactivityTimer.timeout.connect(self.inactiveUser)
    
    def promptForBreak(self):
        if not self.breakPromptWidget:
            w = QtGui.QMessageBox(self.app)
            w.setWindowTitle('Break Time')
            w.setText("Ready for a break?")
            startButton = w.addButton("Ok", QtGui.QMessageBox.YesRole)
            startButton.clicked.connect(self.startBreak)
            snoozeButton = w.addButton("Almost done", QtGui.QMessageBox.NoRole)
            snoozeButton.clicked.connect(self.extendTask)
            self.breakPromptWidget = w
        self.breakPromptWidget.show()
    
    def promptForBreakDone(self):
        if not self.breakDoneWidget:
            w = QtGui.QMessageBox(self.app)
            w.setWindowTitle('Break Done')
            w.setText("Ready for more work?")
            _startButton = w.addButton("Ok", QtGui.QMessageBox.YesRole)
            snoozeButton = w.addButton("Extended break", QtGui.QMessageBox.NoRole)
            snoozeButton.clicked.connect(self.extendBreak)
            self.breakDoneWidget = w
        self.breakDoneWidget.show()
    

    def initUI(self, timeLabel, progressBar):
        self.timeLabel = timeLabel
        self.progressBar = progressBar

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
        self.setTimeToGo(minutes)
        self.endTime = datetime.datetime.now() + self.timeToGo
        self.timer.start()
        self.updateUI()
    
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
        self.progressBar.setValue(seconds)
        hours = seconds / 3600
        minutes = (seconds / 60) % 60
        seconds = seconds % 60
        if hours:
            display = "%d:%02d" % (hours, minutes)
        else:
            display = "%d" % minutes
        display += ":%02d" % seconds
        self.timeLabel.setText(display)

    def tick(self):
        now = datetime.datetime.now()
        self.timeToGo = self.endTime - now
        self.showTimeToGo()
        if now > self.endTime:
            self.timeUp()
    
    def setTask(self, task):
        if task.get_uid() == self.task.get_uid():
            if not self.isRunning():
                self.start()
            return
        else:
            if self.isRunning():
                self.stop()
            self.task = task
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
        self.inactivityTimer.stop()
        if self.isStopped():
            messageBox = QtGui.QMessageBox(self.app)
            messageBox.setText("Still there?")
            messageBox.exec_()
            self.inactivityTimer.start()
    
    def activity(self):
        LOGGER.info("Activity!")
        self.inactivityTimer.start()

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
        self.started.emit(self.task)
        self.timer.start()
        self.updateUI()
    
    def stop(self):
        self.activity()
        self.timer.stop()
        self.endTime = datetime.datetime.now()
        if self.isRunning():
            self.stopped.emit(self.task, self.startTime, self.endTime)
            self.canContinue = True
        self.setState(TimerState.STOPPED)
        self.updateUI()

    def pick(self):
        self.activity()
        self.taskNeeded.emit()
    
def run():
    app = QtGui.QApplication(sys.argv)
    w = TimerWidget()
    
    def onTaskNeeded():
        w.setTask(Task("Some task"))
    w.taskNeeded.connect(onTaskNeeded)
    def onStart(task):
        LOGGER.info("Started %s" % task)
    w.started.connect(onStart)
    def onStop(task):
        LOGGER.info("Stopped %s" % task)
    w.stopped.connect(onStop)
    w.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    run()


        