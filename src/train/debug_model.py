#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型调试脚本
检查模型的实际行为和输出
"""

import os
import sys
import torch
import numpy as np
import traceback

# 添加路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model_integration import LightASREngine
from dataset_generator import SmartHomeSpeechSynthesizer

def debug_model_output():
    """调试模型输出"""
    print("🔍 开始模型调试...")
    print("=" * 50)
    
    # 初始化引擎
    engine = LightASREngine()
    
    # 检查模型是否加载
    print(f"模型是否可用: {engine.is_available()}")
    print(f"模型信息: {engine.get_model_info()}")
    
    # 生成一个简单的测试音频
    print("\n🎵 生成测试音频...")
    synthesizer = SmartHomeSpeechSynthesizer()
    test_command = "打开客厅的灯"
    
    try:
        # 生成音频
        audio = synthesizer.synthesize_speech(test_command, duration=2.0)
        print(f"音频生成成功，形状: {audio.shape}")
        
        # 保存为文件
        import torchaudio
        audio_tensor = torch.from_numpy(audio).unsqueeze(0)
        test_file = "debug_test.wav"
        torchaudio.save(test_file, audio_tensor, synthesizer.sample_rate)
        print(f"音频已保存到: {test_file}")
        
        # 直接测试推理器
        print("\n🚀 测试推理器...")
        if engine.inference:
            result = engine.inference.predict_from_file(test_file)
            print(f"推理结果: {result}")
            
            # 检查各个组件
            class_pred = result.get('class_prediction', None)
            confidence = result.get('class_confidence', None)
            
            print(f"类别预测: {class_pred}")
            print(f"置信度: {confidence}")
            
            # 检查命令映射
            if class_pred is not None and class_pred in engine.command_mapping:
                mapped_command = engine.command_mapping[class_pred]
                print(f"映射的命令: {mapped_command}")
            else:
                print("命令映射失败")
                print(f"可用映射: {list(engine.command_mapping.keys())}")
        
        # 测试完整的recognize_file方法
        print("\n🎯 测试完整识别方法...")
        final_result = engine.recognize_file(test_file)
        print(f"最终识别结果: {final_result}")
        
        # 清理
        if os.path.exists(test_file):
            os.remove(test_file)
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        traceback.print_exc()

def debug_audio_processing():
    """调试音频处理过程"""
    print("\n🔧 调试音频处理...")
    print("=" * 50)
    
    # 直接测试特征提取
    from model import AudioFeatureExtractor, LightASRInference
    
    feature_extractor = AudioFeatureExtractor()
    
    # 生成测试音频
    synthesizer = SmartHomeSpeechSynthesizer()
    audio = synthesizer.synthesize_speech("打开灯", duration=2.0)
    
    print(f"原始音频形状: {audio.shape}")
    print(f"音频采样率: {synthesizer.sample_rate}")
    
    # 转换为tensor
    audio_tensor = torch.from_numpy(audio).float()
    print(f"音频tensor形状: {audio_tensor.shape}")
    
    # 提取特征
    try:
        features = feature_extractor.extract_features(audio_tensor)
        print(f"MFCC特征形状: {features['mfcc'].shape}")
        print(f"梅尔频谱形状: {features['mel_spectrogram'].shape}")
    except Exception as e:
        print(f"❌ 特征提取失败: {e}")
        traceback.print_exc()

def debug_model_weights():
    """调试模型权重"""
    print("\n⚖️ 调试模型权重...")
    print("=" * 50)
    
    engine = LightASREngine()
    
    if engine.inference and engine.inference.model:
        model = engine.inference.model
        
        # 检查模型参数
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        
        print(f"总参数数量: {total_params}")
        print(f"可训练参数数量: {trainable_params}")
        
        # 检查模型状态
        print(f"模型训练模式: {model.training}")
        
        # 检查设备
        device = next(model.parameters()).device
        print(f"模型设备: {device}")
        
        # 检查分类器权重
        classifier_weight = model.classifier[0].weight
        print(f"分类器权重形状: {classifier_weight.shape}")
        print(f"分类器权重范围: [{classifier_weight.min():.3f}, {classifier_weight.max():.3f}]")

if __name__ == "__main__":
    debug_model_output()
    debug_audio_processing()
    debug_model_weights()
