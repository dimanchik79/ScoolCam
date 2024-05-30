from datetime import datetime

from PyQt5 import uic, QtGui, QtWidgets
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QMainWindow, QTableWidget
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
        self.setFixedSize(1120, 756)
        self.message = []
        self.set_message("Добро пожаловать в ScoolCam!!!")

        self.cameras = cameras
        self.microphones = microphones

        self.cam_table.horizontalScrollBar().setStyleSheet(SCROLL_BAR_HORIZONTAL)
        self.cam_table.verticalScrollBar().setStyleSheet(SCROLL_BAR_VERTICAL)

        self.clear_cons.clicked.connect(self.clear_console)
        self.find_cams.clicked.connect(self.add_cams)
        self.auditory_line.textChanged.connect(self.auditory)

    def auditory(self):
        """Метод ввода аудитории"""
        if self.auditory_line.text() != "":
            self.chek2.setStyleSheet(LABEL_GREEN)
        else:
            self.chek2.setStyleSheet(LABEL_RED)

    def add_cams(self):
        """Метод добавления активных камер в таблицу"""
        self.cam_table.setColumnCount(3)
        self.cam_table.setRowCount(len(self.cameras))
        self.cam_table.setHorizontalHeaderLabels(["Выбор", "Предпросмотр", "Название"])
        for index in range(1, 3):
            self.cam_table.horizontalHeaderItem(index).setTextAlignment(Qt.AlignHCenter)

    def clear_console(self):
        """Метод очищает консоль"""
        self.message = []
        self.console.clear()

    def set_message(self, msg: str) -> None:
        message = ""
        self.message.insert(0, f"{current_date(mark=0)} --- {msg}\n")
        for msg in self.message:
            message += msg
        self.console.setText(message)
