from PyQt4 import QtCore

QtCore.QCoreApplication.setOrganizationName('Adam')
QtCore.QCoreApplication.setOrganizationDomain('dagobah.com')
QtCore.QCoreApplication.setApplicationName('TaskList')

def getSettings():
    return QtCore.QSettings()