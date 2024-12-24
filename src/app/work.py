from src.importer import *
from src.module import *


class Work(QWidget):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(text)

        self.__initWidget()

    def __initWidget(self):


        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.main_layout = QVBoxLayout(self)

        self.setLayout(self.main_layout)

    def __connectSignalToSlot(self):
        pass
