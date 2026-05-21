"""Business logic layer."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Optional

from app import strings as S
from app.database import Database
from app.models import Pokemon, PokemonStatsRow, Settings, TriggerRecord
from app.utils.text_width import is_within_width_limit

MAX_TEAM_SIZE = 5

TIME_PERIOD_LABELS = (S.PERIOD_MORNING, S.PERIOD_AFTERNOON, S.PERIOD_NIGHT)


@dataclass
class TimePoint:
    date: date
    period_index: int  # 0=morning, 1=afternoon, 2=night
    label: str


@dataclass
class DistributionSeries:
    pokemon_id: int
    nickname: str
    values: list[float]


class AppService:
    def __init__(self, db: Database) -> None:
        self.db = db

    def get_settings(self) -> Settings:
        return self.db.get_settings()

    def dismiss_first_record_tip(self) -> None:
        self.db.set_show_first_record_tip(False)

    def dismiss_tray_minimize_tip(self) -> None:
        self.db.set_show_tray_minimize_tip(False)

    def validate_name(self, text: str) -> tuple[bool, str]:
        if not text.strip():
            return False, S.ERR_EMPTY
        if not is_within_width_limit(text):
            return False, S.ERR_WIDTH
        return True, ""

    def create_pokemon(
        self,
        species: str,
        nickname: str,
        is_skill_type: bool,
        expected_daily_triggers: Optional[float],
    ) -> Pokemon:
        ok, msg = self.validate_name(species)
        if not ok:
            raise ValueError(S.ERR_SPECIES.format(msg=msg))
        ok, msg = self.validate_name(nickname)
        if not ok:
            raise ValueError(S.ERR_NICKNAME.format(msg=msg))
        if expected_daily_triggers is not None:
            expected_daily_triggers = min(10.0, max(0.1, round(expected_daily_triggers, 1)))
        return self.db.create_pokemon(
            species.strip(),
            nickname.strip(),
            is_skill_type,
            expected_daily_triggers,
        )

    def update_pokemon(
        self,
        pokemon_id: int,
        species: str,
        nickname: str,
        is_skill_type: bool,
        expected_daily_triggers: Optional[float],
    ) -> Pokemon:
        ok, msg = self.validate_name(species)
        if not ok:
            raise ValueError(S.ERR_SPECIES.format(msg=msg))
        ok, msg = self.validate_name(nickname)
        if not ok:
            raise ValueError(S.ERR_NICKNAME.format(msg=msg))
        if expected_daily_triggers is not None:
            expected_daily_triggers = min(10.0, max(0.1, round(expected_daily_triggers, 1)))
        return self.db.update_pokemon(
            pokemon_id,
            species.strip(),
            nickname.strip(),
            is_skill_type,
            expected_daily_triggers,
        )

    def list_pokemon(self) -> list[Pokemon]:
        return self.db.list_pokemon()

    def get_pokemon(self, pokemon_id: int) -> Pokemon:
        return self.db.get_pokemon(pokemon_id)

    def delete_pokemon(self, pokemon_id: int) -> None:
        self.db.delete_pokemon(pokemon_id)

    def create_trigger_record(
        self, trigger_time: datetime, entries: dict[int, int]
    ) -> TriggerRecord:
        filtered = [(pid, c) for pid, c in entries.items() if c > 0]
        if not filtered:
            raise ValueError(S.ERR_NO_TRIGGERS)
        return self.db.create_trigger_record(trigger_time, filtered)

    def list_trigger_records(self) -> list[TriggerRecord]:
        return self.db.list_trigger_records()

    def update_trigger_time(self, record_id: int, trigger_time: datetime) -> None:
        self.db.update_trigger_time(record_id, trigger_time)

    def update_trigger_entries(self, record_id: int, entries: dict[int, int]) -> None:
        filtered = [(pid, c) for pid, c in entries.items() if c > 0]
        if not filtered:
            raise ValueError(S.ERR_NO_TRIGGERS)
        self.db.update_trigger_entries(record_id, filtered)

    def delete_trigger_record(self, record_id: int) -> None:
        self.db.delete_trigger_record(record_id)

    def get_trigger_record(self, record_id: int) -> TriggerRecord:
        return self.db.get_trigger_record(record_id)

    @staticmethod
    def calendar_range_end(days: int) -> tuple[datetime, datetime]:
        """days=1 means today only; 3 means today + previous 2 days."""
        today = date.today()
        start = today - timedelta(days=days - 1)
        return (
            datetime.combine(start, datetime.min.time()),
            datetime.combine(today, datetime.max.time()),
        )

    def compute_statistics(self, days: int) -> list[PokemonStatsRow]:
        start_dt, end_dt = self.calendar_range_end(days)
        records = self.db.records_in_date_range(start_dt, end_dt)
        pokemon_list = self.db.list_pokemon()

        totals: dict[int, int] = defaultdict(int)
        record_counts: dict[int, int] = defaultdict(int)

        for record in records:
            seen_in_record: set[int] = set()
            for entry in record.entries:
                totals[entry.pokemon_id] += entry.trigger_count
                if entry.pokemon_id not in seen_in_record:
                    record_counts[entry.pokemon_id] += 1
                    seen_in_record.add(entry.pokemon_id)

        rows: list[PokemonStatsRow] = []
        for p in pokemon_list:
            total = totals.get(p.id, 0)
            avg_daily = total / days if days > 0 else 0.0
            rows.append(
                PokemonStatsRow(
                    pokemon_id=p.id,
                    nickname=p.nickname,
                    species=p.species,
                    is_skill_type=p.is_skill_type,
                    total_trigger_count=total,
                    valid_record_count=record_counts.get(p.id, 0),
                    avg_daily_triggers=round(avg_daily, 1),
                )
            )

        rows.sort(
            key=lambda r: (
                -r.total_trigger_count,
                -r.valid_record_count,
                r.species.lower(),
            )
        )
        return rows

    @staticmethod
    def classify_time_period(dt: datetime) -> int:
        t = dt.time()
        if time(4, 0) <= t < time(12, 0):
            return 0
        if time(12, 0) <= t < time(18, 0):
            return 1
        return 2

    @staticmethod
    def pokemon_picker_label(nickname: str, species: str) -> str:
        from app import strings as S

        return S.POKEMON_PICKER_LABEL.format(nickname=nickname, species=species)

    def compute_time_distribution(
        self,
        days: int,
        mode: str = "cumulative",
        pokemon_id: Optional[int] = None,
    ) -> tuple[list[TimePoint], list[DistributionSeries]]:
        """
        mode: 'triggered' = 1 if any trigger in period else 0;
              'cumulative' = running sum of triggers along timeline.
        """
        start_dt, end_dt = self.calendar_range_end(days)
        records = self.db.records_in_date_range(start_dt, end_dt)
        pokemon_list = self.db.list_pokemon()
        if pokemon_id is not None:
            pokemon_list = [p for p in pokemon_list if p.id == pokemon_id]

        today = date.today()
        start_date = today - timedelta(days=days - 1)
        points: list[TimePoint] = []
        d = start_date
        while d <= today:
            for idx, label in enumerate(TIME_PERIOD_LABELS):
                points.append(TimePoint(date=d, period_index=idx, label=label))
            d += timedelta(days=1)

        index_map = {(p.date, p.period_index): i for i, p in enumerate(points)}
        if not pokemon_list:
            return points, []

        agg: dict[int, list[float]] = {p.id: [0.0] * len(points) for p in pokemon_list}

        for record in records:
            d = record.trigger_time.date()
            period = self.classify_time_period(record.trigger_time)
            key = (d, period)
            if key not in index_map:
                continue
            idx = index_map[key]
            for entry in record.entries:
                if entry.pokemon_id in agg:
                    agg[entry.pokemon_id][idx] += float(entry.trigger_count)

        series: list[DistributionSeries] = []
        for p in pokemon_list:
            raw = agg[p.id]
            if mode == "triggered":
                values = [1.0 if v > 0 else 0.0 for v in raw]
            elif mode == "cumulative":
                total = 0.0
                values = []
                for v in raw:
                    total += v
                    values.append(total)
            else:
                values = raw

            if pokemon_id is not None or any(v > 0 for v in values):
                series.append(
                    DistributionSeries(
                        pokemon_id=p.id,
                        nickname=p.nickname,
                        values=values,
                    )
                )
        return points, series

    @staticmethod
    def next_trigger_count(current: int, is_skill_type: bool) -> int:
        if is_skill_type:
            return (current + 1) % 3
        return (current + 1) % 2
