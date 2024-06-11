import os
import subprocess
import sys
import threading
import wave

import cv2

from datetime import datetime

import pyaudio
from PyQt5 import uic, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QDialog, QListWidgetItem, QFileDialog
from typing_extensions import Dict

from config import MSG_WHITE, MSG_GREEN, MSG_RED

from micselect import *
from mixins import *


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


class PreviewCam(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("GUI/preview.ui", self)
        self.setFixedSize(1024, 780)


class StartWindow(QMainWindow):
    def __init__(self, cameras: Dict, microphones: Dict) -> None:
        super(QMainWindow, self).__init__()
        self.fourcc = None
        self.video_file = []
        self.out = []
        self.preview_dialog = None
        self.stream_thread = None
        self.index_camera = None
        self.index_microphone = None

        uic.loadUi("GUI/main.ui", self)
        self.setFixedSize(982, 855)

        # self.cameras = cameras
        self.cameras = cameras
        if len(self.cameras) <= 6:
            self.active_cam = self.cameras.copy()

        self.microphones = microphones
        self.capture = []

        self.initial = False
        self.stream = False
        self.preview = False

        self.record_video = False

        self.temp = {'prev_1': 0, 'prev_2': 1, 'prev_3': 2, 'prev_4': 3, 'prev_5': 4, 'prev_6': 5}
        self.main_objects = {'camera_name': (self.nam_1, self.nam_2, self.nam_3, self.nam_4, self.nam_5, self.nam_6),
                             'camera': (self.cam_1, self.cam_2, self.cam_3, self.cam_4, self.cam_5, self.cam_6),
                             'preview': (self.prev_1, self.prev_2, self.prev_3, self.prev_4, self.prev_5, self.prev_6)}

        for camera in self.main_objects['preview']:
            camera.clicked.connect(self.set_cameras_preview)

        self.mic_select.clicked.connect(self.add_microphone)
        self.path_select.clicked.connect(self.thread_add_path)
        self.button.clicked.connect(self.init_connections)
        self.record.clicked.connect(self.start_record)
        self.exit.clicked.connect(self.exit_program)

        self.set_enabled_flag()
        self.define_cameras()

    def init_connections(self):
        if not self.initial:
            self.initial = True
            for count in range(len(self.active_cam)):
                self.main_objects['camera_name'][count].setText(self.active_cam[count])
            threading.Thread(target=self.thread_camera_initial, args=(), daemon=True).start()
            for count in range(len(self.active_cam)):
                self.main_objects['camera_name'][count].setEnabled(True)
                self.main_objects['preview'][count].setEnabled(True)

    def thread_camera_initial(self):
        if not self.stream:
            self.stream = True
            for index, name in self.active_cam.items():
                SetMessage(self.msg_label, f"Идет подключение {name}. Пожалуйста, ждите...", MSG_WHITE)
                self.capture.append(cv2.VideoCapture(index))

            SetMessage(self.msg_label, "Камеры подключены. Отметьте галочкой нужные устройства и включите запись",
                       MSG_GREEN)
            self.record.setEnabled(True)
            self.stop.setEnabled(True)
            threading.Thread(target=self.thread_stream, args=(), daemon=True).start()

    def thread_stream(self):
        # TODO optimize
        while True:
            count = 0
            if self.preview:
                correct_frame, frame = self.capture[self.index_camera].read()
                if correct_frame:
                    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    flipped_image = cv2.flip(image, 1)
                    qt_image = QtGui.QImage(flipped_image.data, flipped_image.shape[1], flipped_image.shape[0],
                                            QtGui.QImage.Format_RGB888)
                    pic = qt_image.scaled(1001, 661, QtCore.Qt.KeepAspectRatio)
                    pixmap = QtGui.QPixmap.fromImage(pic)
                    self.preview_dialog.preview.setPixmap(pixmap)
            else:
                for capture in self.capture:
                    correct_frame, frame = capture.read()
                    if correct_frame:
                        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        flipped_image = cv2.flip(image, 1)
                        qt_image = QtGui.QImage(flipped_image.data, flipped_image.shape[1], flipped_image.shape[0],
                                                QtGui.QImage.Format_RGB888)
                        pic = qt_image.scaled(281, 231, QtCore.Qt.KeepAspectRatio)
                        pixmap = QtGui.QPixmap.fromImage(pic)
                        self.main_objects['camera'][count].setPixmap(pixmap)
                        count += 1

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
            self.index_microphone = list(self.microphones)[dialog.microplace.currentIndex()]
            self.mic.setText(dialog.microplace.currentText())

    def set_enabled_flag(self):
        for index in range(6):
            self.main_objects['camera_name'][index].setEnabled(False)
            self.main_objects['preview'][index].setEnabled(False)

        self.record.setEnabled(False)
        self.stop.setEnabled(False)

    def thread_add_path(self):

        # threading.Thread(target=self.add_path, args=(), daemon=True).start()
        self.add_path()

    def add_path(self):
        dir_path = QFileDialog.getExistingDirectory(None,
                                                    'Выбирете путь, куда будет будет записываться видеофайлы:',
                                                    '')
        if not dir_path:
            return
        else:
            self.path.setText(dir_path)

    def set_cameras_preview(self):
        index = self.temp[self.sender().objectName()]
        camera_name = self.active_cam[index]
        for key, word in self.active_cam.items():
            if word == camera_name:
                self.index_camera = key
                break
        if not self.preview:
            self.preview = True
            self.preview_dialog = PreviewCam()
            self.preview_dialog.show()
            self.preview_dialog.exec_()
            if self.preview_dialog.result() == 0:
                self.preview = False
            return

    def closeEvent(self, event) -> None:
        """Метод закрывает окно программы"""
        self.exit_program()

    @staticmethod
    def exit_program():
        """Метод закрывает окно программы"""
        sys.exit()

    def start_record(self):
        SetMessage(self.time_label, "Идет запись с выбранных камер...", MSG_RED)
        self.record.setEnabled(False)
        self.stop.setEnabled(True)
        self.record_video = True

    def stop_record(self):
        SetMessage(self.time_label, "Монтаж видео завершен", MSG_GREEN)
        self.record.setEnabled(True)
        self.stop.setEnabled(False)
        self.record_video = False
