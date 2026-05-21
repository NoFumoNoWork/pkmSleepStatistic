"""SQLite persistence and schema initialization."""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Generator, Iterable, Optional

from app.models import Pokemon, Settings, TriggerEntry, TriggerRecord

SCHEMA_VERSION = 1

INIT_SQL = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS pokemon (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    species TEXT NOT NULL,
    nickname TEXT NOT NULL,
    is_skill_type INTEGER NOT NULL DEFAULT 0,
    expected_daily_triggers INTEGER,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS trigger_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trigger_time TEXT NOT NULL,
    added_time TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS trigger_record_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    record_id INTEGER NOT NULL,
    pokemon_id INTEGER NOT NULL,
    trigger_count INTEGER NOT NULL,
    FOREIGN KEY (record_id) REFERENCES trigger_records(id) ON DELETE CASCADE,
    FOREIGN KEY (pokemon_id) REFERENCES pokemon(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def _dt_to_str(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")


def _str_to_dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


class Database:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    @contextmanager
    def connection(self) -> Generator[sqlite3.Connection, None, None]:
        conn = self._connect()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_schema(self) -> None:
        with self.connection() as conn:
            conn.executescript(INIT_SQL)
            row = conn.execute("SELECT version FROM schema_version LIMIT 1").fetchone()
            if row is None:
                conn.execute(
                    "INSERT INTO schema_version (version) VALUES (?)",
                    (SCHEMA_VERSION,),
                )
                conn.execute(
                    "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                    ("show_first_record_tip", "true"),
                )
                conn.execute(
                    "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                    ("show_tray_minimize_tip", "true"),
                )
            else:
                conn.execute(
                    "INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)",
                    ("show_tray_minimize_tip", "true"),
                )

    # --- Settings ---

    def _get_bool_setting(self, key: str, default: bool = True) -> bool:
        with self.connection() as conn:
            row = conn.execute(
                "SELECT value FROM settings WHERE key = ?", (key,)
            ).fetchone()
        if row is None:
            return default
        return row["value"].lower() == "true"

    def _set_bool_setting(self, key: str, value: bool) -> None:
        with self.connection() as conn:
            conn.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (key, "true" if value else "false"),
            )

    def get_settings(self) -> Settings:
        return Settings(
            show_first_record_tip=self._get_bool_setting("show_first_record_tip"),
            show_tray_minimize_tip=self._get_bool_setting("show_tray_minimize_tip"),
        )

    def set_show_first_record_tip(self, show: bool) -> None:
        self._set_bool_setting("show_first_record_tip", show)

    def set_show_tray_minimize_tip(self, show: bool) -> None:
        self._set_bool_setting("show_tray_minimize_tip", show)

    # --- Pokemon ---

    def create_pokemon(
        self,
        species: str,
        nickname: str,
        is_skill_type: bool,
        expected_daily_triggers: Optional[float],
    ) -> Pokemon:
        now = datetime.now()
        with self.connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO pokemon (
                    species, nickname, is_skill_type,
                    expected_daily_triggers, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    species,
                    nickname,
                    1 if is_skill_type else 0,
                    expected_daily_triggers,
                    _dt_to_str(now),
                    _dt_to_str(now),
                ),
            )
            pid = int(cur.lastrowid)
        return self.get_pokemon(pid)

    def get_pokemon(self, pokemon_id: int) -> Pokemon:
        with self.connection() as conn:
            row = conn.execute(
                "SELECT * FROM pokemon WHERE id = ?", (pokemon_id,)
            ).fetchone()
        if row is None:
            raise ValueError(f"Pokémon not found: {pokemon_id}")
        return self._row_to_pokemon(row)

    def list_pokemon(self) -> list[Pokemon]:
        with self.connection() as conn:
            rows = conn.execute(
                "SELECT * FROM pokemon ORDER BY nickname COLLATE NOCASE"
            ).fetchall()
        return [self._row_to_pokemon(r) for r in rows]

    def update_pokemon(
        self,
        pokemon_id: int,
        species: str,
        nickname: str,
        is_skill_type: bool,
        expected_daily_triggers: Optional[float],
    ) -> Pokemon:
        now = datetime.now()
        with self.connection() as conn:
            conn.execute(
                """
                UPDATE pokemon SET
                    species = ?, nickname = ?, is_skill_type = ?,
                    expected_daily_triggers = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    species,
                    nickname,
                    1 if is_skill_type else 0,
                    expected_daily_triggers,
                    _dt_to_str(now),
                    pokemon_id,
                ),
            )
        return self.get_pokemon(pokemon_id)

    def delete_pokemon(self, pokemon_id: int) -> None:
        with self.connection() as conn:
            conn.execute("DELETE FROM pokemon WHERE id = ?", (pokemon_id,))

    def _row_to_pokemon(self, row: sqlite3.Row) -> Pokemon:
        daily = row["expected_daily_triggers"]
        if daily is not None:
            daily = float(daily)
        return Pokemon(
            id=row["id"],
            species=row["species"],
            nickname=row["nickname"],
            is_skill_type=bool(row["is_skill_type"]),
            expected_daily_triggers=daily,
            created_at=_str_to_dt(row["created_at"]),
            updated_at=_str_to_dt(row["updated_at"]),
        )

    # --- Trigger records ---

    def create_trigger_record(
        self,
        trigger_time: datetime,
        entries: Iterable[tuple[int, int]],
    ) -> TriggerRecord:
        added = datetime.now()
        with self.connection() as conn:
            cur = conn.execute(
                """
                INSERT INTO trigger_records (trigger_time, added_time)
                VALUES (?, ?)
                """,
                (_dt_to_str(trigger_time), _dt_to_str(added)),
            )
            record_id = int(cur.lastrowid)
            for pokemon_id, count in entries:
                conn.execute(
                    """
                    INSERT INTO trigger_record_entries
                        (record_id, pokemon_id, trigger_count)
                    VALUES (?, ?, ?)
                    """,
                    (record_id, pokemon_id, count),
                )
        return self.get_trigger_record(record_id)

    def get_trigger_record(self, record_id: int) -> TriggerRecord:
        with self.connection() as conn:
            row = conn.execute(
                "SELECT * FROM trigger_records WHERE id = ?", (record_id,)
            ).fetchone()
            if row is None:
                raise ValueError(f"Record not found: {record_id}")
            entries = self._fetch_entries(conn, record_id)
        return TriggerRecord(
            id=row["id"],
            trigger_time=_str_to_dt(row["trigger_time"]),
            added_time=_str_to_dt(row["added_time"]),
            entries=entries,
        )

    def list_trigger_records(self) -> list[TriggerRecord]:
        with self.connection() as conn:
            rows = conn.execute(
                "SELECT id FROM trigger_records ORDER BY added_time DESC"
            ).fetchall()
        return [self.get_trigger_record(r["id"]) for r in rows]

    def update_trigger_time(self, record_id: int, trigger_time: datetime) -> None:
        with self.connection() as conn:
            conn.execute(
                "UPDATE trigger_records SET trigger_time = ? WHERE id = ?",
                (_dt_to_str(trigger_time), record_id),
            )

    def update_trigger_entries(
        self, record_id: int, entries: Iterable[tuple[int, int]]
    ) -> None:
        with self.connection() as conn:
            conn.execute(
                "DELETE FROM trigger_record_entries WHERE record_id = ?",
                (record_id,),
            )
            for pokemon_id, count in entries:
                conn.execute(
                    """
                    INSERT INTO trigger_record_entries
                        (record_id, pokemon_id, trigger_count)
                    VALUES (?, ?, ?)
                    """,
                    (record_id, pokemon_id, count),
                )

    def delete_trigger_record(self, record_id: int) -> None:
        with self.connection() as conn:
            conn.execute("DELETE FROM trigger_records WHERE id = ?", (record_id,))

    def _fetch_entries(self, conn: sqlite3.Connection, record_id: int) -> list[TriggerEntry]:
        rows = conn.execute(
            """
            SELECT e.pokemon_id, e.trigger_count, p.nickname, p.species
            FROM trigger_record_entries e
            JOIN pokemon p ON p.id = e.pokemon_id
            WHERE e.record_id = ?
            ORDER BY p.nickname COLLATE NOCASE
            """,
            (record_id,),
        ).fetchall()
        return [
            TriggerEntry(
                pokemon_id=r["pokemon_id"],
                trigger_count=r["trigger_count"],
                nickname=r["nickname"],
                species=r["species"],
            )
            for r in rows
        ]

    def records_in_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> list[TriggerRecord]:
        """Inclusive local calendar date range [start_date.date, end_date.date]."""
        start = datetime.combine(start_date.date(), datetime.min.time())
        end = datetime.combine(end_date.date(), datetime.max.time())
        with self.connection() as conn:
            rows = conn.execute(
                """
                SELECT id FROM trigger_records
                WHERE trigger_time >= ? AND trigger_time <= ?
                ORDER BY trigger_time
                """,
                (_dt_to_str(start), _dt_to_str(end)),
            ).fetchall()
        return [self.get_trigger_record(r["id"]) for r in rows]
