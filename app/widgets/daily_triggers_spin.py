"""Optional expected daily triggers: 0.1–10.0 or unset."""

from __future__ import annotations

from typing import Optional

from PySide6.QtWidgets import QDoubleSpinBox


class DailyTriggersSpinBox(QDoubleSpinBox):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setRange(0.0, 10.0)
        self.setDecimals(1)
        self.setSingleStep(0.1)
        self.setSpecialValueText("—")
        self.setValue(0.0)

    def optional_value(self) -> Optional[float]:
        v = round(self.value(), 1)
        if v <= 0:
            return None
        return min(10.0, v)

    def set_optional_value(self, value: Optional[float]) -> None:
        if value is None or value <= 0:
            self.setValue(0.0)
        else:
            self.setValue(min(10.0, float(value)))
