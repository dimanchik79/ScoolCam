from typing import List

import speech_recognition as sr
import subprocess
import os

import cv2

from videorecorder import VideoRecorder


class VideoStream:
    def __init__(self, port: List):
        self.port = port
        self.video = []
        for port in self.port:
            self.video.append(cv2.VideoCapture(port))
            print(port)

    def record(self):
        while True:
            for index in range(0, len(self.video)):
                ret, frame = self.video[index].read()


def main():
    pass


def save_sound():
    camera = VideoRecorder(cam_number=0)
    camera.video_save()
    cmd = "ffmpeg -y -i camera_0.avi -i audio_0.wav -c:v copy -c:a aac record_camera_0.avi"
    subprocess.call(cmd, shell=True)
    os.remove("camera_0.wav")
    os.remove("camera_0.avi")


if __name__ == "__main__":
    main()
