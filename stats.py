from PyQt4 import QtGui, QtCore
import sys
import requests
import json
from models import Task, NO_TASK, TaskLog
from settings import AppSettings
from socket import gethostname
from mpl_widget import MPLWidget
import random
import datetime
import numpy as np
from matplotlib import cm

class StatsDialogSettings(AppSettings):
    GEOMETRY = None
    
SETTINGS = StatsDialogSettings()

kelly_colors_hex = [
    '#FFB300', # Vivid Yellow
    '#803E75', # Strong Purple
    '#FF6800', # Vivid Orange
    '#A6BDD7', # Very Light Blue
    '#C10020', # Vivid Red
    '#CEA262', # Grayish Yellow
    '#817066', # Medium Gray

    # The following don't work well for people with defective color vision
    '#007D34', # Vivid Green
    '#F6768E', # Strong Purplish Pink
    '#00538A', # Strong Blue
    '#FF7A5C', # Strong Yellowish Pink
    '#53377A', # Strong Violet
    '#FF8E00', # Vivid Orange Yellow
    '#B32851', # Strong Purplish Red
    '#F4C800', # Vivid Greenish Yellow
    '#7F180D', # Strong Reddish Brown
    '#93AA00', # Vivid Yellowish Green
    '#593315', # Deep Yellowish Brown
    '#F13A13', # Vivid Reddish Orange
    '#232C16', # Dark Olive Green
    ]

class StatsWidget(MPLWidget):
    plot_days = 7
    def plot_data(self):
        today = datetime.date.today()
        series = {}
        logs = TaskLog.query().all()
        totals = []
        for log in logs:
            task_name = log.task.name
            series_data = series.setdefault(task_name, [])
            days_ago = (today - log.start_time.date()).days
            time_spent = (log.end_time - log.start_time).total_seconds()
            while len(totals) <= days_ago:
                totals.append(0)
            while len(series_data) < len(totals):
                series_data.append(0)
            series_data[days_ago] += time_spent
            totals[days_ago] += time_spent
        
        totals = np.array(totals)
        totals = totals / 3600
        totals = totals[::-1]
#         totals = [t/3600 for t in reversed(totals)]
        print ",".join([str(t) for t in totals])
        xvalues = np.arange(len(totals))
#        self.ax.bar(xvalues, totals)
        self.ax.hold(True)
        cumulative = np.zeros(len(totals))
        num_tasks = len(series)
        task_data_list = []
        for task_num, task_name in enumerate(series.iterkeys()):
            series_data = series[task_name]
            task_data = np.zeros(len(totals))
            task_data = task_data + np.array(series_data)
            task_data = task_data / 3600
            task_data = task_data[::-1]
#             if len(series_data) < len(totals):
#                 series_data.append(0)
#             series_data = np.asarray([d/3600 for d in reversed(series_data)])
            print "%s: %s" % (task_name, ",".join([str(d) for d in task_data]))
            task_data_list.append(task_data)
#             self.ax.bar(xvalues, task_data, label=task_name, bottom=cumulative,
#                 # color='rgbrgbrgbrgb'[task_num]) # 
#                 color=kelly_colors_hex[task_num%len(kelly_colors_hex)])
            cumulative = cumulative + task_data
#         self.ax.legend()
        self.ax.stackplot(xvalues, *task_data_list)

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

