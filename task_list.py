#!/usr/bin/env pythonw

from PyQt4 import QtGui, QtCore
import sys
import requests
import subprocess
import json

REDMINE_URL = ''
# REDMINE_URL = 'http://dmscode.iris.washington.edu/'
ISSUES_URL = REDMINE_URL + '/issues.json?assigned_to=%s&sort=updated_on:desc&status_id=open' % (REDMINE_HOME, REDMINE_USER)
ISSUE_URL = REDMINE_HOME + '/issues/%s'
POMODORO_SCRIPT = """
set theDuration to 29
set theBreak to 1

tell application "Pomodoro"
    start "%s" duration theDuration break theBreak
end tell
"""

class TaskList(QtGui.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(TaskList, self).__init__(*args, **kwargs)
        self.initWindow()
        self.initWidgets()

    def initWindow(self):
        self.setWindowTitle('PyWeed')
        self.resize(800,400)
        self.setMinimumWidth(400)

        self.file_menu = QtGui.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QtGui.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)
    
    def initWidgets(self):
#         main_widget = QtGui.QWidget(self)
#         self.map = BasemapWidget(main_widget)
#         self.waveforms = MPLWidget(main_widget)
        self.list = QtGui.QTreeWidget(self)
        self.setCentralWidget(self.list)
        self.list.setHeaderLabels([ 'Id', 'Project', 'Title' ])
        self.list.itemClicked.connect(self.on_click)
        self.list.doubleClicked.connect(self.on_doubleclick)
        self.add_tasks()
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
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
    
    def on_doubleclick(self):
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
    if 'localhost' in REDMINE_HOME:
        import test_server
        test_server.run()

    app = QtGui.QApplication(sys.argv)

    icon = QtGui.QIcon(QtGui.QPixmap(10,20))
    trayicon = QtGui.QSystemTrayIcon(icon)
#     trayicon.setContextMenu(menu)
    trayicon.show()

    print trayicon.geometry()

    menu = QtGui.QMenu('test')
    pm = QtGui.QPixmap(trayicon.geometry().size())
    painter = QtGui.QPainter()
    painter.begin(pm)
    font = menu.font()
    font.setPixelSize(pm.height())
    painter.setFont(font)
    
    print painter.font()
    painter.fillRect(0,0,pm.width(),pm.height(),QtCore.Qt.red)
    painter.drawText(0, pm.height(), "Test")
    painter.end()
    trayicon.setIcon(QtGui.QIcon(pm))

#     trayicon.showMessage('test', 'test message')
    w = TaskList()
#     w = QtGui.QWidget()
    w.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    run()

