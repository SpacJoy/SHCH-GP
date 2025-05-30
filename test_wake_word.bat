@echo off
chcp 65001 >nul
echo 🎯 唤醒词功能测试
echo ===============================================
echo.
echo 📋 功能说明:
echo - 支持唤醒词: 小智、智能助手、小助手、语音助手、你好智能
echo - 两阶段识别: 先检测唤醒词，再识别具体指令
echo - 降低资源消耗: 避免频繁调用AI识别服务
echo.
echo 🎤 使用方法:
echo 1. 确保麦克风正常工作
echo 2. 先说唤醒词 (如: "小智")
echo 3. 听到提示音后说指令 (如: "打开客厅的灯")
echo.
pause
echo.
echo 🚀 启动测试...
python test_wake_word.py
pause
