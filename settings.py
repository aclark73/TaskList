from PyQt4 import QtCore

QtCore.QCoreApplication.setOrganizationName('Adam')
QtCore.QCoreApplication.setOrganizationDomain('dagobah.com')
QtCore.QCoreApplication.setApplicationName('TaskList')

class Settings:
    def __init__(self, prefix):
        self.prefix = prefix
    def __enter__(self):
        self.settings = QtCore.QSettings()
        self.settings.beginGroup(self.prefix)
        return self.settings
    def __exit__(self, *args, **kwargs):
        self.settings.endGroup()
