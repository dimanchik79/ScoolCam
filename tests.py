from typing import List

import speech_recognition as sr
import subprocess
import os

import cv2

from videorecorder import VideoRecorder


class VideoStream:
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def record(self):
        while True:
            ret, frame = self.video.read()
            if ret:
                image = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                image = cv2.flip(image, 1)
                cv2.imshow('frame', image)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        self.video.release()
        cv2.destroyAllWindows()


def main():
    video = VideoStream()
    video.record()


def save_sound():
    camera = VideoRecorder(cam_number=0)
    camera.video_save()
    cmd = "ffmpeg -y -i camera_0.avi -i audio_0.wav -c:v copy -c:a aac record_camera_0.avi"
    subprocess.call(cmd, shell=True)
    os.remove("camera_0.wav")
    os.remove("camera_0.avi")


if __name__ == "__main__":
    main()
