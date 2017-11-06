from __future__ import print_function
import warnings
import copy
import sip

import PyQt5.QtCore as QtCore
from PyQt5.QtCore import QRect, pyqtSlot, QObject
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QLabel, QDialog, QProgressBar,
                             QApplication, QGridLayout, QFileDialog, QColorDialog, QWidget)
from PyQt5.Qt import Qt, QColor
import numpy as np
from scipy.optimize import curve_fit

import MainWindow_gui
from Plotters import SimplePlotter

def read_file(fname):
    x = []
    y = []
    with open(fname) as fin:
        dataflag = 0
        # 0: not recording, 1: start of dataset, 2: inside dataset
        for line in fin:
            l = line.strip()
            if "Data Analysis [Thermophoresis With Temperature Jump]" in l:
                dataflag = 1
                continue
            if dataflag:
                if l == "":
                    continue
                elif "Average and Error Bars" in l:
                    dataflag = 0
                    break
                else:
                    # print(l.split("\t"))
                    xl, yl = l.split("\t")
                    x.append(xl)
                    y.append(yl)
    return [np.array(x, dtype=float), np.array(y, dtype=float)]


class MST_CurveFit(object):
    """docstring for MST_CurveFit."""

    def __init__(self, fname, protein_conc):
        super(MST_CurveFit, self).__init__()
        self.read_in = read_file(fname)
        self.lig_conc = self.read_in[0] # ligand concentrations (unlabeled substance)
        self.ratios = self.read_in[1] # depletion ratio
        print(self.lig_conc)
        print(self.ratios)
        self.protein_conc = float(protein_conc)

    def fluo_func(self, a, kd, fnb, fnab):
        b = self.protein_conc
        rad = np.power(a+b+kd,2) - 4*a*b
        ab = (a+b+kd-np.sqrt(rad))/2
        b_l = b-ab
        return (ab/b)*fnab + (b_l/b)*fnb

    def fit_mst_curve(self, name):
        x_min = 10
        x_max_offset = 1e6
        dx = 100
        x = self.lig_conc
        y = self.ratios
        # run fit
        self.popt, self.pcov = curve_fit(self.fluo_func, x, y)
        # prepare plot
        self.kd = self.popt[0]
        residuals = y - self.fluo_func(x, *self.popt)
        ss_res = np.sum(residuals**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        self.r_squared = 1 - (ss_res / ss_tot)
        print(self.r_squared)

        self.x_lin = np.arange(x_min, np.max(x) + x_max_offset, dx)


class MainWindow(QMainWindow, MainWindow_gui.Ui_MainWindow, QObject):
    """PyContact Application Main Window with timeline."""

    def closeEvent(self, event):
        """Closing application when Exit on MainWindow is clicked."""
        print("Closing Application")
        event.accept()
        QApplication.quit()

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.actionLoad.triggered.connect(self.loadFile)
        self.fitButton.clicked.connect(self.loadFile)
        self.grid = QGridLayout()
        self.plotWidget.setLayout(self.grid)
        self.plot = SimplePlotter()
        self.grid.addWidget(self.plot)
        self.kdField = QLabel("Kd = ---")
        self.gridLayout_2.addWidget(self.kdField, 3, 1, 1, 1)



    def loadFile(self):
        """Imports a text file from MST device."""
        fnames = QFileDialog.getOpenFileNames(self, "Open file")
        importfile = ""
        for f in fnames[0]:
            importfile = f
            break
        if importfile == "" or len(fnames) == 0:
            return
        mst = MST_CurveFit(importfile, self.concField.text())
        mst.fit_mst_curve('test')
        sip.delete(self.plot)
        self.plot = SimplePlotter()
        self.grid.addWidget(self.plot)
        self.plot.plot(mst.x_lin, mst.lig_conc, mst.ratios, mst.popt, mst.fluo_func)
        self.kdField.setText("Kd = %.2f nM" % mst.kd)
