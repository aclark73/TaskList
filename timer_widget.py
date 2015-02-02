from PyQt4 import QtGui, QtCore
import sys
import datetime
from logging import getLogger
from settings import AppSettings

LOGGER = getLogger(__name__)

class TimerSettings(AppSettings):
    TASK_TIME = 29
    TASK_EXTENSION = 5
    INACTIVE_TIME = 1
    BREAK_TIME = 1
    BREAK_EXTENSION = 10
SETTINGS = TimerSettings()


class TimerState():
    STOPPED = 0
    RUNNING = 1
    ON_BREAK = 2
    

class Task(object):
    def __init__(self, s):
        self.s = s
    def __str__(self):
        return self.s

NO_TASK = Task("None")


class TimerWidget(QtGui.QWidget):
    
    started = QtCore.pyqtSignal(Task)
    stopped = QtCore.pyqtSignal(Task, datetime.datetime, datetime.datetime)
    taskNeeded = QtCore.pyqtSignal()
    
    state = None
    
    breakPromptWidget = None
    breakDoneWidget = None
    
    canContinue = False
    needsBreak = False
    task = NO_TASK
    
    def __init__(self, *args, **kwargs):
        super(TimerWidget, self).__init__(*args, **kwargs)
        self.initTimers()
        self.initUI()
        self.updateUI()
    
    def initTimers(self):
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.tick)
        self.timeToGo = datetime.timedelta(seconds=SETTINGS.TASK_TIME)
        
        self.inactivityTimer = QtCore.QTimer(self)
        self.inactivityTimer.setInterval(SETTINGS.INACTIVE_TIME*60*1000)
        self.inactivityTimer.timeout.connect(self.inactiveUser)
    
    def promptForBreak(self):
        if not self.breakPromptWidget:
            w = QtGui.QMessageBox(self)
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
            w = QtGui.QMessageBox(self)
            w.setWindowTitle('Break Done')
            w.setText("Ready for more work?")
            _startButton = w.addButton("Ok", QtGui.QMessageBox.YesRole)
            snoozeButton = w.addButton("Extended break", QtGui.QMessageBox.NoRole)
            snoozeButton.clicked.connect(self.extendBreak)
            self.breakDoneWidget = w
        self.breakDoneWidget.show()
    

    def initUI(self):

        layout = QtGui.QVBoxLayout()

        self.taskLabel = QtGui.QLabel("--", self)
        layout.addWidget(self.taskLabel)
        
        sublayout = QtGui.QHBoxLayout()
        self.timeLabel = QtGui.QLabel("--", self)
        font = self.timeLabel.font()
        font.setPointSize(24)
        self.timeLabel.setFont(font)
        sublayout.addWidget(self.timeLabel)
        
        self.displayMessage = QtGui.QLabel("", self)
        self.displayMessage.hide()
        sublayout.addWidget(self.displayMessage)
        
        layout.addLayout(sublayout)
        
        toolbar = QtGui.QToolBar(self)
        
        self.startButton = QtGui.QAction(
            self.style().standardIcon(QtGui.QStyle.SP_MediaPlay),
            'Start', 
            self)
        self.startButton.triggered.connect(self.start)
        toolbar.addAction(self.startButton)
        
        self.stopButton = QtGui.QAction(
            self.style().standardIcon(QtGui.QStyle.SP_MediaStop),
            # QtGui.QIcon.fromTheme('media-playback-stop'), 
            'Stop', 
            self)
        self.stopButton.triggered.connect(self.stop)
        toolbar.addAction(self.stopButton)
        
        self.breakButton = QtGui.QAction(
            self.style().standardIcon(QtGui.QStyle.SP_MediaPause),
            'Start Break',
            self
        )
        self.breakButton.triggered.connect(self.startBreak)
        toolbar.addAction(self.breakButton)

        self.pickButton = QtGui.QAction(
            self.style().standardIcon(QtGui.QStyle.SP_DirOpenIcon),
            'Change', 
            self)
        self.pickButton.triggered.connect(self.pick)
        toolbar.addAction(self.pickButton)
        
        # layout.addWidget(toolbar)
        self.toolbar = toolbar
        self.setLayout(layout)

    def updateUI(self):
        self.pickButton.setText(
            "Change" if self.hasTask()
            else "Pick"
        )
        self.startButton.setText(
            "Continue" if self.canContinue
            else "Start"
        )
        if self.isOnBreak():
            self.displayMessage.setText("On break")
            self.displayMessage.setVisible(True)
        elif self.needsBreak:
            self.displayMessage.setText("You need a break!")
            self.displayMessage.setVisible(True)
        else:
            self.displayMessage.setVisible(False)
        self.startButton.setDisabled(
            self.isRunning() or not self.hasTask() 
            or self.isOnBreak() or self.needsBreak)
        self.stopButton.setDisabled(
            not self.isRunning())
        self.breakButton.setDisabled(
            not self.isRunning() and not self.needsBreak)
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
        self.timeToGo = datetime.timedelta(minutes=minutes)
        self.endTime = datetime.datetime.now() + self.timeToGo
        self.timer.start()
        self.updateUI()
    
    def extendBreak(self):
        self.startBreak(extended=True)
    
    def extendTask(self):
        """ Add additional task time """
        self.timeToGo = datetime.timedelta(seconds=SETTINGS.TASK_EXTENSION)
        self.start()
    
    def hasTask(self):
        return self.task != NO_TASK

    def setState(self, state):
        if state == self.state:
            return
        self.state = state
    
    def showTimeToGo(self):
        seconds = self.timeToGo.seconds
        # Round up number of seconds
        if self.timeToGo.microseconds:
            seconds += 1
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
        if now > self.endTime:
            self.timeUp()
        else:
            self.timeToGo = self.endTime - now
            self.showTimeToGo()
    
    def setTask(self, task):
        if task == self.task:
            return
        if self.isRunning():
            self.stop()
            wasRunning = True
        else:
            wasRunning = False
        self.task = task
        self.taskLabel.setText(str(task))
        self.canContinue = False
        self.updateUI()
        if wasRunning:
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
            messageBox = QtGui.QMessageBox(self)
            messageBox.setText("Still there?")
            messageBox.exec_()
            self.inactivityTimer.start()
    
    def activity(self):
        LOGGER.info("Activity!")
        self.inactivityTimer.start()

    def start(self):
        self.activity()
        if self.isRunning():
            return
        self.startTime = datetime.datetime.now()
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
        self.timeToGo = datetime.timedelta(minutes=SETTINGS.TASK_TIME)
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


        