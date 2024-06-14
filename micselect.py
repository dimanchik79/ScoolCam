import threading
import time
from typing import Dict

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog

from mixins import TimeRuner
from audiorecorder import AudioRecord, AudioPlayer


class MicSelect(QDialog):
    """
    Класс MicSelect
    класс реализует процесс выбора микрофона, проверки записи звука
    """
    def __init__(self, microphones: Dict):
        super().__init__()

        self.player = None
        self.timer = None
        self.recorder = None

        self.microphones = microphones
        self.id_microphone = 0

        uic.loadUi("GUI/micselect.ui", self)
        self.setFixedSize(400, 300)

        self.start_record = True
        self.start_play = True
        self.start_timer = True

        self.stop.setEnabled(False)
        self.play.setEnabled(False)

        self.record.clicked.connect(self.record_audio)
        self.stop.clicked.connect(self.stop_audio)
        self.play.clicked.connect(self.play_audio)
        self.microplace.currentTextChanged.connect(self.get_id_microphone)

        self.buttonBox.accepted.connect(self.exit_micselect)
        self.buttonBox.rejected.connect(self.exit_micselect)

        self.timer = TimeRuner(self.time)
        self.player = AudioPlayer()
        self.recorder = AudioRecord(self.id_microphone)
        self.add_item()

    def exit_micselect(self) -> None:
        """Метод реализует выход из micselect с закрытием всех запущенных потоков"""
        for process in threading.enumerate():
            if process.name.count("thread_timer_run"):
                self.start_timer = False
            if process.name.count("thread_wav_play"):
                self.start_play = False
            if process.name.count("thread_wav_record"):
                self.start_record = False
        time.sleep(1)

    def record_audio(self) -> None:
        """Метод реализует процесс подготовки потока записи звука с выбранного микрофона"""
        self.record.setEnabled(False)
        self.stop.setEnabled(True)
        self.play.setEnabled(False)

        self.start_timer = True
        self.start_record = True

        self.timer.timer_set_zero()
        self.recorder.audiorecord_init()

        threading.Thread(target=self.thread_wav_record, args=(), daemon=True).start()
        threading.Thread(target=self.thread_timer_run, args=(), daemon=True).start()

    def play_audio(self) -> None:
        """Метод реализует полготовку потоков к воспроизведению звука с выбранного микрофона"""
        self.play.setEnabled(False)
        self.stop.setEnabled(True)
        self.record.setEnabled(False)

        self.start_timer = True
        self.start_play = True

        self.timer.timer_set_zero()
        self.player.player_init()

        threading.Thread(target=self.thread_wav_play, args=(), daemon=True).start()
        threading.Thread(target=self.thread_timer_run, args=(), daemon=True).start()

    def stop_audio(self) -> None:
        """Метод реализует процесс остановки записи или воспроизведения звука"""
        self.record.setEnabled(True)
        self.stop.setEnabled(False)
        self.play.setEnabled(True)

        self.start_timer = False
        self.start_record = False
        self.start_play = False

    def thread_wav_record(self) -> None:
        """Метод реализует процесс записи звука с выбранного микрофона"""
        while self.start_record:
            self.recorder.audio_record()
        self.recorder.stop_record()
        self.stop_audio()

    def thread_wav_play(self) -> None:
        """Метод реализует процесс воспроизведения звука с выбранного микрофона"""
        while self.player.frame != b'':
            if self.start_play is False:
                break
            self.player.play_audio()
        self.player.stop_player()
        self.stop_audio()

    def thread_timer_run(self) -> None:
        """Метод реализует процесс таймера"""
        while self.start_timer:
            self.timer.run_time()

    def add_item(self) -> None:
        """Метод реализует заполнение раскрывающегося списка microplace"""
        microphones = [mic for _, mic in self.microphones.items()]
        self.microplace.addItems(microphones)

    def get_id_microphone(self) -> None:
        """Метод реализует сопоставления id микрофона по его названию из словаря microphones"""
        for key, word in self.microphones.items():
            if word == self.microplace.currentText():
                self.id_microphone = key
                break
