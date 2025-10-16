@echo off
setlocal enabledelayedexpansion

:: Resolve repository root (two levels up from this script directory)
set SCRIPT_DIR=%~dp0
for %%I in (.) do set SCRIPT_DRIVE=%%~dI
pushd "%SCRIPT_DIR%..\.."
set REPO_ROOT=%CD%
popd

pushd "%REPO_ROOT%"

if not exist .build-venv (
    echo [Orchard] Creating isolated build virtual environment...
    py -3 -m venv .build-venv || python -m venv .build-venv
)

if exist .build-venv\Scripts\activate.bat (
    call .build-venv\Scripts\activate.bat
) else (
    echo [Orchard] Failed to create virtual environment.
    pause
    exit /b 1
)

python -m pip install --upgrade pip wheel
python -m pip install --upgrade -e .
python -m pip install --upgrade pyinstaller

set SPEC=packaging\windows\orchard_portable.spec

pyinstaller --clean --noconfirm "%SPEC%"
if errorlevel 1 (
    echo [Orchard] PyInstaller 打包失败，请检查上方日志。
    pause
    exit /b 1
)

echo.
echo [Orchard] 便携版本已生成：dist\OrchardVideoDownloader\OrchardVideoDownloader.exe
if exist dist\OrchardVideoDownloader\ffmpeg (
    echo [提示] 请确认 ffmpeg.exe 位于 dist\OrchardVideoDownloader\ffmpeg\ 目录内。
) else (
    echo [提示] 如需随应用分发 ffmpeg，请新建 dist\OrchardVideoDownloader\ffmpeg\ 并放入 ffmpeg.exe。
)

echo.
echo [Orchard] 可将 dist\OrchardVideoDownloader\ 整个文件夹压缩后分享给最终用户，
echo          用户只需双击 OrchardVideoDownloader.exe 即可使用。

deactivate >nul 2>&1
popd
pause
