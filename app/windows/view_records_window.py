"""View trigger records with history, statistics, and chart."""

from __future__ import annotations

from datetime import datetime
from typing import Callable, Optional

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Segoe UI"]
plt.rcParams["axes.unicode_minus"] = False
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QButtonGroup,
    QComboBox,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app import strings as S
from app.widgets.table_buttons import make_history_actions, make_info_button
from app.widgets.table_items import readonly_item
from app.services import AppService, TimePoint
from app.windows.pokemon_detail_window import PokemonDetailWindow
from app.windows.trigger_time_window import TriggerTimeWindow


class ViewRecordsWindow(QDialog):
    def __init__(
        self,
        service: AppService,
        on_data_changed: Optional[Callable[[], None]] = None,
        on_edit_team: Optional[Callable[[int], None]] = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._service = service
        self._on_data_changed = on_data_changed
        self._on_edit_team = on_edit_team
        self.setWindowTitle(S.VIEW_RECORDS_TITLE)
        self.resize(900, 620)
        self._stats_days = 7
        self._chart_days = 7
        self._chart_mode = "cumulative"
        self._chart_pokemon_id: int | None = None
        self._build_ui()
        self._refresh_history()
        self._refresh_stats()
        self._refresh_chart_pokemon_combo()
        self._refresh_chart()

    def _build_ui(self) -> None:
        root = QHBoxLayout(self)

        nav = QVBoxLayout()
        nav.setSpacing(6)
        self._nav_buttons: list[QPushButton] = []
        tabs = [S.TAB_HISTORY, S.TAB_STATISTICS, S.TAB_DISTRIBUTION]
        for i, name in enumerate(tabs):
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setStyleSheet(
                """
                QPushButton { text-align: left; padding: 12px 16px; border-radius: 8px; }
                QPushButton:checked {
                    background: #4f6ef7; color: white; border: none; font-weight: 600;
                }
                """
            )
            btn.clicked.connect(lambda _checked=False, idx=i: self._switch_tab(idx))
            nav.addWidget(btn)
            self._nav_buttons.append(btn)
        nav.addStretch()
        root.addLayout(nav)

        self._stack = QStackedWidget()
        self._history_page = self._build_history_page()
        self._stats_page = self._build_stats_page()
        self._chart_page = self._build_chart_page()
        self._stack.addWidget(self._history_page)
        self._stack.addWidget(self._stats_page)
        self._stack.addWidget(self._chart_page)
        root.addWidget(self._stack, 1)

        self._nav_buttons[0].setChecked(True)

    def _switch_tab(self, index: int) -> None:
        self._stack.setCurrentIndex(index)
        for i, btn in enumerate(self._nav_buttons):
            btn.setChecked(i == index)

    def _build_history_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        self._history_table = QTableWidget(0, 3)
        self._history_table.setHorizontalHeaderLabels(
            [S.COL_ADDED_TIME, S.COL_TRIGGERS, S.COL_ACTIONS]
        )
        self._history_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self._history_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self._history_table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Fixed
        )
        self._history_table.setColumnWidth(2, 140)
        self._history_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._history_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._history_table.verticalHeader().setDefaultSectionSize(52)
        layout.addWidget(self._history_table)
        return page

    def _build_stats_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(self._make_span_selector(self._stats_days, self._set_stats_days))
        self._stats_table = QTableWidget(0, 6)
        self._stats_table.setHorizontalHeaderLabels(
            [
                S.COL_NICKNAME,
                S.COL_SPECIES,
                S.COL_SKILL,
                S.COL_TOTAL,
                S.COL_AVG_DAILY,
                S.COL_INFO,
            ]
        )
        header = self._stats_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self._stats_table.setColumnWidth(5, 52)
        self._stats_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._stats_table.verticalHeader().setDefaultSectionSize(40)
        layout.addWidget(self._stats_table)
        return page

    def _build_chart_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)

        pokemon_bar = QWidget()
        pokemon_row = QHBoxLayout(pokemon_bar)
        pokemon_row.addWidget(QLabel(S.LABEL_CHART_POKEMON))
        self._chart_pokemon_combo = QComboBox()
        self._chart_pokemon_combo.setMinimumWidth(220)
        self._chart_pokemon_combo.currentIndexChanged.connect(
            self._on_chart_pokemon_changed
        )
        pokemon_row.addWidget(self._chart_pokemon_combo, 1)
        pokemon_row.addStretch()
        layout.addWidget(pokemon_bar)

        layout.addWidget(self._make_span_selector(self._chart_days, self._set_chart_days))
        mode_bar = QWidget()
        mode_row = QHBoxLayout(mode_bar)
        mode_row.addWidget(QLabel(S.LABEL_CHART_MODE))
        self._chart_mode_group = QButtonGroup(mode_bar)
        for mode, label in (
            ("triggered", S.CHART_MODE_TRIGGERED),
            ("cumulative", S.CHART_MODE_CUMULATIVE),
        ):
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setProperty("chartMode", mode)
            if mode == self._chart_mode:
                btn.setChecked(True)
            self._chart_mode_group.addButton(btn)
            btn.clicked.connect(
                lambda checked, m=mode: self._set_chart_mode(m) if checked else None
            )
            mode_row.addWidget(btn)
        mode_row.addStretch()
        layout.addWidget(mode_bar)
        self._figure = Figure(figsize=(8, 4), dpi=100)
        self._canvas = FigureCanvasQTAgg(self._figure)
        layout.addWidget(self._canvas)
        return page

    def _set_chart_mode(self, mode: str) -> None:
        self._chart_mode = mode
        self._refresh_chart()

    def _make_span_selector(self, current: int, handler) -> QWidget:
        bar = QWidget()
        row = QHBoxLayout(bar)
        row.addWidget(QLabel(S.LABEL_TIME_SPAN))
        group = QButtonGroup(bar)
        for days in (1, 3, 7, 14, 30):
            btn = QPushButton(S.DAY_1 if days == 1 else S.DAY_N.format(n=days))
            btn.setCheckable(True)
            btn.setProperty("days", days)
            if days == current:
                btn.setChecked(True)
            group.addButton(btn)
            btn.clicked.connect(lambda checked, d=days: handler(d) if checked else None)
            row.addWidget(btn)
        row.addStretch()
        return bar

    def _set_stats_days(self, days: int) -> None:
        self._stats_days = days
        self._refresh_stats()

    def _set_chart_days(self, days: int) -> None:
        self._chart_days = days
        self._refresh_chart()

    def _on_chart_pokemon_changed(self, index: int) -> None:
        if index < 0:
            return
        pid = self._chart_pokemon_combo.currentData()
        if pid is not None:
            self._chart_pokemon_id = int(pid)
            self._refresh_chart()

    def _refresh_chart_pokemon_combo(self) -> None:
        self._chart_pokemon_combo.blockSignals(True)
        prev = self._chart_pokemon_id
        self._chart_pokemon_combo.clear()
        pokemon_list = self._service.list_pokemon()
        if not pokemon_list:
            self._chart_pokemon_id = None
            self._chart_pokemon_combo.blockSignals(False)
            return
        for p in pokemon_list:
            self._chart_pokemon_combo.addItem(
                self._service.pokemon_picker_label(p.nickname, p.species),
                p.id,
            )
        if prev is not None:
            idx = self._chart_pokemon_combo.findData(prev)
            if idx >= 0:
                self._chart_pokemon_combo.setCurrentIndex(idx)
        if self._chart_pokemon_combo.currentIndex() < 0:
            self._chart_pokemon_combo.setCurrentIndex(0)
        pid = self._chart_pokemon_combo.currentData()
        self._chart_pokemon_id = int(pid) if pid is not None else None
        self._chart_pokemon_combo.blockSignals(False)

    def _refresh_history(self) -> None:
        records = self._service.list_trigger_records()
        self._history_table.setRowCount(len(records))
        for row, rec in enumerate(records):
            self._history_table.setItem(
                row,
                0,
                readonly_item(rec.added_time.strftime("%Y-%m-%d %H:%M:%S")),
            )
            line = "; ".join(
                f"{e.nickname}: {e.trigger_count}" for e in rec.entries
            )
            self._history_table.setItem(row, 1, readonly_item(line))

            actions = make_history_actions(
                on_edit_time=lambda _=False, rid=rec.id, t=rec.trigger_time: self._edit_time(
                    rid, t
                ),
                on_edit_team=lambda _=False, rid=rec.id: self._edit_team(rid),
                on_delete=lambda _=False, rid=rec.id: self._delete_record(rid),
                tip_edit_time=S.TIP_EDIT_TIME,
                tip_edit_team=S.TIP_EDIT_TEAM,
                tip_delete=S.TIP_DELETE_RECORD,
            )
            self._history_table.setCellWidget(row, 2, actions)

    def _refresh_stats(self) -> None:
        rows = self._service.compute_statistics(self._stats_days)
        self._stats_table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self._stats_table.setItem(i, 0, readonly_item(r.nickname))
            self._stats_table.setItem(i, 1, readonly_item(r.species))
            skill_item = readonly_item("✓" if r.is_skill_type else "")
            skill_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._stats_table.setItem(i, 2, skill_item)
            self._stats_table.setItem(
                i, 3, readonly_item(str(r.total_trigger_count))
            )
            self._stats_table.setItem(
                i, 4, readonly_item(f"{r.avg_daily_triggers:.1f}")
            )
            info_cell = make_info_button(
                lambda _=False, pid=r.pokemon_id: self._open_pokemon(pid)
            )
            self._stats_table.setCellWidget(i, 5, info_cell)

    def _refresh_chart(self) -> None:
        if self._chart_pokemon_id is None:
            self._figure.clear()
            ax = self._figure.add_subplot(111)
            ax.text(0.5, 0.5, S.CHART_NO_DATA, ha="center", va="center")
            self._canvas.draw()
            return

        points, series = self._service.compute_time_distribution(
            self._chart_days,
            self._chart_mode,
            self._chart_pokemon_id,
        )
        self._figure.clear()
        ax = self._figure.add_subplot(111)
        if not points or not series:
            ax.text(0.5, 0.5, S.CHART_NO_DATA, ha="center", va="center")
            self._canvas.draw()
            return

        x_positions = list(range(len(points)))
        x_labels = self._compute_x_labels(points)

        s = series[0]
        label = self._chart_pokemon_combo.currentText() or s.nickname
        period_colors = ("#2e7d32", "#1565c0", "#c62828")  # 早/午/晚：绿/蓝/红
        marker_colors = [period_colors[p.period_index] for p in points]

        ax.plot(
            x_positions,
            s.values,
            color="#000000",
            linewidth=1.5,
            label=label,
            zorder=1,
        )
        ax.scatter(
            x_positions,
            s.values,
            c=marker_colors,
            s=42,
            zorder=2,
            edgecolors="#ffffff",
            linewidths=0.6,
        )

        ax.set_xticks(x_positions)
        ax.set_xticklabels(x_labels, rotation=0, ha="center", fontsize=7)
        ylabel = (
            S.CHART_Y_CUMULATIVE
            if self._chart_mode == "cumulative"
            else S.CHART_Y_TRIGGERED
        )
        ax.set_ylabel(ylabel)
        if self._chart_mode == "triggered":
            ax.set_ylim(-0.05, 1.15)
            ax.set_yticks([0, 1])
        ax.legend(fontsize=8, loc="upper right")
        ax.grid(True, alpha=0.3)
        self._figure.tight_layout()
        self._canvas.draw()

    @staticmethod
    def _compute_x_labels(points: list[TimePoint]) -> list[str]:
        labels: list[str] = []
        for p in points:
            if p.period_index == 0:
                labels.append(p.date.strftime("%m/%d"))
            else:
                labels.append("")
        return labels

    def _edit_time(self, record_id: int, current: datetime) -> None:
        dlg = TriggerTimeWindow(current, self)
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.selected_time():
            self._service.update_trigger_time(record_id, dlg.selected_time())
            self._notify_changed()
            self._refresh_history()

    def _edit_team(self, record_id: int) -> None:
        if self._on_edit_team:
            self._on_edit_team(record_id)
            self.hide()

    def _delete_record(self, record_id: int) -> None:
        reply = QMessageBox.question(
            self,
            S.MSG_DELETE_RECORD_TITLE,
            S.MSG_DELETE_RECORD,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._service.delete_trigger_record(record_id)
            self._notify_changed()
            self._refresh_history()
            self._refresh_stats()
            self._refresh_chart()

    def _open_pokemon(self, pokemon_id: int) -> None:
        dlg = PokemonDetailWindow(
            self._service,
            pokemon_id,
            on_changed=self._notify_changed,
            parent=self,
        )
        if dlg.exec() == 2:
            self._notify_changed()
        self._refresh_stats()

    def _notify_changed(self) -> None:
        self._refresh_stats()
        self._refresh_chart_pokemon_combo()
        self._refresh_chart()
        if self._on_data_changed:
            self._on_data_changed()

    def refresh_all(self) -> None:
        self._refresh_history()
        self._refresh_stats()
        self._refresh_chart_pokemon_combo()
        self._refresh_chart()

    def show_and_refresh(self) -> None:
        self.refresh_all()
        self.show()
        self.raise_()
        self.activateWindow()
