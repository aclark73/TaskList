#!/usr/bin/env pythonw

from PyQt4 import QtGui, QtCore
from models import Task


class TaskHistory(QtCore.QObject):

    picked = QtCore.pyqtSignal(str)

    def __init__(self, app, comboBox):
        super(TaskHistory, self).__init__()
        self.app = app
        self.comboBox = comboBox
        self.initWidgets()

    def initWidgets(self):
        self.comboBox.currentIndexChanged.connect(self.onIndexChanged)

    def onIndexChanged(self, index):
        task_uid = self.comboBox.itemData(index)
        self.picked.emit(task_uid.toString())

    def addTask(self, task):
        self.comboBox.addItem(str(task), task.get_uid())
        self.comboBox.setCurrentIndex(0)


def run():
    pass

if __name__ == '__main__':
    run()

