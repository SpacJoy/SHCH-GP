# -*- coding: utf-8 -*-
"""
唤醒词性能监控和调优工具
实时监控唤醒词检测性能，提供调优建议
"""

import sys
import os
import time
import json
import threading
from datetime import datetime, timedelta

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ai_speech_recognition import AISpeechRecognizer
from config import WAKE_WORD_CONFIG

class WakeWordPerformanceMonitor:
    """唤醒词性能监控器"""
    
    def __init__(self):
        self.recognizer = None
        self.monitoring = False
        self.start_time = None
        self.performance_data = []
        self.recommendations = []
    
    def initialize_recognizer(self):
        """初始化语音识别器"""
        try:
            print("🔧 初始化语音识别器...")
            self.recognizer = AISpeechRecognizer(
                status_callback=self._status_callback
            )
            print("✅ 语音识别器初始化成功")
            return True
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            return False
    
    def _status_callback(self, message):
        """状态回调"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
        # 记录性能数据
        if self.monitoring:
            self.performance_data.append({
                'timestamp': datetime.now(),
                'message': message,
                'type': self._classify_message(message)
            })
    
    def _classify_message(self, message):
        """分类状态消息"""
        if "等待唤醒词" in message:
            return "waiting"
        elif "检测到唤醒词" in message:
            return "wake_detected"
        elif "识别到指令" in message:
            return "command_recognized"
        elif "错误" in message or "❌" in message:
            return "error"
        elif "超时" in message:
            return "timeout"
        else:
            return "other"
    
    def start_monitoring(self, duration_minutes=5):
        """开始性能监控"""
        print(f"📊 开始性能监控，持续 {duration_minutes} 分钟...")
        print("   请正常使用唤醒词功能，系统将自动收集性能数据")
        print("   按 Ctrl+C 可提前结束监控")
        
        self.monitoring = True
        self.start_time = datetime.now()
        self.performance_data = []
        
        # 设置结束时间
        end_time = self.start_time + timedelta(minutes=duration_minutes)
        
        try:
            while datetime.now() < end_time and self.monitoring:
                # 模拟唤醒词检测
                result = self.recognizer.listen_with_wake_word() # type: ignore
                time.sleep(0.1)  # 短暂休息
                
        except KeyboardInterrupt:
            print("\n🛑 监控被用户中断")
        
        self.monitoring = False
        print("📈 性能监控完成，开始分析数据...")
        self._analyze_performance()
    
    def _analyze_performance(self):
        """分析性能数据"""
        if not self.performance_data:
            print("⚠️ 没有收集到足够的性能数据")
            return
        
        print("\n📊 性能分析报告")
        print("=" * 50)
        
        # 统计各类事件
        event_counts = {}
        for data in self.performance_data:
            event_type = data['type']
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        print("📋 事件统计:")
        for event_type, count in event_counts.items():
            print(f"   - {event_type}: {count} 次")
        
        # 计算成功率
        wake_detected = event_counts.get('wake_detected', 0)
        waiting_events = event_counts.get('waiting', 0)
        
        if waiting_events > 0:
            success_rate = wake_detected / waiting_events * 100
            print(f"\n📈 唤醒词检测成功率: {success_rate:.1f}%")
        
        # 获取识别器统计
        if self.recognizer:
            stats = self.recognizer.get_wake_word_stats()
            print(f"\n🎯 识别器统计:")
            for key, value in stats.items():
                if isinstance(value, float):
                    print(f"   - {key}: {value:.2f}")
                else:
                    print(f"   - {key}: {value}")
        
        # 生成建议
        self._generate_recommendations(event_counts, stats if self.recognizer else {})
        
        # 显示建议
        if self.recommendations:
            print(f"\n💡 性能优化建议:")
            for i, recommendation in enumerate(self.recommendations, 1):
                print(f"   {i}. {recommendation}")
    
    def _generate_recommendations(self, event_counts, stats):
        """生成性能优化建议"""
        self.recommendations = []
        
        # 基于错误率的建议
        errors = event_counts.get('error', 0)
        total_events = sum(event_counts.values())
        
        if total_events > 0:
            error_rate = errors / total_events
            if error_rate > 0.1:  # 错误率超过10%
                self.recommendations.append(
                    "错误率较高，建议检查麦克风设备和网络连接"
                )
        
        # 基于超时的建议
        timeouts = event_counts.get('timeout', 0)
        if timeouts > 5:
            self.recommendations.append(
                "超时次数较多，建议增加超时时间或改善语音环境"
            )
        
        # 基于检测率的建议
        detection_rate = stats.get('detection_rate', 0)
        if detection_rate < 0.7:
            self.recommendations.append(
                "检测率较低，建议调整麦克风位置或降低环境噪音"
            )
        
        # 基于阈值的建议
        current_threshold = stats.get('current_threshold', 0)
        if current_threshold > 400:
            self.recommendations.append(
                "能量阈值较高，可能影响敏感度，建议在安静环境中重新校准"
            )
        elif current_threshold < 200:
            self.recommendations.append(
                "能量阈值较低，可能导致误检，建议增加背景噪音过滤"
            )
    
    def export_performance_data(self, filename=None):
        """导出性能数据"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wake_word_performance_{timestamp}.json"
        
        try:
            export_data = {
                'monitoring_period': {
                    'start': self.start_time.isoformat() if self.start_time else None,
                    'end': datetime.now().isoformat(),
                    'duration_minutes': (datetime.now() - self.start_time).total_seconds() / 60 if self.start_time else 0
                },
                'performance_data': [
                    {
                        'timestamp': data['timestamp'].isoformat(),
                        'message': data['message'],
                        'type': data['type']
                    }
                    for data in self.performance_data
                ],
                'statistics': self.recognizer.get_wake_word_stats() if self.recognizer else {},
                'recommendations': self.recommendations,
                'configuration': WAKE_WORD_CONFIG
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            print(f"📁 性能数据已导出到: {filename}")
            
        except Exception as e:
            print(f"❌ 导出失败: {e}")
    
    def run_interactive_tuning(self):
        """交互式调优"""
        print("\n🎛️ 交互式性能调优")
        print("=" * 30)
        
        while True:
            print("\n可用选项:")
            print("1. 查看当前配置")
            print("2. 调整能量阈值")
            print("3. 调整超时时间")
            print("4. 测试当前设置")
            print("5. 重置统计数据")
            print("6. 退出调优")
            
            try:
                choice = input("\n请选择操作 (1-6): ").strip()
                
                if choice == '1':
                    self._show_current_config()
                elif choice == '2':
                    self._adjust_energy_threshold()
                elif choice == '3':
                    self._adjust_timeout()
                elif choice == '4':
                    self._test_current_settings()
                elif choice == '5':
                    self._reset_statistics()
                elif choice == '6':
                    print("👋 退出调优模式")
                    break
                else:
                    print("❌ 无效选择，请重试")
                    
            except KeyboardInterrupt:
                print("\n👋 调优被用户中断")
                break
    
    def _show_current_config(self):
        """显示当前配置"""
        print(f"\n📋 当前配置:")
        if self.recognizer:
            print(f"   - 能量阈值: {self.recognizer.dynamic_energy_threshold}")
            print(f"   - 唤醒词超时: {self.recognizer.wake_word_timeout}s")
            print(f"   - 命令超时: {self.recognizer.command_timeout}s")
            print(f"   - 自适应阈值: {self.recognizer.adaptive_threshold}")
            
            stats = self.recognizer.get_wake_word_stats()
            print(f"\n📊 统计信息:")
            for key, value in stats.items():
                if isinstance(value, float):
                    print(f"   - {key}: {value:.2f}")
                else:
                    print(f"   - {key}: {value}")
    
    def _adjust_energy_threshold(self):
        """调整能量阈值"""
        try:
            current = self.recognizer.dynamic_energy_threshold# type: ignore
            print(f"\n当前能量阈值: {current}")
            print("建议范围: 200-500")
            
            new_threshold = input("输入新的能量阈值 (回车保持不变): ").strip()
            if new_threshold:
                new_threshold = float(new_threshold)
                self.recognizer.dynamic_energy_threshold = new_threshold # type: ignore
                self.recognizer.recognizer.energy_threshold = new_threshold# type: ignore
                print(f"✅ 能量阈值已更新为: {new_threshold}")
        except ValueError:
            print("❌ 无效的数值")
        except Exception as e:
            print(f"❌ 调整失败: {e}")
    
    def _adjust_timeout(self):
        """调整超时时间"""
        try:
            print(f"\n当前唤醒词超时: {self.recognizer.wake_word_timeout}s")# type: ignore
            print(f"当前命令超时: {self.recognizer.command_timeout}s")# type: ignore
            
            wake_timeout = input("输入新的唤醒词超时时间 (回车保持不变): ").strip()
            if wake_timeout:
                self.recognizer.wake_word_timeout = float(wake_timeout)# type: ignore
                print(f"✅ 唤醒词超时已更新为: {wake_timeout}s")
            
            cmd_timeout = input("输入新的命令超时时间 (回车保持不变): ").strip()
            if cmd_timeout:
                self.recognizer.command_timeout = float(cmd_timeout)# type: ignore
                print(f"✅ 命令超时已更新为: {cmd_timeout}s")
                
        except ValueError:
            print("❌ 无效的数值")
        except Exception as e:
            print(f"❌ 调整失败: {e}")
    
    def _test_current_settings(self):
        """测试当前设置"""
        print("\n🧪 测试当前设置 (说几个唤醒词试试)")
        print("按 Ctrl+C 结束测试")
        
        test_count = 0
        try:
            while test_count < 5:  # 最多测试5次
                test_count += 1
                print(f"\n第 {test_count} 次测试:")
                result = self.recognizer.listen_with_wake_word()# type: ignore
                if result:
                    print(f"✅ 识别成功: {result}")
                else:
                    print("⏸️ 未识别到内容")
        except KeyboardInterrupt:
            print("\n测试结束")
    
    def _reset_statistics(self):
        """重置统计数据"""
        if self.recognizer:
            self.recognizer.reset_wake_word_stats()
            print("✅ 统计数据已重置")
        else:
            print("❌ 识别器未初始化")

def main():
    """主函数"""
    print("🎛️ 唤醒词性能监控和调优工具")
    print("=" * 50)
    
    monitor = WakeWordPerformanceMonitor()
    
    # 初始化识别器
    if not monitor.initialize_recognizer():
        return False
    
    try:
        while True:
            print("\n📋 可用功能:")
            print("1. 开始性能监控")
            print("2. 交互式调优")
            print("3. 导出性能数据")
            print("4. 退出")
            
            choice = input("\n请选择功能 (1-4): ").strip()
            
            if choice == '1':
                duration = input("监控时长 (分钟，默认5): ").strip()
                duration = int(duration) if duration.isdigit() else 5
                monitor.start_monitoring(duration)
                
            elif choice == '2':
                monitor.run_interactive_tuning()
                
            elif choice == '3':
                filename = input("导出文件名 (回车使用默认): ").strip()
                monitor.export_performance_data(filename if filename else None)
                
            elif choice == '4':
                print("👋 再见！")
                break
                
            else:
                print("❌ 无效选择")
    
    except KeyboardInterrupt:
        print("\n👋 程序被用户中断")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"💥 程序异常: {e}")
        sys.exit(1)
