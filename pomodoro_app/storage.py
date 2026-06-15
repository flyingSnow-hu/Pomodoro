from __future__ import annotations

import json
import os
import random
from datetime import datetime
from pathlib import Path

from .models import DailyState, LifetimeStats, TomatoRecord


class StateRepository:
    def __init__(self, app_name: str) -> None:
        self.data_dir = self._resolve_data_dir(app_name)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.daily_file = self.data_dir / "daily_state.json"
        self.stats_file = self.data_dir / "lifetime_stats.json"

    def load_state(self) -> tuple[DailyState, LifetimeStats]:
        today = self._today()
        daily = self._load_daily_state(today)
        stats = self._load_lifetime_stats()
        if daily.date != today:
            daily = DailyState(date=today)
            self._write_json(self.daily_file, daily.to_dict())
        return daily, stats

    def ensure_today(self) -> tuple[DailyState, LifetimeStats, bool]:
        today = self._today()
        daily = self._load_daily_state(today)
        stats = self._load_lifetime_stats()
        if daily.date != today:
            daily = DailyState(date=today)
            self._write_json(self.daily_file, daily.to_dict())
            return daily, stats, True
        return daily, stats, False

    def award_tomato(self, position_count: int) -> tuple[DailyState, LifetimeStats, TomatoRecord]:
        daily, stats = self.load_state()
        used_positions = {item.position_index for item in daily.tomatoes}
        available_positions = [index for index in range(position_count) if index not in used_positions]
        position_pool = available_positions or list(range(position_count))
        record = TomatoRecord(
            position_index=random.choice(position_pool),
            sprite_index=random.randrange(16),
            created_at=datetime.now().isoformat(timespec="seconds"),
        )
        daily.tomatoes.append(record)
        daily.completed_today += 1
        stats.total_completed += 1
        self._write_json(self.daily_file, daily.to_dict())
        self._write_json(self.stats_file, stats.to_dict())
        return daily, stats, record

    def _load_daily_state(self, today: str) -> DailyState:
        data = self._read_json(self.daily_file)
        if not isinstance(data, dict):
            return DailyState(date=today)
        return DailyState.from_mapping(data, today)

    def _load_lifetime_stats(self) -> LifetimeStats:
        data = self._read_json(self.stats_file)
        if not isinstance(data, dict):
            return LifetimeStats()
        return LifetimeStats.from_mapping(data)

    @staticmethod
    def _read_json(path: Path) -> dict[str, object] | None:
        if not path.exists() or path.stat().st_size == 0:
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        return data if isinstance(data, dict) else None

    @staticmethod
    def _write_json(path: Path, data: dict[str, object]) -> None:
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    @staticmethod
    def _resolve_data_dir(app_name: str) -> Path:
        if os.name == "nt":
            base_dir = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
            return base_dir / app_name
        return Path.home() / "Library" / "Application Support" / app_name

    @staticmethod
    def _today() -> str:
        return datetime.now().date().isoformat()