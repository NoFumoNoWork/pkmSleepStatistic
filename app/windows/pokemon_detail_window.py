"""Pokémon detail and edit window."""

from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app import strings as S
from app.models import Pokemon
from app.services import AppService
from app.widgets.daily_triggers_spin import DailyTriggersSpinBox


class PokemonDetailWindow(QDialog):
    def __init__(
        self,
        service: AppService,
        pokemon_id: int,
        on_changed: Optional[Callable[[], None]] = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._service = service
        self._pokemon_id = pokemon_id
        self._on_changed = on_changed
        self._pokemon: Pokemon = service.get_pokemon(pokemon_id)
        self.setWindowTitle(S.DETAIL_TITLE.format(nickname=self._pokemon.nickname))
        self.setMinimumSize(480, 520)
        self._build_ui()
        self._load_records()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(0)

        info_panel = QWidget()
        info_panel.setObjectName("infoPanel")
        info_panel.setStyleSheet(
            """
            QWidget#infoPanel {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e8f0ff, stop:1 #f5f8fc
                );
            }
            QWidget#infoPanel QLabel {
                color: #1a1a2e;
                background: transparent;
            }
            QWidget#infoPanel QLineEdit,
            QWidget#infoPanel QDoubleSpinBox,
            QWidget#infoPanel QSpinBox {
                color: #1a1a2e;
                background: #ffffff;
                border: 1px solid #c8d0e0;
                border-radius: 6px;
                padding: 4px 8px;
            }
            QWidget#infoPanel QCheckBox {
                color: #1a1a2e;
                spacing: 8px;
            }
            """
        )
        info_layout = QVBoxLayout(info_panel)
        info_layout.setContentsMargins(20, 20, 20, 20)

        form = QFormLayout()
        self._species = QLineEdit(self._pokemon.species)
        form.addRow(S.LABEL_SPECIES, self._species)
        self._nickname = QLineEdit(self._pokemon.nickname)
        form.addRow(S.LABEL_NICKNAME, self._nickname)
        self._skill = QCheckBox(S.LABEL_SKILL_TYPE)
        self._skill.setChecked(self._pokemon.is_skill_type)
        form.addRow(S.LABEL_SKILL_TYPE_SHORT, self._skill)
        self._daily = DailyTriggersSpinBox()
        self._daily.set_optional_value(self._pokemon.expected_daily_triggers)
        form.addRow(S.LABEL_DAILY_TRIGGERS, self._daily)
        info_layout.addLayout(form)

        btn_row = QHBoxLayout()
        save_btn = QPushButton(S.BTN_SAVE_CHANGES)
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self._save)
        delete_btn = QPushButton(S.BTN_DELETE_POKEMON)
        delete_btn.setObjectName("dangerButton")
        delete_btn.clicked.connect(self._delete)
        btn_row.addWidget(save_btn)
        btn_row.addStretch()
        btn_row.addWidget(delete_btn)
        info_layout.addLayout(btn_row)
        layout.addWidget(info_panel)

        records_panel = QWidget()
        records_panel.setStyleSheet(
            "background: #ffffff; QLabel { color: #1a1a2e; }"
        )
        records_layout = QVBoxLayout(records_panel)
        records_layout.setContentsMargins(20, 16, 20, 16)
        title = QLabel(S.DETAIL_RECORDS_TITLE)
        title.setObjectName("panelTitle")
        records_layout.addWidget(title)

        self._records_area = QScrollArea()
        self._records_area.setWidgetResizable(True)
        self._records_area.setStyleSheet("border: none; background: transparent;")
        self._records_container = QWidget()
        self._records_layout = QVBoxLayout(self._records_container)
        self._records_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._records_area.setWidget(self._records_container)
        records_layout.addWidget(self._records_area)
        layout.addWidget(records_panel, 1)

    def _load_records(self) -> None:
        while self._records_layout.count():
            item = self._records_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        records = self._service.list_trigger_records()
        found = False
        for rec in records:
            for entry in rec.entries:
                if entry.pokemon_id == self._pokemon_id:
                    found = True
                    row = QLabel(
                        S.DETAIL_RECORD_LINE.format(
                            time=rec.trigger_time.strftime("%Y-%m-%d %H:%M"),
                            count=entry.trigger_count,
                        )
                    )
                    self._records_layout.addWidget(row)
                    break
        if not found:
            self._records_layout.addWidget(QLabel(S.DETAIL_NO_RECORDS))

    def _save(self) -> None:
        try:
            self._pokemon = self._service.update_pokemon(
                self._pokemon_id,
                self._species.text(),
                self._nickname.text(),
                self._skill.isChecked(),
                self._daily.optional_value(),
            )
            if self._on_changed:
                self._on_changed()
            QMessageBox.information(self, S.MSG_SAVED_TITLE, S.MSG_SAVED)
        except ValueError as e:
            QMessageBox.warning(self, S.MSG_VALIDATION_TITLE, str(e))

    def _delete(self) -> None:
        reply = QMessageBox.question(
            self,
            S.MSG_DELETE_POKEMON_TITLE,
            S.MSG_DELETE_POKEMON.format(nickname=self._pokemon.nickname),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self._service.delete_pokemon(self._pokemon_id)
        if self._on_changed:
            self._on_changed()
        self.done(2)
