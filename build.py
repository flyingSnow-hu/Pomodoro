from __future__ import annotations

import os
from pathlib import Path

import PyInstaller.__main__
from PIL import Image


ROOT = Path(__file__).resolve().parent
SEPARATOR = ";" if os.name == "nt" else ":"


def _resolve_build_icon() -> Path:
    icon_png = ROOT / "imgs" / "icon.png"
    if os.name != "nt":
        return icon_png
    icon_ico = ROOT / "build" / "icon.ico"
    icon_ico.parent.mkdir(parents=True, exist_ok=True)
    Image.open(icon_png).save(icon_ico, format="ICO")
    return icon_ico


def build() -> None:
    build_icon = _resolve_build_icon()
    PyInstaller.__main__.run(
        [
            str(ROOT / "main.py"),
            "--name",
            "PomodoroPy",
            "--windowed",
            "--noconfirm",
            "--clean",
            "--icon",
            str(build_icon),
            "--add-data",
            f"{ROOT / 'imgs'}{SEPARATOR}imgs",
            "--add-data",
            f"{ROOT / 'configs'}{SEPARATOR}configs",
        ]
    )


if __name__ == "__main__":
    build()