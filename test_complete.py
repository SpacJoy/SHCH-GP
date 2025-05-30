# -*- coding: utf-8 -*-
"""
智能语音控制家居系统 - 系统测试脚本
"""

import sys
import os

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """测试所有模块导入"""
    print("=== 测试模块导入 ===")
    try:
        # 测试配置模块
        from src.config import MQTT_CONFIG, GUI_CONFIG, DEVICE_COMMANDS
        print("✅ 配置模块导入成功")
        
        # 测试意图识别模块
        from src.intent_recognition import IntentRecognizer, EXAMPLE_COMMANDS
        print("✅ 意图识别模块导入成功")
        
        # 测试MQTT客户端模块
        from src.mqtt_client import MQTTClient, control_device
        print("✅ MQTT客户端模块导入成功")
        
        # 测试语音识别模块
        from src.speech_recognition_module import SpeechRecognizer
        print("✅ 语音识别模块导入成功")
        
        # 测试GUI模块
        from src.main_gui import SmartHomeGUI
        print("✅ GUI模块导入成功")
        
        return True
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 模块导入异常: {e}")
        return False

def test_intent_recognition():
    """测试意图识别功能"""
    print("\n=== 测试意图识别 ===")
    try:
        from src.intent_recognition import IntentRecognizer
        recognizer = IntentRecognizer()
        
        # 测试几个语音命令
        test_commands = [
            "打开客厅的灯",
            "关闭空调",
            "开启电视",
            "拉开窗帘",
            "关闭风扇"
        ]
        
        for cmd in test_commands:
            intent = recognizer.recognize_intent(cmd)
            if intent:
                print(f"✅ '{cmd}' -> 设备: {intent.get('device')}, 操作: {intent.get('action')}")
            else:
                print(f"❌ '{cmd}' -> 未识别到意图")
        
        return True
    except Exception as e:
        print(f"❌ 意图识别测试失败: {e}")
        return False

def test_speech_recognition():
    """测试语音识别模块初始化"""
    print("\n=== 测试语音识别模块 ===")
    try:
        from src.speech_recognition_module import SpeechRecognizer
        recognizer = SpeechRecognizer()
        print("✅ 语音识别器初始化成功")
        print("🎤 注意：实际语音识别需要麦克风设备")
        return True
    except RuntimeError as e:
        if "setuptools" in str(e) or "distutils" in str(e):
            print("❌ 语音识别需要setuptools支持")
            print("💡 解决方案：运行 pip install setuptools>=65.0.0")
            print("💡 或运行 fix_python312.bat")
        else:
            print(f"❌ 语音识别初始化失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 语音识别测试异常: {e}")
        return False

def test_mqtt_client():
    """测试MQTT客户端初始化"""
    print("\n=== 测试MQTT客户端 ===")
    try:
        from src.mqtt_client import MQTTClient
        
        # 测试配置验证
        try:
            client = MQTTClient()
            print("❌ 应该检测到配置错误，但没有")
            return False
        except ValueError as e:
            if "配置无效" in str(e):
                print("✅ MQTT配置验证正常工作")
                print("💡 提示：需要配置巴法云私钥才能连接MQTT")
                return True
            else:
                print(f"❌ 配置验证异常: {e}")
                return False
    except Exception as e:
        print(f"❌ MQTT客户端测试异常: {e}")
        return False

def test_dependencies():
    """测试Python依赖包"""
    print("\n=== 测试Python依赖包 ===")
    required_packages = [
        'tkinter',
        'speech_recognition', 
        'paho.mqtt.client',
        'pyaudio'
    ]
    
    all_ok = True
    for package in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            elif package == 'speech_recognition':
                import speech_recognition
            elif package == 'paho.mqtt.client':
                import paho.mqtt.client
            elif package == 'pyaudio':
                import pyaudio
            print(f"✅ {package} 已安装")
        except ImportError:
            print(f"❌ {package} 未安装")
            all_ok = False
        except Exception as e:
            print(f"⚠️ {package} 导入异常: {e}")
    
    return all_ok

def main():
    """主测试函数"""
    print("🏠 智能语音控制家居系统 - 系统测试")
    print("=" * 50)
    
    # 执行所有测试
    tests = [
        ("依赖包测试", test_dependencies),
        ("模块导入测试", test_imports),
        ("意图识别测试", test_intent_recognition),
        ("语音识别测试", test_speech_recognition),
        ("MQTT客户端测试", test_mqtt_client)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}执行异常: {e}")
            results.append((test_name, False))
    
    # 显示测试结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！系统准备就绪。")
        print("\n📝 下一步操作:")
        print("1. 运行 config.bat 配置巴法云连接")
        print("2. 运行 python src/main_gui.py 启动图形界面")
        print("3. 在界面中测试语音识别和设备控制功能")
    else:
        print("⚠️ 部分测试失败，请检查上述错误信息。")
        
        if not any(name == "依赖包测试" and result for name, result in results):
            print("\n💡 建议运行：pip install -r requirements.txt")
        
        if not any(name == "语音识别测试" and result for name, result in results):
            print("💡 建议运行：fix_python312.bat")

if __name__ == "__main__":
    main()
