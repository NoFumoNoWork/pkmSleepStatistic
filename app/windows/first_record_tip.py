"""First successful record tip dialog."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app import strings as S
from app.services import AppService


class FirstRecordTipDialog(QDialog):
    def __init__(self, service: AppService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._service = service
        self.setWindowTitle(S.TIP_TITLE)
        self.setMinimumWidth(380)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(S.TIP_FIRST_RECORD))
        self._dont_show = QCheckBox(S.TIP_DONT_SHOW)
        layout.addWidget(self._dont_show)
        row = QHBoxLayout()
        row.addStretch()
        ok = QPushButton(S.BTN_OK)
        ok.setObjectName("primaryButton")
        ok.clicked.connect(self._on_ok)
        row.addWidget(ok)
        layout.addLayout(row)

    def _on_ok(self) -> None:
        if self._dont_show.isChecked():
            self._service.dismiss_first_record_tip()
        self.accept()
