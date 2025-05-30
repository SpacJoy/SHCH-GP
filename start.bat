@echo off
chcp 65001 >nul
echo ===============================================
echo     智能语音控制家居系统 - 启动程序
echo ===============================================
echo.

echo 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH环境变量
    echo 请先运行 install.bat 安装环境
    pause
    exit /b 1
)

echo ✅ Python环境正常
echo.

echo 启动智能语音控制家居系统...
echo 请在程序界面中配置MQTT连接信息
echo.

python run.py

echo.
echo 程序已退出
pause
