"""Create new Pokémon dialog."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app import strings as S
from app.services import AppService
from app.widgets.daily_triggers_spin import DailyTriggersSpinBox
from app.widgets.inline_hint import InlineHintPopup


class CreatePokemonWindow(QDialog):
    def __init__(self, service: AppService, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._service = service
        self._hint: InlineHintPopup | None = None
        self.setWindowTitle(S.CREATE_TITLE)
        self.setMinimumWidth(400)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(12)

        self._species = QLineEdit()
        self._species.setPlaceholderText(S.PLACEHOLDER_SPECIES)
        form.addRow(S.LABEL_SPECIES, self._species)

        self._nickname = QLineEdit()
        self._nickname.setPlaceholderText(S.PLACEHOLDER_NICKNAME)
        form.addRow(S.LABEL_NICKNAME, self._nickname)

        self._skill_type = QCheckBox(S.LABEL_SKILL_TYPE)
        form.addRow("", self._skill_type)

        daily_row = QHBoxLayout()
        self._daily = DailyTriggersSpinBox()
        daily_row.addWidget(self._daily)

        info_btn = QToolButton()
        info_btn.setObjectName("infoButton")
        info_btn.setText("i")
        info_btn.clicked.connect(self._toggle_hint)
        daily_row.addWidget(info_btn)
        daily_row.addStretch()
        form.addRow(S.LABEL_DAILY_TRIGGERS, daily_row)

        layout.addLayout(form)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        save_btn = buttons.button(QDialogButtonBox.StandardButton.Save)
        if save_btn:
            save_btn.setObjectName("primaryButton")
            save_btn.setText(S.BTN_SAVE)
        cancel_btn = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        if cancel_btn:
            cancel_btn.setText(S.BTN_CANCEL)
        buttons.accepted.connect(self._on_save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _toggle_hint(self) -> None:
        sender = self.sender()
        if self._hint and self._hint.isVisible():
            self._hint.close()
            self._hint = None
            return
        self._hint = InlineHintPopup(S.HINT_DAILY_TRIGGERS, self)
        if isinstance(sender, QToolButton):
            self._hint.show_near(sender)

    def _on_save(self) -> None:
        try:
            self._service.create_pokemon(
                self._species.text().strip(),
                self._nickname.text().strip(),
                self._skill_type.isChecked(),
                self._daily.optional_value(),
            )
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, S.MSG_VALIDATION_TITLE, str(e))

    def closeEvent(self, event) -> None:
        if self._hint:
            self._hint.close()
        super().closeEvent(event)
