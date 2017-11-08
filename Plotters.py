import matplotlib
from PyQt5.QtWidgets import QSizePolicy
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg \
    as FigureCanvas
from matplotlib.figure import Figure
plt.style.use('ggplot')

font = {'family' : 'normal',
        'weight' : 'normal',
        'size'   : 14}

matplotlib.rc('font', **font)


class MplPlotter(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        # We want the axes cleared every time plot() is called
        # self.axes.hold(False)

        self.compute_initial_figure()

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass


class SimplePlotter(MplPlotter):
    """Simple plotter, used in the SASA view."""
    def onpick(self, event, line):
        print("EVENT!")
        if event.artist!=line: return True

        N = len(event.ind)
        if not N: return True


        # figi = plt.figure()
        for subplotnum, dataind in enumerate(event.ind):
            print(subplotnum, dataind)
        return True

    def plot(self, x_lin, x_raw, y_raw, popt, func, ymin, ymax, title='', showKD=False):
        line, = self.axes.semilogx(x_raw, y_raw, "o", picker=5)

        line2, = self.axes.semilogx(x_lin, func(x_lin, *popt), "-", label=r"$K_d$ = %.2f nM" % popt[0])
        # plt.semilogx(x, y, "o")

        self.axes.set_ylim([ymin, ymax])
        self.fig.canvas.mpl_connect('pick_event', lambda event: self.onpick(event, line))
        # self.axes.plot(x, y)
        self.axes.set_xlabel("concentration [nM]")
        self.axes.set_ylabel("fluo. ratio")
        self.axes.set_title(title)
        if showKD:
            self.axes.legend(loc='lower left')
        # self.axes.xaxis.set_label_position('top')

    def saveFigure(self, path, outputFormat):
        self.fig.savefig(path + "." + outputFormat, format=outputFormat)

    def clearFigure(self):
        self.fig.clf()
