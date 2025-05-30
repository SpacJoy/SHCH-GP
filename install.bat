@echo off
chcp 65001 >nul
echo ===============================================
echo     智能语音控制家居系统 - 安装脚本
echo ===============================================
echo.

echo 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH环境变量
    echo 请从 https://python.org 下载安装Python
    echo 安装时请确保勾选 "Add Python to PATH"
    pause
    exit /b 1
)

python --version
echo ✅ Python环境正常
echo.

echo 安装依赖包...
echo 正在安装 setuptools (Python 3.12兼容性)...
python -m pip install setuptools>=65.0.0
if errorlevel 1 (
    echo ❌ setuptools 安装失败
    goto :error
)

echo 正在安装 SpeechRecognition...
python -m pip install SpeechRecognition==3.10.0
if errorlevel 1 (
    echo ❌ SpeechRecognition 安装失败
    goto :error
)

echo 正在安装 paho-mqtt...
python -m pip install paho-mqtt==1.6.1
if errorlevel 1 (
    echo ❌ paho-mqtt 安装失败
    goto :error
)

echo 正在安装 pyaudio...
python -m pip install pyaudio==0.2.11
@REM if errorlevel 1 (
@REM     echo ❌ pyaudio 安装失败
@REM     echo 正在尝试备用安装方法...
@REM     python -m pip install pipwin
@REM     python -m pipwin install pyaudio
@REM     if errorlevel 1 (
@REM         echo ❌ pyaudio 安装失败
@REM         echo 请手动安装pyaudio或使用conda: conda install pyaudio
@REM         goto :error
@REM     )
@REM )

echo.
echo ✅ 所有依赖包安装完成！
echo.

echo 运行系统测试...
python test_system.py
echo.

echo 📝 配置巴法云MQTT连接...
echo 你可以使用以下方式配置：
echo   1. 运行配置助手: python config_helper.py
echo   2. 手动编辑: src/config.py
echo.

echo 安装完成！使用以下命令：
echo   配置系统: python config_helper.py  
echo   启动系统: python run.py
echo   演示版本: python demo.py
echo.
pause
exit /b 0

:error
echo.
echo ❌ 安装过程中出现错误
echo 请检查网络连接和Python环境
echo 或手动运行以下命令：
echo   python -m pip install SpeechRecognition paho-mqtt pyaudio
echo.
pause
exit /b 1
