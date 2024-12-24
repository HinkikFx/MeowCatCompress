from src.importer import *
from src.module import *


class About_Background(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pixmap = QPixmap(os.path.join(cfg.IMAGE, 'bg_about.png'))
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 20, 20)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, self.width(), self.height(), pixmap)

        painter.setPen(Qt.white)
        painter.setFont(QFont(cfg.APP_FONT, 45))
        painter.drawText(self.rect().adjusted(0, -30, 0, 0), Qt.AlignHCenter | Qt.AlignVCenter, cfg.APP_NAME)
        painter.setFont(QFont(cfg.APP_FONT, 30))
        painter.drawText(self.rect().adjusted(0, 120, 0, 0), Qt.AlignHCenter | Qt.AlignVCenter, cfg.APP_VERSION)


class About(QWidget):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(text)

        self.__initWidget()

    def __initWidget(self):
        self.about_image = About_Background()
        self.about_image.setFixedSize(1100, 500)

        self.link_writer = PushButton(FluentIcon.HOME, self.tr('   作者主页'))
        self.link_repo = PushButton(FluentIcon.GITHUB, self.tr('   项目仓库'))
        self.link_releases = PushButton(FluentIcon.MESSAGE, self.tr('   版本发布'))
        self.link_issues = PushButton(FluentIcon.HELP, self.tr('   反馈交流'))

        for link_button in [self.link_writer, self.link_repo, self.link_releases, self.link_issues]:
            link_button.setFixedSize(260, 70)
            link_button.setIconSize(QSize(16, 16))
            link_button.setFont(QFont(f'{cfg.APP_FONT}', 12))
            setCustomStyleSheet(link_button, 'PushButton{border-radius: 12px}', 'PushButton{border-radius: 12px}')

        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.image_layout = QVBoxLayout()
        self.image_layout.addWidget(self.about_image, alignment=Qt.AlignHCenter)

        self.info_button_layout = QHBoxLayout()
        self.info_button_layout.addWidget(self.link_writer)
        self.info_button_layout.addWidget(self.link_repo)
        self.info_button_layout.addWidget(self.link_releases)
        self.info_button_layout.addWidget(self.link_issues)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.addLayout(self.image_layout)
        self.main_layout.addSpacing(20)
        self.main_layout.addLayout(self.info_button_layout)
        self.setLayout(self.main_layout)

    def __connectSignalToSlot(self):
        self.link_writer.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(cfg.URL_WRITER)))
        self.link_repo.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(cfg.URL_REPO)))
        self.link_releases.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(cfg.URL_RELEASES)))
        self.link_issues.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(cfg.URL_ISSUES)))
