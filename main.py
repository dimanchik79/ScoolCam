import sys
import pyaudio
import subprocess
import os

from os import path
from PyQt5.QtWidgets import QApplication
from gui import StartWindow

from videorecorder import VideoRecorder


def start():
    app = QApplication(sys.argv)
    main_window = StartWindow()
    main_window.show()
    sys.exit(app.exec())

    # camera = VideoRecorder(cam_number=0)
    # camera.video_save()

    # cmd = "ffmpeg -i camera_0.wav -i camera_0.avi -c:v copy -c:a aac record_camera_0.avi"
    # subprocess.call(cmd, shell=True)
    # os.remove("camera_0.wav")
    # os.remove("camera_0.avi")


if __name__ == "__main__":
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        print(p.get_device_info_by_index(i))
    start()
