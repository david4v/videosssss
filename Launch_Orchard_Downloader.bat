@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

set "SCRIPT=%~dp0double_click_to_start.pyw"
if not exist "%SCRIPT%" (
    echo [Orchard] 无法找到 double_click_to_start.pyw，请确认沒有移动文件。
    pause
    exit /b 1
)

echo [Orchard] 正在寻找可用的 Python 解释器...

for %%P in (pyw.exe pythonw.exe py.exe python.exe) do (
    for /f "delims=" %%F in ('where %%P 2^>nul') do (
        set "LAUNCHER=%%F"
        set "LAUNCHER_BASENAME=%%~nxP"
        goto :launch
    )
)

echo [Orchard] 未检测到 Python。请先从 https://www.python.org/downloads/ 安装 3.10 以上版本并勾选 "Add Python to PATH"。
pause
exit /b 1

:launch
echo [Orchard] 找到 %LAUNCHER_BASENAME%，正在启动 Orchard Video Downloader...
if /I "!LAUNCHER_BASENAME!"=="py.exe" (
    py -3 "%SCRIPT%"
) else if /I "!LAUNCHER_BASENAME!"=="pyw.exe" (
    "!LAUNCHER!" "%SCRIPT%"
) else if /I "!LAUNCHER_BASENAME!"=="pythonw.exe" (
    "!LAUNCHER!" "%SCRIPT%"
) else (
    "!LAUNCHER!" "%SCRIPT%"
)
exit /b %errorlevel%
