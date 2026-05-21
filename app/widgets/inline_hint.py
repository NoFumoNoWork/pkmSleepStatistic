"""Non-modal inline hint popup."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class InlineHintPopup(QFrame):
    def __init__(self, text: str, parent=None) -> None:
        super().__init__(parent, Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setObjectName("inlineHint")
        self.setStyleSheet(
            """
            QFrame#inlineHint {
                background: #fffff0;
                border: 1px solid #e0c878;
                border-radius: 8px;
                padding: 4px;
            }
            QLabel { color: #4a4020; font-size: 9pt; }
            """
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        label = QLabel(text)
        label.setWordWrap(True)
        layout.addWidget(label)
        self.adjustSize()

    def show_near(self, widget) -> None:
        pos = widget.mapToGlobal(widget.rect().bottomLeft())
        self.move(pos.x(), pos.y() + 4)
        self.show()
