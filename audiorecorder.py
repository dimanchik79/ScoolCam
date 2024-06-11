import wave
import pyaudio


class AudioRecord:
    def __init__(self, microphone_index):
        self.wave_file = None
        self.frame = None
        self.audio_stream = None
        self.audio_frames = None
        self.format = None
        self.frames_per_buffer = None
        self.channels = None
        self.rate = None
        self.audio = None

        self.microphone_index = microphone_index

    def audiorecord_init(self):
        self.audio = pyaudio.PyAudio()
        self.rate = 44100
        self.channels = 1
        self.frames_per_buffer = 1024
        self.format = pyaudio.paInt16
        self.audio_stream = self.audio.open(format=self.format, channels=self.channels, rate=self.rate,
                                            input_device_index=self.microphone_index,
                                            frames_per_buffer=self.frames_per_buffer, input=True)
        self.wave_file = wave.open(f"temp_audio.wav", 'wb')
        self.wave_file.setnchannels(self.channels)
        self.wave_file.setsampwidth(self.audio.get_sample_size(self.format))
        self.wave_file.setframerate(self.rate)

    def audio_record(self):
        self.frame = self.audio_stream.read(self.frames_per_buffer)
        self.wave_file.writeframes(b''.join([self.frame]))

    def stop_record(self):
        self.audio_stream.stop_stream()
        self.audio_stream.close()
        self.audio.terminate()
        self.wave_file.close()


class AudioPlayer:

    def __init__(self):
        self.frame = None
        self.wav_stream = None
        self.py_audio = None
        self.wav_file = None
        self.chunk = None

    def player_init(self):
        self.chunk = 1024
        self.wav_file = wave.open("temp_audio.wav", 'rb')
        self.py_audio = pyaudio.PyAudio()
        self.wav_stream = self.py_audio.open(format=self.py_audio.get_format_from_width(self.wav_file.getsampwidth()),
                                             channels=self.wav_file.getnchannels(), rate=self.wav_file.getframerate(),
                                             output=True)

    def play_audio(self):
        self.frame = self.wav_file.readframes(self.chunk)
        self.wav_stream.write(self.frame)

    def stop_player(self):
        self.frame = None
        self.wav_stream.close()
        self.py_audio.terminate()
        self.wav_file.close()

