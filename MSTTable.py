from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import QtGui, QtCore

class MstTableModel(QAbstractTableModel):
    """
    keep the method names
    they are an integral part of the model
    """
    def __init__(self, parent, data, header, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.mst_data = data
        self.header = header

        # self.rowCheckStateMap = {}

    def setDataList(self, data):
        self.mst_data = data
        self.layoutAboutToBeChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
        self.layoutChanged.emit()

    def updateModel(self):
        self.mst_data = dataList2
        self.layoutAboutToBeChanged.emit()
        self.dataChanged.emit(self.createIndex(0, 0), self.createIndex(self.rowCount(0), self.columnCount(0)))
        self.layoutChanged.emit()

    def rowCount(self, parent):
        return len(self.mst_data)

    def columnCount(self, parent):
        try:
            return len(self.mst_data[0])
        except IndexError as e:
            return 0

    def data(self, index, role):
        if not index.isValid():
            return None
        if (index.column() == 0):
            value = self.mst_data[index.row()][index.column()].text()
        else:
            value = "%.2f" % float(self.mst_data[index.row()][index.column()])
        if role == QtCore.Qt.EditRole:
            return value
        elif role == QtCore.Qt.DisplayRole:
            return value
        elif role == QtCore.Qt.CheckStateRole:
            if index.column() == 0:
                # print(">>> data() row,col = %d, %d" % (index.row(), index.column()))
                if self.mst_data[index.row()][index.column()].isChecked():
                    return QtCore.Qt.Checked
                else:
                    return QtCore.Qt.Unchecked

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return None

    # def sort(self, col, order):
    #     """sort table by given column number col"""
    #     # print(">>> sort() col = ", col)
    #     if col != 0:
    #         self.emit(SIGNAL("layoutAboutToBeChanged()"))
    #         self.mst_data = sorted(self.mst_data, key=operator.itemgetter(col))
    #         if order == Qt.DescendingOrder:
    #             self.mst_data.reverse()
    #         self.emit(SIGNAL("layoutChanged()"))

    def flags(self, index):
        if not index.isValid():
            return None
        # print(">>> flags() index.column() = ", index.column())
        if index.column() == 0:
            # return Qt::ItemIsEnabled | Qt::ItemIsSelectable | Qt::ItemIsUserCheckable
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsUserCheckable
        else:
            return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def setData(self, index, value, role):
        if not index.isValid():
            return False
        # print(">>> setData() role = ", role)
        # print(">>> setData() index.column() = ", index.column())
        # print(">>> setData() value = ", value)
        if role == QtCore.Qt.CheckStateRole and index.column() == 0:
            # print(">>> setData() role = ", role)
            # print(">>> setData() index.column() = ", index.column())
            if value == QtCore.Qt.Checked:
                self.mst_data[index.row()][index.column()].setChecked(True)
            else:
                self.mst_data[index.row()][index.column()].setChecked(False)
        else:
            print(">>> setData() role = ", role)
            print(">>> setData() index.column() = ", index.column())
        # self.emit(SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
        # print(">>> setData() index.row = ", index.row())
        # print(">>> setData() index.column = ", index.column())
        self.dataChanged.emit(index, index)
        return True
