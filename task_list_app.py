from PyQt4 import QtGui, QtCore
from task_list_gui import TaskListGui
import sys

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = TaskListGui()
    window.show()
    sys.exit(app.exec_())
