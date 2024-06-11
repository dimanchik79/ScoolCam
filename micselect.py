import threading
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

        self.recorder = AudioRecord(self.id_microphone, self.time)
        self.player = AudioPlayer(self.time)

        self.stop.setEnabled(False)
        self.play.setEnabled(False)
        self.record.clicked.connect(self.record_audio)
        self.stop.clicked.connect(self.stop_audio)
        self.microplace.currentTextChanged.connect(self.get_id_microphone)
        self.play.clicked.connect(self.play_audio)
        self.add_item()

    def record_audio(self):
        self.record.setEnabled(False)
        self.stop.setEnabled(True)
        self.play.setEnabled(False)

        self.recorder.audiorecord_init()
        threading.Thread(target=self.recorder.audio_record, args=(), daemon=True).start()

    def stop_audio(self):
        self.record.setEnabled(True)
        self.stop.setEnabled(False)
        self.play.setEnabled(True)
        self.recorder.stop_record = True
        self.player.play_stop = True

    def play_audio(self):
        self.play.setEnabled(False)
        self.stop.setEnabled(True)
        self.record.setEnabled(False)

        self.player.play_initial()
        threading.Thread(target=self.player.play_audio, args=(), daemon=True).start()

    def add_item(self):
        microphones = [mic for _, mic in self.microphones.items()]
        self.microplace.addItems(microphones)

    def get_id_microphone(self):
        for key, word in self.microphones.items():
            if word == self.microplace.currentText():
                self.id_microphone = key
                break
