@echo off
title AI语音识别演示
color 0a

echo.
echo     ╔══════════════════════════════════════════════════════════╗
echo     ║          🤖 智能家居AI语音识别系统演示 🏠                ║
echo     ╚══════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

:menu
echo 🎯 请选择演示项目:
echo.
echo     1. 🧪 测试AI语音识别功能
echo     2. 🔧 配置AI引擎 (百度AI/Whisper)
echo     3. 🚀 启动AI版本GUI界面
echo     4. 📊 查看系统状态
echo     5. 📖 查看使用说明
echo     6. 🚪 退出演示
echo.
set /p choice=请输入选择 (1-6): 

if "%choice%"=="1" goto test_ai
if "%choice%"=="2" goto config_ai
if "%choice%"=="3" goto start_gui
if "%choice%"=="4" goto check_status
if "%choice%"=="5" goto show_help
if "%choice%"=="6" goto exit
goto invalid

:test_ai
echo.
echo 🧪 启动AI语音识别测试...
echo ═══════════════════════════════════
echo 💡 提示: 测试将检查麦克风和AI引擎状态
echo.
pause
python test_ai_speech.py
echo.
echo 🔙 测试完成，按任意键返回菜单...
pause >nul
goto menu

:config_ai
echo.
echo 🔧 启动AI配置向导...
echo ═══════════════════════════════════
echo 💡 提示: 可配置百度AI、Whisper等引擎
echo.
pause
python ai_config_wizard.py
echo.
echo 🔙 配置完成，按任意键返回菜单...
pause >nul
goto menu

:start_gui
echo.
echo 🚀 启动AI版本GUI界面...
echo ═══════════════════════════════════
echo 💡 提示: 将打开完整的AI语音控制界面
echo.
pause
start "AI语音控制系统" python src/main_gui_ai.py
echo ✅ GUI已启动（新窗口）
echo.
echo 🔙 按任意键返回菜单...
pause >nul
goto menu

:check_status
echo.
echo 📊 系统状态检查
echo ═══════════════════════════════════
echo.

REM 检查Python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Python: 已安装
    python --version
) else (
    echo ❌ Python: 未安装
)

REM 检查依赖
python -c "import speech_recognition" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ SpeechRecognition: 已安装
) else (
    echo ❌ SpeechRecognition: 未安装
)

python -c "import paho.mqtt.client" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ MQTT客户端: 已安装
) else (
    echo ❌ MQTT客户端: 未安装
)

python -c "import requests" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Requests: 已安装
) else (
    echo ❌ Requests: 未安装
)

REM 检查可选依赖
python -c "import whisper" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Whisper AI: 已安装
) else (
    echo ⚠️ Whisper AI: 未安装 (可选)
)

REM 检查配置文件
if exist "src\config.py" (
    echo ✅ 配置文件: 存在
) else (
    echo ❌ 配置文件: 不存在
)

REM 检查AI模块
if exist "src\ai_speech_recognition.py" (
    echo ✅ AI语音模块: 存在
) else (
    echo ❌ AI语音模块: 不存在
)

echo.
echo 🔙 检查完成，按任意键返回菜单...
pause >nul
goto menu

:show_help
echo.
echo 📖 AI语音识别系统使用说明
echo ═══════════════════════════════════
echo.
echo 🎤 语音命令示例:
echo    • "打开客厅的灯"
echo    • "关闭空调"
echo    • "打开窗帘"
echo    • "关闭电视和风扇"
echo.
echo 🤖 支持的AI引擎:
echo    • 百度AI - 高精度，需要API密钥
echo    • Whisper - 本地识别，离线可用
echo    • Google - 默认引擎，免费但有限制
echo.
echo 🔧 配置步骤:
echo    1. 运行"配置AI引擎"选项
echo    2. 选择要使用的AI引擎
echo    3. 按向导提示完成配置
echo    4. 重新启动系统
echo.
echo 💡 使用技巧:
echo    • 保持环境安静
echo    • 说话清晰，语速适中
echo    • 观察状态栏的实时反馈
echo    • 确保麦克风权限已开启
echo.
echo 📁 更多帮助文档:
echo    • AI语音识别升级说明.md
echo    • AI升级完成报告.md
echo    • README.md
echo.
echo 🔙 按任意键返回菜单...
pause >nul
goto menu

:invalid
echo.
echo ❌ 无效选择，请重新输入
echo.
goto menu

:exit
echo.
echo 👋 感谢使用AI语音识别演示系统！
echo.
echo 🎉 主要特性:
echo    ✅ 多AI引擎支持 (百度AI/Whisper/Google)
echo    ✅ 实时状态显示和反馈
echo    ✅ 智能错误处理和降级
echo    ✅ 完善的配置和测试工具
echo.
echo 📞 技术支持: 查看项目文档或运行测试工具
echo.
pause
exit
