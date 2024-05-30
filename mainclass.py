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
        self.setFixedSize(1120, 756)

        self.message = []
        self.check_list = [0] * 6

        self.cameras = cameras
        self.microphones = microphones

        self.cam_table.horizontalScrollBar().setStyleSheet(SCROLL_BAR_HORIZONTAL)
        self.cam_table.verticalScrollBar().setStyleSheet(SCROLL_BAR_VERTICAL)

        self.clear_cons.clicked.connect(self.clear_console)
        self.find_cams.clicked.connect(self.add_cams)
        self.auditory_line.textChanged.connect(self.auditory)

        self.set_message("Добро пожаловать в ScoolCam!!!")

    def auditory(self):
        """Метод ввода аудитории"""
        if self.auditory_line.text() != "":
            self.check_list[1] = 1
            self.check2.setStyleSheet(LABEL_GREEN)
        else:
            self.check_list[1] = 0
            self.check2.setStyleSheet(LABEL_RED)

    def add_cams(self):
        """Метод добавления активных камер в таблицу"""
        self.set_message("Ждите... Идет подключение активных камер.")
        self.cam_table.setColumnCount(3)
        self.cam_table.setRowCount(len(self.cameras))
        self.cam_table.setHorizontalHeaderLabels(["Выбор", "Предпросмотр", "Название камеры"])
        for index in range(1, 3):
            self.cam_table.horizontalHeaderItem(index).setTextAlignment(Qt.AlignHCenter)

        for row in range(len(self.cameras)):
            self.cam_table.setRowHeight(row, 200)
            self.cam_table.setColumnWidth(0, 55)
            self.cam_table.setColumnWidth(1, 200)
            self.cam_table.setColumnWidth(2, 250)

            # Установка items для 3й колонки
            item = QTableWidgetItem(self.cameras[row])
            item.setTextAlignment(2)
            item.setFlags(item.flags() & ~-1)
            self.cam_table.setItem(row, 2, item)

            item = QTableWidgetItem("")
            item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            item.setCheckState(QtCore.Qt.Unchecked)
            item.setFlags(item.flags() & ~1)
            self.cam_table.setItem(row, 0, item)

            label = QLabel(str(row), alignment=132)
            self.cam_table.setCellWidget(row, 1, label)

        self.check_list[0] = 1
        self.check1.setStyleSheet(LABEL_GREEN)

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
