from datetime import datetime

from PyQt5 import uic, QtGui, QtWidgets
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QMainWindow, QTableWidget
from typing_extensions import Dict


class StartWindow(QMainWindow):
    def __init__(self, cameras: Dict, microphones: Dict) -> None:
        super(StartWindow, self).__init__()
        uic.loadUi("GUI/main.ui", self)
        self.setFixedSize(1120, 756)

        self.cameras = cameras
        self.microphones = microphones
        self.message = []

        self.set_message("Добро пожаловать в ScoolCam!!!")

    def set_message(self, msg):
        message = ""
        current_date = datetime.now().strftime('%d.%m.%y %H:%M:%S')
        self.message.insert(0, f"{str(current_date)} --- {msg}\n")
        for msg in self.message:
            message += msg
        self.console.setText(message)
