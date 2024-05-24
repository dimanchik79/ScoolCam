from video import *
import subprocess
import os


def merge_audio_video():
    cmd = "ffmpeg -i temp_audio.wav -i temp_video.avi -c:v copy -c:a aac output.mp4"
    subprocess.call(cmd, shell=True)
    os.remove("temp_audio.wav")
    os.remove("temp_video.avi")


def start():
    camera = VideoCapture(cam_number=0)
    camera.video_save()


if __name__ == "__main__":
    start()

