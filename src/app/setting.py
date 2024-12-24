from src.importer import *
from src.module import *


class Setting(SmoothScrollArea):
    def __init__(self, text, parent=None):
        super().__init__(parent=parent)
        self.parent = parent
        self.setObjectName(text)
        self.setWidgetResizable(True)

        self.scrollWidget = QWidget()
        self.scrollWidget.setObjectName('scrollWidget')
        self.setWidget(self.scrollWidget)
        self.expandLayout = ExpandLayout(self.scrollWidget)

        self.__initWidget()
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initWidget(self):
        self.PersonalInterface = SettingCardGroup(self.scrollWidget)
        self.themeColorCard = CustomColorSettingCard(
            cfg.themeColor,
            FluentIcon.PALETTE,
            self.tr('主题色'),
            self.tr('修改组件主题颜色')
        )
        self.zoomCard = ComboBoxSettingCard(
            cfg.dpiScale,
            FluentIcon.ZOOM,
            "DPI",
            self.tr("调整全局缩放"),
            texts=["100%", "125%", "150%", "175%", "200%", self.tr("跟随系统设置")]
        )
        self.languageCard = ComboBoxSettingCard(
            cfg.language,
            FluentIcon.LANGUAGE,
            self.tr('语言'),
            self.tr('界面显示语言'),
            texts=['简体中文', '繁體中文', 'English', self.tr('跟随系统设置')]
        )
        self.restartCard = PrimaryPushSettingCard(
            self.tr('重启程序'),
            FluentIcon.ROTATE,
            self.tr('重启程序'),
            self.tr('无奖竞猜，存在即合理')
        )

    def __initLayout(self):
        self.PersonalInterface.addSettingCard(self.themeColorCard)
        self.PersonalInterface.addSettingCard(self.zoomCard)
        self.PersonalInterface.addSettingCard(self.languageCard)
        self.PersonalInterface.addSettingCard(self.restartCard)

        self.expandLayout.setContentsMargins(20, 20, 20, 20)
        self.expandLayout.addWidget(self.PersonalInterface)

    def __connectSignalToSlot(self):
        self.themeColorCard.colorChanged.connect(lambda c: setThemeColor(c, lazy=True))
        self.zoomCard.comboBox.currentIndexChanged.connect(self.restart_application)
        self.languageCard.comboBox.currentIndexChanged.connect(self.restart_application)
        self.restartCard.clicked.connect(self.restart_application)

    def restart_application(self):
        current_process = QProcess()
        current_process.startDetached(sys.executable, sys.argv)
        sys.exit()
