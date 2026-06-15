from __future__ import annotations

import json
from pathlib import Path

from .assets import config_path
from .models import AppConfig


DEFAULT_CONFIG = AppConfig()


def load_app_config() -> AppConfig:
    path = config_path("app_config.json")
    if not path.exists() or path.stat().st_size == 0:
        save_app_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        save_app_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

    if not isinstance(data, dict):
        save_app_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

    config = AppConfig.from_mapping(data)
    save_app_config(config)
    return config


def save_app_config(config: AppConfig) -> None:
    path = config_path("app_config.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")


def load_tomato_positions() -> list[tuple[int, int]]:
    path = config_path("tomato_positions.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    positions = data.get("positions", [])
    result: list[tuple[int, int]] = []
    for item in positions:
        if isinstance(item, dict) and "x" in item and "y" in item:
            result.append((int(item["x"]), int(item["y"])))
    return result