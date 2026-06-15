from __future__ import annotations

import platform
import subprocess
from abc import ABC, abstractmethod


class PlatformIntegration(ABC):
    @abstractmethod
    def notify(self, title: str, message: str) -> None:
        raise NotImplementedError


class WindowsPlatformIntegration(PlatformIntegration):
    def __init__(self) -> None:
        self._notifier = None
        try:
            from win10toast import ToastNotifier

            self._notifier = ToastNotifier()
        except Exception:
            self._notifier = None

    def notify(self, title: str, message: str) -> None:
        if self._notifier is None:
            return
        try:
            self._notifier.show_toast(title, message, threaded=True, duration=5)
        except Exception:
            return


class MacOSPlatformIntegration(PlatformIntegration):
    def notify(self, title: str, message: str) -> None:
        safe_title = title.replace('"', '\\"')
        safe_message = message.replace('"', '\\"')
        command = (
            "display notification \""
            f"{safe_message}"
            "\" with title \""
            f"{safe_title}"
            "\""
        )
        try:
            subprocess.run(["osascript", "-e", command], check=False)
        except Exception:
            return


class GenericPlatformIntegration(PlatformIntegration):
    def notify(self, title: str, message: str) -> None:
        return


def get_platform_integration() -> PlatformIntegration:
    system = platform.system()
    if system == "Windows":
        return WindowsPlatformIntegration()
    if system == "Darwin":
        return MacOSPlatformIntegration()
    return GenericPlatformIntegration()