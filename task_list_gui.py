from PyQt4 import QtGui
from task_list_ui import Ui_MainWindow
from task_picker import TaskPicker
from task_timer import TaskTimer
from models import TaskLog
import sys

class TaskListGui(QtGui.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(TaskListGui, self).__init__(*args, **kwargs)
    
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.taskPicker = TaskPicker(self, self.ui.treeWidget)

        self.taskTimer = TaskTimer(self, self.ui.timeLabel, self.ui.taskLabel, self.ui.progressBar)
        self.taskTimer.started.connect(self.onStarted)
        self.taskTimer.stopped.connect(self.onStopped)
    
    def onStarted(self, task):
        self.ui.workButton.setChecked(True)
        self.ui.statusBar.showMessage("Running")

    def onStopped(self, task, start_time, end_time):
        log = TaskLog.log(task, start_time, end_time)
        print(log)
        self.ui.breakButton.setChecked(True)
        self.ui.statusBar.showMessage("Paused")
    
    def taskPicked(self, item):
        self.taskTimer.setTask(item.get_task())
        self.ui.statusBar.showMessage('Task picked')
    
    def refreshTaskPicker(self):
        self.taskPicker.fetchTasks()
        self.ui.statusBar.showMessage("Picking task")
    
    def go(self):
        self.taskTimer.setTask(self.taskPicker.pickedTask)
        self.taskTimer.start()
    
    def pause(self):
        self.taskTimer.startBreak(self.taskTimer.isOnBreak())

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = TaskListGui()
    window.show()
    sys.exit(app.exec_())
