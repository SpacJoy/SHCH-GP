@echo off
chcp 65001 >nul
echo ===============================================
echo     Python 3.12 兼容性修复工具
echo ===============================================
echo.

echo 正在安装setuptools以修复distutils兼容性问题...
python -m pip install --upgrade setuptools>=65.0.0

if errorlevel 1 (
    echo ❌ setuptools 安装失败
    echo.
    echo 请尝试以下解决方案：
    echo 1. 使用管理员权限运行此脚本
    echo 2. 手动执行: python -m pip install setuptools
    echo 3. 检查Python环境是否正确安装
    pause
    exit /b 1
) else (
    echo ✅ setuptools 安装成功！
    echo.
    echo 现在可以运行程序了：
    echo - 双击 start.bat 启动完整版本
    echo - 或者运行: python run.py
    echo.
)

pause
