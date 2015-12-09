from PyQt4 import QtGui, QtCore
from task_list_gui import TaskListGui
from models import UPLOADER
import sys

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = TaskListGui()
    window.show()
    UPLOADER.start()
    sys.exit(app.exec_())
