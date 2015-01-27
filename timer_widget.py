from PyQt4 import QtGui, QtCore
import sys
import datetime
from logging import getLogger

LOGGER = getLogger(__name__)
    
class Preferences(object):
    timeToGo = datetime.timedelta(seconds=4)
    inactivityTime = datetime.timedelta(seconds=2)
    breakTime = datetime.timedelta(seconds=5)
    
PREFS = Preferences()


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
    stopped = QtCore.pyqtSignal(Task)
    needsPick = QtCore.pyqtSignal()
    state = None
    
    canContinue = False
    needsBreak = False
    task = NO_TASK
    
    def __init__(self, *args, **kwargs):
        super(TimerWidget, self).__init__(*args, **kwargs)
        self.initTimers()
        self.initUI()
        self.updateUI()
    
    def initTimers(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.tick)
        self.timeToGo = PREFS.timeToGo
        self.inactivityTimer = QtCore.QTimer()
        self.inactivityTimer.timeout.connect(self.inactiveUser)

    def initUI(self):

        layout = QtGui.QVBoxLayout()

        self.taskLabel = QtGui.QLabel("--", self)
        layout.addWidget(self.taskLabel)
        self.timeLabel = QtGui.QLabel("--", self)
        layout.addWidget(self.timeLabel)
        
        self.displayMessage = QtGui.QLabel("", self)
        self.displayMessage.hide()
        layout.addWidget(self.displayMessage)
        
        toolbar = QtGui.QToolBar(self)
        
        self.startButton = QtGui.QAction(
            # QtGui.QIcon.fromTheme('media-playback-start'),
            QtGui.QIcon('icon.png'), 
            'Start', 
            self)
        self.startButton.triggered.connect(self.start)
        toolbar.addAction(self.startButton)
        
        self.stopButton = QtGui.QAction(
            QtGui.QIcon.fromTheme('media-playback-stop'), 
            'Stop', 
            self)
        self.stopButton.triggered.connect(self.stop)
        toolbar.addAction(self.stopButton)
        
        self.breakButton = QtGui.QAction(
            'Start Break',
            self
        )
        self.breakButton.triggered.connect(self.startBreak)
        toolbar.addAction(self.breakButton)

        icon = QtGui.QIcon.fromTheme('media-eject')
        
        self.pickButton = QtGui.QAction(
            icon, 
            'Change', 
            self)
        self.pickButton.triggered.connect(self.activity)
        self.pickButton.triggered.connect(self.pick)
        toolbar.addAction(self.pickButton)
        
        layout.addWidget(toolbar)
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
    
    def startBreak(self):
        self.stop()
        self.setState(TimerState.ON_BREAK)
        self.needsBreak = False
        self.timeToGo = PREFS.breakTime
        self.endTime = datetime.datetime.now() + self.timeToGo
        self.timer.start(1000)
        self.updateUI()
    
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
            self.needsBreak = True
        elif self.isOnBreak():
            LOGGER.info("Break over")
            self.needsBreak = False
        self.stop()
        
    def inactiveUser(self):
        LOGGER.info("Inactivity!")
        self.inactivityTimer.stop()
        if self.isStopped():
            messageBox = QtGui.QMessageBox(self)
            messageBox.setText("Still there?")
            messageBox.show()
    
    def activity(self):
        LOGGER.info("Activity!")
        self.inactivityTimer.stop()

    def start(self):
        self.activity()
        if self.isRunning():
            return
        self.startTime = datetime.datetime.now()
        self.endTime = self.startTime + self.timeToGo
        self.setState(TimerState.RUNNING)
        self.started.emit(self.task)
        self.timer.start(1000)
        self.updateUI()
    
    def stop(self):
        self.activity()
        self.timer.stop()
        self.endTime = datetime.datetime.now()
        if self.isRunning():
            self.stopped.emit(self.task)
            self.canContinue = True
        self.timeToGo = PREFS.timeToGo
        self.setState(TimerState.STOPPED)
        self.updateUI()
        self.inactivityTimer.start(PREFS.inactivityTime.seconds*1000)

    def pick(self):
        self.activity()
        self.needsPick.emit()
    
def run():
    app = QtGui.QApplication(sys.argv)
    w = TimerWidget()
    
    def onNeedsPick():
        w.setTask(Task("Some task"))
    w.needsPick.connect(onNeedsPick)
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


        