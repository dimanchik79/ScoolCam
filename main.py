import sys
import speech_recognition as sr

from os import path
from pygrabber.dshow_graph import FilterGraph

from PyQt5.QtWidgets import QApplication
from models import Configurations
from mainclass import StartWindow


def define_devices():
    available_cameras = {}
    available_microphone = {}
    devices = FilterGraph().get_input_devices()

    for device_index, device_name in enumerate(devices):
        available_cameras[device_index] = device_name
    for key, words in sr.Microphone.list_working_microphones().items():
        available_microphone[key] = words.encode('cp1251').decode('utf-8')
    return available_cameras, available_microphone


def start():
    cams, mics = define_devices()
    print(cams)
    print(mics)
    app = QApplication(sys.argv)
    main_window = StartWindow(cameras=cams, microphones=mics)
    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    start()
