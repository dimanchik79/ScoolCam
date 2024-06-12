from typing import Dict

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QListWidgetItem


class CamSelect(QDialog):
    def __init__(self, cameras: Dict):
        super().__init__()
        self.cameras = cameras
        uic.loadUi("GUI/camselect.ui", self)
        self.setFixedSize(400, 552)
        self.add_item()

    def add_item(self):
        for key, cam in self.cameras.items():
            item = QListWidgetItem(cam)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.camplace.addItem(item)