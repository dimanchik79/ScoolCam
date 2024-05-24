import pyaudio
import wave
import threading


class AudioRecorder:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.rate = 44100
        self.channels = 2
        self.frames_per_buffer = 1024
        self.format = pyaudio.paInt16
        self.audio_frames = []
        self.open = True
        self.audio_stream = self.audio.open(format=self.format, channels=self.channels,
                                            rate=self.rate, input=True,
                                            frames_per_buffer=self.frames_per_buffer)

    def record(self):
        while self.open:
            data = self.audio_stream.read(self.frames_per_buffer)
            self.audio_frames.append(data)

    def stop(self):
        if self.open:
            self.open = False
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            self.audio.terminate()
            wave_file = wave.open("audio_0.wav", 'wb')
            wave_file.setnchannels(self.channels)
            wave_file.setsampwidth(self.audio.get_sample_size(self.format))
            wave_file.setframerate(self.rate)
            wave_file.writeframes(b''.join(self.audio_frames))
            wave_file.close()
