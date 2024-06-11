import threading
import time
from typing import Dict

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog

from mixins import TimeRuner
from audiorecorder import AudioRecord, AudioPlayer


class MicSelect(QDialog):
    def __init__(self, microphones: Dict):
        super().__init__()

        self.player = None
        self.timer = None
        self.recorder = None

        self.microphones = microphones
        self.id_microphone = 0

        uic.loadUi("GUI/micselect.ui", self)
        self.setFixedSize(400, 300)

        self.recorder = AudioRecord(self.id_microphone)
        self.player = AudioPlayer()
        self.timer = TimeRuner(self.time)

        self.stop_record = False
        self.stop_play = False
        self.stop_timer = False

        self.stop.setEnabled(False)
        self.play.setEnabled(False)

        self.record.clicked.connect(self.record_audio)
        self.stop.clicked.connect(self.stop_audio)
        self.play.clicked.connect(self.play_audio)
        self.microplace.currentTextChanged.connect(self.get_id_microphone)

        self.buttonBox.accepted.connect(self.exit_micselect)
        self.buttonBox.rejected.connect(self.exit_micselect)

        self.add_item()

    def exit_micselect(self):
        for process in threading.enumerate():
            if process.name.count("thread_timer_run"):
                self.stop_timer = True
            if process.name.count("thread_wav_play"):
                self.stop_play = True
            if process.name.count("thread_wav_record"):
                self.stop_record = True
        time.sleep(1)

    def record_audio(self):
        self.record.setEnabled(False)
        self.stop.setEnabled(True)
        self.play.setEnabled(False)

        self.timer.timer_set_zero()
        self.recorder.audiorecord_init()

        threading.Thread(target=self.thread_wav_record, args=(), daemon=True).start()
        threading.Thread(target=self.thread_timer_run, args=(), daemon=True).start()

    def thread_wav_record(self):
        while not self.stop_record:
            self.recorder.audio_record()
        self.recorder.stop_record()

    def thread_wav_play(self):
        while self.player.frame != b'':
            if self.stop_play:
                break
            self.player.play_audio()
        self.player.stop_player()
        self.stop_audio()

    def thread_timer_run(self):
        while not self.stop_timer:
            self.timer.run_time()

    def stop_audio(self):
        self.record.setEnabled(True)
        self.stop.setEnabled(False)
        self.play.setEnabled(True)

        self.stop_record = True
        self.stop_play = True
        self.stop_timer = True

    def play_audio(self):
        self.play.setEnabled(False)
        self.stop.setEnabled(True)
        self.record.setEnabled(False)

        self.stop_play = False
        self.stop_timer = False
        self.stop_record = False

        self.timer.timer_set_zero()
        self.player.player_init()

        threading.Thread(target=self.thread_wav_play, args=(), daemon=True).start()
        threading.Thread(target=self.thread_timer_run, args=(), daemon=True).start()

    def add_item(self):
        microphones = [mic for _, mic in self.microphones.items()]
        self.microplace.addItems(microphones)

    def get_id_microphone(self):
        for key, word in self.microphones.items():
            if word == self.microplace.currentText():
                self.id_microphone = key
                break
