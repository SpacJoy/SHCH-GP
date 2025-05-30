# -*- coding: utf-8 -*-
"""
唤醒词配置优化器
自动测试不同参数组合，找到最佳的唤醒词检测配置
"""

import sys
import os
import time
import json
import itertools
from datetime import datetime

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ai_speech_recognition import AISpeechRecognizer
from config import WAKE_WORD_CONFIG

class WakeWordOptimizer:
    """唤醒词配置优化器"""
    
    def __init__(self):
        self.test_results = []
        self.best_config = None
        self.best_score = 0
    
    def generate_test_configs(self):
        """生成测试配置组合"""
        # 定义参数范围
        energy_thresholds = [200, 300, 400, 500]
        wake_timeouts = [2, 3, 4, 5]
        sensitivities = [0.6, 0.7, 0.8, 0.9]
        
        configs = []
        for energy, timeout, sensitivity in itertools.product(
            energy_thresholds, wake_timeouts, sensitivities
        ):
            config = WAKE_WORD_CONFIG.copy()
            config.update({
                'energy_threshold': energy,
                'timeout': timeout,
                'sensitivity': sensitivity
            })
            configs.append(config)
        
        return configs
    
    def test_config(self, config, test_duration=30):
        """测试特定配置"""
        print(f"🧪 测试配置: 阈值={config['energy_threshold']}, "
              f"超时={config['timeout']}s, 敏感度={config['sensitivity']}")
        
        try:
            # 创建识别器实例
            recognizer = AISpeechRecognizer()
            
            # 应用测试配置
            recognizer.dynamic_energy_threshold = config['energy_threshold']
            recognizer.recognizer.energy_threshold = config['energy_threshold']
            recognizer.wake_word_timeout = config['timeout']
            recognizer.wake_sensitivity = config['sensitivity']
            
            # 重置统计
            recognizer.reset_wake_word_stats()
            
            # 进行测试
            start_time = time.time()
            test_attempts = 0
            successful_detections = 0
            false_positives = 0
            
            print(f"   开始 {test_duration} 秒测试...")
            
            while time.time() - start_time < test_duration:
                test_attempts += 1
                
                # 模拟唤醒词检测
                result = recognizer.listen_with_wake_word()
                
                if result:
                    # 简单验证是否是有效指令
                    if any(word in result.lower() for word in ['灯', '空调', '电视', '风扇', '窗帘']): # type: ignore
                        successful_detections += 1
                    else:
                        false_positives += 1
                
                time.sleep(0.5)  # 短暂休息
            
            # 计算性能指标
            total_time = time.time() - start_time
            detection_rate = successful_detections / max(1, test_attempts)
            false_positive_rate = false_positives / max(1, test_attempts)
            avg_response_time = total_time / max(1, test_attempts)
            
            # 计算综合得分
            score = self._calculate_score(
                detection_rate, false_positive_rate, avg_response_time
            )
            
            result = {
                'config': config,
                'test_attempts': test_attempts,
                'successful_detections': successful_detections,
                'false_positives': false_positives,
                'detection_rate': detection_rate,
                'false_positive_rate': false_positive_rate,
                'avg_response_time': avg_response_time,
                'score': score,
                'test_duration': total_time
            }
            
            print(f"   结果: 成功率={detection_rate:.2f}, "
                  f"误报率={false_positive_rate:.2f}, "
                  f"得分={score:.2f}")
            
            return result
            
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")
            return None
    
    def _calculate_score(self, detection_rate, false_positive_rate, avg_response_time):
        """计算配置得分"""
        # 综合评分公式
        # 检测率权重40%，误报率权重30%，响应时间权重30%
        detection_score = detection_rate * 40
        false_positive_penalty = false_positive_rate * 30
        response_time_score = max(0, (5 - avg_response_time) / 5) * 30  # 5秒内响应得满分
        
        total_score = detection_score - false_positive_penalty + response_time_score
        return max(0, min(100, total_score))  # 限制在0-100范围内
    
    def run_optimization(self, configs_per_batch=5, test_duration=30):
        """运行优化过程"""
        print("🎯 开始唤醒词配置优化")
        print("=" * 50)
        
        configs = self.generate_test_configs()
        total_configs = len(configs)
        
        print(f"📋 将测试 {total_configs} 种配置组合")
        print(f"⏱️ 每个配置测试 {test_duration} 秒")
        print(f"🚀 预计总时间: {total_configs * test_duration / 60:.1f} 分钟")
        print()
        
        # 询问是否继续
        response = input("是否开始优化？(y/n): ").lower().strip()
        if response not in ['y', 'yes', '是', '']:
            print("优化已取消")
            return
        
        print("\n开始测试...")
        
        for i, config in enumerate(configs[:configs_per_batch], 1):
            print(f"\n📊 进度: {i}/{min(configs_per_batch, total_configs)}")
            
            result = self.test_config(config, test_duration)
            if result:
                self.test_results.append(result)
                
                # 更新最佳配置
                if result['score'] > self.best_score:
                    self.best_score = result['score']
                    self.best_config = result
        
        # 显示结果
        self._show_results()
    
    def _show_results(self):
        """显示优化结果"""
        if not self.test_results:
            print("❌ 没有有效的测试结果")
            return
        
        print("\n🏆 优化结果")
        print("=" * 50)
        
        # 按得分排序
        sorted_results = sorted(self.test_results, key=lambda x: x['score'], reverse=True)
        
        print("📊 前5名配置:")
        for i, result in enumerate(sorted_results[:5], 1):
            config = result['config']
            print(f"\n{i}. 得分: {result['score']:.2f}")
            print(f"   - 能量阈值: {config['energy_threshold']}")
            print(f"   - 超时时间: {config['timeout']}s")
            print(f"   - 敏感度: {config['sensitivity']}")
            print(f"   - 检测率: {result['detection_rate']:.2f}")
            print(f"   - 误报率: {result['false_positive_rate']:.2f}")
            print(f"   - 平均响应时间: {result['avg_response_time']:.2f}s")
        
        # 最佳配置建议
        if self.best_config:
            print("\n💡 推荐配置:")
            best_config = self.best_config['config']
            print(f"WAKE_WORD_CONFIG = {{")
            for key, value in best_config.items():
                if isinstance(value, str):
                    print(f"    '{key}': '{value}',")
                else:
                    print(f"    '{key}': {value},")
            print("}")
    
    def export_results(self, filename=None):
        """导出优化结果"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wake_word_optimization_{timestamp}.json"
        
        try:
            export_data = {
                'optimization_timestamp': datetime.now().isoformat(),
                'test_results': self.test_results,
                'best_config': self.best_config,
                'summary': {
                    'total_configs_tested': len(self.test_results),
                    'best_score': self.best_score,
                    'avg_score': sum(r['score'] for r in self.test_results) / len(self.test_results) if self.test_results else 0
                }
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            print(f"📁 优化结果已导出到: {filename}")
            
        except Exception as e:
            print(f"❌ 导出失败: {e}")
    
    def apply_best_config(self):
        """应用最佳配置到配置文件"""
        if not self.best_config:
            print("❌ 没有找到最佳配置")
            return
        
        try:
            config_file = os.path.join('src', 'config.py')
            
            # 读取当前配置文件
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 备份原配置
            backup_file = f"{config_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"📁 原配置已备份到: {backup_file}")
            
            # 更新配置
            best_config = self.best_config['config']
            
            # 简单的文本替换（实际项目中可能需要更复杂的解析）
            for key, value in best_config.items():
                if key in ['energy_threshold', 'timeout', 'sensitivity']:
                    pattern = f"'{key}': [\d\.]+" # type: ignore
                    replacement = f"'{key}': {value}"
                    import re
                    content = re.sub(pattern, replacement, content)
            
            # 写入更新后的配置
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ 最佳配置已应用到 {config_file}")
            print("重启程序以使用新配置")
            
        except Exception as e:
            print(f"❌ 应用配置失败: {e}")

def main():
    """主函数"""
    print("⚡ 唤醒词配置优化器")
    print("=" * 30)
    print("这个工具将自动测试不同的配置组合，")
    print("找到最适合您环境的唤醒词设置。")
    print()
    
    optimizer = WakeWordOptimizer()
    
    try:
        while True:
            print("\n📋 可用功能:")
            print("1. 开始配置优化 (快速测试)")
            print("2. 开始配置优化 (完整测试)")
            print("3. 导出结果")
            print("4. 应用最佳配置")
            print("5. 退出")
            
            choice = input("\n请选择功能 (1-5): ").strip()
            
            if choice == '1':
                optimizer.run_optimization(configs_per_batch=5, test_duration=15)
                
            elif choice == '2':
                optimizer.run_optimization(configs_per_batch=10, test_duration=30)
                
            elif choice == '3':
                filename = input("导出文件名 (回车使用默认): ").strip()
                optimizer.export_results(filename if filename else None)
                
            elif choice == '4':
                optimizer.apply_best_config()
                
            elif choice == '5':
                print("👋 优化完成！")
                break
                
            else:
                print("❌ 无效选择")
    
    except KeyboardInterrupt:
        print("\n👋 优化被用户中断")
    
    except Exception as e:
        print(f"💥 优化过程中发生异常: {e}")

if __name__ == "__main__":
    main()
