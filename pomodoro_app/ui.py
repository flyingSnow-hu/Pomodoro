from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Callable

from PIL import Image, ImageTk

from .models import AppConfig, DailyState


class TreeWindow:
    def __init__(
        self,
        root: tk.Misc,
        background_path: str,
        sprite_sheet_path: str,
        positions: list[tuple[int, int]],
    ) -> None:
        self._root = root
        self._positions = positions
        self._background_source = Image.open(background_path).convert("RGBA")
        self._sprite_source = Image.open(sprite_sheet_path).convert("RGBA")
        self._window = tk.Toplevel(root)
        self._window.title("PomodoroPy")
        self._window.protocol("WM_DELETE_WINDOW", self.hide)
        self._window.withdraw()
        self._window.resizable(False, False)
        self._canvas = tk.Canvas(self._window, highlightthickness=0, bd=0)
        self._canvas.pack(fill="both", expand=True)
        self._scale = 1.0
        self._background_image: ImageTk.PhotoImage | None = None
        self._sprite_images: list[ImageTk.PhotoImage] = []

    @property
    def visible(self) -> bool:
        return self._window.state() != "withdrawn"

    def show(self, daily_state: DailyState, total_completed: int, status_text: str) -> None:
        self.refresh(daily_state, total_completed, status_text)
        self._window.deiconify()
        self._window.lift()
        self._window.focus_force()

    def hide(self) -> None:
        self._window.withdraw()

    def refresh(self, daily_state: DailyState, total_completed: int, status_text: str) -> None:
        self._prepare_images()
        self._canvas.delete("all")
        if self._background_image is not None:
            self._canvas.create_image(0, 0, anchor="nw", image=self._background_image)
        for tomato in daily_state.tomatoes:
            if not self._sprite_images:
                break
            x, y = self._positions[tomato.position_index % len(self._positions)]
            self._canvas.create_image(
                int(x * self._scale),
                int(y * self._scale),
                anchor="center",
                image=self._sprite_images[tomato.sprite_index % len(self._sprite_images)],
            )
        padding = max(18, int(24 * self._scale))
        width = self._background_image.width() if self._background_image is not None else 960
        height = self._background_image.height() if self._background_image is not None else 960
        self._canvas.create_text(
            padding,
            padding,
            anchor="nw",
            text=status_text,
            fill="#254117",
            font=("Microsoft YaHei UI", max(16, int(24 * self._scale)), "bold"),
        )
        self._canvas.create_text(
            padding,
            height - padding,
            anchor="sw",
            text=f"总番茄数：{total_completed}",
            fill="#ff160c",
            font=("Microsoft YaHei UI", max(16, int(28 * self._scale)), "bold"),
        )
        self._canvas.configure(width=width, height=height)

    def _prepare_images(self) -> None:
        bg_width, bg_height = self._background_source.size
        screen_width = self._window.winfo_screenwidth()
        screen_height = self._window.winfo_screenheight()
        new_scale = min((screen_width * 0.82) / bg_width, (screen_height * 0.82) / bg_height, 1.0)
        if self._background_image is not None and abs(new_scale - self._scale) < 0.001:
            return
        self._scale = new_scale
        display_size = (max(1, int(bg_width * self._scale)), max(1, int(bg_height * self._scale)))
        background = self._background_source.resize(display_size, Image.Resampling.LANCZOS)
        self._background_image = ImageTk.PhotoImage(background)
        self._window.geometry(f"{display_size[0]}x{display_size[1]}")

        cell_width = self._sprite_source.width // 4
        cell_height = self._sprite_source.height // 4
        target_size = max(36, int(76 * self._scale))
        self._sprite_images = []
        for row in range(4):
            for column in range(4):
                crop = self._sprite_source.crop(
                    (
                        column * cell_width,
                        row * cell_height,
                        (column + 1) * cell_width,
                        (row + 1) * cell_height,
                    )
                )
                resized = crop.resize((target_size, target_size), Image.Resampling.LANCZOS)
                self._sprite_images.append(ImageTk.PhotoImage(resized))


class SettingsWindow:
    def __init__(self, root: tk.Misc, on_save: Callable[[AppConfig], None]) -> None:
        self._root = root
        self._on_save = on_save
        self._window = tk.Toplevel(root)
        self._window.title("番茄钟设置")
        self._window.withdraw()
        self._window.resizable(False, False)
        self._window.protocol("WM_DELETE_WINDOW", self.hide)

        self._entries: dict[str, ttk.Entry] = {}
        fields = [
            ("focus_minutes", "番茄钟时长（分钟）"),
            ("short_break_minutes", "短休息时长（分钟）"),
            ("long_break_every", "多少次后长休息"),
            ("long_break_minutes", "长休息时长（分钟）"),
        ]

        container = ttk.Frame(self._window, padding=18)
        container.grid(row=0, column=0, sticky="nsew")
        for row, (field_name, label_text) in enumerate(fields):
            ttk.Label(container, text=label_text).grid(row=row, column=0, sticky="w", pady=6)
            entry = ttk.Entry(container, width=10)
            entry.grid(row=row, column=1, sticky="ew", pady=6, padx=(12, 0))
            self._entries[field_name] = entry

        button = ttk.Button(container, text="保存设置", command=self._save)
        button.grid(row=len(fields), column=0, columnspan=2, sticky="ew", pady=(14, 0))
        container.columnconfigure(1, weight=1)

    def show(self, config: AppConfig) -> None:
        for field_name, entry in self._entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, str(getattr(config, field_name)))
        self._window.deiconify()
        self._window.lift()
        self._window.focus_force()

    def hide(self) -> None:
        self._window.withdraw()

    def _save(self) -> None:
        try:
            config = AppConfig(
                focus_minutes=max(1, int(self._entries["focus_minutes"].get())),
                short_break_minutes=max(1, int(self._entries["short_break_minutes"].get())),
                long_break_every=max(1, int(self._entries["long_break_every"].get())),
                long_break_minutes=max(1, int(self._entries["long_break_minutes"].get())),
            )
        except ValueError:
            messagebox.showerror("输入无效", "请填写大于 0 的整数。", parent=self._window)
            return
        self._on_save(config)
        messagebox.showinfo("保存成功", "设置已更新，当前阶段计时已重置。", parent=self._window)
        self.hide()