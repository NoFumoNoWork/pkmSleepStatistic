"""Main application window."""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtGui import QCloseEvent, QShowEvent
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app import strings as S
from app.services import AppService, MAX_TEAM_SIZE
from app.widgets.flow_grid import (
    GRID_COLUMNS,
    GRID_MARGIN,
    GRID_SPACING,
    FlowGridWidget,
    fixed_card_size,
    main_window_fixed_size,
    scroll_viewport_height,
)
from app.widgets.pokemon_card import PokemonCard
from app.windows.create_pokemon_window import CreatePokemonWindow
from app.windows.first_record_tip import FirstRecordTipDialog
from app.windows.pokemon_detail_window import PokemonDetailWindow
from app.windows.trigger_time_window import TriggerTimeWindow
from app.windows.view_records_window import ViewRecordsWindow


class MainWindow(QWidget):
    toggle_visibility_requested = Signal()

    def __init__(
        self,
        service: AppService,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._service = service
        self._record_mode = False
        self._selection: dict[int, int] = {}
        self._cards: dict[int, PokemonCard] = {}
        self._edit_record_id: Optional[int] = None

        self.setWindowTitle(S.MAIN_TITLE)
        self._layout_applied = False
        self._build_ui()
        self.refresh_cards()

        self._view_window = ViewRecordsWindow(
            service,
            on_data_changed=self.refresh_cards,
            on_edit_team=self._start_edit_team_for_record,
            parent=None,
        )

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self._grid_host = FlowGridWidget(fixed_columns=GRID_COLUMNS)
        self._scroll.setWidget(self._grid_host)
        self._grid_host.installEventFilter(self)
        self._scroll.viewport().installEventFilter(self)
        root.addWidget(self._scroll, 1)

        footer = QWidget()
        footer.setObjectName("mainFooter")
        footer.setStyleSheet(
            """
            QWidget#mainFooter {
                background: #ffffff;
                border-top: 1px solid #dde3ef;
            }
            QWidget#mainFooter QPushButton {
                color: #1a1a2e;
                background-color: #ffffff;
            }
            QWidget#mainFooter QPushButton#accentButton {
                background-color: #e8f0fe;
                color: #2b4acb;
                border: 1px solid #b8ccf9;
                font-weight: 600;
            }
            QWidget#mainFooter QPushButton#createPokemonButton,
            QWidget#mainFooter QPushButton#primaryButton {
                background-color: #4f6ef7;
                color: #ffffff;
                border: none;
                font-weight: 600;
            }
            QWidget#mainFooter QPushButton#createPokemonButton:hover,
            QWidget#mainFooter QPushButton#primaryButton:hover {
                background-color: #3d5ce6;
                color: #ffffff;
            }
            """
        )
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(16, 10, 16, 10)

        self._btn_add_record = QPushButton(S.BTN_ADD_RECORD)
        self._btn_add_record.setObjectName("accentButton")
        self._btn_add_record.clicked.connect(self._enter_record_mode)
        footer_layout.addWidget(self._btn_add_record)

        self._btn_view_records = QPushButton(S.BTN_VIEW_RECORDS)
        self._btn_view_records.clicked.connect(self._open_view_records)
        footer_layout.addWidget(self._btn_view_records)

        self._btn_cancel_record = QPushButton(S.BTN_CANCEL_RECORD)
        self._btn_cancel_record.clicked.connect(self._exit_record_mode)
        self._btn_cancel_record.hide()
        footer_layout.addWidget(self._btn_cancel_record)

        self._btn_confirm_team = QPushButton(S.BTN_CONFIRM_TEAM)
        self._btn_confirm_team.setObjectName("primaryButton")
        self._btn_confirm_team.clicked.connect(self._confirm_team)
        self._btn_confirm_team.hide()
        footer_layout.addWidget(self._btn_confirm_team)

        footer_layout.addStretch()

        self._btn_create = QPushButton(S.BTN_CREATE_POKEMON)
        self._btn_create.setObjectName("createPokemonButton")
        self._btn_create.setMinimumWidth(140)
        self._btn_create.clicked.connect(self._open_create)
        footer_layout.addWidget(self._btn_create)

        root.addWidget(footer)

    def _lock_window_layout(self) -> None:
        """锁定主界面：每行 5 张卡片，可视区域 4 行，超出部分滚轮滚动。"""
        card = fixed_card_size()
        self._scroll.setFixedHeight(scroll_viewport_height(card.height()))
        size = main_window_fixed_size(card.width(), card.height())
        self.setFixedSize(size)
        min_w = (
            GRID_COLUMNS * card.width()
            + (GRID_COLUMNS - 1) * GRID_SPACING
            + 2 * GRID_MARGIN
        )
        self._grid_host.setMinimumWidth(min_w)
        self._grid_host.setFixedWidth(min_w)
        self._grid_host.relayout()
        self.refresh_cards()

    def _apply_window_layout(self) -> None:
        if not self._layout_applied:
            self._lock_window_layout()
            self._layout_applied = True

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self._apply_window_layout()

    def eventFilter(self, watched, event) -> bool:
        if (
            event.type() == QEvent.Type.Wheel
            and self._scroll is not None
            and watched in (self._grid_host, self._scroll.viewport())
        ):
            bar = self._scroll.verticalScrollBar()
            delta = event.angleDelta().y()
            bar.setValue(bar.value() - delta // 4)
            event.accept()
            return True
        return super().eventFilter(watched, event)

    def refresh_cards(self) -> None:
        for card in list(self._cards.values()):
            try:
                card.clicked_body.disconnect()
                card.clicked_count.disconnect()
            except RuntimeError:
                pass
            card.setParent(None)
            card.deleteLater()
        self._cards.clear()

        new_cards: list[PokemonCard] = []
        for pokemon in self._service.list_pokemon():
            card = PokemonCard(
                pokemon.id,
                pokemon.nickname,
                pokemon.species,
                pokemon.is_skill_type,
                self._grid_host,
            )
            card.clicked_body.connect(self._on_card_body)
            card.clicked_count.connect(self._on_card_count)
            if self._record_mode:
                card.set_record_mode(True)
                if pokemon.id in self._selection:
                    card.set_trigger_count(self._selection[pokemon.id])
                    if self._selection[pokemon.id] > 0:
                        card.set_selected(True)
            self._cards[pokemon.id] = card
            new_cards.append(card)

        self._grid_host.rebuild_cards(new_cards)

    def _on_card_body(self, pokemon_id: int) -> None:
        if self._record_mode:
            self._toggle_team_selection(pokemon_id)
        else:
            self._open_detail(pokemon_id)

    def _on_card_count(self, pokemon_id: int) -> None:
        if not self._record_mode:
            return
        pokemon = self._service.get_pokemon(pokemon_id)
        card = self._cards.get(pokemon_id)
        if not card:
            return
        current = card.trigger_count()
        new_count = self._service.next_trigger_count(current, pokemon.is_skill_type)
        if new_count > 0 and not card.is_selected():
            selected_count = sum(1 for c in self._cards.values() if c.is_selected())
            if selected_count >= MAX_TEAM_SIZE:
                msg = QMessageBox(self)
                msg.setWindowTitle(S.MSG_TEAM_LIMIT_TITLE)
                msg.setText(S.MSG_TEAM_LIMIT)
                msg.addButton(S.MSG_TEAM_LIMIT_OK, QMessageBox.ButtonRole.AcceptRole)
                msg.exec()
                return
            card.set_selected(True)
        card.set_trigger_count(new_count)
        self._selection[pokemon_id] = new_count

    def _toggle_team_selection(self, pokemon_id: int) -> None:
        card = self._cards.get(pokemon_id)
        if not card:
            return
        if card.is_selected():
            card.set_selected(False)
            self._selection.pop(pokemon_id, None)
            card.set_trigger_count(0)
            return

        selected_count = sum(1 for c in self._cards.values() if c.is_selected())
        if selected_count >= MAX_TEAM_SIZE:
            msg = QMessageBox(self)
            msg.setWindowTitle(S.MSG_TEAM_LIMIT_TITLE)
            msg.setText(S.MSG_TEAM_LIMIT)
            msg.addButton(S.MSG_TEAM_LIMIT_OK, QMessageBox.ButtonRole.AcceptRole)
            msg.exec()
            return

        card.set_selected(True)
        self._selection[pokemon_id] = card.trigger_count()

    def _enter_record_mode(self) -> None:
        self._edit_record_id = None
        self._record_mode = True
        self._selection.clear()
        self._update_record_ui()
        self.refresh_cards()

    def _exit_record_mode(self) -> None:
        self._record_mode = False
        self._edit_record_id = None
        self._selection.clear()
        self._update_record_ui()
        self.refresh_cards()

    def _update_record_ui(self) -> None:
        in_mode = self._record_mode
        self._btn_add_record.setVisible(not in_mode)
        self._btn_view_records.setVisible(not in_mode)
        self._btn_create.setVisible(not in_mode)
        self._btn_cancel_record.setVisible(in_mode)
        self._btn_confirm_team.setVisible(in_mode)

    def _confirm_team(self) -> None:
        entries = {
            pid: card.trigger_count()
            for pid, card in self._cards.items()
            if card.is_selected() and card.trigger_count() > 0
        }
        if not entries:
            QMessageBox.warning(self, S.MSG_NO_SELECTION_TITLE, S.MSG_NO_SELECTION)
            return

        initial_time = None
        if self._edit_record_id:
            rec = self._service.get_trigger_record(self._edit_record_id)
            initial_time = rec.trigger_time

        dlg = TriggerTimeWindow(initial_time, self)
        if dlg.exec() != TriggerTimeWindow.DialogCode.Accepted:
            return
        trigger_time = dlg.selected_time()
        if not trigger_time:
            return

        try:
            if self._edit_record_id:
                self._service.update_trigger_entries(self._edit_record_id, entries)
                self._service.update_trigger_time(self._edit_record_id, trigger_time)
            else:
                self._service.create_trigger_record(trigger_time, entries)
                settings = self._service.get_settings()
                if settings.show_first_record_tip:
                    FirstRecordTipDialog(self._service, self).exec()
        except ValueError as e:
            QMessageBox.warning(self, S.MSG_ERROR_TITLE, str(e))
            return

        self._exit_record_mode()
        self._view_window.refresh_all()
        if self._view_window.isVisible():
            self._view_window.show_and_refresh()

    def _start_edit_team_for_record(self, record_id: int) -> None:
        self.show()
        self.raise_()
        rec = self._service.get_trigger_record(record_id)
        self._edit_record_id = record_id
        self._record_mode = True
        self._selection = {e.pokemon_id: e.trigger_count for e in rec.entries}
        self._update_record_ui()
        self.refresh_cards()
        for pid, count in self._selection.items():
            card = self._cards.get(pid)
            if card:
                card.set_trigger_count(count)
                card.set_selected(True)

    def _open_create(self) -> None:
        dlg = CreatePokemonWindow(self._service, self)
        if dlg.exec() == CreatePokemonWindow.DialogCode.Accepted:
            self.refresh_cards()

    def _open_detail(self, pokemon_id: int) -> None:
        dlg = PokemonDetailWindow(
            self._service,
            pokemon_id,
            on_changed=self.refresh_cards,
            parent=self,
        )
        result = dlg.exec()
        if result == 2 or result == QDialog.DialogCode.Accepted:
            self.refresh_cards()
            self._view_window.refresh_all()

    def _open_view_records(self) -> None:
        self._view_window.show_and_refresh()

    def closeEvent(self, event: QCloseEvent) -> None:
        event.ignore()
        self.hide()
        self.toggle_visibility_requested.emit()
