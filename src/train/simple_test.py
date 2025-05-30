# -*- coding: utf-8 -*-
"""
简化的轻量级ASR性能测试
"""

import os
import sys
import time
import speech_recognition as sr
import warnings
import librosa
import numpy as np
import io
import wave

warnings.filterwarnings("ignore")

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def load_audio_file_robust(audio_file_path):
    """使用多种方法加载音频文件"""
    try:
        # 方法1: 直接使用speech_recognition
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file_path) as source:
            audio = recognizer.record(source)
        return audio
    except:
        pass
    
    try:
        # 方法2: 使用librosa加载，然后转换为wav格式
        y, sr_orig = librosa.load(audio_file_path, sr=16000)
        
        # 转换为PCM格式
        y_int = np.int16(y / np.max(np.abs(y)) * 32767)
          # 创建临时wav文件
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_file.close()  # 关闭文件句柄以便其他进程访问
        
        # 使用wave模块写入标准wav格式
        with wave.open(temp_file.name, 'wb') as wav_file:
            wav_file.setnchannels(1)  # 单声道
            wav_file.setsampwidth(2)  # 16位
            wav_file.setframerate(16000)  # 16kHz
            wav_file.writeframes(y_int.tobytes())
        
        # 重新加载
        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_file.name) as source:
            audio = recognizer.record(source)
        
        # 清理临时文件
        os.unlink(temp_file.name)
        return audio
    except Exception as e:
        print(f"无法加载音频文件: {e}")
        return None

def test_light_asr_basic():
    """基础ASR测试"""
    try:
        from train.model_integration import LightASREngine
        
        print("🔍 初始化轻量级ASR引擎...")
        start_time = time.time()
        engine = LightASREngine()
        load_time = time.time() - start_time
        print(f"📊 引擎初始化时间: {load_time:.3f}秒")
        
        if not engine.is_available():
            print("❌ 轻量级ASR不可用")
            return
        
        print("✅ 轻量级ASR引擎可用")
        
        # 获取引擎状态
        status = engine.get_model_info()
        print(f"📊 模型状态: {status}")
        
        # 测试音频文件推理
        test_audio_dir = "src/train/res/smart_home_dataset/audio"
        if os.path.exists(test_audio_dir):
            print(f"🎵 测试音频目录: {test_audio_dir}")
            
            # 获取第一个音频文件进行测试
            test_files = [f for f in os.listdir(test_audio_dir) if f.endswith('.wav')]
            
            if test_files:
                test_file = os.path.join(test_audio_dir, test_files[0])
                print(f"🎯 测试文件: {test_file}")
                
                try:
                    audio = load_audio_file_robust(test_file)
                    if audio is None:
                        print("❌ 无法加载音频文件")
                        return
                    
                    print("🚀 开始推理...")
                    start_time = time.time()
                    result = engine.recognize(audio)
                    inference_time = time.time() - start_time
                    
                    print(f"📊 推理时间: {inference_time:.3f}秒")
                    print(f"🎯 识别结果: {result}")
                    
                except Exception as e:
                    print(f"❌ 推理失败: {e}")
            else:
                print("❌ 未找到测试音频文件")
        else:
            print("❌ 测试音频目录不存在")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_enhanced_asr():
    """测试增强的ASR系统"""
    try:
        from train.model_integration import EnhancedAISpeechRecognizer
        
        print("🔍 初始化增强语音识别器...")
        
        def status_callback(message):
            print(f"[Status] {message}")
        
        enhanced_asr = EnhancedAISpeechRecognizer(
            status_callback=status_callback,
            use_light_asr=True
        )
        
        # 获取引擎状态
        status = enhanced_asr.get_engine_status()
        print(f"📊 引擎状态:")
        for key, value in status.items():
            print(f"  - {key}: {value}")
        
        # 检查麦克风
        if enhanced_asr.is_microphone_available():
            print("✅ 麦克风可用")
        else:
            print("⚠️ 麦克风不可用")
            
    except Exception as e:
        print(f"❌ 增强ASR测试失败: {e}")

def main():
    """主函数"""
    print("🏁 开始轻量级ASR基础性能测试")
    print("=" * 50)
    
    # 基础测试
    test_light_asr_basic()
    
    print("-" * 30)
    
    # 增强ASR测试
    test_enhanced_asr()
    
    print("=" * 50)
    print("✅ 测试完成")

if __name__ == "__main__":
    main()
