"""Fixed-column card grid (5 per row) with vertical scroll for extra rows."""

from __future__ import annotations

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import QGridLayout, QSizePolicy, QWidget

GRID_COLUMNS = 5
GRID_VISIBLE_ROWS = 4
GRID_MARGIN = 12
GRID_SPACING = 14
GRID_ASPECT = 16 / 9
FOOTER_HEIGHT = 56
GRID_INNER_WIDTH = 920


def fixed_card_size() -> QSize:
    """Card size derived from locked grid width (stable before first paint)."""
    usable = GRID_INNER_WIDTH - 2 * GRID_MARGIN
    card_w = (usable - (GRID_COLUMNS - 1) * GRID_SPACING) // GRID_COLUMNS
    card_h = max(1, int(card_w / GRID_ASPECT))
    return QSize(card_w, card_h)


def card_size_for_viewport(viewport_width: int, cols: int = GRID_COLUMNS) -> QSize:
    usable = max(1, viewport_width - 2 * GRID_MARGIN)
    card_w = (usable - (cols - 1) * GRID_SPACING) // cols
    card_h = max(1, int(card_w / GRID_ASPECT))
    return QSize(card_w, card_h)


def scroll_viewport_height(card_h: int, visible_rows: int = GRID_VISIBLE_ROWS) -> int:
    return (
        2 * GRID_MARGIN
        + visible_rows * card_h
        + max(0, visible_rows - 1) * GRID_SPACING
    )


def main_window_fixed_size(card_w: int, card_h: int) -> QSize:
    grid_w = (
        GRID_COLUMNS * card_w
        + (GRID_COLUMNS - 1) * GRID_SPACING
        + 2 * GRID_MARGIN
    )
    grid_h = scroll_viewport_height(card_h)
    return QSize(grid_w, grid_h + FOOTER_HEIGHT)


class FlowGridWidget(QWidget):
    """Top-left grid with a fixed number of columns per row."""

    def __init__(
        self,
        parent: QWidget | None = None,
        fixed_columns: int = GRID_COLUMNS,
        lock_card_size: bool = True,
    ) -> None:
        super().__init__(parent)
        self._fixed_columns = fixed_columns
        self._lock_card_size = lock_card_size
        self._reflowing = False
        self._card_widgets: list[QWidget] = []
        self._last_card_size = fixed_card_size()

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self._grid = QGridLayout(self)
        self._grid.setContentsMargins(GRID_MARGIN, GRID_MARGIN, GRID_MARGIN, GRID_MARGIN)
        self._grid.setHorizontalSpacing(GRID_SPACING)
        self._grid.setVerticalSpacing(GRID_SPACING)
        self._grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

    def card_size(self) -> QSize:
        return QSize(self._last_card_size)

    def relayout(self) -> None:
        self._reflow()

    def rebuild_cards(self, widgets: list[QWidget]) -> None:
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

    def _resolve_card_size(self) -> QSize:
        if self._lock_card_size:
            return fixed_card_size()
        width = max(self.width(), GRID_INNER_WIDTH)
        return card_size_for_viewport(width, self._fixed_columns)

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

            self._last_card_size = self._resolve_card_size()
            cols = self._fixed_columns
            align = Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft

            for i, child in enumerate(children):
                child.setFixedSize(self._last_card_size)
                child.show()
                row = i // cols
                col = i % cols
                self._grid.addWidget(child, row, col, align)

            rows = (len(children) + cols - 1) // cols
            total_h = (
                2 * GRID_MARGIN
                + rows * self._last_card_size.height()
                + max(0, rows - 1) * GRID_SPACING
            )
            self.setMinimumHeight(total_h)
            self.setMinimumWidth(
                cols * self._last_card_size.width()
                + (cols - 1) * GRID_SPACING
                + 2 * GRID_MARGIN
            )
            self._grid.setRowStretch(rows, 1)
            self.updateGeometry()
        finally:
            self._reflowing = False

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        if not self._lock_card_size:
            self._reflow()
