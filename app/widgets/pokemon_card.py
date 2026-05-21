"""Pokémon card widget with selection and overlay trigger-count badge."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont, QResizeEvent
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
)


class PokemonCard(QFrame):
    clicked_body = Signal(int)
    clicked_count = Signal(int)

    _BADGE_W = 40
    _BADGE_H = 30
    _BADGE_INSET = 6

    _SPECIES_INSET = 8

    def __init__(
        self,
        pokemon_id: int,
        nickname: str,
        species: str,
        is_skill_type: bool,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.pokemon_id = pokemon_id
        self.is_skill_type = is_skill_type
        self._selected = False
        self._record_mode = False
        self._trigger_count = 0
        self._hover = False

        self.setObjectName("PokemonCard")
        self.setProperty("skillType", "true" if is_skill_type else "false")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(30, 40, 80, 50))
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(0)

        self._name_label = QLabel(nickname)
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        self._name_label.setFont(font)
        self._name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._name_label.setWordWrap(True)
        self._name_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self._name_label, 1)

        # 左下角种族（叠加层，小字灰色）
        self._species_label = QLabel(species, self)
        species_font = QFont()
        species_font.setPointSize(9)
        self._species_label.setFont(species_font)
        self._species_label.setStyleSheet("color: #8a919e; background: transparent;")
        self._species_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom
        )
        self._species_label.adjustSize()

        # 叠加层：不参与布局，固定在卡片右下角之上
        self._count_btn = QPushButton("0", self)
        self._count_btn.setObjectName("triggerCountBadge")
        self._count_btn.setFixedSize(self._BADGE_W, self._BADGE_H)
        self._count_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._count_btn.clicked.connect(self._on_count_clicked)
        self._count_btn.hide()
        self._apply_badge_style()
        self._position_overlays()

        self._apply_style()
        self._update_skill_glow()

    def set_nickname(self, nickname: str) -> None:
        self._name_label.setText(nickname)

    def set_species(self, species: str) -> None:
        self._species_label.setText(species)
        self._species_label.adjustSize()
        self._position_overlays()

    def set_record_mode(self, enabled: bool) -> None:
        self._record_mode = enabled
        self._count_btn.setVisible(enabled)
        if enabled:
            self._count_btn.raise_()
            self._position_overlays()
        if not enabled:
            self.set_selected(False)
            self.set_trigger_count(0)

    def set_selected(self, selected: bool) -> None:
        self._selected = selected
        self._apply_style()

    def is_selected(self) -> bool:
        return self._selected

    def trigger_count(self) -> int:
        return self._trigger_count

    def set_trigger_count(self, count: int) -> None:
        self._trigger_count = count
        self._count_btn.setText(str(count))
        if self._record_mode:
            self._count_btn.raise_()

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._position_overlays()

    def _position_overlays(self) -> None:
        self._species_label.adjustSize()
        sw = self._species_label.width()
        sh = self._species_label.height()
        self._species_label.move(
            self._SPECIES_INSET,
            max(0, self.height() - sh - self._SPECIES_INSET),
        )

        x = self.width() - self._BADGE_W - self._BADGE_INSET
        y = self.height() - self._BADGE_H - self._BADGE_INSET
        self._count_btn.move(max(0, x), max(0, y))
        self._species_label.show()
        self._species_label.raise_()
        if self._record_mode:
            self._count_btn.raise_()

    def enterEvent(self, event) -> None:
        self._hover = True
        self._apply_style()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._hover = False
        self._apply_style()
        super().leaveEvent(event)

    def mousePressEvent(self, event) -> None:
        if not self.isVisible() or self.parent() is None:
            return
        if event.button() == Qt.MouseButton.LeftButton:
            w = self.childAt(event.position().toPoint())
            while w is not None:
                if w is self._count_btn or w is self._species_label:
                    super().mousePressEvent(event)
                    return
                w = w.parent()  # type: ignore[assignment]
            self.clicked_body.emit(self.pokemon_id)
        super().mousePressEvent(event)

    def _on_count_clicked(self) -> None:
        self.clicked_count.emit(self.pokemon_id)

    def _apply_badge_style(self) -> None:
        self._count_btn.setStyleSheet(
            """
            QPushButton#triggerCountBadge {
                background: #4f6ef7;
                color: #ffffff;
                border: 2px solid #ffffff;
                border-radius: 8px;
                font-weight: bold;
                font-size: 11pt;
                padding: 0;
            }
            QPushButton#triggerCountBadge:hover {
                background: #3d5ce6;
            }
            QPushButton#triggerCountBadge:pressed {
                background: #2f4ed4;
            }
            """
        )

    def _apply_style(self) -> None:
        if self._selected:
            bg = "qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #e8f0ff, stop:1 #d0dcff)"
            border = "2px solid #4f6ef7"
        elif self._hover:
            bg = "qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #ffffff, stop:1 #e8eeff)"
            border = "1px solid #8aa8ff"
        else:
            bg = "qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #ffffff, stop:1 #f0f3fa)"
            border = "1px solid #d0d8ea"
        self.setStyleSheet(
            f"""
            PokemonCard {{
                background: {bg};
                border: {border};
                border-radius: 14px;
            }}
            """
        )

    def _update_skill_glow(self) -> None:
        effect = self.graphicsEffect()
        if isinstance(effect, QGraphicsDropShadowEffect):
            if self.is_skill_type:
                effect.setColor(QColor(124, 92, 255, 120))
                effect.setBlurRadius(28)
            else:
                effect.setColor(QColor(30, 40, 80, 50))
                effect.setBlurRadius(18)
