"""Application bootstrap: tray, hotkey, main window."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QApplication, QMenu, QMessageBox, QSystemTrayIcon

from app import strings as S
from app.database import Database
from app.services import AppService
from app.styles.theme import APP_STYLESHEET
from app.system.hotkey import setup_global_hotkey
from app.windows.main_window import MainWindow


def default_db_path() -> Path:
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).parent
    else:
        base = Path(__file__).resolve().parent.parent
    data_dir = base / "data"
    return data_dir / "pokemon_sleep.db"


class PokemonSleepApp:
    def __init__(self) -> None:
        self.qt_app = QApplication(sys.argv)
        self.qt_app.setQuitOnLastWindowClosed(False)
        self.qt_app.setApplicationName(S.APP_NAME)
        self.qt_app.setStyle("Fusion")
        self.qt_app.setStyleSheet(APP_STYLESHEET)

        self._db = Database(default_db_path())
        self._service = AppService(self._db)
        self._hotkey_filter = None

        self._main = MainWindow(self._service)
        self._main.toggle_visibility_requested.connect(self._on_close_to_tray)

        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.warning(
                None,
                "系统托盘不可用",
                "未检测到系统托盘，应用仍可运行，但关闭窗口后请重新启动程序。",
            )

        self._tray = QSystemTrayIcon(self._create_tray_icon())
        self._tray.setToolTip(S.APP_NAME)
        menu = QMenu()
        open_action = QAction(S.TRAY_OPEN, self._tray)
        open_action.triggered.connect(self.show_main_window)
        exit_action = QAction(S.TRAY_EXIT, self._tray)
        exit_action.triggered.connect(self.quit_app)
        menu.addAction(open_action)
        menu.addSeparator()
        menu.addAction(exit_action)
        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._on_tray_activated)
        self._tray.show()

        self._hotkey_filter = setup_global_hotkey(
            self.qt_app, self.toggle_main_window
        )

    @staticmethod
    def _create_tray_icon() -> QIcon:
        from PySide6.QtGui import QColor, QPixmap, QPainter

        pix = QPixmap(32, 32)
        pix.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pix)
        painter.setBrush(QColor(79, 110, 247))
        painter.setPen(QColor(60, 80, 200))
        painter.drawRoundedRect(2, 2, 28, 28, 8, 8)
        painter.setPen(QColor(255, 255, 255))
        font = painter.font()
        font.setBold(True)
        font.setPointSize(14)
        painter.setFont(font)
        painter.drawText(pix.rect(), 0x0084, "P")
        painter.end()
        return QIcon(pix)

    def show_main_window(self) -> None:
        self._main.show()
        self._main.raise_()
        self._main.activateWindow()

    def hide_main_window(self) -> None:
        self._main.hide()

    def toggle_main_window(self) -> None:
        if self._main.isVisible() and not self._main.isMinimized():
            self.hide_main_window()
        else:
            self.show_main_window()

    def _on_close_to_tray(self) -> None:
        self.hide_main_window()
        if self._service.get_settings().show_tray_minimize_tip:
            self._tray.showMessage(
                S.APP_NAME,
                S.TRAY_STARTED,
                QSystemTrayIcon.MessageIcon.Information,
                3000,
            )
            self._service.dismiss_tray_minimize_tip()

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_main_window()

    def quit_app(self) -> None:
        if self._hotkey_filter:
            self._hotkey_filter.unregister()
        self._tray.hide()
        self.qt_app.quit()

    def run(self) -> int:
        self.show_main_window()
        return self.qt_app.exec()
