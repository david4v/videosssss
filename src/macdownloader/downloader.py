from __future__ import annotations

import traceback
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from PySide6.QtCore import QObject, Signal
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from .formatting import format_bytes, format_eta


@dataclass
class DownloadRequest:
    task_id: int
    url: str
    output_dir: Path
    format_code: str
    ffmpeg_location: Optional[Path] = None


class DownloadWorker(QObject):
    progress = Signal(dict)
    error = Signal(dict)
    finished = Signal(dict)
    log = Signal(str)

    def __init__(self, request: DownloadRequest) -> None:
        super().__init__()
        self.request = request
        self._last_filename: Optional[str] = None

    def run(self) -> None:
        try:
            payload = self._run_download()
            self.finished.emit(payload)
        except Exception as exc:  # pylint: disable=broad-except
            message = self._format_error(exc)
            self.error.emit({
                "task_id": self.request.task_id,
                "message": message,
            })
            self.finished.emit({
                "task_id": self.request.task_id,
                "success": False,
            })

    # ------------------------------------------------------------------
    def _run_download(self) -> Dict:
        output_dir = self.request.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        ydl_opts: Dict = {
            "format": self.request.format_code,
            "outtmpl": str(output_dir / "%(title)s [%(id)s].%(ext)s"),
            "noplaylist": True,
            "progress_hooks": [self._progress_hook],
            "retries": 5,
            "fragment_retries": 15,
            "concurrent_fragment_downloads": 5,
            "nocheckcertificate": False,
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            },
            "postprocessor_args": [
                "-movflags",
                "+faststart",
            ],
            "merge_output_format": "mp4",
            "quiet": True,
            "no_warnings": True,
        }

        if self.request.ffmpeg_location:
            ydl_opts["ffmpeg_location"] = str(self.request.ffmpeg_location)

        start_time = datetime.now()
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.request.url])
        except DownloadError as exc:
            raise RuntimeError(self._map_download_error(exc)) from exc

        duration = datetime.now() - start_time

        return {
            "task_id": self.request.task_id,
            "success": True,
            "duration": duration.total_seconds(),
            "filepath": str(Path(self._last_filename).resolve()) if self._last_filename else str(output_dir),
        }

    # ------------------------------------------------------------------
    def _progress_hook(self, status: Dict) -> None:
        task_id = self.request.task_id
        payload: Dict = {
            "task_id": task_id,
            "status": "运行中",
        }

        info_dict = status.get("info_dict") or {}
        if title := info_dict.get("title"):
            payload["title"] = title

        if filename := status.get("filename"):
            self._last_filename = filename
            payload.setdefault("title", Path(filename).name)

        state = status.get("status")
        if state == "downloading":
            downloaded = status.get("downloaded_bytes") or 0
            total = status.get("total_bytes") or status.get("total_bytes_estimate")
            progress = (downloaded / total * 100) if total else None
            payload["progress_text"] = f"{progress:.1f}%" if progress else f"{format_bytes(downloaded)}"
            speed_text = format_bytes(status.get("speed"))
            payload["speed"] = f"{speed_text}/s" if speed_text != "-" else "-"
            payload["eta"] = format_eta(status.get("eta"))
            payload["status"] = "下载中"
        elif state == "finished":
            payload["progress_text"] = "100%"
            payload["eta"] = "完成"
            payload["status"] = "处理文件中"
        elif state == "error":
            payload["status"] = "出错"
        else:
            payload["status"] = state or "等待"

        self.progress.emit(payload)

    # ------------------------------------------------------------------
    def _map_download_error(self, exc: DownloadError) -> str:
        message = str(exc)
        if "HTTP Error 403" in message:
            return "服务器拒绝访问（403）。请检查链接或稍后重试。"
        if "4294967158" in message or "Errno -138" in message or "status code -138" in message:
            return (
                "网络连接被目标网站拒绝（错误 -138）。\n"
                "建议：1）切换网络；2）在设置里配置代理；3）稍后再试。"
            )
        if "ffmpeg" in message.lower():
            return (
                "FFmpeg 执行失败，请确认已经安装并在设置中指定 ffmpeg 路径。"
            )
        return message or "未知下载错误"

    def _format_error(self, exc: Exception) -> str:
        message = str(exc)
        stack = traceback.format_exc()
        self.log.emit(stack)
        return message or "未知错误"
