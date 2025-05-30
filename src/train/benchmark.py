# -*- coding: utf-8 -*-
"""
轻量级ASR性能基准测试
测试模型在不同场景下的性能表现
"""

import os
import sys
import time
import numpy as np
import torch
import psutil
import threading
from typing import Dict, List, Optional, Tuple
import tempfile
import wave
import speech_recognition as sr
import warnings
warnings.filterwarnings("ignore")

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from train.model import LightASRInference, AudioFeatureExtractor
from train.model_integration import LightASREngine, EnhancedAISpeechRecognizer

class ASRBenchmark:
    """ASR性能基准测试器"""
    
    def __init__(self):
        """初始化基准测试器"""
        self.light_asr = LightASREngine()
        self.results = {}
        self.recognizer = sr.Recognizer()
        
    def test_model_loading_time(self) -> float:
        """测试模型加载时间"""
        print("🔍 测试模型加载时间...")
        
        start_time = time.time()
        engine = LightASREngine()
        if engine.is_available():
            engine.load_model()
        load_time = time.time() - start_time
        
        print(f"📊 模型加载时间: {load_time:.3f}秒")
        return load_time    
    def test_inference_speed(self, num_samples: int = 20) -> Dict[str, float]:
        """测试推理速度"""
        print(f"🚀 测试推理速度 (样本数: {num_samples})...")
        
        if not self.light_asr.is_available():
            print("❌ 轻量级ASR不可用")
            return {}
        
        # 使用现有的测试音频文件
        test_audio_dir = "src/train/res/smart_home_dataset/audio"
        test_files = []
        
        if os.path.exists(test_audio_dir):
            # 收集现有的音频文件
            for file in os.listdir(test_audio_dir):
                if file.endswith('.wav'):
                    test_files.append(os.path.join(test_audio_dir, file))
            
            # 如果文件不够，重复使用
            while len(test_files) < num_samples:
                test_files.extend(test_files[:min(len(test_files), num_samples - len(test_files))])
            
            test_files = test_files[:num_samples]
        else:
            print("❌ 找不到测试音频文件")
            return {}
        
        # 测试推理时间
        inference_times = []
        memory_usage = []
        
        for audio_file in test_files:
            # 记录内存使用
            process = psutil.Process()
            memory_before = process.memory_info().rss / 1024 / 1024  # MB
            
            # 加载音频文件为sr.AudioData
            try:
                with sr.AudioFile(audio_file) as source:
                    audio = self.recognizer.record(source)
                
                # 测试推理
                start_time = time.time()
                result = self.light_asr.recognize(audio)
                inference_time = time.time() - start_time
                inference_times.append(inference_time)
                
                memory_after = process.memory_info().rss / 1024 / 1024  # MB
                memory_usage.append(memory_after - memory_before)
                
            except Exception as e:
                print(f"⚠️ 推理失败: {e}")
                continue
        
        # 计算统计信息
        if inference_times:
            results = {
                'avg_inference_time': np.mean(inference_times),
                'min_inference_time': np.min(inference_times),
                'max_inference_time': np.max(inference_times),
                'std_inference_time': np.std(inference_times),
                'avg_memory_usage': np.mean(memory_usage),
                'total_samples': len(inference_times)
            }
            
            print(f"📊 平均推理时间: {results['avg_inference_time']:.3f}秒")
            print(f"📊 最快推理时间: {results['min_inference_time']:.3f}秒")
            print(f"📊 最慢推理时间: {results['max_inference_time']:.3f}秒")
            print(f"📊 平均内存增量: {results['avg_memory_usage']:.2f}MB")
            
            return results
        
        return {}
    
    def test_concurrent_inference(self, num_threads: int = 4, samples_per_thread: int = 5) -> Dict[str, float]:
        """测试并发推理性能"""
        print(f"🔄 测试并发推理 ({num_threads}线程，每线程{samples_per_thread}样本)...")
        
        if not self.light_asr.is_available():
            print("❌ 轻量级ASR不可用")
            return {}
        
        # 准备测试数据
        self.data_generator.set_output_dir(tempfile.mkdtemp())
        test_file = self.data_generator.generate_sample(
            text="关闭卧室的灯", 
            save_file=True,
            filename="concurrent_test.wav"
        )
        
        if not test_file:
            print("❌ 无法生成测试音频")
            return {}
        
        # 并发测试
        results = []
        threads = []
        
        def worker_thread(thread_id: int):
            """工作线程"""
            thread_times = []
            engine = LightASREngine()  # 每个线程独立的引擎
            
            for i in range(samples_per_thread):
                start_time = time.time()
                try:
                    result = engine.recognize_file(test_file)
                    inference_time = time.time() - start_time
                    thread_times.append(inference_time)
                except Exception as e:
                    print(f"⚠️ 线程{thread_id}推理失败: {e}")
            
            results.extend(thread_times)
        
        # 启动线程
        start_time = time.time()
        for i in range(num_threads):
            thread = threading.Thread(target=worker_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待完成
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        
        if results:
            concurrent_results = {
                'total_time': total_time,
                'avg_inference_time': np.mean(results),
                'throughput': len(results) / total_time,  # samples per second
                'num_threads': num_threads,
                'total_samples': len(results)
            }
            
            print(f"📊 总耗时: {concurrent_results['total_time']:.3f}秒")
            print(f"📊 平均推理时间: {concurrent_results['avg_inference_time']:.3f}秒")
            print(f"📊 吞吐量: {concurrent_results['throughput']:.2f} 样本/秒")
            
            return concurrent_results
        
        return {}
    
    def test_accuracy_on_generated_data(self, num_samples: int = 50) -> Dict[str, float]:
        """在生成数据上测试准确率"""
        print(f"🎯 测试生成数据准确率 (样本数: {num_samples})...")
        
        if not self.light_asr.is_available():
            print("❌ 轻量级ASR不可用")
            return {}
        
        # 生成测试数据集
        self.data_generator.set_output_dir(tempfile.mkdtemp())
        test_commands = [
            "打开客厅的灯", "关闭卧室的灯", "调高空调温度",
            "播放音乐", "暂停播放", "调节音量", 
            "打开电视", "关闭电视", "切换频道"
        ]
        
        correct_predictions = 0
        total_predictions = 0
        confidence_scores = []
        
        for i in range(num_samples):
            # 随机选择指令
            command = test_commands[i % len(test_commands)]
            
            # 生成音频
            audio_file = self.data_generator.generate_sample(
                text=command,
                save_file=True,
                filename=f"accuracy_test_{i}.wav"
            )
            
            if not audio_file:
                continue
            
            # 识别
            try:
                result = self.light_asr.recognize_file(audio_file)
                total_predictions += 1
                
                if result and command in result:
                    correct_predictions += 1
                
                # 如果有置信度信息，记录下来
                if hasattr(self.light_asr, 'last_confidence'):
                    confidence_scores.append(self.light_asr.last_confidence)
                    
            except Exception as e:
                print(f"⚠️ 识别失败: {e}")
                continue
        
        if total_predictions > 0:
            accuracy = correct_predictions / total_predictions
            avg_confidence = np.mean(confidence_scores) if confidence_scores else 0
            
            accuracy_results = {
                'accuracy': accuracy,
                'correct_predictions': correct_predictions,
                'total_predictions': total_predictions,
                'avg_confidence': avg_confidence
            }
            
            print(f"📊 准确率: {accuracy:.2%}")
            print(f"📊 正确预测: {correct_predictions}/{total_predictions}")
            print(f"📊 平均置信度: {avg_confidence:.3f}")
            
            return accuracy_results
        
        return {}
    
    def test_resource_usage(self, duration_seconds: int = 60) -> Dict[str, float]:
        """测试资源使用情况"""
        print(f"💻 测试资源使用 (持续{duration_seconds}秒)...")
        
        if not self.light_asr.is_available():
            print("❌ 轻量级ASR不可用")
            return {}
        
        # 生成测试音频
        self.data_generator.set_output_dir(tempfile.mkdtemp())
        test_file = self.data_generator.generate_sample(
            text="测试资源使用",
            save_file=True,
            filename="resource_test.wav"
        )
        
        if not test_file:
            print("❌ 无法生成测试音频")
            return {}
        
        # 监控资源使用
        process = psutil.Process()
        cpu_percentages = []
        memory_usage = []
        
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds:
            # 执行推理
            try:
                self.light_asr.recognize_file(test_file)
            except:
                pass
            
            # 记录资源使用
            cpu_percent = process.cpu_percent()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            cpu_percentages.append(cpu_percent)
            memory_usage.append(memory_mb)
            
            time.sleep(0.5)  # 每0.5秒采样一次
        
        if cpu_percentages and memory_usage:
            resource_results = {
                'avg_cpu_percent': np.mean(cpu_percentages),
                'max_cpu_percent': np.max(cpu_percentages),
                'avg_memory_mb': np.mean(memory_usage),
                'max_memory_mb': np.max(memory_usage),
                'duration': duration_seconds
            }
            
            print(f"📊 平均CPU使用率: {resource_results['avg_cpu_percent']:.1f}%")
            print(f"📊 最高CPU使用率: {resource_results['max_cpu_percent']:.1f}%")
            print(f"📊 平均内存使用: {resource_results['avg_memory_mb']:.1f}MB")
            print(f"📊 最高内存使用: {resource_results['max_memory_mb']:.1f}MB")
            
            return resource_results
        
        return {}
    
    def run_full_benchmark(self) -> Dict[str, any]:
        """运行完整基准测试"""
        print("🏁 开始完整基准测试...")
        print("=" * 60)
        
        full_results = {}
        
        # 1. 模型加载时间
        try:
            full_results['loading_time'] = self.test_model_loading_time()
        except Exception as e:
            print(f"❌ 模型加载测试失败: {e}")
            full_results['loading_time'] = None
        
        print("-" * 40)
        
        # 2. 推理速度
        try:
            full_results['inference_speed'] = self.test_inference_speed(20)
        except Exception as e:
            print(f"❌ 推理速度测试失败: {e}")
            full_results['inference_speed'] = None
        
        print("-" * 40)
        
        # 3. 并发性能
        try:
            full_results['concurrent_performance'] = self.test_concurrent_inference(4, 5)
        except Exception as e:
            print(f"❌ 并发性能测试失败: {e}")
            full_results['concurrent_performance'] = None
        
        print("-" * 40)
        
        # 4. 准确率测试
        try:
            full_results['accuracy'] = self.test_accuracy_on_generated_data(30)
        except Exception as e:
            print(f"❌ 准确率测试失败: {e}")
            full_results['accuracy'] = None
        
        print("-" * 40)
        
        # 5. 资源使用
        try:
            full_results['resource_usage'] = self.test_resource_usage(30)
        except Exception as e:
            print(f"❌ 资源使用测试失败: {e}")
            full_results['resource_usage'] = None
        
        print("=" * 60)
        print("✅ 基准测试完成")
        
        return full_results
    
    def generate_report(self, results: Dict[str, any]) -> str:
        """生成测试报告"""
        report = []
        report.append("# 轻量级ASR性能基准测试报告")
        report.append(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 模型加载时间
        if results.get('loading_time'):
            report.append("## 模型加载性能")
            report.append(f"- 加载时间: {results['loading_time']:.3f}秒")
            report.append("")
        
        # 推理速度
        if results.get('inference_speed'):
            speed = results['inference_speed']
            report.append("## 推理速度性能")
            report.append(f"- 平均推理时间: {speed['avg_inference_time']:.3f}秒")
            report.append(f"- 最快推理时间: {speed['min_inference_time']:.3f}秒")
            report.append(f"- 最慢推理时间: {speed['max_inference_time']:.3f}秒")
            report.append(f"- 标准差: {speed['std_inference_time']:.3f}秒")
            report.append(f"- 平均内存增量: {speed['avg_memory_usage']:.2f}MB")
            report.append("")
        
        # 并发性能
        if results.get('concurrent_performance'):
            concurrent = results['concurrent_performance']
            report.append("## 并发性能")
            report.append(f"- 线程数: {concurrent['num_threads']}")
            report.append(f"- 总样本数: {concurrent['total_samples']}")
            report.append(f"- 总耗时: {concurrent['total_time']:.3f}秒")
            report.append(f"- 吞吐量: {concurrent['throughput']:.2f} 样本/秒")
            report.append("")
        
        # 准确率
        if results.get('accuracy'):
            accuracy = results['accuracy']
            report.append("## 准确率性能")
            report.append(f"- 准确率: {accuracy['accuracy']:.2%}")
            report.append(f"- 正确预测: {accuracy['correct_predictions']}/{accuracy['total_predictions']}")
            if accuracy['avg_confidence'] > 0:
                report.append(f"- 平均置信度: {accuracy['avg_confidence']:.3f}")
            report.append("")
        
        # 资源使用
        if results.get('resource_usage'):
            resource = results['resource_usage']
            report.append("## 资源使用")
            report.append(f"- 平均CPU使用率: {resource['avg_cpu_percent']:.1f}%")
            report.append(f"- 最高CPU使用率: {resource['max_cpu_percent']:.1f}%")
            report.append(f"- 平均内存使用: {resource['avg_memory_mb']:.1f}MB")
            report.append(f"- 最高内存使用: {resource['max_memory_mb']:.1f}MB")
            report.append("")
        
        report.append("---")
        report.append("*报告由轻量级ASR基准测试工具自动生成*")
        
        return "\n".join(report)

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="轻量级ASR性能基准测试")
    parser.add_argument('--test', choices=['loading', 'speed', 'concurrent', 'accuracy', 'resource', 'all'],
                       default='all', help='测试类型')
    parser.add_argument('--samples', type=int, default=20, help='测试样本数')
    parser.add_argument('--threads', type=int, default=4, help='并发线程数')
    parser.add_argument('--duration', type=int, default=30, help='资源测试持续时间(秒)')
    parser.add_argument('--report', type=str, help='保存报告到文件')
    
    args = parser.parse_args()
    
    benchmark = ASRBenchmark()
    
    if args.test == 'all':
        results = benchmark.run_full_benchmark()
        
        # 生成报告
        if args.report:
            report = benchmark.generate_report(results)
            with open(args.report, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"📄 报告已保存到: {args.report}")
    
    elif args.test == 'loading':
        benchmark.test_model_loading_time()
    elif args.test == 'speed':
        benchmark.test_inference_speed(args.samples)
    elif args.test == 'concurrent':
        benchmark.test_concurrent_inference(args.threads, args.samples)
    elif args.test == 'accuracy':
        benchmark.test_accuracy_on_generated_data(args.samples)
    elif args.test == 'resource':
        benchmark.test_resource_usage(args.duration)

if __name__ == "__main__":
    main()
