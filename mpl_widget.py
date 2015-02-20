from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
from PyQt4 import QtGui

import random
import sys
from toolbar import Toolbar

class MPLWidget(QtGui.QWidget):

    
    def __init__(self, *args, **kwargs):
        super(MPLWidget, self).__init__(*args, **kwargs)
        self.init_figure()
        self.init_components()
        self.init_layout()
    
    def init_components(self):
        self.init_canvas()
        self.init_toolbar()
        self.init_controls()
        
    def init_figure(self):
        # a figure instance to plot on
        self.figure = Figure() # figsize=(300,200), dpi=100)
        self.init_ax()

    def init_canvas(self):
        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setParent(self)
        self.canvas.setSizePolicy(
            QtGui.QSizePolicy.Expanding,
            QtGui.QSizePolicy.Expanding)
        self.canvas.updateGeometry()
        self.canvas.callbacks.connect('update', self.on_update)

    def init_toolbar(self):
        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = Toolbar(self.canvas, self)

    def init_controls(self):        
        # Just some button connected to `plot` method
        self.button = QtGui.QPushButton('Plot')
        self.button.clicked.connect(self.plot)

    def init_layout(self):
        # set the layout
        layout = QtGui.QVBoxLayout()
        self.layout_components(layout)
        self.setLayout(layout)
    
    def layout_components(self, layout):
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.button)

    def on_update(self, event):
        print('Update: %s' % str(event.kwargs))

    def plot_data(self):
        # random data
        self.ax.plot([random.random() for i in range(10)])
        self.ax.hold(True)
        self.ax.plot([random.random() for i in range(10)])

    def init_ax(self):
        # create an axis
        self.ax = self.figure.add_subplot(111)

    def plot(self):
        ''' plot generic data '''
        # discards the old graph
        self.ax.hold(False)

        # plot data
        self.plot_data()

        self.ax.hold(False)

        # refresh canvas
        self.canvas.draw()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    main = MPLWidget()
    main.show()

    sys.exit(app.exec_())
