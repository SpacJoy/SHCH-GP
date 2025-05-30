# -*- coding: utf-8 -*-
"""
智能家居语音数据集生成器
用于生成合成的智能家居语音控制数据
"""

import os
import numpy as np
import torch
import torchaudio
from typing import List, Tuple, Dict
import json
import random
from dataclasses import dataclass

@dataclass
class AudioSample:
    """音频样本数据类"""
    audio: np.ndarray
    text: str
    tokens: List[int]
    class_label: int
    duration: float
    sample_rate: int

class SmartHomeSpeechSynthesizer:
    """
    智能家居语音合成器
    生成模拟的智能家居控制语音数据
    """
    
    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        
        # 智能家居指令模板
        self.command_templates = [
            # 灯光控制
            ("打开{room}的灯", "light_on", ["打开", "{room}", "的", "灯"]),
            ("关闭{room}的灯", "light_off", ["关闭", "{room}", "的", "灯"]),
            ("调亮{room}的灯", "light_bright", ["调亮", "{room}", "的", "灯"]),
            ("调暗{room}的灯", "light_dim", ["调暗", "{room}", "的", "灯"]),
            
            # 空调控制
            ("打开空调", "ac_on", ["打开", "空调"]),
            ("关闭空调", "ac_off", ["关闭", "空调"]),
            ("调高温度", "ac_temp_up", ["调高", "温度"]),
            ("调低温度", "ac_temp_down", ["调低", "温度"]),
            ("设置温度为{temp}度", "ac_temp_set", ["设置", "温度", "为", "{temp}", "度"]),
            
            # 电视控制
            ("打开电视", "tv_on", ["打开", "电视"]),
            ("关闭电视", "tv_off", ["关闭", "电视"]),
            ("调高音量", "tv_volume_up", ["调高", "音量"]),
            ("调低音量", "tv_volume_down", ["调低", "音量"]),
            
            # 窗帘控制
            ("打开窗帘", "curtain_open", ["打开", "窗帘"]),
            ("关闭窗帘", "curtain_close", ["关闭", "窗帘"]),
            ("拉开{room}的窗帘", "curtain_open_room", ["拉开", "{room}", "的", "窗帘"]),
            
            # 风扇控制
            ("打开风扇", "fan_on", ["打开", "风扇"]),
            ("关闭风扇", "fan_off", ["关闭", "风扇"]),
            ("调节风扇速度", "fan_speed", ["调节", "风扇", "速度"]),
        ]
        
        # 房间名称
        self.rooms = ["客厅", "卧室", "厨房", "书房", "主卧", "次卧"]
        
        # 温度数值
        self.temperatures = ["18", "20", "22", "24", "26", "28"]
        
        # 语音合成参数
        self.voice_params = {
            'male': {
                'f0_range': (80, 200),
                'formants': [700, 1220, 2600],
                'noise_level': 0.05
            },
            'female': {
                'f0_range': (150, 300),
                'formants': [900, 1400, 2800],
                'noise_level': 0.04
            },
            'child': {
                'f0_range': (200, 400),
                'formants': [1000, 1600, 3000],
                'noise_level': 0.06
            }
        }
    
    def generate_command_variations(self) -> List[Tuple[str, str, List[str]]]:
        """生成指令变体"""
        variations = []
        
        for template, intent, tokens in self.command_templates:
            if "{room}" in template:
                for room in self.rooms:
                    text = template.format(room=room)
                    new_tokens = [token.format(room=room) if token == "{room}" else token for token in tokens]
                    variations.append((text, intent, new_tokens))
            elif "{temp}" in template:
                for temp in self.temperatures:
                    text = template.format(temp=temp)
                    new_tokens = [token.format(temp=temp) if token == "{temp}" else token for token in tokens]
                    variations.append((text, intent, new_tokens))
            else:
                variations.append((template, intent, tokens))
        
        return variations
    
    def synthesize_speech(self, 
                         text: str, 
                         duration: float = None,
                         voice_type: str = 'male') -> np.ndarray:
        """
        合成语音信号
        
        Args:
            text: 文本内容
            duration: 音频时长（秒）
            voice_type: 声音类型 ('male', 'female', 'child')
        
        Returns:
            np.ndarray: 合成的音频信号
        """
        if duration is None:
            # 根据文本长度估算时长
            duration = max(1.0, len(text) * 0.15 + np.random.uniform(0.5, 1.0))
        
        samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, samples)
        
        # 获取声音参数
        params = self.voice_params[voice_type]
        f0_min, f0_max = params['f0_range']
        formants = params['formants']
        noise_level = params['noise_level']
        
        # 生成基频轮廓
        f0 = np.random.uniform(f0_min, f0_max)
        f0_contour = f0 * (1 + 0.1 * np.sin(2 * np.pi * 2 * t))  # 添加语调变化
        
        # 生成语音信号
        signal = np.zeros_like(t)
        
        # 添加基频和谐波
        for harmonic in range(1, 6):
            amplitude = 1.0 / harmonic
            harmonic_freq = f0_contour * harmonic
            signal += amplitude * np.sin(2 * np.pi * harmonic_freq * t)
        
        # 添加共振峰（简化版）
        for i, formant_freq in enumerate(formants[:3]):
            formant_amp = 0.3 / (i + 1)
            signal += formant_amp * np.sin(2 * np.pi * formant_freq * t)
        
        # 添加语音包络
        # 模拟语音的起伏
        envelope = np.ones_like(t)
        
        # 添加音节边界
        num_syllables = max(1, len(text) // 2)
        syllable_duration = duration / num_syllables
        
        for i in range(num_syllables):
            start_idx = int(i * syllable_duration * self.sample_rate)
            end_idx = int((i + 1) * syllable_duration * self.sample_rate)
            if end_idx > len(envelope):
                end_idx = len(envelope)
            
            # 音节内的包络
            syl_len = end_idx - start_idx
            if syl_len > 0:
                syl_env = 0.5 + 0.5 * np.cos(np.linspace(0, 2*np.pi, syl_len))
                envelope[start_idx:end_idx] *= syl_env
        
        # 应用包络
        signal *= envelope
        
        # 添加噪声
        noise = np.random.normal(0, noise_level, samples)
        signal += noise
        
        # 应用高通滤波器（模拟麦克风响应）
        # 简化版：使用差分
        signal = np.diff(np.concatenate([[0], signal]))
        
        # 归一化
        if np.max(np.abs(signal)) > 0:
            signal = signal / np.max(np.abs(signal)) * 0.8
        
        return signal.astype(np.float32)
    
    def create_dataset(self, 
                      num_samples: int = 1000,
                      voice_distribution: Dict[str, float] = None) -> List[AudioSample]:
        """
        创建数据集
        
        Args:
            num_samples: 样本数量
            voice_distribution: 声音类型分布
        
        Returns:
            List[AudioSample]: 音频样本列表
        """
        if voice_distribution is None:
            voice_distribution = {'male': 0.4, 'female': 0.4, 'child': 0.2}
        
        print(f"🎙️ 生成 {num_samples} 个语音样本...")
        
        # 生成所有指令变体
        command_variations = self.generate_command_variations()
        
        samples = []
        intent_to_label = {}
        current_label = 0
        
        for i in range(num_samples):
            # 随机选择指令
            text, intent, tokens = random.choice(command_variations)
            
            # 分配类别标签
            if intent not in intent_to_label:
                intent_to_label[intent] = current_label
                current_label += 1
            
            class_label = intent_to_label[intent]
            
            # 随机选择声音类型
            voice_type = np.random.choice(
                list(voice_distribution.keys()),
                p=list(voice_distribution.values())
            )
            
            # 生成语音
            duration = np.random.uniform(1.0, 3.5)
            audio = self.synthesize_speech(text, duration, voice_type)
            
            # 创建token ID列表（简化版）
            token_ids = list(range(len(tokens)))
            
            sample = AudioSample(
                audio=audio,
                text=text,
                tokens=token_ids,
                class_label=class_label,
                duration=duration,
                sample_rate=self.sample_rate
            )
            
            samples.append(sample)
            
            if (i + 1) % 100 == 0:
                print(f"  已生成 {i + 1}/{num_samples} 个样本")
        
        print(f"✅ 数据集生成完成! 共 {len(samples)} 个样本，{len(intent_to_label)} 个类别")
        
        # 保存类别映射
        label_mapping = {intent: label for intent, label in intent_to_label.items()}
        
        return samples, label_mapping
    
    def save_dataset(self, 
                    samples: List[AudioSample], 
                    label_mapping: Dict,
                    save_dir: str):
        """
        保存数据集
        
        Args:
            samples: 音频样本列表
            label_mapping: 标签映射
            save_dir: 保存目录
        """
        os.makedirs(save_dir, exist_ok=True)
        
        print(f"💾 保存数据集到 {save_dir}...")
        
        # 保存音频文件和标注
        audio_dir = os.path.join(save_dir, 'audio')
        os.makedirs(audio_dir, exist_ok=True)
        
        annotations = []
        
        for i, sample in enumerate(samples):
            # 保存音频文件
            audio_filename = f"sample_{i:06d}.wav"
            audio_path = os.path.join(audio_dir, audio_filename)
            
            # 转换为PyTorch张量并保存
            audio_tensor = torch.from_numpy(sample.audio).unsqueeze(0)
            torchaudio.save(audio_path, audio_tensor, sample.sample_rate)
            
            # 添加标注信息
            annotation = {
                'file': audio_filename,
                'text': sample.text,
                'tokens': sample.tokens,
                'class_label': sample.class_label,
                'duration': sample.duration
            }
            annotations.append(annotation)
        
        # 保存标注文件
        annotations_path = os.path.join(save_dir, 'annotations.json')
        with open(annotations_path, 'w', encoding='utf-8') as f:
            json.dump(annotations, f, ensure_ascii=False, indent=2)
        
        # 保存标签映射
        mapping_path = os.path.join(save_dir, 'label_mapping.json')
        with open(mapping_path, 'w', encoding='utf-8') as f:
            json.dump(label_mapping, f, ensure_ascii=False, indent=2)
        
        # 保存数据集统计信息
        stats = {
            'total_samples': len(samples),
            'num_classes': len(label_mapping),
            'total_duration': sum(s.duration for s in samples),
            'avg_duration': np.mean([s.duration for s in samples]),
            'sample_rate': samples[0].sample_rate if samples else 16000
        }
        
        stats_path = os.path.join(save_dir, 'dataset_stats.json')
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 数据集保存完成!")
        print(f"   音频文件: {len(samples)} 个")
        print(f"   总时长: {stats['total_duration']:.1f} 秒")
        print(f"   平均时长: {stats['avg_duration']:.2f} 秒")
        print(f"   类别数: {len(label_mapping)}")

def create_smart_home_dataset(num_samples: int = 1000, save_dir: str = None):
    """
    创建智能家居语音数据集
    
    Args:
        num_samples: 样本数量
        save_dir: 保存目录
    """
    if save_dir is None:
        save_dir = os.path.join(os.path.dirname(__file__), 'res', 'smart_home_dataset')
    
    print("🏠 创建智能家居语音数据集")
    print("=" * 50)
    
    # 创建合成器
    synthesizer = SmartHomeSpeechSynthesizer()
    
    # 生成数据集
    samples, label_mapping = synthesizer.create_dataset(
        num_samples=num_samples,
        voice_distribution={'male': 0.4, 'female': 0.4, 'child': 0.2}
    )
    
    # 保存数据集
    synthesizer.save_dataset(samples, label_mapping, save_dir)
    
    return samples, label_mapping

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='智能家居语音数据集生成器')
    parser.add_argument('--num_samples', type=int, default=1000,
                       help='生成样本数量 (默认: 1000)')
    parser.add_argument('--save_dir', type=str, default=None,
                       help='保存目录 (默认: res/smart_home_dataset)')
    parser.add_argument('--preview', action='store_true',
                       help='预览模式，只生成少量样本')
    
    args = parser.parse_args()
    
    if args.preview:
        num_samples = 10
        print("👀 预览模式，生成 10 个样本")
    else:
        num_samples = args.num_samples
    
    try:
        samples, label_mapping = create_smart_home_dataset(
            num_samples=num_samples,
            save_dir=args.save_dir
        )
        
        print("\n📊 数据集统计:")
        print(f"总样本数: {len(samples)}")
        print(f"类别数: {len(label_mapping)}")
        print(f"类别分布:")
        
        class_counts = {}
        for sample in samples:
            class_counts[sample.class_label] = class_counts.get(sample.class_label, 0) + 1
        
        for intent, label in sorted(label_mapping.items(), key=lambda x: x[1]):
            count = class_counts.get(label, 0)
            print(f"  {intent}: {count} 个样本")
        
        print(f"\n✅ 数据集生成完成!")
        
    except Exception as e:
        print(f"❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
