from __future__ import annotations

import sys
from pathlib import Path


def project_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent.parent


def config_path(name: str) -> Path:
    return project_root() / "configs" / name


def image_path(name: str) -> Path:
    return project_root() / "imgs" / name