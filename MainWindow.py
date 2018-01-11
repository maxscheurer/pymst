from __future__ import print_function
import warnings
import copy
import sip, os

import PyQt5.QtCore as QtCore
from PyQt5.QtCore import QRect, pyqtSlot, QObject
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QLabel, QDialog, QProgressBar,
                             QApplication, QGridLayout, QFileDialog, QColorDialog, QWidget, QAbstractItemView,
                             QCheckBox, QFileDialog)
from PyQt5.Qt import Qt, QColor
import numpy as np

import MainWindow_gui
from MSTTable import MstTableModel
from Plotters import SimplePlotter
from MstCurveFit import MST_CurveFit


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
        self.fitButton.clicked.connect(self.plotMST)
        self.savePlotButton.clicked.connect(self.savePlot)
        self.grid = QGridLayout()
        self.plotWidget.setLayout(self.grid)
        self.plot = SimplePlotter()
        self.grid.addWidget(self.plot)

        # checkbox1 = QCheckBox("exc.");
        # checkbox1.setChecked(True)
        self.table_model = MstTableModel(self, [], ['exc.', 'conc.', 'ratio'])
        #self.table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        # bind cell click to a method reference
        # self.tableView.clicked.connect(self.showSelection)
        # self.tableView.clicked.connect(self.selectRow)

        self.tableView.setModel(self.table_model)
        # enable sorting
        # self.tableView.setSortingEnabled(True)
        self.dataPlotted = False
        self.loadedData = False
        self.importfiles = []


    def plotMST(self):
        idx = 0
        indexList = []
        self.excluded_conc = []
        self.excluded_ratios = []
        showKD = self.checkBox.isChecked()
        if self.table_model.mst_data and len(self.table_model.mst_data):
            for x in self.table_model.mst_data:
                if x[0].isChecked():
                    print("Exclude index ", idx)
                    indexList.append(idx)
                else:
                    self.excluded_conc.append(self.mst.lig_conc_orig[idx])
                    self.excluded_ratios.append(self.mst.ratios_orig[idx])
                idx += 1
            self.mst.lig_conc = np.array(self.excluded_conc, dtype=float)
            self.mst.ratios = np.array(self.excluded_ratios, dtype=float)
        self.mst.protein_conc = float(self.concField.text())
        self.mst.fit_mst_curve()
        sip.delete(self.plot)
        self.plot = SimplePlotter()
        self.grid.addWidget(self.plot)
        self.plot.plot(self.mst.x_lin, self.mst.lig_conc, self.mst.ratios_mean,
                       self.mst.popt, self.mst.fluo_func,
                       float(self.yminField.text()),
                       float(self.ymaxField.text()),
                       self.plotTitleField.text(),
                       showKD, self.mst.sem)
        self.kdField.setText("%.2f nM" % self.mst.kd)
        self.r2Field.setText("%.4f" % self.mst.r_squared)

        self.tableData = []
        idx = 0
        # for conc, ratio in zip(self.mst.lig_conc_orig, self.mst.ratios_orig):
        #     box = QCheckBox()
        #     if idx in indexList:
        #         box.setCheckState(2)
        #     self.tableData.append([box, conc, ratio])
        #     idx += 1
        
        # self.table_model.setDataList([[QCheckBox(), 12.3, 13.12],
                                    #   [QCheckBox(), 12.4, 13.22]])
        # print(self.tableData)
        self.table_model.setDataList(self.tableData)

    def savePlot(self):
        """Saves the generated plot."""
        fileName = QFileDialog.getSaveFileName(self, 'Export Path', self.plotTitleSuggestion)
        if len(fileName[0]) > 0:
            path, file_extension = os.path.splitext(fileName[0])
            if file_extension == "":
                file_extension = ".png"
            file_extension = file_extension[1:]
            try:
                self.plot.saveFigure(path, file_extension)
            except ValueError:
                box = ErrorBox("File format " + file_extension + " is not supported.\nPlease choose from eps, pdf, pgf,"
                                                                 " png, ps, raw, rgba, svg, svgz. ")
                box.exec_()


    def loadFile(self):
        """Imports a text file from MST device."""
        fnames = QFileDialog.getOpenFileNames(self, "Open file")
        importfile = ""
        for f in fnames[0]:
            importfile = f
            break
        if importfile == "" or len(fnames) == 0:
            return
        self.importfiles.append(importfile)
        self.mst = MST_CurveFit(self.importfiles, self.concField.text())
        self.plotTitleSuggestion = importfile.split('/')[-1].split(".")[0]
        self.plotTitleField.setText(self.plotTitleSuggestion)
