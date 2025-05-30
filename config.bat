@echo off
chcp 65001 >nul
echo ===============================================
echo     智能家居系统 - 巴法云配置助手
echo ===============================================
echo.

echo 启动配置助手...
python config_helper.py

if errorlevel 1 (
    echo.
    echo ❌ 配置助手运行失败
    echo 请确保Python环境正常
    pause
    exit /b 1
)

echo.
echo ✅ 配置完成！
echo 现在可以运行: start.bat 启动系统
echo.
pause
