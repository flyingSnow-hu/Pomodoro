from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .models import AppConfig


class TimerPhase(str, Enum):
    FOCUS = "focus"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"


class TimerStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"


@dataclass(slots=True)
class TimerSnapshot:
    phase: TimerPhase
    status: TimerStatus
    remaining_seconds: int
    completed_focus_cycles: int


class PomodoroTimer:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.phase = TimerPhase.FOCUS
        self.status = TimerStatus.IDLE
        self.completed_focus_cycles = 0
        self.remaining_seconds = self._phase_duration_seconds(self.phase)

    def start_or_resume(self) -> None:
        if self.status in {TimerStatus.IDLE, TimerStatus.PAUSED}:
            self.status = TimerStatus.RUNNING

    def pause(self) -> None:
        if self.status == TimerStatus.RUNNING:
            self.status = TimerStatus.PAUSED

    def reset_current_phase(self) -> None:
        self.remaining_seconds = self._phase_duration_seconds(self.phase)
        if self.status == TimerStatus.RUNNING:
            self.status = TimerStatus.PAUSED

    def apply_config(self, config: AppConfig) -> None:
        self.config = config
        self.reset_current_phase()

    def tick(self) -> str | None:
        if self.status != TimerStatus.RUNNING:
            return None
        self.remaining_seconds -= 1
        if self.remaining_seconds > 0:
            return None
        if self.phase == TimerPhase.FOCUS:
            self.completed_focus_cycles += 1
            self.phase = self._next_break_phase()
            self.remaining_seconds = self._phase_duration_seconds(self.phase)
            return "focus_completed"
        self.phase = TimerPhase.FOCUS
        self.remaining_seconds = self._phase_duration_seconds(self.phase)
        return "break_completed"

    def skip_current_phase(self) -> str:
        if self.phase == TimerPhase.FOCUS:
            self.phase = self._next_break_phase()
            self.remaining_seconds = self._phase_duration_seconds(self.phase)
            return "focus_skipped"
        self.phase = TimerPhase.FOCUS
        self.remaining_seconds = self._phase_duration_seconds(self.phase)
        return "break_skipped"

    def snapshot(self) -> TimerSnapshot:
        return TimerSnapshot(
            phase=self.phase,
            status=self.status,
            remaining_seconds=self.remaining_seconds,
            completed_focus_cycles=self.completed_focus_cycles,
        )

    def _next_break_phase(self) -> TimerPhase:
        if self.completed_focus_cycles % self.config.long_break_every == 0:
            return TimerPhase.LONG_BREAK
        return TimerPhase.SHORT_BREAK

    def _phase_duration_seconds(self, phase: TimerPhase) -> int:
        if phase == TimerPhase.FOCUS:
            return self.config.focus_minutes * 60
        if phase == TimerPhase.SHORT_BREAK:
            return self.config.short_break_minutes * 60
        return self.config.long_break_minutes * 60