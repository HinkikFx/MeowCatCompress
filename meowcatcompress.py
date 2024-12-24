import os
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QLocale, QTranslator
from qfluentwidgets import FluentTranslator
from src.app.main import Main
from src.module.config import cfg

if cfg.get(cfg.dpiScale) != "Auto":
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))

app = QApplication(sys.argv)
app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)

locale = cfg.get(cfg.language).value
translator = FluentTranslator(locale)
localTranslator = QTranslator()
localTranslator.load(f"data\\translate\\{locale.name()}.qm")

app.installTranslator(translator)
app.installTranslator(localTranslator)

window = Main()
window.show()
sys.exit(app.exec())
