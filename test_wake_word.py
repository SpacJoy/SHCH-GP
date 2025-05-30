# -*- coding: utf-8 -*-
"""
唤醒词功能测试脚本
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_wake_word_feature():
    """测试唤醒词功能"""
    print("🎯 测试唤醒词功能")
    print("=" * 50)
    
    try:
        from src.ai_speech_recognition import AISpeechRecognizer
        from src.config import WAKE_WORD_CONFIG
        
        def status_callback(message):
            print(f"[状态] {message}")
        
        # 初始化语音识别器
        print("📝 初始化语音识别器...")
        recognizer = AISpeechRecognizer(status_callback=status_callback)
        
        # 显示配置信息
        print(f"\n📋 唤醒词配置:")
        print(f"   - 启用状态: {WAKE_WORD_CONFIG.get('enabled', False)}")
        print(f"   - 支持的唤醒词: {', '.join(WAKE_WORD_CONFIG.get('keywords', []))}")
        print(f"   - 唤醒词检测超时: {WAKE_WORD_CONFIG.get('timeout', 3)}秒")
        print(f"   - 命令等待超时: {WAKE_WORD_CONFIG.get('command_timeout', 10)}秒")
        
        if not recognizer.wake_word_enabled:
            print("\n⚠️ 唤醒词功能未启用，将使用普通模式")
            return
        
        print(f"\n🎤 开始测试唤醒词功能...")
        print(f"   请先说唤醒词：{', '.join(recognizer.wake_words)}")
        print(f"   然后说出控制指令")
        print(f"   按 Ctrl+C 退出测试")
        
        try:
            while True:
                result = recognizer.listen_with_wake_word()
                if result:
                    print(f"✅ 识别成功: {result}")
                    break
                else:
                    print("⏸️ 本次循环未识别到内容，继续监听...")
                    
        except KeyboardInterrupt:
            print("\n🛑 测试已停止")
            
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保已安装所有依赖包")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_configuration():
    """测试配置是否正确"""
    print("\n🔧 检查配置...")
    
    try:
        from src.config import WAKE_WORD_CONFIG, SPEECH_CONFIG, AI_SPEECH_CONFIG
        
        print("✅ 配置文件加载成功")
        print(f"   - 语音识别语言: {SPEECH_CONFIG.get('language', 'zh-CN')}")
        print(f"   - AI引擎: {AI_SPEECH_CONFIG.get('engine', 'baidu')}")
        print(f"   - 唤醒词功能: {'启用' if WAKE_WORD_CONFIG.get('enabled') else '禁用'}")
        
        return True
    except Exception as e:
        print(f"❌ 配置检查失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 唤醒词功能测试")
    print("=" * 50)
    
    # 检查配置
    if not test_configuration():
        return
    
    # 提示用户
    print(f"\n📢 使用说明:")
    print(f"1. 确保麦克风正常工作")
    print(f"2. 在安静的环境中进行测试")
    print(f"3. 先说唤醒词，等待系统提示后再说指令")
    print(f"4. 支持的唤醒词：小智、智能助手、小助手、语音助手、你好智能")
    
    choice = input(f"\n是否开始测试？(y/n): ").lower().strip()
    if choice in ['y', 'yes', '是']:
        test_wake_word_feature()
    else:
        print("测试已取消")

if __name__ == "__main__":
    main()
