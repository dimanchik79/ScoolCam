from datetime import datetime

from PyQt5 import uic, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QLabel, QCheckBox
from typing_extensions import Dict

from config import SCROLL_BAR_VERTICAL, SCROLL_BAR_HORIZONTAL, LABEL_RED, LABEL_GREEN


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
        self.setFixedSize(982, 782)

        self.cameras = cameras
        self.microphones = microphones
