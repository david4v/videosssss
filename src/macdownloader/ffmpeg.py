from __future__ import annotations

import os
import platform
import sys
from dataclasses import dataclass
from pathlib import Path
from shutil import which
from typing import Optional


@dataclass
class FFmpegStatus:
    path: Optional[Path]
    hint: Optional[str] = None
    warning: Optional[str] = None


def locate_ffmpeg() -> FFmpegStatus:
    """Try to locate the ffmpeg executable and produce hints."""
    bundled_path = _detect_bundled_ffmpeg()
    if bundled_path:
        return FFmpegStatus(path=bundled_path, hint="来自应用内置 ffmpeg")

    env_path = os.environ.get("FFMPEG_PATH")
    if env_path:
        candidate = Path(env_path).expanduser()
        if candidate.is_file():
            return FFmpegStatus(path=candidate, hint="来自环境变量 FFMPEG_PATH")

    discovered = which("ffmpeg")
    if discovered:
        return FFmpegStatus(path=Path(discovered))

    system = platform.system()
    if system == "Windows":
        hint = "到 https://www.gyan.dev/ffmpeg/builds/ 下载解压后，将 ffmpeg/bin 加入 Path。"
    elif system == "Darwin":
        hint = "推荐用 Homebrew 安装：brew install ffmpeg"
    else:
        hint = "使用系统包管理器安装，例如 Ubuntu 上执行 sudo apt install ffmpeg"

    warning = (
        "未检测到 ffmpeg，yt-dlp 在某些网站上将无法合并音频视频。"
        " 请安装后在环境变量 FFMPEG_PATH 中设置路径或加入系统 PATH。"
    )

    return FFmpegStatus(path=None, hint=hint, warning=warning)


def _detect_bundled_ffmpeg() -> Optional[Path]:
    """Detect ffmpeg packaged alongside the application (PyInstaller, portable build)."""

    candidates = []

    if getattr(sys, "frozen", False):  # PyInstaller runtime
        exe_dir = Path(sys.executable).resolve().parent
        candidates.extend(
            [
                exe_dir / "ffmpeg" / "ffmpeg.exe",
                exe_dir / "ffmpeg" / "ffmpeg",
                exe_dir / "ffmpeg.exe",
                exe_dir / "ffmpeg",
            ]
        )

    # Also check next to the source tree (useful for developer zip packages)
    here = Path(__file__).resolve().parent
    candidates.extend(
        [
            here.parent / "ffmpeg" / "ffmpeg.exe",
            here.parent / "ffmpeg" / "ffmpeg",
        ]
    )

    for path in candidates:
        if path.is_file():
            return path
    return None
