@echo off
chcp 65001 >nul 2>&1
title 一人公司AI团队 v1.0

echo.
echo ====================================================
echo   一人公司AI团队  v1.0 (免费版)
echo   5个AI员工，一人搞定一家公司
echo ====================================================
echo.

:: 检查Python是否安装
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python，请先安装Python 3.10+
    echo 下载地址: https://www.python.org/downloads/
    echo 安装时请勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

:: 显示Python版本
python --version
echo.

:: 检查是否首次运行（没有config.local.yaml）
if not exist config.local.yaml (
    if not exist config.free.yaml (
        echo [错误] 缺少配置文件，请重新下载完整包
        pause
        exit /b 1
    )
    echo [首次运行] 自动生成配置文件...
    copy config.free.yaml config.local.yaml >nul 2>&1
    echo.
    echo ====================================================
    echo   请打开 config.local.yaml，填入你的 API Key 后
    echo   再双击 start.bat 启动！
    echo ====================================================
    echo.
    notepad config.local.yaml
    pause
    exit /b 0
)

:: 检查API Key是否已填写
findstr /C:"your-api-key-here" config.local.yaml >nul 2>&1
if %errorlevel% equ 0 (
    echo [提示] 检测到API Key未填写，请先配置！
    echo.
    notepad config.local.yaml
    echo 配置完成后，请重新双击 start.bat
    pause
    exit /b 0
)

:: 启动
python start.py

:: 如果异常退出
if %errorlevel% neq 0 (
    echo.
    echo [启动失败] 请检查上方错误信息
    pause
)
