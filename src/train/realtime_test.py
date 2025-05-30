# -*- coding: utf-8 -*-
"""
轻量级ASR实时语音测试
测试麦克风输入的实时识别
"""

import os
import sys
import time
import threading
import warnings
warnings.filterwarnings("ignore")

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_real_time_recognition():
    """测试实时语音识别"""
    try:
        from train.model_integration import EnhancedAISpeechRecognizer
        
        print("🎤 启动实时语音识别测试")
        print("=" * 50)
        
        def status_callback(message):
            print(f"[Status] {message}")
        
        # 初始化增强识别器
        recognizer = EnhancedAISpeechRecognizer(
            status_callback=status_callback,
            use_light_asr=True
        )
        
        # 检查系统状态
        status = recognizer.get_engine_status()
        print("📊 系统状态:")
        print(f"  - 轻量级ASR可用: {status['light_asr_available']}")
        print(f"  - 识别策略: {status['recognition_strategy']}")
        print(f"  - 基础引擎: {status['base_engine']}")
        
        if not recognizer.is_microphone_available():
            print("❌ 麦克风不可用，无法进行实时测试")
            return
        
        print("\n🎤 开始实时语音识别测试")
        print("说出智能家居指令，如：'打开客厅的灯'、'关闭空调'等")
        print("按 Ctrl+C 退出测试")
        print("-" * 30)
        
        test_count = 0
        success_count = 0
        recognition_times = []
        
        try:
            while test_count < 10:  # 最多测试10次
                print(f"\n[{test_count + 1}/10] 请说话...")
                
                start_time = time.time()
                result = recognizer.recognize_once(timeout=10)
                recognition_time = time.time() - start_time
                
                test_count += 1
                recognition_times.append(recognition_time)
                
                if result:
                    success_count += 1
                    print(f"✅ 识别结果: {result}")
                    print(f"⏱️ 识别时间: {recognition_time:.2f}秒")
                else:
                    print("❌ 未识别到语音或识别失败")
                    print(f"⏱️ 超时时间: {recognition_time:.2f}秒")
                
                # 短暂停顿
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n👋 用户中断测试")
        
        # 显示统计信息
        print("\n" + "=" * 50)
        print("📊 测试统计:")
        print(f"  - 总测试次数: {test_count}")
        print(f"  - 成功识别次数: {success_count}")
        print(f"  - 识别成功率: {success_count/max(test_count,1)*100:.1f}%")
        if recognition_times:
            avg_time = sum(recognition_times) / len(recognition_times)
            print(f"  - 平均响应时间: {avg_time:.2f}秒")
        
    except Exception as e:
        print(f"❌ 实时测试失败: {e}")

def test_wake_word_functionality():
    """测试唤醒词功能"""
    try:
        from train.model_integration import EnhancedAISpeechRecognizer
        
        print("\n🔊 启动唤醒词功能测试")
        print("=" * 50)
        
        def status_callback(message):
            print(f"[Wake] {message}")
        
        recognizer = EnhancedAISpeechRecognizer(
            status_callback=status_callback,
            use_light_asr=True
        )
        
        if not recognizer.is_microphone_available():
            print("❌ 麦克风不可用")
            return
        
        print("🎤 唤醒词测试模式")
        print("支持的唤醒词: '小智'、'智能助手'、'小空'、'小助手'等")
        print("请说出唤醒词，然后说出指令")
        print("测试时间: 30秒")
        print("-" * 30)
        
        start_time = time.time()
        wake_count = 0
        
        try:
            while time.time() - start_time < 30:  # 30秒测试
                print("🎯 等待唤醒词...")
                result = recognizer.listen_with_wake_word()
                
                if result:
                    wake_count += 1
                    print(f"✅ 唤醒成功 #{wake_count}: {result}")
                else:
                    print("⏰ 未检测到唤醒词")
                
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\n👋 用户中断测试")
        
        elapsed_time = time.time() - start_time
        print(f"\n📊 唤醒词测试结果:")
        print(f"  - 测试时长: {elapsed_time:.1f}秒")
        print(f"  - 唤醒次数: {wake_count}")
        
    except Exception as e:
        print(f"❌ 唤醒词测试失败: {e}")

def test_hybrid_strategy():
    """测试混合识别策略"""
    try:
        from train.model_integration import EnhancedAISpeechRecognizer
        
        print("\n🔄 启动混合策略测试")
        print("=" * 50)
        
        def status_callback(message):
            print(f"[Hybrid] {message}")
        
        recognizer = EnhancedAISpeechRecognizer(
            status_callback=status_callback,
            use_light_asr=True
        )
        
        if not recognizer.is_microphone_available():
            print("❌ 麦克风不可用")
            return
        
        print("🎤 混合策略测试")
        print("系统将同时使用轻量级ASR和标准ASR进行识别")
        print("请说出各种智能家居指令进行测试")
        print("-" * 30)
        
        test_phrases = [
            "请说出: '打开客厅的灯'",
            "请说出: '关闭空调'", 
            "请说出: '调高音量'",
            "请说出: '播放音乐'",
            "请说出: '调节温度'"
        ]
        
        for i, prompt in enumerate(test_phrases):
            print(f"\n[{i+1}/{len(test_phrases)}] {prompt}")
            
            start_time = time.time()
            result = recognizer.recognize_with_strategy(None)  # 使用默认策略
            recognition_time = time.time() - start_time
            
            if result:
                print(f"✅ 混合识别结果: {result}")
            else:
                print("❌ 识别失败")
            
            print(f"⏱️ 处理时间: {recognition_time:.2f}秒")
            
            if i < len(test_phrases) - 1:
                print("⏸️ 准备下一个测试...")
                time.sleep(2)
        
    except Exception as e:
        print(f"❌ 混合策略测试失败: {e}")

def main():
    """主函数"""
    print("🎤 轻量级ASR实时语音测试套件")
    print("=" * 60)
    
    import argparse
    parser = argparse.ArgumentParser(description="实时语音识别测试")
    parser.add_argument('--test', choices=['realtime', 'wake', 'hybrid', 'all'], 
                       default='realtime', help='测试类型')
    
    args = parser.parse_args()
    
    if args.test == 'all':
        # 运行所有测试
        test_real_time_recognition()
        test_wake_word_functionality() 
        test_hybrid_strategy()
    elif args.test == 'realtime':
        test_real_time_recognition()
    elif args.test == 'wake':
        test_wake_word_functionality()
    elif args.test == 'hybrid':
        test_hybrid_strategy()
    
    print("\n" + "=" * 60)
    print("🎊 测试完成！")

if __name__ == "__main__":
    main()
