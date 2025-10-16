"""Double-click launcher for Orchard Video Downloader."""
from __future__ import annotations

import importlib
import os
import subprocess
import sys
import traceback
from pathlib import Path

try:
    import tkinter as _tk
    from tkinter import messagebox as _messagebox
except Exception:  # pragma: no cover - fallback when Tk unavailable
    _tk = None
    _messagebox = None

PACKAGE_REQUIREMENTS = ["PySide6>=6.7", "yt-dlp>=2023.12.30"]


def _show_message(title: str, message: str, *, error: bool = False) -> None:
    if _tk is None or _messagebox is None:
        return
    root = _tk.Tk()
    root.withdraw()
    try:
        if error:
            _messagebox.showerror(title, message)
        else:
            _messagebox.showinfo(title, message)
    finally:
        root.destroy()


def _ensure_requirements() -> None:
    missing: list[str] = []
    for spec in PACKAGE_REQUIREMENTS:
        pkg_name = spec.split(">=")[0].split("==")[0]
        module_name = pkg_name.replace("-", "_")
        try:
            importlib.import_module(module_name)
        except ImportError:
            missing.append(spec)
    if not missing:
        return

    _show_message(
        "Orchard Video Downloader",
        "正在为首次启动准备依赖，请稍等……",
    )

    cmd = [sys.executable, "-m", "pip", "install", *missing]
    env = os.environ.copy()
    env.setdefault("PYTHONUTF8", "1")
    subprocess.check_call(cmd, env=env)


def _launch_gui() -> None:
    root_dir = Path(__file__).resolve().parent
    src_dir = root_dir / "src"
    if src_dir.exists():
        sys.path.insert(0, str(src_dir))

    from macdownloader.__main__ import main as run_gui

    run_gui()


def main() -> None:
    try:
        _ensure_requirements()
        _launch_gui()
    except subprocess.CalledProcessError:
        _show_message(
            "启动失败",
            "依赖安装失败，请确认网络连接或稍后重试。",
            error=True,
        )
    except Exception as exc:  # pylint: disable=broad-except
        details = "".join(traceback.format_exception(exc))
        _show_message("启动失败", f"出现意外错误：\n{exc}\n\n详细信息已写入日志。", error=True)
        log_path = Path.home() / "OrchardVideoDownloader-error.log"
        try:
            log_path.write_text(details, encoding="utf-8")
        except OSError:
            pass


if __name__ == "__main__":
    main()
