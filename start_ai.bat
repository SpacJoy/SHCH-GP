@echo off
echo 🚀 启动智能语音控制家居系统 - AI版本
echo.

cd /d "%~dp0"

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装或未添加到PATH
    echo 请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查依赖
echo 🔍 检查依赖包...
python -c "import speech_recognition, paho.mqtt.client, requests" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ 缺少必要依赖，正在安装...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
)

REM 启动AI版本的GUI
echo 🤖 启动AI语音识别版本...
python src/main_gui_ai.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ 程序运行出错
    echo 💡 你可以尝试:
    echo    1. 运行 test_ai_speech.py 测试AI语音识别
    echo    2. 检查配置文件 src/config.py
    echo    3. 确保麦克风权限已开启
    pause
)

echo.
echo 👋 程序已退出
pause
