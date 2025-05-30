#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
轻量级ASR性能基准测试 v4
使用SmartHomeSpeechSynthesizer的简化版本
"""

import time
import os
import sys
import traceback
import psutil
import numpy as np
import torch
import torchaudio
from pathlib import Path

# 添加路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from model_integration import LightASREngine
    from dataset_generator import SmartHomeSpeechSynthesizer
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    sys.exit(1)


class SimpleBenchmark:
    """简化的ASR性能基准测试器"""
    
    def __init__(self):
        """初始化基准测试器"""
        self.engine = None
        self.speech_synthesizer = SmartHomeSpeechSynthesizer()
        
    def test_model_loading(self):
        """测试模型加载性能"""
        print("🔍 测试模型加载时间...")
        
        start_time = time.time()
        try:
            self.engine = LightASREngine()
            load_time = time.time() - start_time
            print(f"✅ 模型加载成功，耗时: {load_time:.3f}秒")
            return load_time
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            return None
    
    def create_test_audio(self, text, filename):
        """创建测试音频文件"""
        try:
            # 使用SmartHomeSpeechSynthesizer生成音频
            audio = self.speech_synthesizer.synthesize_speech(text, duration=2.0, voice_type='male')
            
            # 保存为临时文件
            audio_tensor = torch.from_numpy(audio).unsqueeze(0)
            temp_path = os.path.join(os.path.dirname(__file__), f"temp_{filename}")
            torchaudio.save(temp_path, audio_tensor, self.speech_synthesizer.sample_rate)
            
            return temp_path        except Exception as e:
            print(f"⚠️ 生成音频失败: {e}")
            return None
    
    def test_inference_speed(self, num_samples=5):
        """测试推理速度"""
        print(f"🚀 测试推理速度 (样本数: {num_samples})...")
        
        if not self.engine:
            print("❌ 模型未加载")
            return None
            
        test_commands = [
            "打开客厅的灯",
            "关闭卧室的灯", 
            "调高空调温度",
            "播放音乐",
            "拉上窗帘"
        ]
        
        inference_times = []
        
        for i, command in enumerate(test_commands[:num_samples]):
            try:
                # 生成测试音频
                audio_path = self.create_test_audio(command, f"test_audio_{i}.wav")
                
                if audio_path and os.path.exists(audio_path):
                    # 测试推理时间
                    start_time = time.time()
                    result = self.engine.recognize_file(audio_path)
                    inference_time = time.time() - start_time
                    
                    inference_times.append(inference_time)
                    print(f"  样本 {i+1}: {command} -> {result} ({inference_time:.3f}秒)")
                    
                    # 清理临时文件
                    try:
                        os.remove(audio_path)
                    except:
                        pass
                else:
                    print(f"  ⚠️ 样本 {i+1}: 音频生成失败")
                    
            except Exception as e:
                print(f"  ❌ 样本 {i+1} 推理失败: {e}")
        
        if inference_times:
            avg_time = np.mean(inference_times)
            min_time = np.min(inference_times)
            max_time = np.max(inference_times)
            
            print(f"📊 推理性能统计:")
            print(f"   平均时间: {avg_time:.3f}秒")
            print(f"   最快时间: {min_time:.3f}秒")
            print(f"   最慢时间: {max_time:.3f}秒")
            print(f"   吞吐量: {1/avg_time:.1f} 样本/秒")
            
            return {
                'avg_time': avg_time,
                'min_time': min_time,
                'max_time': max_time,
                'throughput': 1/avg_time
            }
        
        return None
    
    def test_memory_usage(self):
        """测试内存使用情况"""
        print("💾 测试内存使用...")
        
        process = psutil.Process()
        
        # 获取初始内存
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # 如果模型未加载，先加载
        if not self.engine:
            self.test_model_loading()
        
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_used = memory_after - memory_before
        
        print(f"📈 内存使用情况:")
        print(f"   加载前: {memory_before:.1f} MB")
        print(f"   加载后: {memory_after:.1f} MB")
        print(f"   模型占用: {memory_used:.1f} MB")
        
        return {
            'before': memory_before,
            'after': memory_after,
            'used': memory_used
        }
    
    def test_model_accuracy(self, num_samples=5):
        """测试模型准确性"""
        print(f"🎯 测试模型准确性 (样本数: {num_samples})...")
        
        if not self.engine:
            print("❌ 模型未加载")
            return None
        
        test_commands = [
            "打开客厅的灯", "关闭卧室的灯", "调高空调温度", "调低空调温度",
            "播放音乐", "停止音乐", "拉上窗帘", "拉开窗帘",
            "打开风扇", "关闭风扇"
        ]
        
        correct_predictions = 0
        total_predictions = 0
        
        for i, command in enumerate(test_commands[:num_samples]):
            try:                # 生成测试音频
                audio_path = self.create_test_audio(command, f"accuracy_test_{i}.wav")
                
                if audio_path and os.path.exists(audio_path):
                    result = self.engine.recognize_file(audio_path)
                    
                    # 简单的准确性检查（包含关键词）
                    if result:  # 确保result不是None
                        key_words = command.replace("的", "").split()
                        is_correct = any(word in result for word in key_words if len(word) > 1)
                        
                        if is_correct:
                            correct_predictions += 1
                            status = "✅"
                        else:
                            status = "❌"
                        
                        total_predictions += 1
                        print(f"  {status} {command} -> {result}")
                    else:
                        total_predictions += 1
                        print(f"  ❌ {command} -> None")
                    
                    # 清理临时文件
                    try:
                        os.remove(audio_path)
                    except:
                        pass
                        
            except Exception as e:
                print(f"  ❌ 测试失败: {e}")
        
        if total_predictions > 0:
            accuracy = correct_predictions / total_predictions * 100
            print(f"🎯 准确率: {accuracy:.1f}% ({correct_predictions}/{total_predictions})")
            return accuracy
        
        return None
    
    def test_existing_audio_files(self):
        """测试现有音频文件"""
        print("🎵 测试现有音频文件...")
        
        if not self.engine:
            print("❌ 模型未加载")
            return None
        
        # 查找现有的音频文件
        audio_dirs = [
            os.path.join(os.path.dirname(__file__), "res"),
            os.path.join(os.path.dirname(__file__), "res", "smart_home_dataset", "audio"),
            os.path.join(os.path.dirname(__file__), "res", "enhanced_dataset", "audio")
        ]
        
        audio_files = []
        for audio_dir in audio_dirs:
            if os.path.exists(audio_dir):
                for file in os.listdir(audio_dir):
                    if file.endswith(('.wav', '.mp3', '.flac')):
                        audio_files.append(os.path.join(audio_dir, file))
                        if len(audio_files) >= 5:  # 限制测试文件数量
                            break
            if len(audio_files) >= 5:
                break
        
        if not audio_files:
            print("  ⚠️ 未找到现有音频文件")
            return None
          results = []
        for i, audio_path in enumerate(audio_files[:5]):
            try:
                start_time = time.time()
                result = self.engine.recognize_file(audio_path)
                inference_time = time.time() - start_time
                
                filename = os.path.basename(audio_path)
                print(f"  文件 {i+1}: {filename} -> {result} ({inference_time:.3f}秒)")
                results.append(inference_time)
                
            except Exception as e:
                print(f"  ❌ 文件 {i+1} 识别失败: {e}")
        
        if results:
            avg_time = np.mean(results)
            print(f"📊 现有文件推理平均时间: {avg_time:.3f}秒")
            return avg_time
        
        return None
    
    def run_full_benchmark(self):
        """运行完整基准测试"""
        print("🏁 开始完整基准测试...")
        print("=" * 50)
        
        results = {}
        
        # 1. 模型加载测试
        load_time = self.test_model_loading()
        if load_time:
            results['load_time'] = load_time
        
        print("\n" + "=" * 50)
        
        # 2. 内存使用测试
        memory_stats = self.test_memory_usage()
        if memory_stats:
            results['memory'] = memory_stats
        
        print("\n" + "=" * 50)
        
        # 3. 现有文件测试
        existing_file_time = self.test_existing_audio_files()
        if existing_file_time:
            results['existing_files'] = existing_file_time
        
        print("\n" + "=" * 50)
        
        # 4. 推理速度测试
        inference_stats = self.test_inference_speed(5)
        if inference_stats:
            results['inference'] = inference_stats
        
        print("\n" + "=" * 50)
        
        # 5. 准确性测试
        accuracy = self.test_model_accuracy(5)
        if accuracy:
            results['accuracy'] = accuracy
        
        print("\n" + "=" * 50)
        print("📋 基准测试完成!")
        print("=" * 50)
        
        return results


def main():
    """主函数"""
    try:
        benchmark = SimpleBenchmark()
        results = benchmark.run_full_benchmark()
        
        if results:
            print("\n📊 测试结果摘要:")
            if 'load_time' in results:
                print(f"   模型加载时间: {results['load_time']:.3f}秒")
            if 'memory' in results:
                print(f"   内存使用: {results['memory']['used']:.1f} MB")
            if 'existing_files' in results:
                print(f"   现有文件平均推理时间: {results['existing_files']:.3f}秒")
            if 'inference' in results:
                print(f"   合成文件平均推理时间: {results['inference']['avg_time']:.3f}秒")
                print(f"   推理吞吐量: {results['inference']['throughput']:.1f} 样本/秒")
            if 'accuracy' in results:
                print(f"   模型准确率: {results['accuracy']:.1f}%")
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断测试")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
