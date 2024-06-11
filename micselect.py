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

    def exit_micselect(self):
        for process in threading.enumerate():
            if process.name.count("thread_timer_run"):
                self.start_timer = True
            if process.name.count("thread_wav_play"):
                self.start_play = True
            if process.name.count("thread_wav_record"):
                self.start_record = True
        time.sleep(1)

    def record_audio(self):
        self.record.setEnabled(False)
        self.stop.setEnabled(True)
        self.play.setEnabled(False)

        self.start_timer = True
        self.start_record = True

        self.timer.timer_set_zero()
        self.recorder.audiorecord_init()

        threading.Thread(target=self.thread_wav_record, args=(), daemon=True).start()
        threading.Thread(target=self.thread_timer_run, args=(), daemon=True).start()

    def play_audio(self):
        self.play.setEnabled(False)
        self.stop.setEnabled(True)
        self.record.setEnabled(False)

        self.start_timer = True
        self.start_play = True

        self.timer.timer_set_zero()
        self.player.player_init()

        threading.Thread(target=self.thread_wav_play, args=(), daemon=True).start()
        threading.Thread(target=self.thread_timer_run, args=(), daemon=True).start()

    def stop_audio(self):
        self.record.setEnabled(True)
        self.stop.setEnabled(False)
        self.play.setEnabled(True)
        self.start_timer = False
        self.start_record = False
        self.start_play = False
        time.sleep(1)

    def thread_wav_record(self):
        while self.start_record:
            self.recorder.audio_record()
        self.recorder.stop_record()
        self.stop_audio()

    def thread_wav_play(self):
        while self.player.frame != b'' or not self.start_play:
            self.player.play_audio()
        self.player.stop_player()
        self.stop_audio()

    def thread_timer_run(self):
        while self.start_timer:
            self.timer.run_time()

    def add_item(self):
        microphones = [mic for _, mic in self.microphones.items()]
        self.microplace.addItems(microphones)

    def get_id_microphone(self):
        for key, word in self.microphones.items():
            if word == self.microplace.currentText():
                self.id_microphone = key
                break
