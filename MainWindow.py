from __future__ import print_function
import warnings
import copy
import sip

import PyQt5.QtCore as QtCore
from PyQt5.QtCore import QRect, pyqtSlot, QObject
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QLabel, QDialog, QProgressBar,
                             QApplication, QGridLayout, QFileDialog, QColorDialog, QWidget, QAbstractItemView,
                             QCheckBox)
from PyQt5.Qt import Qt, QColor

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


    def plotMST(self):
        self.mst.protein_conc = float(self.concField.text())
        self.mst.fit_mst_curve()
        sip.delete(self.plot)
        self.plot = SimplePlotter()
        self.grid.addWidget(self.plot)
        self.plot.plot(self.mst.x_lin, self.mst.lig_conc, self.mst.ratios,
                       self.mst.popt, self.mst.fluo_func,
                       float(self.yminField.text()),
                       float(self.ymaxField.text()),
                       self.plotTitleField.text())
        self.kdField.setText("%.2f nM" % self.mst.kd)

        self.tableData = []
        for conc, ratio in zip(self.mst.lig_conc, self.mst.ratios):
            self.tableData.append([QCheckBox(), conc, ratio])
        # self.table_model.setDataList([[QCheckBox(), 12.3, 13.12],
                                    #   [QCheckBox(), 12.4, 13.22]])
        # print(self.tableData)
        self.table_model.setDataList(self.tableData)


    def loadFile(self):
        """Imports a text file from MST device."""
        fnames = QFileDialog.getOpenFileNames(self, "Open file")
        importfile = ""
        for f in fnames[0]:
            importfile = f
            break
        if importfile == "" or len(fnames) == 0:
            return
        self.importfile = importfile
        self.mst = MST_CurveFit(self.importfile, self.concField.text())
        self.plotTitleSuggestion = self.importfile.split('/')[-1].split(".")[0]
        self.plotTitleField.setText(self.plotTitleSuggestion)
