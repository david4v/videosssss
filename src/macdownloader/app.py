from __future__ import annotations

import platform
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from PySide6.QtCore import QThread, Qt, Slot
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QSizePolicy,
    QStatusBar,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
    QFileDialog,
)

from .downloader import DownloadRequest, DownloadWorker
from .ffmpeg import FFmpegStatus, locate_ffmpeg


@dataclass
class DownloadUIState:
    item: QTreeWidgetItem
    thread: QThread
    worker: DownloadWorker


class MainWindow(QMainWindow):
    """Primary macOS-inspired download window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Orchard Video Downloader")
        self.setMinimumSize(920, 600)

        self._ffmpeg_status: Optional[FFmpegStatus] = None
        self._download_counter = 0
        self._downloads: Dict[int, DownloadUIState] = {}

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(18, 18, 18, 12)
        layout.setSpacing(12)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("粘贴你要下载的视频链接，例如 https://example.com/video")
        self.url_input.setClearButtonEnabled(True)

        self.output_input = QLineEdit()
        self.output_input.setPlaceholderText("保存到…")
        self.output_input.setText(str(Path.home() / "Downloads"))
        self.output_input.setClearButtonEnabled(True)
        self.output_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        browse_button = QPushButton("选择…")
        browse_button.clicked.connect(self.select_output_directory)

        format_box = QComboBox()
        format_box.addItem("最佳可用质量 (自动合并)", "bv*+ba/b")
        format_box.addItem("仅下载视频+音频打包 (MP4优先)", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best")
        format_box.addItem("仅音频 (M4A/MP3)", "bestaudio/best")
        self.format_box = format_box

        header_box = QGroupBox("下载设置")
        form = QFormLayout(header_box)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.addRow("视频链接", self.url_input)

        output_row = QHBoxLayout()
        output_row.addWidget(self.output_input)
        output_row.addWidget(browse_button)
        form.addRow("保存位置", output_row)
        form.addRow("格式", format_box)

        self.start_button = QPushButton("开始下载")
        self.start_button.clicked.connect(self.start_download)
        self.start_button.setDefault(True)
        self.start_button.setFixedHeight(36)

        downloads_group = QGroupBox("下载任务")
        downloads_layout = QVBoxLayout(downloads_group)
        self.downloads_view = QTreeWidget()
        self.downloads_view.setColumnCount(5)
        self.downloads_view.setHeaderLabels([
            "名称",
            "进度",
            "速度",
            "剩余时间",
            "状态",
        ])
        self.downloads_view.setRootIsDecorated(False)
        self.downloads_view.setAlternatingRowColors(True)
        downloads_layout.addWidget(self.downloads_view)

        self.log_panel = QPlainTextEdit()
        self.log_panel.setPlaceholderText("下载日志将在这里显示，包括错误提示和FFmpeg输出。")
        self.log_panel.setReadOnly(True)
        self.log_panel.setMinimumHeight(150)

        layout.addWidget(header_box)
        layout.addWidget(self.start_button)
        layout.addWidget(downloads_group, stretch=1)
        layout.addWidget(self.log_panel, stretch=1)

        status_bar = QStatusBar()
        self.ffmpeg_label = QLabel()
        status_bar.addWidget(self.ffmpeg_label)
        self.setStatusBar(status_bar)

        self.setCentralWidget(central)

        self.refresh_ffmpeg_status()

    @Slot()
    def select_output_directory(self) -> None:
        directory = QFileDialog.getExistingDirectory(self, "选择下载保存目录", self.output_input.text())
        if directory:
            self.output_input.setText(directory)

    @Slot()
    def start_download(self) -> None:
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "缺少链接", "请输入要下载的视频链接。")
            return

        output_dir = Path(self.output_input.text()).expanduser().resolve()
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            QMessageBox.critical(self, "无法创建目录", f"创建或访问目录失败：{exc}")
            return

        self._download_counter += 1
        task_id = self._download_counter

        item = QTreeWidgetItem(
            [url, "0%", "-", "-", "准备中"]
        )
        self.downloads_view.addTopLevelItem(item)
        self.downloads_view.scrollToItem(item)

        request = DownloadRequest(
            task_id=task_id,
            url=url,
            output_dir=output_dir,
            format_code=self.format_box.currentData(),
            ffmpeg_location=self._ffmpeg_status.path if self._ffmpeg_status else None,
        )

        worker = DownloadWorker(request)
        thread = QThread(self)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)

        worker.progress.connect(self.handle_progress)
        worker.log.connect(self.append_log)
        worker.error.connect(self.handle_error)
        worker.finished.connect(self.handle_finished)

        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)

        self._downloads[task_id] = DownloadUIState(item=item, thread=thread, worker=worker)

        thread.start()
        self.append_log(f"开始下载任务 #{task_id}: {url}")
        self.url_input.clear()

    @Slot(dict)
    def handle_progress(self, payload: Dict) -> None:
        task_id = payload["task_id"]
        state = self._downloads.get(task_id)
        if not state:
            return

        item = state.item
        title = payload.get("title") or item.text(0)
        if title:
            item.setText(0, title)

        progress_text = payload.get("progress_text", "-")
        item.setText(1, progress_text)
        item.setText(2, payload.get("speed", "-"))
        item.setText(3, payload.get("eta", "-"))
        status_text = payload.get("status", "运行中")
        item.setText(4, status_text)

    @Slot(dict)
    def handle_error(self, payload: Dict) -> None:
        task_id = payload.get("task_id")
        message = payload.get("message", "未知错误")
        if task_id and task_id in self._downloads:
            item = self._downloads[task_id].item
            item.setText(4, "失败")
        QMessageBox.critical(self, "下载失败", message)
        self.append_log(f"任务 #{task_id} 失败: {message}")

    @Slot(dict)
    def handle_finished(self, payload: Dict) -> None:
        task_id = payload.get("task_id")
        success = payload.get("success", False)
        if not task_id or task_id not in self._downloads:
            return
        item = self._downloads[task_id].item
        if success:
            item.setText(4, "已完成")
            self.append_log(f"任务 #{task_id} 完成: {payload.get('filepath', '')}")
        else:
            if item.text(4) != "失败":
                item.setText(4, "已结束")
        self._downloads[task_id].thread.wait(50)
        self._downloads.pop(task_id, None)

    def refresh_ffmpeg_status(self) -> None:
        self._ffmpeg_status = locate_ffmpeg()
        if not self._ffmpeg_status.path:
            text = "未检测到 ffmpeg，可在设置里手动指定或安装后重启应用。"
            if self._ffmpeg_status.hint:
                text += f" 提示: {self._ffmpeg_status.hint}"
        else:
            text = f"ffmpeg: {self._ffmpeg_status.path}"
            if self._ffmpeg_status.hint:
                text += f" ({self._ffmpeg_status.hint})"
        self.ffmpeg_label.setText(text)
        if self._ffmpeg_status.warning:
            self.append_log(self._ffmpeg_status.warning)

    @Slot(str)
    def append_log(self, message: str) -> None:
        self.log_panel.appendPlainText(message)


def configure_app(app: QApplication) -> None:
    """Apply a macOS-inspired palette for a clean light look."""
    app.setStyle("Fusion")
    palette = QPalette()

    base = QColor(246, 246, 248)
    window = QColor(236, 236, 239)
    text = QColor(30, 30, 30)
    highlight = QColor(0, 122, 255)

    palette.setColor(QPalette.ColorRole.Window, window)
    palette.setColor(QPalette.ColorRole.WindowText, text)
    palette.setColor(QPalette.ColorRole.Base, base)
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(230, 230, 233))
    palette.setColor(QPalette.ColorRole.ToolTipBase, base)
    palette.setColor(QPalette.ColorRole.ToolTipText, text)
    palette.setColor(QPalette.ColorRole.Text, text)
    palette.setColor(QPalette.ColorRole.Button, base)
    palette.setColor(QPalette.ColorRole.ButtonText, text)
    palette.setColor(QPalette.ColorRole.Highlight, highlight)
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("white"))

    palette.setColor(QPalette.ColorRole.Light, QColor(255, 255, 255))
    palette.setColor(QPalette.ColorRole.Midlight, QColor(225, 225, 228))
    palette.setColor(QPalette.ColorRole.Dark, QColor(160, 160, 163))
    palette.setColor(QPalette.ColorRole.Mid, QColor(200, 200, 203))
    palette.setColor(QPalette.ColorRole.Shadow, QColor(120, 120, 123))

    app.setPalette(palette)
    app.setStyleSheet(
        """
        QMainWindow { background-color: #ECF0F3; }
        QGroupBox { border: 1px solid #D0D3D8; border-radius: 8px; margin-top: 1.4em; padding: 12px; }
        QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 0 4px; color: #3C3C3C; }
        QPushButton { border-radius: 6px; padding: 6px 18px; background-color: #F9F9FA; border: 1px solid #C9CCD1; }
        QPushButton:hover { background-color: #F1F5FF; }
        QPushButton:pressed { background-color: #E5E9F7; }
        QPushButton:disabled { background-color: #E0E0E0; color: #A0A0A0; }
        QLineEdit, QComboBox { border-radius: 6px; border: 1px solid #C9CCD1; padding: 6px; }
        QTreeWidget { border-radius: 8px; border: 1px solid #D0D3D8; background-color: #FFFFFF; }
        QPlainTextEdit { border-radius: 8px; border: 1px solid #D0D3D8; background-color: #FFFFFF; }
        """
    )

    if platform.system() == "Darwin":
        app.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, True)
