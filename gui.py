from datetime import datetime

from PyQt5 import uic, QtGui, QtWidgets
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QMainWindow, QTableWidget


class StartWindow(QMainWindow):
    def __init__(self, parent=None) -> None:
        super(StartWindow, self).__init__(parent)
        uic.loadUi("GUI/main.ui", self)
        self.setFixedSize(1097, 850)
