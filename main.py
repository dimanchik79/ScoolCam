import sys
from typing import Tuple, Dict, Any

import speech_recognition as sr

from pygrabber.dshow_graph import FilterGraph
from PyQt5.QtWidgets import QApplication
from mainclass import StartWindow


def define_devices() -> tuple[dict[int, Any], dict[Any, Any]]:
    """Функция возвращает словарь камер и микрофонов на вашем компьютере"""
    available_cameras = {}
    available_microphone = {}
    devices = FilterGraph().get_input_devices()

    for device_index, device_name in enumerate(devices):
        available_cameras[device_index] = device_name
    for key, words in sr.Microphone.list_working_microphones().items():
        available_microphone[key] = words.encode('cp1251').decode('utf-8')
    return available_cameras, available_microphone


def start() -> None:
    """Функция запуска главного окна"""
    cams, mics = define_devices()
    # print(cams)
    # print(mics)
    app = QApplication(sys.argv)
    main_window = StartWindow(cameras=cams, microphones=mics)
    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    start()
