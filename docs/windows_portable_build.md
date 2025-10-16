# Windows 便携版本打包指南

本文演示如何将 Orchard Video Downloader 打包成一个可以直接双击运行的 `OrchardVideoDownloader.exe`，最终用户无需再安装 Python 或打开命令行即可使用。

## 准备工作

1. 安装 [Python 3.10+ 64 位版本](https://www.python.org/downloads/windows/)，安装时务必勾选 **Add Python to PATH**。
2. 建议提前安装 [Microsoft Visual C++ Redistributable](https://learn.microsoft.com/cpp/windows/latest-supported-vc-redist)（大部分 Windows 11/10 已预装）。
3. 准备好 `ffmpeg.exe`。推荐下载 [Gyan.dev 提供的 Windows 版本](https://www.gyan.dev/ffmpeg/builds/) 并解压。

## 一键构建

仓库已经包含 `packaging/windows/build_portable.cmd`。只需双击它即可自动完成以下步骤：

- 创建独立的虚拟环境 `.build-venv`，不会污染系统 Python。
- 安装项目自身依赖及 PyInstaller。
- 调用 `pyinstaller` 生成 `dist/OrchardVideoDownloader/OrchardVideoDownloader.exe`。

首次运行会联网下载依赖，耗时取决于带宽。后续再次执行会复用虚拟环境，只会增量升级依赖。

## 打包 ffmpeg

1. 构建完成后，打开 `dist/OrchardVideoDownloader/` 目录。
2. 新建 `ffmpeg/` 子目录（如尚未自动创建）。
3. 将 `ffmpeg.exe` 拷贝到 `dist/OrchardVideoDownloader/ffmpeg/` 中。
4. 如需支持 `ffprobe`、`ffplay`，也可一起放入该目录。

应用启动时会优先使用该目录内的 ffmpeg，省去用户手动配置。

## 分发给最终用户

1. 确认文件结构如下：

```
dist/OrchardVideoDownloader/
├── OrchardVideoDownloader.exe
├── ffmpeg/
│   └── ffmpeg.exe
└── ...（PyInstaller 生成的其他文件夹和 DLL）
```

2. 将整个 `OrchardVideoDownloader/` 文件夹打包成 zip 或 7z。
3. 分享给用户后，他们只需解压并双击 `OrchardVideoDownloader.exe` 即可启动。

## 常见问题

- **首次启动没有反应**：确认用户系统中没有被安全软件拦截，或者尝试以管理员身份运行一次。
- **缺少 MSVCP140.dll 等**：请安装上文提到的 VC++ 运行库。
- **下载时报错 -138**：通常是网络或站点防护导致，参见 `docs/getting_started_walkthrough.md` 的排错章节。

如需自定义图标或修改 PyInstaller 参数，可编辑 `packaging/windows/orchard_portable.spec` 后重新运行构建脚本。
