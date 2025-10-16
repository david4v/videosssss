# Orchard Video Downloader

一个以 macOS 风格呈现的本地视频下载器，基于 [PySide6](https://doc.qt.io/qtforpython/) 桌面界面与 [yt-dlp](https://github.com/yt-dlp/yt-dlp) 下载引擎，支持 HLS/DASH 等常见网站的视频抓取与 FFmpeg 合并。

## 功能亮点
- 🍎 **苹果风格界面**：使用 Fusion 主题 + 自定义配色打造轻量、干净的窗口体验。
- 📥 **多格式下载**：内置最佳质量、MP4 优先以及音频提取三种格式模板。
- 📊 **实时进度与日志**：展示百分比、速度、剩余时间，并在日志面板输出详细状态。
- 🧰 **FFmpeg 检测**：自动检查 FFmpeg 路径并提供安装提示，针对 `4294967158/-138` 等常见错误给出指导。

## 最快方式：双击即用

> 如果你不想和命令行打交道，只需完成一次 Python 安装，然后照下面两个步骤即可。

1. **第一次准备**
   1. 安装 [Python 3.10+](https://www.python.org/downloads/)（Windows 记得勾选 *Add Python to PATH*）。
   2. 下载本项目 ZIP 并解压。
   3. 双击仓库根目录里的 **`double_click_to_start.pyw`**。
      - 第一次启动会自动通过 `pip` 安装 PySide6 与 yt-dlp，弹出提示后稍等。
      - 如果自动安装失败，脚本会弹窗提示，同时把详细日志写到 `~/OrchardVideoDownloader-error.log` 方便排查。

2. **以后使用**
   - 直接再次双击 `double_click_to_start.pyw` 就能打开苹果风格的下载器窗口。
   - 如果你把整个文件夹复制到 U 盘/桌面，也只需要双击同一个文件即可。

> **macOS 双击提醒**：第一次运行如果系统阻止打开，请在“系统设置 → 隐私与安全性”里选择“仍要打开”。

## 进阶操作（需要终端）
仍然可以使用传统的 Python 项目方式安装运行，这样便于开发和打包：

1. **创建虚拟环境并激活**：
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS / Linux
   source .venv/bin/activate
   ```

2. **安装依赖并运行**：
   ```bash
   pip install --upgrade pip
   pip install .
   python -m macdownloader
   ```
   - 第一次运行若提示缺少 FFmpeg，请根据状态栏提示安装（Windows 推荐 [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) 提供的编译版，macOS 使用 `brew install ffmpeg`）。
   - 如果安装在自定义路径，可在启动前设置环境变量：
     ```bash
     # Windows PowerShell
     setx FFMPEG_PATH "C:\\path\\to\\ffmpeg.exe"

     # macOS / Linux（当前终端会话）
     export FFMPEG_PATH="/usr/local/bin/ffmpeg"
     ```

3. **开始下载**：
   1. 粘贴视频网址。
   2. 选择保存目录（默认是“下载”文件夹）。
   3. 选择格式模板。
   4. 点击“开始下载”，等待进度条完成。
   5. 若想跟着演练一次，请参阅下方“接下来做什么？”中的入门演练。

## 接下来做什么？
- ✅ **完成第一次演练**：按照 [docs/getting_started_walkthrough.md](docs/getting_started_walkthrough.md) 中的“10 分钟上手”逐步操作，可验证环境与 FFmpeg 设置。
- ⚙️ **个性化配置**：尝试在界面右下角状态栏检查 FFmpeg 路径，必要时手动指定 `FFMPEG_PATH` 环境变量或更新到最新版本。
- 📦 **打包分发**：准备向朋友分享？按照下文“打包成独立 APP”小节使用 PyInstaller 生成单文件或 `.app` 包。
- 🧪 **收集兼容性数据**：若遇到下载失败，将日志导出并记录网址，方便后续扩展反爬虫解析策略。

## 常见问题
- **错误 -138 / 4294967158**：说明网站拒绝连接，尝试更换网络、配置代理或稍后重试。
- **FFmpeg 相关错误**：确认 FFmpeg 已安装并能在命令行执行 `ffmpeg -version`；必要时重新设置 `FFMPEG_PATH`。
- **需要批量或队列下载？** 目前单个任务模式更稳定，可多次粘贴链接开启多个线程，后续版本将加入批量导入。

## 打包成独立 APP
- Windows 可使用 [PyInstaller](https://pyinstaller.org/)：`pyinstaller -w -F src/macdownloader/__main__.py`
- macOS 可使用 `pyinstaller --windowed --name OrchardDownloader src/macdownloader/__main__.py`，再用 `create-dmg`/`appdmg` 打包 DMG。
- 打包后请将 `ffmpeg` 同目录分发，或在程序启动时提示用户下载。

## 开发说明
- 依赖声明于 `pyproject.toml`。
- 核心逻辑位于 `src/macdownloader/` 目录。
- 欢迎根据 `docs/download_app_plan.md` 继续扩展反爬虫策略与错误恢复逻辑。
