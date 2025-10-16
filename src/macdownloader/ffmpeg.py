from __future__ import annotations

import os
import platform
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
