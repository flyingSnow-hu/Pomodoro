from __future__ import annotations

import tkinter as tk

import pystray
from PIL import Image
from pystray import Menu, MenuItem

from .assets import image_path
from .config import load_app_config, load_tomato_positions, save_app_config
from .models import AppConfig
from .platforms import PlatformIntegration, get_platform_integration
from .storage import StateRepository
from .timer import PomodoroTimer, TimerPhase, TimerStatus
from .sound import SoundManager
from .ui import SettingsWindow, SoundSettingsWindow, TreeWindow


class PomodoroApp:
    def __init__(self) -> None:
        self.app_name = "PomodoroPy"
        self.platform: PlatformIntegration = get_platform_integration()
        self.config = load_app_config()
        self.positions = load_tomato_positions()
        self.repository = StateRepository(self.app_name)
        self.daily_state, self.stats = self.repository.load_state()
        self.timer = PomodoroTimer(self.config)
        self.sound_manager = SoundManager(self.platform)
        self.root = tk.Tk()
        self.root.withdraw()
        self._window_icon = tk.PhotoImage(file=str(image_path("icon.png")))
        self.root.iconphoto(True, self._window_icon)

        self.tree_window = TreeWindow(
            self.root,
            str(image_path("bg.png")),
            str(image_path("tomatos16.png")),
            self.positions,
        )
        self.settings_window = SettingsWindow(self.root, self._save_settings)
        self.sound_settings_window = SoundSettingsWindow(self.root, self._save_settings)
        self.icon = pystray.Icon(
            self.app_name,
            self._load_tray_icon(),
            self._tray_title(),
            self._build_menu(),
        )

    def run(self) -> None:
        self.icon.run_detached()
        self._show_tree()
        self.root.after(1000, self._tick)
        self.root.mainloop()

    def _tick(self) -> None:
        self._sync_state()
        self.sound_manager.update()
        event = self.timer.tick()
        if event == "focus_completed":
            self._handle_focus_completed()
        elif event == "break_completed":
            self.sound_manager.play_end_sound(self.config.end_sound_mode, self.config.end_sound_path)
            self.platform.notify("准备开始下一轮", "休息结束，请手动点击开始/继续。")
        self._refresh_views()
        self.root.after(1000, self._tick)

    def _handle_focus_completed(self) -> None:
        self.platform.notify("番茄完成", "休息开始，1 秒后会在树上长出一个番茄。")
        self.sound_manager.play_end_sound(self.config.end_sound_mode, self.config.end_sound_path)
        self.tree_window.show(self.daily_state, self.stats.total_completed, self._status_text())
        self.root.after(1000, self._award_tomato)

    def _award_tomato(self) -> None:
        self.daily_state, self.stats, _ = self.repository.award_tomato(len(self.positions))
        self.platform.notify(
            "收获番茄",
            f"今日番茄 {self.daily_state.completed_today} 个，总番茄 {self.stats.total_completed} 个。",
        )
        self._refresh_views()

    def _start_or_resume(self) -> None:
        self.sound_manager.stop()
        self.timer.start_or_resume()
        self.platform.notify("番茄钟启动", "计时已开始。")
        self._refresh_views()

    def _pause(self) -> None:
        self.timer.pause()
        self._refresh_views()

    def _reset_phase(self) -> None:
        self.timer.reset_current_phase()
        self._refresh_views()

    def _skip_phase(self) -> None:
        event = self.timer.skip_current_phase()
        if event == "focus_skipped":
            self.platform.notify("已跳过番茄钟", "本轮不会计入番茄，已进入休息阶段。")
        else:
            self.platform.notify("已跳过休息", "新的番茄钟已开始。")
        self._refresh_views()

    def _show_tree(self) -> None:
        self._sync_state()
        self.tree_window.show(self.daily_state, self.stats.total_completed, self._status_text())

    def _show_settings(self) -> None:
        self.settings_window.show(self.config)

    def _show_sound_settings(self) -> None:
        self.sound_settings_window.show(self.config)

    def _save_settings(self, config: AppConfig) -> None:
        self.config = config
        save_app_config(config)
        self.timer.apply_config(config)
        self._refresh_views()

    def _quit(self) -> None:
        self.icon.stop()
        self.root.quit()

    def _sync_state(self) -> None:
        self.daily_state, self.stats, rolled = self.repository.ensure_today()
        if rolled:
            self.platform.notify("新的一天", "今日番茄树已清空，继续努力。")

    def _refresh_views(self) -> None:
        self.icon.title = self._tray_title()
        self.icon.menu = self._build_menu()
        if self.tree_window.visible:
            self.tree_window.refresh(self.daily_state, self.stats.total_completed, self._status_text())

    def _tray_title(self) -> str:
        return f"{self.app_name} | {self._status_text()}"

    def _status_text(self) -> str:
        snapshot = self.timer.snapshot()
        phase_label = {
            TimerPhase.FOCUS: "专注中",
            TimerPhase.SHORT_BREAK: "短休息",
            TimerPhase.LONG_BREAK: "长休息",
        }[snapshot.phase]
        status_label = {
            TimerStatus.IDLE: "未开始",
            TimerStatus.RUNNING: "进行中",
            TimerStatus.PAUSED: "已暂停",
        }[snapshot.status]
        return f"{phase_label} {status_label} {self._format_seconds(snapshot.remaining_seconds)}"

    def _build_menu(self) -> Menu:
        snapshot = self.timer.snapshot()
        
        # 根据状态判断各菜单项是否启用
        can_start_resume = snapshot.status in {TimerStatus.IDLE, TimerStatus.PAUSED}
        can_pause = snapshot.status == TimerStatus.RUNNING
        can_control = snapshot.status in {TimerStatus.RUNNING, TimerStatus.PAUSED}
        
        return Menu(
            MenuItem("显示番茄树", self._on_menu(self._show_tree), enabled=True),
            MenuItem("开始/继续", self._on_menu(self._start_or_resume), enabled=can_start_resume),
            MenuItem("暂停", self._on_menu(self._pause), enabled=can_pause),
            MenuItem("重置当前阶段", self._on_menu(self._reset_phase), enabled=can_control),
            MenuItem("跳过当前阶段", self._on_menu(self._skip_phase), enabled=can_control),
            MenuItem("设置", self._on_menu(self._show_settings), enabled=True),
            MenuItem("提示音设置", self._on_menu(self._show_sound_settings), enabled=True),
            MenuItem("停止音乐", self._on_menu(self._stop_music), enabled=True),
            MenuItem("退出", self._on_menu(self._quit), enabled=True),
        )

    def _stop_music(self) -> None:
        self.sound_manager.stop()

    def _on_menu(self, callback):
        def handler(icon, item) -> None:
            self.root.after(0, callback)

        return handler

    @staticmethod
    def _format_seconds(total_seconds: int) -> str:
        minutes, seconds = divmod(max(0, total_seconds), 60)
        return f"{minutes:02d}:{seconds:02d}"

    @staticmethod
    def _load_tray_icon() -> Image.Image:
        icon_source = Image.open(image_path("icon.png")).convert("RGBA")
        return icon_source.resize((64, 64), Image.Resampling.LANCZOS)