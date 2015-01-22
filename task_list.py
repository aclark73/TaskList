#!/usr/bin/env pythonw

from PySide import QtGui, QtCore
import sys
import requests
import subprocess
import json

REDMINE_URL = None
# REDMINE_URL = 'http://dmscode.iris.washington.edu/'
ISSUES_URL = 'http://dmscode.iris.washington.edu/issues.json?assigned_to=adam&sort=updated_on:desc&status_id=open'
ISSUE_URL = 'http://dmscode.iris.washington.edu/issues/%s'
POMODORO_SCRIPT = """
set theDuration to 29
set theBreak to 1

tell application "Pomodoro"
    start "%s" duration theDuration break theBreak
end tell
"""

class TaskList(QtGui.QMainWindow):

    def __init__(self):
        super(TaskList, self).__init__()
        self.initUI()
        
    def initUI(self):               

        self.resize(800,400)
        self.list = QtGui.QTreeWidget(self)
        self.setCentralWidget(self.list)
        self.list.setHeaderLabels([ 'Id', 'Project', 'Title' ])
        self.list.itemClicked.connect(self.on_click)
        self.list.doubleClicked.connect(self.on_select)
        self.add_tasks()
        self.show()
 
    def add_tasks(self):
        if REDMINE_URL:
            r = requests.get(ISSUES_URL)
            if r.ok:
                j = r.json()
        else:
            with open('issues.json') as f:
                j = json.load(f)
        for issue in j.get('issues'):
            link = ISSUE_URL % issue.get('id')
            item = QtGui.QTreeWidgetItem(self.list, [ "#%s" % issue.get('id'), issue.get('project').get('name'), issue.get('subject') ])
            item.setData(0, QtCore.Qt.ItemDataRole.ToolTipRole, QtCore.QUrl(link))
        for column in range(self.list.columnCount()):
            self.list.resizeColumnToContents(column)
    
    def on_click(self, item, column):
        if column == 0:
            url = item.data(0, QtCore.Qt.ItemDataRole.ToolTipRole)
            QtGui.QDesktopServices.openUrl(url)
    
    def on_select(self):
        item = self.list.currentItem()
        task_label = "%s | %s" % (item.text(1), item.text(2))
        self.asrun(POMODORO_SCRIPT % task_label)
        QtCore.QCoreApplication.instance().quit()

    def asrun(self, ascript):
      "Run the given AppleScript and return the standard output and error."
      osa = subprocess.Popen(['osascript', '-'],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE)
      return osa.communicate(ascript)[0]

def run():
    app = QtGui.QApplication(sys.argv)
    w = TaskList()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run()

