"""Read-only table cell helpers."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem


def readonly_item(text: str = "") -> QTableWidgetItem:
    item = QTableWidgetItem(text)
    item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
    return item
