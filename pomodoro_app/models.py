from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(slots=True)
class AppConfig:
    focus_minutes: int = 25
    short_break_minutes: int = 5
    long_break_every: int = 4
    long_break_minutes: int = 15
    end_sound_mode: str = "system"
    end_sound_path: str = ""
    end_sound_stop_mode: str = "next_focus"

    @classmethod
    def from_mapping(cls, data: dict[str, object]) -> "AppConfig":
        return cls(
            focus_minutes=max(1, int(data.get("focus_minutes", cls.focus_minutes))),
            short_break_minutes=max(1, int(data.get("short_break_minutes", cls.short_break_minutes))),
            long_break_every=max(1, int(data.get("long_break_every", cls.long_break_every))),
            long_break_minutes=max(1, int(data.get("long_break_minutes", cls.long_break_minutes))),
            end_sound_mode=str(data.get("end_sound_mode", cls.end_sound_mode)),
            end_sound_path=str(data.get("end_sound_path", cls.end_sound_path)),
            end_sound_stop_mode=str(data.get("end_sound_stop_mode", cls.end_sound_stop_mode)),
        )

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


@dataclass(slots=True)
class TomatoRecord:
    position_index: int
    sprite_index: int
    created_at: str

    @classmethod
    def from_mapping(cls, data: dict[str, object]) -> "TomatoRecord":
        return cls(
            position_index=int(data.get("position_index", 0)),
            sprite_index=int(data.get("sprite_index", 0)),
            created_at=str(data.get("created_at", "")),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class DailyState:
    date: str
    completed_today: int = 0
    tomatoes: list[TomatoRecord] = field(default_factory=list)

    @classmethod
    def from_mapping(cls, data: dict[str, object], today: str) -> "DailyState":
        raw_tomatoes = data.get("tomatoes", [])
        tomatoes = [TomatoRecord.from_mapping(item) for item in raw_tomatoes if isinstance(item, dict)]
        return cls(
            date=str(data.get("date", today)),
            completed_today=max(0, int(data.get("completed_today", len(tomatoes)))),
            tomatoes=tomatoes,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "date": self.date,
            "completed_today": self.completed_today,
            "tomatoes": [tomato.to_dict() for tomato in self.tomatoes],
        }


@dataclass(slots=True)
class LifetimeStats:
    total_completed: int = 0

    @classmethod
    def from_mapping(cls, data: dict[str, object]) -> "LifetimeStats":
        return cls(total_completed=max(0, int(data.get("total_completed", 0))))

    def to_dict(self) -> dict[str, int]:
        return asdict(self)