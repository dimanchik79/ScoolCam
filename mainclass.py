import os
import sys
import threading
import wave
import cv2
import pyaudio

from datetime import datetime
from playsound import playsound

from PyQt5 import uic, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QDialog, QListWidgetItem, QFileDialog
from typing_extensions import Dict

from config import MSG_WHITE, MSG_GREEN


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


class Mixins:
    def __init__(self, *args, **kwargs):
        self.file_name = None
        self.msg_label = None
        self.audio_stream = None
        self.audio_frames = None
        self.format = None
        self.frames_per_buffer = None
        self.channels = None
        self.rate = None
        self.audio = None
        self.id_mic = None
        self.stream = True

    def set_message(self, msg, color_style):
        self.msg_label.setText(msg)
        self.msg_label.setStyleSheet(color_style)

    def record_audio(self):
        # Параметры аудио
        self.stop.setEnabled(True)

        self.audio = pyaudio.PyAudio()
        self.rate = 44100
        self.channels = 1
        self.frames_per_buffer = 2048
        self.format = pyaudio.paInt16
        self.audio_frames = []
        self.audio_stream = self.audio.open(format=self.format, channels=self.channels,
                                            rate=self.rate, input=True,
                                            input_device_index=self.id_mic,
                                            frames_per_buffer=self.frames_per_buffer)
        self.record.setEnabled(False)
        self.play.setEnabled(False)

        for process in threading.enumerate():
            if process.name.count("thread_record"):
                return
        else:
            threading.Thread(target=self.thread_record, args=(), daemon=True).start()

    def thread_record(self):
        while self.stream:
            data = self.audio_stream.read(self.frames_per_buffer)
            self.audio_frames.append(data)
            self.set_time()

        self.audio_stream.stop_stream()
        self.audio_stream.close()
        self.audio.terminate()

        wave_file = wave.open(f"{self.file_name}", 'wb')
        wave_file.setnchannels(self.channels)
        wave_file.setsampwidth(self.audio.get_sample_size(self.format))
        wave_file.setframerate(self.rate)
        wave_file.writeframes(b''.join(self.audio_frames))
        wave_file.close()
        self.record.setEnabled(True)
        self.stop.setEnabled(False)
        if os.path.exists(f"self.file_name"):
            self.play.setEnabled(True)
            self.stream = True

    def set_time(self):
        # TODO дописать течение времени
        pass

    def play_audio(self):
        playsound(f"{self.file_name}")


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


class MicSelect(QDialog, Mixins):
    def __init__(self, microphones: Dict):
        super().__init__()

        self.microphones = microphones
        uic.loadUi("GUI/micselect.ui", self)
        self.setFixedSize(400, 300)

        self.stop.setEnabled(False)
        self.play.setEnabled(False)

        self.file_name = "temp.wav"

        self.record.clicked.connect(self.record_audio)
        self.stop.clicked.connect(self.stop_audio)
        self.microplace.currentTextChanged.connect(self.get_id_microphone)
        self.play.clicked.connect(self.wav_play)

        self.add_item()

    def add_item(self):
        microphones = [mic for _, mic in self.microphones.items()]
        self.microplace.addItems(microphones)

    def get_id_microphone(self):
        for key, word in self.microphones.items():
            if word == self.microplace.currentText():
                self.id_mic = key
                break

    def stop_audio(self):
        self.play.setEnabled(True)
        self.stream = False

    def wav_play(self):
        threading.Thread(target=self.play_audio, args=(), daemon=True).start()

class PreviewCam(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("GUI/preview.ui", self)
        self.setFixedSize(1024, 780)


class StartWindow(QMainWindow, Mixins):
    def __init__(self, cameras: Dict, microphones: Dict) -> None:
        super(QMainWindow, self).__init__()
        self.preview_dialog = None
        self.stream_thread = None
        self.index_camera = None

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
        self.temp = {'prev_1': 0, 'prev_2': 1, 'prev_3': 2, 'prev_4': 3, 'prev_5': 4, 'prev_6': 5}
        self.main_objects = {'camera_name': (self.nam_1, self.nam_2, self.nam_3, self.nam_4, self.nam_5, self.nam_6),
                             'camera': (self.cam_1, self.cam_2, self.cam_3, self.cam_4, self.cam_5, self.cam_6),
                             'preview': (self.prev_1, self.prev_2, self.prev_3, self.prev_4, self.prev_5, self.prev_6)}

        for camera in self.main_objects['preview']:
            camera.clicked.connect(self.set_cameras_preview)

        self.mic_select.clicked.connect(self.add_microphone)
        self.path_select.clicked.connect(self.thread_add_path)
        self.button.clicked.connect(self.init_connections)
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
                self.set_message(f"Идет подключение {name}. Пожалуйста, ждите...", MSG_WHITE)
                self.capture.append(cv2.VideoCapture(index))
                # cv2.VideoCapture(index).set(cv2.CAP_PROP_FPS, 25)
                # cv2.VideoCapture(index).set(cv2.CAP_PROP_FRAME_WIDTH, 1024)
                # cv2.VideoCapture(index).set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

            self.set_message("Камеры подключены. Отметьте галочкой нужные устройства и включите запись", MSG_GREEN)
            self.record.setEnabled(True)
            self.stop.setEnabled(True)
            threading.Thread(target=self.thread_stream, args=(), daemon=True).start()

    def thread_stream(self):
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

        if os.path.exists("temp.wav"):
            os.remove("temp.wav")

        if dialog.result() == 1:
            pass

    def set_enabled_flag(self):
        for index in range(6):
            self.main_objects['camera_name'][index].setEnabled(False)
            self.main_objects['preview'][index].setEnabled(False)

        self.record.setEnabled(False)
        self.stop.setEnabled(False)

    def thread_add_path(self):
        for process in threading.enumerate():
            if process.name.count("add_path"):
                return
        else:
            threading.Thread(target=self.add_path, args=(), daemon=True).start()

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
