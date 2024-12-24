from src.importer import *
from .validator import ExeValidator, ExeListValidator, StringValidator


def Info(self, types, time, title, content=''):
    if types == "S":
        InfoBar.success(
            title=title,
            content=content,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=time,
            parent=self
        )
    elif types == "E":
        InfoBar.error(
            title=title,
            content=content,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=time,
            parent=self
        )
    elif types == "W":
        InfoBar.warning(
            title=title,
            content=content,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=time,
            parent=self
        )

def open_file(self, file_path):
    if os.path.exists(file_path):
        os.startfile(file_path)
        Info(self, "S", 1000, self.tr("文件已打开!"))
        return True
    else:
        Info(self, "E", 3000, self.tr("找不到文件!"))
        return False

def get_version_type(version):
    if not os.path.exists('main.py'):
        return f'{version} REL'
    else:
        return f'{version} DEV'


class Language(Enum):
    CHINESE_SIMPLIFIED = QLocale(QLocale.Chinese, QLocale.China)
    CHINESE_TRADITIONAL = QLocale(QLocale.Chinese, QLocale.Taiwan)
    ENGLISH = QLocale(QLocale.English)


class LanguageSerializer(ConfigSerializer):
    def serialize(self, language):
        return language.value.name()

    def deserialize(self, value: str):
        return Language(QLocale(value))


class Config(QConfig):
    ############### CONFIG ITEMS ###############
    dpiScale = OptionsConfigItem(
        "Style", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)
    language = OptionsConfigItem(
        "Style", "Language", Language.ENGLISH, OptionsValidator(Language), LanguageSerializer(), restart=True)

    ############### APP INFO ###############
    ROOT = os.getcwd()
    IMAGE = os.path.join(ROOT, 'data/image')
    ICON = os.path.join(ROOT, 'data/image/icon.ico')

    APP_NAME = "MeowCatCompress"
    APP_VERSION = get_version_type("v1.0.0")
    APP_FONT = "SDK_SC_Web"

    ############### LINK CONFIG ###############
    URL_LATEST = "https://github.com/letheriver2007/MeowCatCompress/releases/latest"
    URL_WRITER = "https://github.com/letheriver2007"
    URL_REPO = "https://github.com/letheriver2007/MeowCatCompress"
    URL_RELEASES = "https://github.com/letheriver2007/MeowCatCompress/releases"
    URL_ISSUES = "https://github.com/letheriver2007/MeowCatCompress/issues"


cfg = Config()
cfg.themeColor.defaultValue = QColor("#FFC0CB")
cfg.set(cfg.themeColor, QColor("#FFC0CB"))
qconfig.load(f'{cfg.ROOT}/Config.json', cfg)
