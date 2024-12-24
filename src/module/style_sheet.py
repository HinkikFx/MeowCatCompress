from src.importer import *
from src.module import cfg

class StyleSheet(StyleSheetBase, Enum):
    SETTING_INTERFACE = "setting_interface"

    def path(self, theme=Theme.AUTO):
        theme = qconfig.theme if theme == Theme.AUTO else theme
        return f"{cfg.ROOT}\\data\\qss\\{theme.value.lower()}\\{self.value}.qss"
