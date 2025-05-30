# -*- coding: utf-8 -*-
"""
增强的智能家居语音数据集生成器
生成更多样化和真实的训练数据
"""

import os
import sys
import numpy as np
import librosa
import soundfile as sf
from typing import List, Dict, Tuple, Optional
import json
import random
import argparse
from dataclasses import dataclass
import warnings
warnings.filterwarnings("ignore")

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

@dataclass
class VoiceProfile:
    """语音特征配置"""
    pitch_shift: float = 0.0  # 音调偏移（半音）
    speed_change: float = 1.0  # 语速变化
    volume_gain: float = 1.0  # 音量增益
    background_noise: float = 0.0  # 背景噪声级别
    voice_type: str = "neutral"  # 声音类型

class EnhancedDatasetGenerator:
    """增强的数据集生成器"""
    
    def __init__(self, output_dir: str = "src/train/res/enhanced_dataset"):
        self.output_dir = output_dir
        self.sample_rate = 16000
        self.target_duration = 2.0  # 目标时长（秒）
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "audio"), exist_ok=True)
        
        # 扩展的智能家居指令集
        self.command_categories = {
            "灯光控制": [
                "打开{room}的灯", "关闭{room}的灯", "调亮{room}的灯", "调暗{room}的灯",
                "设置{room}灯光亮度为{level}", "切换{room}的灯", "开启{room}夜灯模式",
                "关闭所有灯光", "打开全部灯", "灯光场景切换", "开启阅读模式"
            ],
            "空调控制": [
                "打开空调", "关闭空调", "调高温度", "调低温度", "设置温度为{temp}度",
                "空调制冷模式", "空调制热模式", "空调除湿模式", "空调风速调节",
                "打开{room}空调", "关闭{room}空调", "空调定时开启", "空调定时关闭"
            ],
            "电视控制": [
                "打开电视", "关闭电视", "切换频道", "调高音量", "调低音量",
                "电视静音", "取消静音", "播放{channel}", "搜索{content}",
                "回到主页", "打开应用", "电视待机"
            ],
            "音乐控制": [
                "播放音乐", "暂停音乐", "停止播放", "下一首", "上一首",
                "调节音量", "播放{song}", "播放{artist}的歌",
                "播放古典音乐", "播放流行音乐", "音乐循环播放", "随机播放"
            ],
            "窗帘控制": [
                "打开窗帘", "关闭窗帘", "拉开{room}窗帘", "拉上{room}窗帘",
                "窗帘半开", "窗帘全开", "窗帘全关", "自动窗帘模式"
            ],
            "风扇控制": [
                "打开风扇", "关闭风扇", "风扇调速", "风扇摆头",
                "风扇定时", "打开{room}风扇", "关闭{room}风扇",
                "风扇一档", "风扇二档", "风扇三档"
            ],
            "安全控制": [
                "开启安防模式", "关闭安防模式", "查看监控", "锁门", "开门",
                "安防布防", "安防撤防", "报警器开启", "报警器关闭"
            ],
            "环境控制": [
                "查看温度", "查看湿度", "空气净化器开启", "空气净化器关闭",
                "加湿器开启", "加湿器关闭", "检测空气质量", "开启新风系统"
            ]
        }
        
        # 房间类型
        self.rooms = ["客厅", "卧室", "厨房", "书房", "餐厅", "主卧", "次卧", "儿童房"]
        
        # 参数替换选项
        self.replacements = {
            "temp": ["20", "22", "24", "26", "28"],
            "level": ["50%", "80%", "最亮", "最暗", "中等"],
            "channel": ["新闻频道", "电影频道", "综艺频道", "体育频道"],
            "content": ["电影", "新闻", "综艺", "音乐"],
            "song": ["周杰伦的歌", "流行歌曲", "轻音乐", "古典音乐"],
            "artist": ["周杰伦", "邓紫棋", "林俊杰", "王菲"]
        }
        
        # 语音变化配置
        self.voice_profiles = [
            VoiceProfile(pitch_shift=0, speed_change=1.0, voice_type="标准男声"),
            VoiceProfile(pitch_shift=2, speed_change=0.95, voice_type="标准女声"),
            VoiceProfile(pitch_shift=-1, speed_change=1.1, voice_type="低沉男声"),
            VoiceProfile(pitch_shift=3, speed_change=0.9, voice_type="清脆女声"),
            VoiceProfile(pitch_shift=1, speed_change=1.05, voice_type="年轻男声"),
            VoiceProfile(pitch_shift=0, speed_change=0.85, voice_type="缓慢语音"),
            VoiceProfile(pitch_shift=0, speed_change=1.15, voice_type="快速语音"),
        ]
    
    def generate_all_commands(self) -> List[str]:
        """生成所有可能的指令组合"""
        all_commands = []
        
        for category, templates in self.command_categories.items():
            for template in templates:
                if "{room}" in template:
                    for room in self.rooms:
                        command = template.replace("{room}", room)
                        all_commands.extend(self._replace_other_params(command))
                else:
                    all_commands.extend(self._replace_other_params(template))
        
        return list(set(all_commands))  # 去重
    
    def _replace_other_params(self, command: str) -> List[str]:
        """替换指令中的其他参数"""
        if any(param in command for param in ["{temp}", "{level}", "{channel}", "{content}", "{song}", "{artist}"]):
            results = []
            
            # 替换所有参数
            for key, values in self.replacements.items():
                param_placeholder = "{" + key + "}"
                if param_placeholder in command:
                    for value in values:
                        results.append(command.replace(param_placeholder, value))
                    return results
            
            return [command]  # 如果没有找到参数，返回原命令
        else:
            return [command]
    
    def create_synthetic_audio(self, text: str, voice_profile: VoiceProfile) -> np.ndarray:
        """创建合成音频（简化版本）"""
        # 这是一个简化的音频合成函数
        # 在实际应用中，您可能需要使用更高级的TTS引擎
        
        # 基础音频生成（基于文本长度和特征）
        duration = max(len(text) * 0.08, 1.0)  # 基于文本长度估算时长
        duration = min(duration, self.target_duration)
        
        # 生成基础波形
        t = np.linspace(0, duration, int(duration * self.sample_rate))
        
        # 创建多频率组合的音频信号（模拟语音）
        audio = np.zeros_like(t)
        
        # 基础频率（模拟语音的基频）
        f0 = 150 * (2 ** (voice_profile.pitch_shift / 12.0))  # 音调偏移
        
        # 添加多个谐波分量
        for harmonic in range(1, 6):
            frequency = f0 * harmonic
            amplitude = 1.0 / harmonic  # 随谐波次数衰减
            
            # 添加一些随机性模拟语音变化
            freq_modulation = 1 + 0.05 * np.sin(2 * np.pi * 3 * t)  # 轻微频率调制
            audio += amplitude * np.sin(2 * np.pi * frequency * freq_modulation * t)
        
        # 添加语音包络（音量变化）
        envelope = np.exp(-3 * np.abs(t - duration/2) / duration)  # 中间大，两边小
        audio = audio * envelope
        
        # 应用语速变化
        if voice_profile.speed_change != 1.0:
            original_length = len(audio)
            new_length = int(original_length / voice_profile.speed_change)
            audio = np.interp(np.linspace(0, original_length-1, new_length), 
                             np.arange(original_length), audio)
        
        # 应用音量增益
        audio = audio * voice_profile.volume_gain
        
        # 添加背景噪声
        if voice_profile.background_noise > 0:
            noise = np.random.normal(0, voice_profile.background_noise, len(audio))
            audio = audio + noise
        
        # 标准化音频
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio)) * 0.8
        
        # 确保目标时长
        target_samples = int(self.target_duration * self.sample_rate)
        if len(audio) < target_samples:
            # 填充静音
            padding = target_samples - len(audio)
            audio = np.pad(audio, (0, padding), mode='constant')
        elif len(audio) > target_samples:
            # 截断
            audio = audio[:target_samples]
        
        return audio
    
    def generate_enhanced_dataset(self, 
                                 num_samples_per_command: int = 3,
                                 max_total_samples: int = 1000) -> Dict:
        """生成增强的数据集"""
        print("🚀 开始生成增强数据集...")
        
        # 获取所有指令
        all_commands = self.generate_all_commands()
        print(f"📝 总共 {len(all_commands)} 个不同的指令")
        
        # 控制总样本数
        if len(all_commands) * num_samples_per_command > max_total_samples:
            num_samples_per_command = max(1, max_total_samples // len(all_commands))
            print(f"⚡ 调整每个指令的样本数为 {num_samples_per_command} 以控制总量")
        
        # 生成数据
        dataset_info = {
            "total_samples": 0,
            "commands": [],
            "categories": {},
            "voice_profiles": [profile.voice_type for profile in self.voice_profiles],
            "generation_time": "",
            "sample_rate": self.sample_rate,
            "target_duration": self.target_duration
        }
        
        sample_index = 0
        
        for command in all_commands:
            if sample_index >= max_total_samples:
                break
                
            for sample_num in range(num_samples_per_command):
                if sample_index >= max_total_samples:
                    break
                
                # 随机选择语音特征
                voice_profile = random.choice(self.voice_profiles)
                
                # 生成音频
                try:
                    audio = self.create_synthetic_audio(command, voice_profile)
                    
                    # 保存音频文件
                    filename = f"enhanced_sample_{sample_index:06d}.wav"
                    filepath = os.path.join(self.output_dir, "audio", filename)
                    sf.write(filepath, audio, self.sample_rate)
                    
                    # 记录信息
                    sample_info = {
                        "filename": filename,
                        "text": command,
                        "voice_profile": voice_profile.voice_type,
                        "category": self._get_command_category(command),
                        "duration": self.target_duration
                    }
                    
                    dataset_info["commands"].append(sample_info)
                    
                    sample_index += 1
                    
                    if sample_index % 50 == 0:
                        print(f"📊 已生成 {sample_index} 个样本...")
                        
                except Exception as e:
                    print(f"⚠️ 生成样本失败: {e}")
                    continue
        
        # 统计类别信息
        for sample in dataset_info["commands"]:
            category = sample["category"]
            if category not in dataset_info["categories"]:
                dataset_info["categories"][category] = 0
            dataset_info["categories"][category] += 1
        
        dataset_info["total_samples"] = len(dataset_info["commands"])
        
        # 保存数据集信息
        info_file = os.path.join(self.output_dir, "dataset_info.json")
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(dataset_info, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 数据集生成完成！")
        print(f"📊 总样本数: {dataset_info['total_samples']}")
        print(f"📂 保存位置: {self.output_dir}")
        
        return dataset_info
    
    def _get_command_category(self, command: str) -> str:
        """获取指令所属类别"""
        for category, templates in self.command_categories.items():
            for template in templates:
                # 简化的模板匹配
                template_words = template.replace("{room}", "").replace("{temp}", "").replace("{level}", "").replace("{channel}", "").replace("{content}", "").replace("{song}", "").replace("{artist}", "").split()
                if all(word in command for word in template_words if len(word) > 1):
                    return category
        return "其他"
    
    def analyze_dataset(self) -> Dict:
        """分析现有数据集"""
        info_file = os.path.join(self.output_dir, "dataset_info.json")
        
        if not os.path.exists(info_file):
            print("❌ 未找到数据集信息文件")
            return {}
        
        with open(info_file, 'r', encoding='utf-8') as f:
            dataset_info = json.load(f)
        
        print("📊 数据集分析报告")
        print("=" * 40)
        print(f"总样本数: {dataset_info['total_samples']}")
        print(f"采样率: {dataset_info['sample_rate']} Hz")
        print(f"目标时长: {dataset_info['target_duration']} 秒")
        
        print("\n类别分布:")
        for category, count in dataset_info["categories"].items():
            percentage = count / dataset_info["total_samples"] * 100
            print(f"  {category}: {count} 个样本 ({percentage:.1f}%)")
        
        print(f"\n语音类型: {', '.join(dataset_info['voice_profiles'])}")
        
        return dataset_info
    
    def create_training_splits(self, train_ratio: float = 0.8) -> Dict:
        """创建训练/验证数据集分割"""
        info_file = os.path.join(self.output_dir, "dataset_info.json")
        
        if not os.path.exists(info_file):
            print("❌ 未找到数据集信息文件")
            return {}
        
        with open(info_file, 'r', encoding='utf-8') as f:
            dataset_info = json.load(f)
        
        commands = dataset_info["commands"]
        random.shuffle(commands)
        
        split_index = int(len(commands) * train_ratio)
        train_commands = commands[:split_index]
        val_commands = commands[split_index:]
        
        # 保存分割信息
        splits = {
            "train": train_commands,
            "validation": val_commands,
            "train_count": len(train_commands),
            "val_count": len(val_commands),
            "train_ratio": train_ratio
        }
        
        splits_file = os.path.join(self.output_dir, "dataset_splits.json")
        with open(splits_file, 'w', encoding='utf-8') as f:
            json.dump(splits, f, ensure_ascii=False, indent=2)
        
        print(f"📊 数据集分割完成:")
        print(f"  训练集: {len(train_commands)} 个样本 ({train_ratio*100:.1f}%)")
        print(f"  验证集: {len(val_commands)} 个样本 ({(1-train_ratio)*100:.1f}%)")
        
        return splits

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="增强的智能家居语音数据集生成器")
    parser.add_argument('--output_dir', type=str, default="src/train/res/enhanced_dataset",
                       help='输出目录')
    parser.add_argument('--samples_per_command', type=int, default=3,
                       help='每个指令的样本数')
    parser.add_argument('--max_samples', type=int, default=1000,
                       help='最大样本总数')
    parser.add_argument('--action', choices=['generate', 'analyze', 'split'], 
                       default='generate', help='操作类型')
    parser.add_argument('--train_ratio', type=float, default=0.8,
                       help='训练集比例')
    
    args = parser.parse_args()
    
    generator = EnhancedDatasetGenerator(args.output_dir)
    
    if args.action == 'generate':
        generator.generate_enhanced_dataset(
            num_samples_per_command=args.samples_per_command,
            max_total_samples=args.max_samples
        )
    elif args.action == 'analyze':
        generator.analyze_dataset()
    elif args.action == 'split':
        generator.create_training_splits(args.train_ratio)

if __name__ == "__main__":
    main()
