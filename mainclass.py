import sys

from datetime import datetime

from PyQt5 import QtGui
from PyQt5.QtWidgets import QMainWindow, QFileDialog

from config import MSG_WHITE, MSG_GREEN, MSG_RED

from micselect import *
from mixins import *
from camselect import *
from videorecorder import *


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


class PreviewCam(QDialog):
    """
    Класс PreviewCam
    """

    def __init__(self):
        super().__init__()
        uic.loadUi("GUI/preview.ui", self)
        self.setFixedSize(1024, 780)


class StartWindow(QMainWindow):
    def __init__(self, cameras: Dict, microphones: Dict) -> None:
        super(QMainWindow, self).__init__()

        self.videorecord = None
        self.audiorecord = None
        self.recording = None
        self.videoframe = None
        self.fourcc = None
        self.preview_dialog = None
        self.stream_thread = None
        self.stream = False
        self.index_camera = None
        self.index_microphone = None

        uic.loadUi("GUI/main.ui", self)
        self.setFixedSize(959, 795)

        self.cameras = cameras
        if len(self.cameras) <= 6:
            self.active_cam = self.cameras.copy()

        self.microphones = microphones
        self.capture = []
        self.videoframes = [0] * 6
        self.out = []
        self.files = []

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
        self.path_select.clicked.connect(self.add_path)
        self.button.clicked.connect(self.init_connections)
        self.record.clicked.connect(self.start_record)
        self.stop.clicked.connect(self.stop_record)
        self.exit.clicked.connect(self.exit_program)

        self.set_enabled_flag()
        self.timer = TimeRuner(self.time)
        self.define_cameras()

    def init_connections(self) -> None:
        """Метод инициализирует подключение к камерам"""
        if not self.initial:
            try:
                self.initial = True

                for count in range(len(self.active_cam)):
                    self.main_objects['camera_name'][count].setText(f" Камера №{count + 1}")

                threading.Thread(target=self.thread_camera_initial, args=(), daemon=True).start()

                for count in range(len(self.active_cam)):
                    self.main_objects['camera_name'][count].setEnabled(True)
                    self.main_objects['preview'][count].setEnabled(True)
            except Exception as error:
                SetMessage(self.msg_label, f"{error} Упс! Что-то пошло не так, попробуйте еше разок", MSG_RED)
                self.initial = False

    def thread_camera_initial(self) -> None:
        """Метод подключает поток видео с камер"""
        if not self.stream:
            try:
                self.stream = True
                for index, name in self.active_cam.items():
                    SetMessage(self.msg_label, f"Идет подключение {name}. Пожалуйста, ждите...", MSG_WHITE)
                    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                    self.capture.append(cap)

                SetMessage(self.msg_label, "Камеры подключены. Отметьте галочкой нужные устройства и включите запись",
                           MSG_GREEN)
                self.record.setEnabled(True)
                self.stop.setEnabled(True)
                threading.Thread(target=self.thread_main_stream, args=(), daemon=True).start()
            except Exception as error:
                SetMessage(self.msg_label, f"{error} Упс! Что-то пошло не так, попробуйте еше разок", MSG_RED)
                self.initial = False

    def thread_main_stream(self) -> None:
        """Метод воспроизводит главный поток видео с камер"""
        # TODO optimize
        while self.stream:
            count = 0
            for capture in self.capture:
                _, self.videoframes[count] = capture.read()
                count += 1

            if self.record_video:
                count = 0
                for out in self.out:
                    out.write(self.videoframes[count])
                    count += 1

            if self.preview:
                if self.videoframes[self.index_camera] is None:
                    break
                flipped_image = cv2.flip(cv2.cvtColor(self.videoframes[self.index_camera], cv2.COLOR_BGR2RGB), 1)
                qt_image = QtGui.QImage(flipped_image.data, flipped_image.shape[1], flipped_image.shape[0],
                                        QtGui.QImage.Format_RGB888)
                pic = qt_image.scaled(1024, 661, Qt.KeepAspectRatio)
                pixmap = QtGui.QPixmap.fromImage(pic)
                if pixmap is not None:
                    self.preview_dialog.preview.setPixmap(pixmap)
            else:
                for count in range(len(self.active_cam)):
                    if self.videoframes[count] is None:
                        continue
                    flipped_image = cv2.flip(cv2.cvtColor(self.videoframes[count], cv2.COLOR_BGR2RGB), 1)
                    qt_image = QtGui.QImage(flipped_image.data, flipped_image.shape[1], flipped_image.shape[0],
                                            QtGui.QImage.Format_RGB888)
                    pic = qt_image.scaled(281, 231, Qt.KeepAspectRatio)
                    pixmap = QtGui.QPixmap.fromImage(pic)

                    if pixmap is not None:
                        self.main_objects['camera'][count].setPixmap(pixmap)

    def define_cameras(self) -> None:
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

    def add_microphone(self) -> None:
        """Функция реализует выбор микрофона для записи видео"""
        dialog = MicSelect(microphones=self.microphones)
        dialog.show()
        dialog.exec_()

        if dialog.result() == 1:
            self.index_microphone = list(self.microphones)[dialog.microplace.currentIndex()]
            self.mic.setText(dialog.microplace.currentText())

    def set_enabled_flag(self) -> None:
        """Функция выставляет нужные setEnabled элементам формы"""
        for index in range(6):
            self.main_objects['camera_name'][index].setEnabled(False)
            self.main_objects['preview'][index].setEnabled(False)
        self.record.setEnabled(False)
        self.stop.setEnabled(False)

    def add_path(self) -> None:
        """Фунция реализует выбор пути для записи видео"""
        dir_path = QFileDialog.getExistingDirectory(None,
                                                    'Выбирете путь, куда будет будет записываться видеофайлы:',
                                                    '')
        if not dir_path:
            return
        else:
            self.path.setText(dir_path)

    def set_cameras_preview(self) -> None:
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
                time.sleep(0.5)
            return

    def closeEvent(self, event) -> None:
        """Метод закрывает окно программы"""
        self.exit_program()

    def exit_program(self) -> None:
        """Метод закрывает окно программы"""
        self.stream = False
        time.sleep(0.5)
        sys.exit()

    def start_record(self) -> None:
        """Метод запускает в потоке процедуру записи видео"""
        SetMessage(self.msg_label, "Идет запись с выбранных камер...", MSG_RED)
        self.record.setEnabled(False)
        self.stop.setEnabled(True)

        self.record_video = True
        self.timer.timer_set_zero()

        self.audiorecord = AudioRecord(self.index_microphone)
        self.audiorecord.audiorecord_init()

        self.videorecord = VideoRecorder(cameras=self.active_cam, date=current_date(1))
        self.videorecord.videorecord_init()

        threading.Thread(target=self.thread_timer_run, daemon=True).start()
        threading.Thread(target=self.thread_record_run, daemon=True).start()

    def stop_record(self) -> None:
        """Метод останавливает процедуру записи видео"""
        # TODO дописать монтаж видео

        SetMessage(self.msg_label, "Монтаж видео завершен", MSG_GREEN)
        self.record.setEnabled(True)  # PYQT widget button RECORD
        self.stop.setEnabled(False)   # PYQT widget button STOP

        for count in range(len(self.out)):
            self.out[count].release()

        self.record_video = False
        self.videorecord.stop_record()
        self.audiorecord.stop_record()

    def thread_timer_run(self) -> None:
        while self.record_video:
            self.timer.run_time()

    def thread_record_run(self) -> None:
        while self.record_video:
            self.videorecord.video_record(self.videoframes)
            self.audiorecord.audio_record()
