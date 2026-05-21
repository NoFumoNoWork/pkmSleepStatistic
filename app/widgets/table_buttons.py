"""Compact table action buttons."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QHBoxLayout, QToolButton, QWidget

# 添加记录历史：时钟 / 猫咪 / 删除 三个图标共用（改下面两个常量即可）
HISTORY_ACTION_ICON_PX = 22
HISTORY_ACTION_ICON_FONT_PT = 14


def _make_emoji_icon(character: str, px: int, font_pt: int) -> QIcon:
    pixmap = QPixmap(px, px)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    font = QFont("Segoe UI Emoji")
    font.setPointSize(font_pt)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), int(Qt.AlignmentFlag.AlignCenter), character)
    painter.end()
    return QIcon(pixmap)


def make_info_button(on_click: Callable[[], None]) -> QWidget:
    """Small info button centered in its own table cell."""
    cell = QWidget()
    layout = QHBoxLayout(cell)
    layout.setContentsMargins(2, 2, 2, 2)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    btn = QToolButton()
    btn.setObjectName("infoButton")
    btn.setText("i")
    btn.setFixedSize(24, 24)
    btn.clicked.connect(on_click)
    layout.addWidget(btn)
    return cell


def make_history_actions(
    on_edit_time: Callable[[], None],
    on_edit_team: Callable[[], None],
    on_delete: Callable[[], None],
    *,
    tip_edit_time: str = "",
    tip_edit_team: str = "",
    tip_delete: str = "",
) -> QWidget:
    """Clock / team / delete action buttons for history rows."""
    cell = QWidget()
    layout = QHBoxLayout(cell)
    layout.setContentsMargins(8, 6, 8, 8)
    layout.setSpacing(10)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    for emoji, tip, handler, danger in (
        ("🕐", tip_edit_time, on_edit_time, False),
        ("🐱", tip_edit_team, on_edit_team, False),
        ("❌", tip_delete, on_delete, True),
    ):
        btn = QToolButton()
        btn.setObjectName("tableActionButton")
        if danger:
            btn.setProperty("danger", True)
        btn.setIcon(
            _make_emoji_icon(emoji, HISTORY_ACTION_ICON_PX, HISTORY_ACTION_ICON_FONT_PT)
        )
        btn.setIconSize(QSize(HISTORY_ACTION_ICON_PX, HISTORY_ACTION_ICON_PX))
        btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        btn.setToolTip(tip)
        btn.setFixedSize(36, 36)
        btn.clicked.connect(handler)
        layout.addWidget(btn)

    return cell
