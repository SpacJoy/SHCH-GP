@echo off
chcp 65001 >nul
title 唤醒词高级功能测试套件

echo.
echo 🚀 唤醒词高级功能测试套件
echo ================================

:menu
echo.
echo 请选择要运行的测试：
echo.
echo 1. 基础唤醒词功能测试
echo 2. 高级唤醒词功能测试  
echo 3. 性能监控和调优工具
echo 4. 完整功能演示
echo 5. 退出
echo.

set /p choice="请输入选项 (1-5): "

if "%choice%"=="1" goto basic_test
if "%choice%"=="2" goto advanced_test  
if "%choice%"=="3" goto performance_tool
if "%choice%"=="4" goto demo
if "%choice%"=="5" goto exit
goto invalid

:basic_test
echo.
echo 🎯 运行基础唤醒词功能测试...
python test_wake_word.py
pause
goto menu

:advanced_test
echo.
echo 🔬 运行高级唤醒词功能测试...
python test_wake_word_advanced.py
pause
goto menu

:performance_tool
echo.
echo 🎛️ 启动性能监控和调优工具...
python wake_word_tuning.py
pause
goto menu

:demo
echo.
echo 🎬 运行完整功能演示...
echo 这将按顺序运行所有测试，演示唤醒词的完整功能
echo.
echo 第一步：基础功能测试
pause
python test_wake_word.py

echo.
echo 第二步：高级功能测试
pause
python test_wake_word_advanced.py

echo.
echo 第三步：性能调优工具
pause
python wake_word_tuning.py

echo.
echo ✅ 完整演示完成！
pause
goto menu

:invalid
echo.
echo ❌ 无效选择，请重试
goto menu

:exit
echo.
echo 👋 感谢使用唤醒词测试套件！
echo.
pause
exit
