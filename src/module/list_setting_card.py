from src.importer import *


class ListItem(QWidget):
    removed = Signal(QWidget)

    def __init__(self, game: str, parent=None):
        super().__init__(parent=parent)
        self.game = game
        self.hBoxLayout = QHBoxLayout(self)
        self.gameLabel = QLabel(game, self)
        self.removeButton = PrimaryToolButton(FluentIcon.CLOSE, self)

        self.removeButton.setFixedSize(39, 29)
        self.removeButton.setIconSize(QSize(12, 12))

        self.setFixedHeight(53)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        self.hBoxLayout.setContentsMargins(48, 0, 60, 0)
        self.hBoxLayout.addWidget(self.gameLabel, 0, Qt.AlignLeft)
        self.hBoxLayout.addSpacing(16)
        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.removeButton, 0, Qt.AlignRight)
        self.hBoxLayout.setAlignment(Qt.AlignVCenter)

        self.removeButton.clicked.connect(lambda: self.removed.emit(self))


class ListSettingCard(ExpandSettingCard):
    listChanged = Signal(list)

    def __init__(self, icon: FluentIcon, configItem: ConfigItem, title: str, content: str = None, directory="./", parent=None):
        super().__init__(icon, title, content, parent)
        self.configItem = configItem
        self._dialogDirectory = directory
        self.addListButton = PushButton(self.tr('添加'), self, FluentIcon.ADD)
        self.lists = qconfig.get(configItem).copy()   # type:List[str]

        self.addWidget(self.addListButton)
        self.viewLayout.setSpacing(0)
        self.viewLayout.setAlignment(Qt.AlignTop)
        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        for game in self.lists:
            self.__addListItem(game)

        self.addListButton.clicked.connect(self.__showgameDialog)

    def __showgameDialog(self):
        game, _ = QFileDialog.getOpenFileName(
            self, self.tr("选择游戏程序目录"), self._dialogDirectory, "Executable Files (*.exe)")

        if not game or game in self.lists:
            return

        self.__addListItem(game)
        self.lists.append(game)
        qconfig.set(self.configItem, self.lists)
        self.listChanged.emit(self.lists)

    def __addListItem(self, game: str):
        item = ListItem(game, self.view)
        item.removed.connect(self.__removegame)
        self.viewLayout.addWidget(item)
        item.show()
        self._adjustViewSize()

    def __removegame(self, item: ListItem):
        if item.game not in self.lists:
            return

        self.lists.remove(item.game)
        self.viewLayout.removeWidget(item)
        item.deleteLater()
        self._adjustViewSize()

        self.listChanged.emit(self.lists)
        qconfig.set(self.configItem, self.lists)
