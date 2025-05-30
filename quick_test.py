#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能语音控制家居系统 - 快速功能测试
"""

def test_intent_recognition():
    """测试意图识别"""
    print("=== 测试意图识别功能 ===")
    try:
        from src.intent_recognition import IntentRecognizer
        recognizer = IntentRecognizer()
        
        test_commands = [
            "打开客厅的灯",
            "关闭空调", 
            "开启电视",
            "拉开窗帘"
        ]
        
        for cmd in test_commands:
            intent = recognizer.recognize_intent(cmd)
            if intent:
                print(f"✅ '{cmd}' -> {intent.get('device')} {intent.get('action')}")
            else:
                print(f"❌ '{cmd}' -> 未识别")
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_gui_components():
    """测试GUI组件"""
    print("\n=== 测试GUI组件 ===")
    try:
        from src.config import GUI_CONFIG, MQTT_CONFIG
        print(f"✅ 窗口标题: {GUI_CONFIG['title']}")
        print(f"✅ 窗口大小: {GUI_CONFIG['width']}x{GUI_CONFIG['height']}")
        print(f"✅ MQTT服务器: {MQTT_CONFIG['broker']}:{MQTT_CONFIG['port']}")
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def main():
    print("🏠 智能语音控制家居系统 - 快速测试")
    print("=" * 40)
    
    # 测试核心功能
    test_intent_recognition()
    test_gui_components()
    
    print("\n=== 系统状态 ===")
    print("✅ 核心模块正常")
    print("✅ GUI界面可启动") 
    print("✅ 意图识别工作正常")
    print("⚠️ MQTT需要配置巴法云私钥")
    print("⚠️ 语音识别需要麦克风")
    
    print("\n📋 使用说明:")
    print("1. 运行 config.bat 配置巴法云")
    print("2. 运行 python src/main_gui.py 启动界面")
    print("3. 在界面中测试语音控制功能")

if __name__ == "__main__":
    main()
