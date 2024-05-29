from datetime import datetime

from PyQt5 import uic, QtGui, QtWidgets
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QMainWindow, QTableWidget
from typing_extensions import Dict


def current_date(mark: int) -> str:
    """
    Функция возвращает текущую дату и время определенного формата
    mark - признак определенного формата
    """
    if mark == 0:
        # Возвращает дату для консоли
        return str(datetime.now().strftime('%d.%m.%y %H:%M:%S'))
    elif mark == 1:
        # Возвращает дату для файла
        return str(datetime.now().strftime('%d%m%y_%H%M%S'))
    else:
        return ""


class StartWindow(QMainWindow):
    def __init__(self, cameras: Dict, microphones: Dict) -> None:
        super(StartWindow, self).__init__()
        uic.loadUi("GUI/main.ui", self)
        self.setFixedSize(1120, 756)

        self.cameras = cameras
        self.microphones = microphones
        self.message = []

        self.set_message("Добро пожаловать в ScoolCam!!!")

    def set_message(self, msg: str) -> None:
        message = ""
        self.message.insert(0, f"{current_date(mark=0)} --- {msg}\n")
        for msg in self.message:
            message += msg
        self.console.setText(message)
