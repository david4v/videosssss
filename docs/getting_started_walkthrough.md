# 10 分钟上手 Orchard Video Downloader

这份演练假设你是第一次接触命令行或 Python，跟随步骤即可完成首次下载并熟悉常见报错的排查方式。

## 1. 准备环境
1. 如果你希望“一键启动”，可以在 Windows 上直接使用 `packaging/windows/build_portable.cmd` 打包出 `OrchardVideoDownloader.exe`，或按照 `README.md` 中的“最快方式：双击即用”章节运行现成的启动脚本（Windows 双击 `Launch_Orchard_Downloader.bat`，其余系统双击 `double_click_to_start.pyw`），让脚本自动安装依赖。
1. 如果你希望“一键启动”，先按照 `README.md` 的“最快方式：双击即用”完成初次双击（Windows 双击 `Launch_Orchard_Downloader.bat`，其余系统双击 `double_click_to_start.pyw`），让脚本自动安装依赖。
2. 想进一步熟悉命令行，请继续下面的终端步骤，在虚拟环境中运行：
   ```bash
   pip install --upgrade pip
   pip install .
   ```
   看到 `Successfully installed macdownloader-...` 即表示依赖已就绪。

## 2. 验证 FFmpeg
1. 在终端运行 `ffmpeg -version`，若能输出版本号则表示系统已安装。
2. 如果提示 `command not found`，请根据系统执行：
   - **Windows**：到 [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) 下载最新 `ffmpeg-git-full.7z`，解压后将 `bin/ffmpeg.exe` 路径复制出来。
   - **macOS**：运行 `brew install ffmpeg`。
   - **Linux**：例如 Ubuntu 执行 `sudo apt install ffmpeg`。
3. 若安装在自定义目录，启动前设置环境变量：
   ```bash
   # Windows PowerShell
   setx FFMPEG_PATH "C:\\path\\to\\ffmpeg.exe"

   # macOS / Linux（当前终端会话）
   export FFMPEG_PATH="/usr/local/bin/ffmpeg"
   ```

## 3. 启动应用
1. 保证虚拟环境处于激活状态。
2. 执行：
   ```bash
   python -m macdownloader
   ```
3. 首次进入请留意窗口底部状态栏，若显示 `未检测到 ffmpeg`，说明上一步配置有误，请重新检查。

## 4. 完成第一次下载
1. 复制一个可公开访问的视频链接，例如 [https://www.pexels.com/video/856227](https://www.pexels.com/video/856227)。
2. 在界面中粘贴链接、确认保存目录，然后点击“开始下载”。
3. 观察“下载任务”列表：
   - `进度` 列会从 `0%` 缓慢增长到 `100%`；
   - `速度` 显示当前传输速率；
   - `剩余时间` 动态更新；
   - `状态` 会依次经历“下载中”→“处理文件中”→“已完成”。
4. 下载结束后，点击右下角日志面板可查看 yt-dlp 与 FFmpeg 的详细输出。

## 5. 排查常见错误
| 现象 | 原因 | 解决办法 |
|------|------|----------|
| 弹窗提示“服务器拒绝访问（403）” | 目标站点阻止请求 | 确认链接是否需要登录，或稍后重试。 |
| 状态栏出现 `4294967158/-138` | 网络被远端拒绝或中间人干扰 | 尝试切换网络、使用代理或更新证书。 |
| 日志提到 `ffmpeg not found` | 未正确配置 ffmpeg | 回到第 2 步安装或设置 `FFMPEG_PATH`。 |
| 下载完成但找不到文件 | 仍在合并音视频 | 稍等片刻，或在输出目录中搜索视频标题。 |

## 6. 下一步
- 想做批量下载？可以多次粘贴链接开启多个任务，后续计划加入队列管理。
- 遇到特定网站失败？将日志保存后记录网址，稍后在 `docs/download_app_plan.md` 中扩展反爬策略。
- 需要封装应用？参考 `README.md` 中的“打包成独立 APP”章节。

祝使用愉快！
