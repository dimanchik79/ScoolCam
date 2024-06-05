import cv2
import threading

from datetime import datetime
from typing_extensions import Dict

from PyQt5 import uic, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QDialog, QListWidgetItem, QFileDialog


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
        return str(datetime.now())


class CamSelect(QDialog):
    def __init__(self, cameras: Dict):
        super().__init__()
        self.cameras = cameras
        uic.loadUi("GUI/camselect.ui", self)
        self.setFixedSize(400, 552)
        self.add_item()

    def add_item(self):
        for key, cam in self.cameras.items():
            item = QListWidgetItem(cam)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.camplace.addItem(item)


class MicSelect(QDialog):
    def __init__(self, microphones: Dict):
        super().__init__()
        self.micro = microphones
        uic.loadUi("GUI/micselect.ui", self)
        self.setFixedSize(400, 300)
        self.add_item()

    def add_item(self):
        microphones = [mic for _, mic in self.micro.items()]
        self.microplace.addItems(microphones)


class StreamThread(QtCore.QThread):
    change_pixmap = QtCore.pyqtSignal(QtGui.QPixmap)

    def __init__(self, msg_label, index_cam, cam_name, count):
        super().__init__()
        self.msg_label = msg_label
        self.index_cam = index_cam
        self.cam_name = cam_name
        self.count = count

    def run(self):
        cap = cv2.VideoCapture(self.index_cam)

        while True:
            correct, frame = cap.read()
            if correct:
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                flipped_image = cv2.flip(image, 1)
                qt_image = QtGui.QImage(flipped_image.data, flipped_image.shape[1], flipped_image.shape[0],
                                        QtGui.QImage.Format_RGB888)
                pic = qt_image.scaled(281, 221, QtCore.Qt.KeepAspectRatio)
                pixmap = QtGui.QPixmap.fromImage(pic)
                self.change_pixmap.emit(pixmap)


class StartWindow(QMainWindow):
    def __init__(self, cameras: Dict, microphones: Dict) -> None:
        super(QMainWindow, self).__init__()
        self.stream_thread = None
        uic.loadUi("GUI/main.ui", self)
        self.setFixedSize(982, 821)

        # self.cameras = cameras
        self.cameras = cameras
        if len(self.cameras) <= 6:
            self.active_cam = self.cameras.copy()

        self.microphones = microphones
        self.check_list = [0, 0, 0]

        self.cam_nam = [self.nam_1, self.nam_2, self.nam_3, self.nam_4, self.nam_5, self.nam_6]
        self.cam = [self.cam_1, self.cam_2, self.cam_3, self.cam_4, self.cam_5, self.cam_6]
        self.full_scr = [self.full_1, self.full_2, self.full_3, self.full_4, self.full_5, self.full_6]

        self.mic_select.clicked.connect(self.add_microphone)
        self.path_select.clicked.connect(self.add_path)
        self.button.clicked.connect(self.init_connections)

        self.set_enabled_flag()
        self.define_cameras()

    @QtCore.pyqtSlot(bool)
    def init_connections(self):
        count = 0
        for index, cam_name in self.active_cam.items():
            self.stream_thread = StreamThread(msg_label=self.msg_label, index_cam=index, cam_name=cam_name, count=count)
            self.stream_thread.change_pixmap.connect(self.cam[count].setPixmap)
            count += 1
            self.stream_thread.start()

    def define_cameras(self):
        if len(self.cameras) > 6:
            dialog = CamSelect(cameras=self.cameras)
            dialog.show()
            dialog.exec_()

            if dialog.result() == 1:
                count = dialog.camplace.count()
                cb_list = [dialog.camplace.item(i) for i in range(count)]
                count = 0
                for cb in cb_list:
                    if cb.checkState():
                        self.active_cam[str(count)] = cb.text()
                    count += 1

    def add_microphone(self):
        dialog = MicSelect(microphones=self.microphones)
        dialog.show()
        dialog.exec_()

        if dialog.result() == 1:
            pass

    def set_enabled_flag(self):
        for index in range(6):
            self.cam_nam[index].setEnabled(False)
            self.full_scr[index].setEnabled(False)
        self.record.setEnabled(False)
        self.stop.setEnabled(False)

    def add_path(self):
        dir_path = QFileDialog.getExistingDirectory(None,
                                                    'Выбирете путь, куда будет будет записываться видеофайлы:', '')
        if not dir_path:
            return
        else:
            self.path.setText(dir_path)
