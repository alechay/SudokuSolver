import sys
import os
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import numpy as np
import pandas as pd
import functools
import signal
from playsound import playsound
from modules import solver

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException

signal.signal(signal.SIGALRM, timeout_handler)

class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
        # See below for the nested-list data structure.
        # .row() indexes into the outer list,
        # .column() indexes into the sub-list
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        # The length of the outer list.
        return len(self._data)

    def columnCount(self, index):
    # The following takes the first sub-list, and returns
    # the length (only works if all rows are an equal length)
        return len(self._data[0])

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Enter sudoku puzzle") 
        self.widget = QWidget()
        self.layout = QGridLayout() 

        self.table = QTableWidget(9, 9, self)
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

        self.pybutton = QPushButton('OK', self)
        self.pybutton.clicked.connect(self.clickMethod)

        self.pybutton1 = QPushButton('Clear', self)
        self.pybutton1.clicked.connect(self.clearMethod)

        self.layout.addWidget(self.table, 0, 0, 1, 2)
        self.layout.addWidget(self.pybutton, 1, 1, 1, 1)
        self.layout.addWidget(self.pybutton1, 1, 0, 1, 1)

        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

    def collectTableData(self, table):
        text = []
        for row in range(table.rowCount()):
            rowdata = []
            for column in range(table.columnCount()):
                item = table.item(row,column)
                if item is None:
                    rowdata.append('0')
                elif item.text() == '':
                    rowdata.append('0')
                else:
                    rowdata.append(item.text())
            
            text.append(rowdata)

        df = pd.DataFrame(text)
        mask = functools.reduce(np.logical_and, [df[i].str.contains('^\d{1}$', regex=True) for i in range(9)])
        return df, mask

    def trySolve(self, data):
        solutions = []
        signal.alarm(5)
        try:
            solver.solve(data, solutions)
            signal.alarm(0)
            playsound(f'{os.path.dirname(os.path.abspath(__file__))}/sounds/lets_go.m4a')
            self.second = Second(solutions)
            self.second.show()
        except TimeoutException:
            playsound(f'{os.path.dirname(os.path.abspath(__file__))}/sounds/waaaha.m4a')
            self.alert = QMessageBox()
            self.alert.setText("The board entered has too many solutions")
            self.alert.setInformativeText("Showing a few solutions, if enough time has passed to find some")
            self.alert.exec_()
            self.second = Second(solutions)
            self.second.show()
    
    def clickMethod(self):
        df, mask = self.collectTableData(self.table)

        if np.any(mask == False):
            playsound(f'{os.path.dirname(os.path.abspath(__file__))}/sounds/waaaha.m4a')
            self.alert = QMessageBox()
            self.alert.setText("Enter a valid integer 1-9")
            self.alert.exec_()
        else:
            df = df.astype(int)
            data = df.to_numpy().tolist()
            # self.grid = [[3,0,0,8,0,1,0,0,2],
            # [2,0,1,0,3,0,6,0,4],
            # [0,0,0,2,0,4,0,0,0],
            # [8,0,9,0,0,0,1,0,6],
            # [0,6,0,0,0,0,0,5,0],
            # [7,0,2,0,0,0,4,0,9],
            # [0,0,0,5,0,9,0,0,0],
            # [9,0,4,0,8,0,7,0,5],
            # [6,0,0,1,0,7,0,0,3]]
            if solver.isValidSudoku(data) == False:
                playsound(f'{os.path.dirname(os.path.abspath(__file__))}/sounds/waaaha.m4a')
                self.alert = QMessageBox()
                self.alert.setText("Invalid sudoku board entered")
                self.alert.exec_()
            else:
                self.trySolve(data)

    def clearMethod(self):
        self.table.clearContents() 

class Second(QMainWindow):

    def __init__(self, solutions):
        super(Second, self).__init__()
        self.setWindowTitle("Solution")
        self.widget = QWidget()
        self.layout = QGridLayout()

        self.solutions = [x.tolist() for x in solutions]
        self.num_sols = len(self.solutions)

        self.l1 = QLabel(f"There are {self.num_sols} solutions")

        self.l2 = QLabel(f"There is {self.num_sols} solution")

        self.comboBox = QComboBox()
        for i in range(self.num_sols):
            self.comboBox.addItem(f"{i+1}")

        self.table = QTableView()

        self.comboBox.activated[str].connect(self.onChanged)

        self.layout.addWidget(self.comboBox, 1, 0)
        self.layout.addWidget(self.table, 2, 0)

        if self.num_sols == 1:
            self.layout.addWidget(self.l2, 0, 0)
        else:
            self.layout.addWidget(self.l1, 0, 0)

        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

    def onChanged(self, text):
        self.index = int(text) - 1
        self.model = TableModel(self.solutions[self.index])
        self.table.setModel(self.model)
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit( app.exec_() )