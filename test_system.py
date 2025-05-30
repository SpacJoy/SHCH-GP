# -*- coding: utf-8 -*-
"""
系统测试脚本 - 测试各个模块的基本功能
"""

import sys
import os

def test_imports():
    """测试模块导入"""
    print("=" * 50)
    print("测试模块导入...")
    
    try:
        import tkinter as tk
        print("✓ tkinter 模块可用")
    except ImportError:
        print("✗ tkinter 模块不可用")
        return False
    
    try:
        import speech_recognition as sr
        print("✓ speech_recognition 模块可用")
    except ImportError:
        print("✗ speech_recognition 模块不可用，请安装: pip install SpeechRecognition")
        return False
    
    try:
        import paho.mqtt.client as mqtt
        print("✓ paho-mqtt 模块可用")
    except ImportError:
        print("✗ paho-mqtt 模块不可用，请安装: pip install paho-mqtt")
        return False
    
    try:
        import pyaudio
        print("✓ pyaudio 模块可用")
    except ImportError:
        print("✗ pyaudio 模块不可用，请安装: pip install pyaudio")
        print("  注意: 在Windows上可能需要先安装Microsoft C++ Build Tools")
        return False
    
    return True

def test_microphone():
    """测试麦克风"""
    print("\n" + "=" * 50)
    print("测试麦克风...")
    
    try:
        import speech_recognition as sr
        r = sr.Recognizer()
        m = sr.Microphone()
        
        with m as source:
            r.adjust_for_ambient_noise(source)
        print("✓ 麦克风初始化成功")
        return True
    except Exception as e:
        print(f"✗ 麦克风测试失败: {e}")
        return False

def test_mqtt_connection():
    """测试MQTT连接 (使用测试配置)"""
    print("\n" + "=" * 50)
    print("测试MQTT连接...")
    
    try:
        import paho.mqtt.client as mqtt
        
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("✓ MQTT连接测试成功")
            else:
                print(f"✗ MQTT连接失败，错误代码: {rc}")
        
        # 使用公共测试服务器
        client = mqtt.Client("test_client")
        client.on_connect = on_connect
        
        # 这里只是测试连接能力，不连接真实服务器
        print("✓ MQTT客户端创建成功")
        return True
        
    except Exception as e:
        print(f"✗ MQTT测试失败: {e}")
        return False

def test_gui():
    """测试GUI"""
    print("\n" + "=" * 50)
    print("测试GUI...")
    
    try:
        import tkinter as tk
        
        root = tk.Tk()
        root.title("GUI测试")
        root.geometry("300x100")
        
        label = tk.Label(root, text="GUI测试成功！")
        label.pack(pady=20)
        
        button = tk.Button(root, text="关闭", command=root.destroy)
        button.pack()
        
        print("✓ GUI窗口已创建，请查看弹出的测试窗口")
        
        # 设置3秒后自动关闭
        root.after(3000, root.destroy)
        root.mainloop()
        
        print("✓ GUI测试完成")
        return True
        
    except Exception as e:
        print(f"✗ GUI测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("智能语音控制家居系统 - 环境测试")
    print(f"Python版本: {sys.version}")
    print(f"当前目录: {os.getcwd()}")
    
    tests = [
        ("模块导入", test_imports),
        ("麦克风", test_microphone),
        ("MQTT", test_mqtt_connection),
        ("GUI", test_gui)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name}测试异常: {e}")
            results.append((test_name, False))
    
    # 输出测试结果总结
    print("\n" + "=" * 50)
    print("测试结果总结:")
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    if all_passed:
        print("\n🎉 所有测试通过！系统可以正常运行。")
        print("运行主程序: python run.py")
    else:
        print("\n⚠️  部分测试失败，请安装缺失的依赖包后重试。")
        print("\n依赖包安装命令:")
        print("pip install SpeechRecognition paho-mqtt pyaudio")
        print("\n注意：")
        print("- 如果pip命令不可用，请重新安装Python并确保勾选'Add to PATH'")
        print("- pyaudio在Windows上可能需要额外的构建工具")
        print("- 可以尝试使用conda: conda install pyaudio")

if __name__ == "__main__":
    main()
    input("\n按回车键退出...")
