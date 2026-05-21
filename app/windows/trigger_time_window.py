"""Trigger time input dialog."""

from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import QDateTime
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QDateTimeEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app import strings as S


class TriggerTimeWindow(QDialog):
    def __init__(
        self,
        initial: datetime | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(S.TRIGGER_TIME_TITLE)
        self.setMinimumWidth(360)
        self._result_time: datetime | None = None
        self._build_ui(initial or datetime.now())

    def _build_ui(self, initial: datetime) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        self._datetime = QDateTimeEdit()
        self._datetime.setCalendarPopup(True)
        self._datetime.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self._datetime.setDateTime(
            QDateTime(
                initial.year,
                initial.month,
                initial.day,
                initial.hour,
                initial.minute,
                initial.second,
            )
        )
        layout.addWidget(self._datetime)

        shortcut_row = QHBoxLayout()
        now_btn = QPushButton(S.BTN_USE_NOW)
        now_btn.clicked.connect(self._fill_now)
        shortcut_row.addWidget(now_btn)
        shortcut_row.addStretch()
        layout.addLayout(shortcut_row)

        btn_row = QHBoxLayout()
        cancel = QPushButton(S.BTN_CANCEL)
        cancel.clicked.connect(self.reject)
        confirm = QPushButton(S.BTN_CONFIRM)
        confirm.setObjectName("primaryButton")
        confirm.clicked.connect(self._on_confirm)
        btn_row.addWidget(cancel)
        btn_row.addStretch()
        btn_row.addWidget(confirm)
        layout.addLayout(btn_row)

    def _fill_now(self) -> None:
        now = datetime.now()
        self._datetime.setDateTime(
            QDateTime(now.year, now.month, now.day, now.hour, now.minute, now.second)
        )

    def _on_confirm(self) -> None:
        qdt = self._datetime.dateTime()
        self._result_time = datetime(
            qdt.date().year(),
            qdt.date().month(),
            qdt.date().day(),
            qdt.time().hour(),
            qdt.time().minute(),
            qdt.time().second(),
        )
        self.accept()

    def selected_time(self) -> datetime | None:
        return self._result_time
