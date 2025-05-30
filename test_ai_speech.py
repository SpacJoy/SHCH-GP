# -*- coding: utf-8 -*-
"""
AI语音识别功能测试
"""

import sys
import os
import time
from datetime import datetime

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ai_speech_recognition import AISpeechRecognizer
from config import AI_SPEECH_CONFIG

def test_ai_speech_recognition():
    """测试AI语音识别功能"""
    print("🤖 AI语音识别测试开始")
    print("=" * 50)
    
    # 状态回调函数
    def status_callback(message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] 状态: {message}")
    
    try:
        # 初始化AI语音识别器
        print("🔧 正在初始化AI语音识别器...")
        recognizer = AISpeechRecognizer(status_callback=status_callback)
        print("✅ AI语音识别器初始化成功")
        
        # 检查麦克风
        if not recognizer.is_microphone_available():
            print("❌ 麦克风不可用，请检查设备")
            return
        
        print("🎤 麦克风检查通过")
        print(f"🤖 当前使用的AI引擎: {recognizer.engine}")
        
        # 进行几次单次识别测试
        print("\n📝 开始单次识别测试...")
        print("提示：每次测试后请说一句话")
        
        for i in range(3):
            print(f"\n🔄 第 {i+1} 次测试")
            input("按回车键开始识别，然后说话...")
            
            result = recognizer.recognize_once(timeout=10)
            if result:
                print(f"✅ 识别成功: {result}")
            else:
                print("⚠️ 未识别到内容")
            
            time.sleep(1)
        
        # 持续监听测试
        print("\n🔁 开始持续监听测试...")
        print("说话测试（说'退出'或等待30秒自动结束）:")
        
        start_time = time.time()
        test_count = 0
        max_tests = 10
        
        while time.time() - start_time < 30 and test_count < max_tests:
            result = recognizer.listen_continuous()
            if result:
                test_count += 1
                print(f"🎯 第{test_count}次识别: {result}")
                
                # 检查退出命令
                if "退出" in result or "结束" in result or "stop" in result.lower(): # type: ignore
                    print("👋 收到退出指令，结束测试")
                    break
            
            time.sleep(0.1)  # 短暂休息
        
        print("\n✅ 持续监听测试完成")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
    
    print("\n🏁 AI语音识别测试结束")
    print("=" * 50)

def show_config_info():
    """显示配置信息"""
    print("🔧 当前AI语音识别配置:")
    print(f"   引擎: {AI_SPEECH_CONFIG.get('engine', '未设置')}")
    
    if AI_SPEECH_CONFIG.get('engine') == 'baidu':
        baidu_config = AI_SPEECH_CONFIG.get('baidu', {})
        print(f"   百度配置:")
        print(f"     APP ID: {'已配置' if baidu_config.get('app_id') else '未配置'}")
        print(f"     API Key: {'已配置' if baidu_config.get('api_key') else '未配置'}")
        print(f"     Secret Key: {'已配置' if baidu_config.get('secret_key') else '未配置'}")
    
    print()

if __name__ == "__main__":
    print("🎙️ 智能语音控制家居系统 - AI语音识别测试")
    print()
    
    show_config_info()
    
    try:
        test_ai_speech_recognition()
    except KeyboardInterrupt:
        print("\n⏹️ 测试被用户中断")
    except Exception as e:
        print(f"\n💥 测试失败: {e}")
        print("\n💡 建议:")
        print("   1. 检查麦克风是否正常工作")
        print("   2. 确保网络连接正常")
        print("   3. 检查依赖库是否正确安装")
        print("   4. 如果使用百度AI，请配置API密钥")
    
    input("\n按回车键退出...")
