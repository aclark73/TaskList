#!/usr/bin/env pythonw

from PyQt4 import QtGui, QtCore
from models import Task


class TaskHistory(QtCore.QObject):

    picked = QtCore.pyqtSignal(str)
    _updating = False

    def __init__(self, app, comboBox):
        super(TaskHistory, self).__init__()
        self.app = app
        self.comboBox = comboBox
        self.initWidgets()

    def initWidgets(self):
        self.comboBox.currentIndexChanged.connect(self.onIndexChanged)

    def onIndexChanged(self, index):
        if self._updating:
            return
        task_uid = self.comboBox.itemData(index)
        self.picked.emit(task_uid.toString())

    def addTask(self, task):
        existing = self.comboBox.findData(task.get_uid())
        if existing != 0:
            self._updating = True
            if existing > -1:
                self.comboBox.removeItem(existing)
            self.comboBox.insertItem(0, str(task), task.get_uid())
            self._updating = False
            self.comboBox.setCurrentIndex(0)

def run():
    pass

if __name__ == '__main__':
    run()

