"""Data models for the application."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Pokemon:
    id: int
    species: str
    nickname: str
    is_skill_type: bool
    expected_daily_triggers: Optional[float]
    created_at: datetime
    updated_at: datetime


@dataclass
class TriggerEntry:
    pokemon_id: int
    trigger_count: int
    nickname: str = ""
    species: str = ""


@dataclass
class TriggerRecord:
    id: int
    trigger_time: datetime
    added_time: datetime
    entries: list[TriggerEntry] = field(default_factory=list)


@dataclass
class Settings:
    show_first_record_tip: bool = True
    show_tray_minimize_tip: bool = True


@dataclass
class PokemonStatsRow:
    pokemon_id: int
    nickname: str
    species: str
    is_skill_type: bool
    total_trigger_count: int
    valid_record_count: int
    avg_daily_triggers: float
