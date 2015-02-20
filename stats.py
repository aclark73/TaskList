from PyQt4 import QtGui, QtCore
import sys
import requests
import json
from models import Task, NO_TASK, TaskLog
from settings import AppSettings
from socket import gethostname
from mpl_widget import MPLWidget
import random

class StatsDialogSettings(AppSettings):
    GEOMETRY = None
    
SETTINGS = StatsDialogSettings()

class StatsWidget(MPLWidget):
    def plot_data(self):
        series = {}
        logs = TaskLog.query().all()
        totals = [0]*10
        for log in logs:
            serie = series.setdefault(log.task.name, [0]*10)
            x = random.randint(0, 9)
            y = (log.end_time - log.start_time).total_seconds()
            serie[x] += y
            totals[x] += y
        
        self.ax.plot(totals)
        self.ax.hold(True)
        for task_name, serie in series.iteritems():
            self.ax.plot(serie, label=task_name)

class StatsDialog(QtGui.QDialog):

    savedGeometry = None

    def __init__(self, *args, **kwargs):
        super(StatsDialog, self).__init__(*args, **kwargs)
        geometry = SETTINGS.GEOMETRY
        if geometry:
            self.setGeometry(geometry.toRect())
        self.init_widgets()
        self.show_stats()

    def init_widgets(self):
        self.widget = StatsWidget(self)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.widget)
        self.setLayout(layout)

    def show_stats(self):
        self.widget.plot()

    def closeEvent(self, *args, **kwargs):
        SETTINGS.GEOMETRY = self.geometry()
        super(StatsDialog, self).closeEvent(*args, **kwargs)
        

def run():
    app = QtGui.QApplication(sys.argv)

#     trayicon.showMessage('test', 'test message')
    w = StatsDialog()
    
    w.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    run()

