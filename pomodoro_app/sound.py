from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SoundPlaybackState:
    playing: bool = False
    source_path: str = ""


class SoundManager:
    def __init__(self, platform_integration) -> None:
        self._platform = platform_integration
        self._music = None
        self._available = self._try_initialize()
        self._state = SoundPlaybackState()

    def play_end_sound(self, mode: str, path: str) -> None:
        self.stop()
        if mode == "off":
            return
        if mode == "system":
            self._platform.play_system_sound()
            return
        if not path:
            self._platform.play_system_sound()
            return
        if self._music is None and not self._available:
            self._platform.play_system_sound()
            return
        try:
            self._music.load(path)
            self._music.play(loops=0)
            self._state = SoundPlaybackState(playing=True, source_path=path)
        except Exception:
            self._platform.play_system_sound()

    def stop(self) -> None:
        if self._music is None:
            self._state = SoundPlaybackState()
            return
        try:
            if self._music.get_busy():
                self._music.stop()
        except Exception:
            pass
        self._state = SoundPlaybackState()

    def is_playing_file(self) -> bool:
        return self._state.playing and bool(self._state.source_path)

    def update(self) -> None:
        if self._music is None:
            return
        try:
            if self._state.playing and not self._music.get_busy():
                self._state = SoundPlaybackState()
        except Exception:
            self._state = SoundPlaybackState()

    def should_stop_on_next_focus(self, stop_mode: str) -> bool:
        return self.is_playing_file() and stop_mode == "next_focus"

    def _try_initialize(self) -> bool:
        try:
            import pygame

            pygame.mixer.init()
            self._music = pygame.mixer.music
            return True
        except Exception:
            self._music = None
            return False