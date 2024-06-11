import wave
import pyaudio

from mixins import TimeRuner


class AudioRecord:
    def __init__(self, microphone_index, time_label):

        self.timer = None
        self.frame = None
        self.audio_stream = None
        self.audio_frames = None
        self.format = None
        self.frames_per_buffer = None
        self.channels = None
        self.rate = None
        self.audio = None

        self.stop_record = False
        self.microphone_index = microphone_index
        self.time_label = time_label

    def audiorecord_init(self):
        self.audio = pyaudio.PyAudio()
        self.rate = 44100
        self.channels = 1
        self.frames_per_buffer = 1024
        self.format = pyaudio.paInt16
        self.audio_frames = []
        self.audio_stream = self.audio.open(format=self.format, channels=self.channels, rate=self.rate,
                                            input_device_index=self.microphone_index,
                                            frames_per_buffer=self.frames_per_buffer, input=True)
        self.timer = TimeRuner(self.time_label)
        self.timer.timer_initial()

    def audio_record(self):
        while not self.stop_record:
            self.frame = self.audio_stream.read(self.frames_per_buffer)
            self.audio_frames.append(self.frame)
            self.timer.run_time()

        self.timer.timer_stop = True
        self.stop_record = True

        self.audio_stream.stop_stream()
        self.audio_stream.close()
        self.audio.terminate()
        wave_file = wave.open(f"temp_audio.wav", 'wb')
        wave_file.setnchannels(self.channels)
        wave_file.setsampwidth(self.audio.get_sample_size(self.format))
        wave_file.setframerate(self.rate)
        wave_file.writeframes(b''.join(self.audio_frames))
        wave_file.close()


class AudioPlayer:

    def __init__(self, time_label: object):
        self.frame = None
        self.wav_stream = None
        self.py_audio = None
        self.wav_file = None
        self.chunk = None

        self.time_label = time_label
        self.play_stop = False

    def play_initial(self):
        self.chunk = 1024
        self.wav_file = wave.open("temp_audio.wav", 'rb')
        self.py_audio = pyaudio.PyAudio()
        self.wav_stream = self.py_audio.open(format=self.py_audio.get_format_from_width(self.wav_file.getsampwidth()),
                                             channels=self.wav_file.getnchannels(), rate=self.wav_file.getframerate(),
                                             output=True)
        self.timer = TimeRuner(self.time)
        self.timer.timer_initial()

    def play_audio(self):
        while self.frame != "b''" or not self.play_stop:
            self.frame = self.wav_file.readframes(self.chunk)
            self.wav_stream.write(self.frame)
            self.time.run_time()

        self.play_stop = True
        self.time.timer_stop = True

        self.wav_file.close()
        self.wav_stream.close()
        self.py_audio.terminate()
