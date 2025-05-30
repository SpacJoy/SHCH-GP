# -*- coding: utf-8 -*-
"""
高级唤醒词功能测试脚本
测试自适应阈值、统计信息和性能优化功能
"""

import sys
import os
import time
import json
from datetime import datetime

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ai_speech_recognition import AISpeechRecognizer
from config import WAKE_WORD_CONFIG

def print_banner():
    """打印测试横幅"""
    print("🚀 高级唤醒词功能测试")
    print("=" * 50)

def print_config():
    """打印唤醒词配置"""
    print("🔧 唤醒词配置:")
    for key, value in WAKE_WORD_CONFIG.items():
        print(f"   - {key}: {value}")
    print()

def test_wake_word_stats(recognizer):
    """测试唤醒词统计功能"""
    print("📊 唤醒词统计信息:")
    stats = recognizer.get_wake_word_stats()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"   - {key}: {value:.2f}")
        else:
            print(f"   - {key}: {value}")
    print()

def test_adaptive_threshold(recognizer):
    """测试自适应阈值功能"""
    print("🎛️ 自适应阈值测试:")
    initial_threshold = recognizer.dynamic_energy_threshold
    print(f"   - 初始阈值: {initial_threshold}")
    
    # 模拟几次检测
    print("   - 模拟唤醒词检测...")
    recognizer._adaptive_threshold_adjustment(True)
    print(f"   - 检测后阈值: {recognizer.dynamic_energy_threshold}")
    
    print("   - 模拟误检...")
    recognizer._adaptive_threshold_adjustment(False)
    print(f"   - 误检后阈值: {recognizer.dynamic_energy_threshold}")
    print()

def test_wake_word_detection_loop(recognizer):
    """测试唤醒词检测循环"""
    print("🎤 开始高级唤醒词测试...")
    print("   支持的唤醒词：", ", ".join(recognizer.wake_words))
    print("   按 Ctrl+C 停止测试")
    print()
    
    test_count = 0
    start_time = time.time()
    
    try:
        while True:
            test_count += 1
            print(f"🔄 第 {test_count} 轮测试")
            
            # 测试唤醒词检测
            result = recognizer.listen_with_wake_word()
            
            if result:
                print(f"✅ 成功识别: {result}")
                # 显示统计信息
                test_wake_word_stats(recognizer)
            else:
                print("⏸️ 本次未识别到内容")
            
            # 每10次测试显示一次性能统计
            if test_count % 10 == 0:
                elapsed_time = time.time() - start_time
                print(f"📈 性能统计: {test_count} 次测试，耗时 {elapsed_time:.1f} 秒")
                test_wake_word_stats(recognizer)
                
            time.sleep(0.5)  # 短暂休息
            
    except KeyboardInterrupt:
        print("\n🛑 测试被用户中断")
        
    finally:
        # 显示最终统计
        elapsed_time = time.time() - start_time
        print(f"\n📋 测试总结:")
        print(f"   - 总测试次数: {test_count}")
        print(f"   - 总耗时: {elapsed_time:.1f} 秒")
        print(f"   - 平均每次: {elapsed_time/max(1, test_count):.2f} 秒")
        test_wake_word_stats(recognizer)

def test_fallback_detection(recognizer):
    """测试备用检测机制"""
    print("🔄 测试备用检测机制...")
    
    # 临时禁用主检测，测试备用检测
    original_fallback = recognizer.fallback_detection
    recognizer.fallback_detection = True
    
    print("   - 备用检测已启用")
    
    # 恢复设置
    recognizer.fallback_detection = original_fallback
    print("   - 备用检测测试完成")
    print()

def main():
    """主测试函数"""
    print_banner()
    
    # 检查配置
    print_config()
    
    # 初始化语音识别器
    print("📝 初始化AI语音识别器...")
    try:
        recognizer = AISpeechRecognizer(status_callback=lambda msg: print(f"[状态] {msg}"))
        print("✅ AI语音识别器初始化成功")
        print()
        
        # 测试各项功能
        test_adaptive_threshold(recognizer)
        test_fallback_detection(recognizer)
        test_wake_word_stats(recognizer)
        
        # 询问是否进行实际测试
        response = input("是否开始实际语音测试？(y/n): ").lower().strip()
        if response in ['y', 'yes', '是', '']:
            test_wake_word_detection_loop(recognizer)
        else:
            print("跳过实际语音测试")
            
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return False
    
    print("\n🎯 高级唤醒词测试完成！")
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 测试被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 测试过程中发生异常: {e}")
        sys.exit(1)
