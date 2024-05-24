from video import *


def start():
    camera = VideoCapture(cam_number=0)
    camera.video_save()


if __name__ == "__main__":
    start()

