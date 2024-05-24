import cv2
import pyaudio
import wave


class VideoRecorder:
    def __init__(self, cam_number: int):
        # Параметры видео
        self.cam_number = cam_number
        self.cap = cv2.VideoCapture(self.cam_number)
        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.out = cv2.VideoWriter('camera_0.avi', self.fourcc, 25.0, (640, 480))

        # Параметры аудио
        self.audio = pyaudio.PyAudio()
        self.rate = 44100
        self.channels = 1
        self.frames_per_buffer = 4048
        self.format = pyaudio.paInt16
        self.audio_frames = []
        self.open = True
        self.audio_stream = self.audio.open(format=self.format, channels=self.channels,
                                            rate=self.rate, input=True,
                                            input_device_index=1,
                                            frames_per_buffer=self.frames_per_buffer)

    def video_save(self):
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        while True:
            ret, frame = self.cap.read()
            self.out.write(frame)
            data = self.audio_stream.read(self.frames_per_buffer)
            self.audio_frames.append(data)

            cv2.imshow("Camera-0", frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

        self.audio_stream.stop_stream()
        self.audio_stream.close()
        self.audio.terminate()

        wave_file = wave.open("audio_0.wav", 'wb')
        wave_file.setnchannels(self.channels)
        wave_file.setsampwidth(self.audio.get_sample_size(self.format))
        wave_file.setframerate(self.rate)
        wave_file.writeframes(b''.join(self.audio_frames))
        wave_file.close()
        self.out.release()
        self.cap.release()
        cv2.destroyAllWindows()
