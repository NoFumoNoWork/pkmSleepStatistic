"""Responsive left-to-right, top-to-bottom card grid from top-left."""

from __future__ import annotations

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import QGridLayout, QSizePolicy, QWidget


class FlowGridWidget(QWidget):
    """Container that reflows child widgets in a responsive grid (top-left aligned)."""

    def __init__(
        self,
        parent: QWidget | None = None,
        margin: int = 12,
        spacing: int = 14,
        aspect_ratio: float = 16 / 9,
        min_card_width: int = 160,
    ) -> None:
        super().__init__(parent)
        self._margin = margin
        self._spacing = spacing
        self._aspect = aspect_ratio
        self._min_card_width = min_card_width
        self._reflowing = False
        self._card_widgets: list[QWidget] = []

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self._grid = QGridLayout(self)
        self._grid.setContentsMargins(margin, margin, margin, margin)
        self._grid.setHorizontalSpacing(spacing)
        self._grid.setVerticalSpacing(spacing)
        self._grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

    def rebuild_cards(self, widgets: list[QWidget]) -> None:
        """Replace all cards and lay out once (avoids partial reflow glitches)."""
        for w in self._card_widgets:
            if w.parent() is self:
                self._grid.removeWidget(w)
            w.setParent(None)
        self._card_widgets = []
        for widget in widgets:
            widget.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            widget.setParent(self)
            widget.show()
            self._card_widgets.append(widget)
        self._reflow()

    def _card_size(self, width: int) -> QSize:
        usable = max(1, width - 2 * self._margin)
        cols = max(1, usable // (self._min_card_width + self._spacing))
        card_w = (usable - (cols - 1) * self._spacing) // cols
        card_h = max(1, int(card_w / self._aspect))
        return QSize(card_w, card_h)

    def _reflow(self) -> None:
        if self._reflowing:
            return
        self._reflowing = True
        try:
            children = list(self._card_widgets)
            while self._grid.count():
                self._grid.takeAt(0)

            for r in range(self._grid.rowCount()):
                self._grid.setRowStretch(r, 0)

            if not children:
                self.setMinimumHeight(120)
                return

            width = max(self.width(), self._min_card_width + 2 * self._margin)
            card_size = self._card_size(width)
            cols = max(
                1,
                (width - 2 * self._margin + self._spacing)
                // (card_size.width() + self._spacing),
            )
            align = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft

            for i, child in enumerate(children):
                child.setFixedSize(card_size)
                child.show()
                row = i // cols
                col = i % cols
                self._grid.addWidget(child, row, col, align)

            rows = (len(children) + cols - 1) // cols
            total_h = (
                2 * self._margin
                + rows * card_size.height()
                + max(0, rows - 1) * self._spacing
            )
            self.setMinimumHeight(total_h)
            self._grid.setRowStretch(rows, 1)
            self.updateGeometry()
        finally:
            self._reflowing = False

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._reflow()
