from PyQt4 import QtGui, QtCore
import sys
import datetime
from enable.savage.compliance.svg_component import now

class TimerWidget(QtGui.QWidget):
    
    started = QtCore.pyqtSignal()
    stopped = QtCore.pyqtSignal()
    needsPick = QtCore.pyqtSignal()
    
    def __init__(self, *args, **kwargs):
        super(TimerWidget, self).__init__(*args, **kwargs)
        self.initTimer()
        self.initUI()
    
    def initTimer(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.tick)
        self.startTime = datetime.datetime.now()
        self.endTime = self.startTime + datetime.timedelta(minutes=30)
        self.timer.start(1000)
    
    def tick(self):
        now = datetime.datetime.now()
        if now > self.endTime:
            self.end()
        else:
            timeToGo = self.endTime - now
            hours = timeToGo.seconds / 3600
            minutes = (timeToGo.seconds / 60) % 60
            seconds = timeToGo.seconds % 60
            if hours:
                display = "%d:%02d" % (hours, minutes)
            else:
                display = "%d" % minutes
            display += ":%02d" % seconds
            
            
    
    def initUI(self):
        layout = QtGui.QVBoxLayout()

        self.statusPanel = QtGui.QLabel("--")
        layout.addWidget(self.statusPanel)
        
        button_layout = QtGui.QHBoxLayout()

        self.startButton = QtGui.QPushButton('Start')
        self.startButton.clicked.connect(self.start)
        button_layout.addWidget(self.startButton)
        
        self.stopButton = QtGui.QPushButton('Stop')
        self.stopButton.clicked.connect(self.stop)
        button_layout.addWidget(self.stopButton)
        
        self.pickButton = QtGui.QPushButton('Pick')
        self.pickButton.clicked.connect(self.pick)
        button_layout.addWidget(self.pickButton)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def setTask(self, task):
        self.statusPanel.setText(task)

    def start(self):
        self.started.emit()
    
    def stop(self):
        self.stopped.emit()
    
    def pick(self):
        self.needsPick.emit()
    
def run():
    app = QtGui.QApplication(sys.argv)
    w = TimerWidget()
    
    def on_start():
        print("Started")
    w.started.connect(on_start)
    def on_stop():
        print("Stopped")
    w.stopped.connect(on_stop)
    w.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    run()


        