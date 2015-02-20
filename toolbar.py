from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.backend_bases import Event

class Toolbar(NavigationToolbar):

    def notify(self, event_name, **kwargs):
        event = Event(event_name, self)
        event.kwargs = kwargs
        self.canvas.callbacks.process(event_name, event)
    
    def update(self):
        self.notify('update')
        super(Toolbar, self).update()
    
    def push_current(self):
        lims = []
        pos = []
        for a in self.canvas.figure.get_axes():
            xmin, xmax = a.get_xlim()
            ymin, ymax = a.get_ylim()
            lims.append((xmin, xmax, ymin, ymax))
            # Store both the original and modified positions
            pos.append((
                a.get_position(True).frozen(),
                a.get_position().frozen()))
        self.notify('update', pos=pos, lims=lims)
        super(Toolbar, self).push_current()

class LeanToolbar(Toolbar):
    toolitems = (
        ('Home', 'Reset original view', 'home', 'home'),
        (None, None, None, None),
        ('Back', 'Back to  previous view', 'back', 'back'),
        ('Forward', 'Forward to next view', 'forward', 'forward'),
        (None, None, None, None),
        ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
        ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
        (None, None, None, None),
        ('Save', 'Save the figure', 'filesave', 'save_figure'),
      )
