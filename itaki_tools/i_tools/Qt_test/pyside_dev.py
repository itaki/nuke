import nuke
import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets
from nukescripts import panels

class NukeTestWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setLayout(QtWidgets.QVBoxLayout())
        self.myTable    = QtWidgets.QTableWidget()
        self.myTable.header = ['Date', 'Files', 'Size', 'Path' ]
        self.myTable.size = [ 75, 375, 85, 600 ]
        self.myTable.setColumnCount(len(self.myTable.header))
        self.myTable.setHorizontalHeaderLabels(self.myTable.header)
        self.myTable.setSelectionMode(QtWidgets.QTableView.ExtendedSelection)
        self.myTable.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.myTable.setSortingEnabled(1)
        self.myTable.sortByColumn(1, QtCore.Qt.DescendingOrder)
        self.myTable.setAlternatingRowColors(True)
        self.myTable.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.myTable.setRowCount(50)
        self.layout().addWidget(self.myTable)
        self.myTable.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

panels.registerWidgetAsPanel('NukeTestWindow', 'Test table panel', 'uk.co.thefoundry.NukeTestWindow')