import os
import threading
import time
import wave
from datetime import datetime

import pyaudio


class Mixins:
    def __init__(self, *args, **kwargs):

        self.wav_stream = None
        self.py_audio = None
        self.wav_file = None
        self.chunk = None

        self.hour = None
        self.minute = None
        self.second = None
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

        self.play_stream = False
        self.time_stream = False
        self.record_stream = False

    def set_message(self, msg, color_style):
        self.msg_label.setText(msg)
        self.msg_label.setStyleSheet(color_style)

    def record_audio(self):
        self.stop.setEnabled(True)
        self.audio = pyaudio.PyAudio()
        self.rate = 44100
        self.channels = 1
        self.frames_per_buffer = 1024
        self.format = pyaudio.paInt16
        self.audio_frames = []
        self.audio_stream = self.audio.open(format=self.format, channels=self.channels,
                                            rate=self.rate, input=True,
                                            input_device_index=self.id_mic,
                                            frames_per_buffer=self.frames_per_buffer)
        self.record.setEnabled(False)
        self.play.setEnabled(False)

        self.set_time()
        self.record_stream = True
        self.time_stream = True
        threading.Thread(target=self.thread_record, args=(), daemon=True).start()
        threading.Thread(target=self.run_time, args=(), daemon=True).start()

    def thread_record(self):
        while self.record_stream:
            data = self.audio_stream.read(self.frames_per_buffer)
            self.audio_frames.append(data)

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

        # if os.path.exists(f"{self.file_name}"):
        #     self.play.setEnabled(True)

        self.play_stream = False
        self.record_stream = False
        self.time_stream = False

    def set_play_audio(self):
        self.chunk = 1024
        self.wav_file = wave.open(self.file_name, 'rb')
        self.py_audio = pyaudio.PyAudio()
        self.wav_stream = self.py_audio.open(format=self.py_audio.get_format_from_width(self.wav_file.getsampwidth()),
                                             channels=self.wav_file.getnchannels(),
                                             rate=self.wav_file.getframerate(),
                                             output=True)

    def play_audio(self):
        data = self.wav_file.readframes(self.chunk)
        while data != '' or self.play_stream:
            self.wav_stream.write(data)
            data = self.wav_file.readframes(self.chunk)
            print(data)

        self.wav_file.close()
        self.wav_stream.close()
        self.py_audio.terminate()

        self.time_stream = False
        self.play_stream = False

    def set_time(self):
        self.second = 0
        self.minute = 0
        self.hour = 0
        self.time.setText(f'[{self.hour:02d}:{self.minute:02d}:{self.second:02d}]')

    def run_time(self):
        while self.time_stream:
            self.time.setText(f'[{self.hour:02d}:{self.minute:02d}:{self.second:02d}]')
            if self.second != 59:
                self.second += 1
            else:
                self.second = 0
                if self.minute != 59:
                    self.minute += 1
                else:
                    self.minute = 0
                    self.hour += 1
            time.sleep(1)
