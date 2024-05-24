from classes import VideoRecorder
import pyaudio
import subprocess
import os


def merge_audio_video():
    cmd = "ffmpeg -i camera_0.wav -i camera_0.avi -c:v copy -c:a aac record_comera_0.avi"
    subprocess.call(cmd, shell=True)
    os.remove("camera_0.wav")
    os.remove("camera_0.avi")


def start():

    camera = VideoRecorder(cam_number=0)
    camera.video_save()
    merge_audio_video()


if __name__ == "__main__":
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        print(i, p.get_device_info_by_index(i))
    start()

