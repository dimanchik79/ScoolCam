from typing import Dict

import cv2
import pyaudio
import wave


class VideoRecorder:
    def __init__(self, current_frame):
        # Параметры видео
        self.audio_stream = None
        self.audio_frames = None
        self.format = None
        self.frames_per_buffer = None
        self.channels = None
        self.rate = None
        self.audio = None
        self.out = None
        self.fps = None
        self.height = None
        self.width = None
        self.frame = current_frame

    def videorecord_init(self):
        self.width = 1024
        self.height = 768
        self.fps = 21
        fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
        self.out = cv2.VideoWriter('camera_0.avi', fourcc, self.fps, (self.width, self.height))

    def video_save(self):
        self.capture.set(cv2.CAP_PROP_FPS, self.fps)
        self.out.write(frame)
        data = self.audio_stream.read(self.frames_per_buffer)
        self.audio_frames.append(data)

    def stop_record(self):
        self.audio_stream.stop_stream()
        self.audio_stream.close()
        self.audio.terminate()

        self.audio_stream.stop_stream()
        self.audio_stream.close()
        self.audio.terminate()
        wave_file = wave.open("temp.wav", 'wb')
        wave_file.setnchannels(self.channels)
        wave_file.setsampwidth(self.audio.get_sample_size(self.format))
        wave_file.setframerate(self.rate)
        wave_file.writeframes(b''.join(self.audio_frames))
        wave_file.close()
        self.out[0].release()
        #
        # subprocess.run(f"ffmpeg -i {self.video_file[0]} -i temp.wav -c copy {self.video_file[0]}")
