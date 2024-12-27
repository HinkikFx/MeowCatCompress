from . import *
from src.importer import *
from src.module import *


class Main(MSFluentWindow):
    def __init__(self):
        super().__init__()
        self.handleFontCheck()

        self.titleBar.maxBtn.setHidden(True)
        self.titleBar.maxBtn.setDisabled(True)
        self.titleBar.setDoubleClickEnabled(False)
        self.setMicaEffectEnabled(True)
        self.setResizeEnabled(False)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowMaximizeButtonHint)
        self.setWindowTitle(cfg.APP_NAME)
        self.setFixedSize(1280, 768)
        self.setWindowIcon(QIcon(cfg.ICON))
        self.handleCenterWindow()
        self.compressorWidget = CompressorWidget(self)
        self.addSubInterface(self.compressorWidget, FluentIcon.FOLDER, self.tr('压缩工具'), FluentIcon.FOLDER_OPEN)
        setTheme(cfg.get(cfg.themeMode))
        setThemeColor(cfg.get(cfg.themeColor))

        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(200, 200))
        self.splashScreen.raise_()
        self.show()
        QApplication.processEvents()
        self.__initNavigation()
        self.splashScreen.finish()
        self.__initInfo()

    def __initNavigation(self):
        self.workInterface = Work('WorkInterface', self)
        self.addSubInterface(self.workInterface, FluentIcon.HOME, self.tr('主页'), FluentIcon.HOME_FILL)
        self.settingInterface = Setting('SettingInterface', self)
        self.addSubInterface(self.settingInterface, FluentIcon.SETTING, self.tr('设置'), FluentIcon.SETTING)
        StyleSheet.SETTING_INTERFACE.apply(self.settingInterface)
        self.aboutInterface = About('AboutInterface', self)
        self.addSubInterface(self.aboutInterface, FluentIcon.INFO, self.tr('关于'), FluentIcon.INFO)

        self.navigationInterface.addItem(
            routeKey='theme',
            icon=FluentIcon.CONSTRACT,
            text=self.tr('主题'),
            onClick=self.handleThemeChanged,
            selectable=False,
            position=NavigationItemPosition.BOTTOM
        )

    def __initInfo(self):
        pass

    def handleCenterWindow(self):
        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def handleFontCheck(self):
        isSetupFont = False
        registry_keys = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"),
            (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows NT\CurrentVersion\Fonts")
        ]
        try:
            for hkey, sub_key in registry_keys:
                reg = winreg.ConnectRegistry(None, hkey)
                reg_key = winreg.OpenKey(reg, sub_key)
                i = 0
                while True:
                    try:
                        name, data, types = winreg.EnumValue(reg_key, i)
                        if cfg.APP_FONT.lower() in name.lower():
                            isSetupFont = True
                        i += 1
                    except OSError:
                        break
                winreg.CloseKey(reg_key)
        except Exception as e:
            Info(self, 'E', 3000, self.tr('检查字体失败: '), str(e))

        if not isSetupFont:
            subprocess.run(f'cd {cfg.ROOT}/src/patch/font && start zh-cn.ttf', shell=True)
            sys.exit()

    def handleThemeChanged(self):
        new_theme = Theme.LIGHT if cfg.get(cfg.themeMode) == Theme.DARK else Theme.DARK
        setTheme(new_theme)
        cfg.set(cfg.themeMode, new_theme)
        cfg.save() # Bug
