# -*- coding: utf-8 -*-
"""
轻量级语音识别模型训练脚本
用于训练专门针对智能家居控制的语音识别模型
"""

import os
import sys
import argparse
import numpy as np
import torch
from datetime import datetime

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from train.model import (
    LightASRModel, 
    LightASRTrainer, 
    LightASRInference,
    SmartHomeVocab,
    create_demo_model,
    test_inference
)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='轻量级语音识别模型训练')
    
    parser.add_argument('--mode', type=str, default='demo', 
                       choices=['demo', 'train', 'test', 'inference'],
                       help='运行模式: demo(演示), train(训练), test(测试), inference(推理)')
    
    parser.add_argument('--epochs', type=int, default=20,
                       help='训练轮数 (默认: 20)')
    
    parser.add_argument('--batch_size', type=int, default=8,
                       help='批次大小 (默认: 8)')
    
    parser.add_argument('--learning_rate', type=float, default=1e-3,
                       help='学习率 (默认: 1e-3)')
    
    parser.add_argument('--hidden_dim', type=int, default=128,
                       help='隐藏层维度 (默认: 128)')
    
    parser.add_argument('--num_layers', type=int, default=1,
                       help='RNN层数 (默认: 1)')
    
    parser.add_argument('--model_path', type=str, default=None,
                       help='模型路径 (用于加载或保存)')
    
    parser.add_argument('--audio_file', type=str, default=None,
                       help='音频文件路径 (用于推理模式)')
    
    parser.add_argument('--save_name', type=str, default='light_asr_model.pth',
                       help='保存模型的文件名')
    
    args = parser.parse_args()
    
    print("🏠 智能家居轻量级语音识别模型训练工具")
    print("=" * 60)
    print(f"运行模式: {args.mode}")
    print(f"设备: {'GPU' if torch.cuda.is_available() else 'CPU'}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        if args.mode == 'demo':
            # 演示模式 - 创建并训练小型模型
            print("🎯 运行演示模式...")
            model, trainer = create_demo_model()
            test_inference()
            
        elif args.mode == 'train':
            # 训练模式 - 自定义参数训练
            print("🚀 开始自定义训练...")
            
            vocab = SmartHomeVocab()
            model = LightASRModel(
                vocab_size=vocab.vocab_size,
                num_classes=50,
                hidden_dim=args.hidden_dim,
                num_layers=args.num_layers
            )
            
            trainer = LightASRTrainer(model, learning_rate=args.learning_rate)
            
            history = trainer.train(
                num_epochs=args.epochs,
                batch_size=args.batch_size
            )
            
            # 保存模型
            trainer.save_model(args.save_name)
            
            print(f"\n📊 训练完成!")
            print(f"最终训练准确率: {history['train_acc'][-1]:.4f}")
            print(f"最终验证准确率: {history['val_acc'][-1]:.4f}")
            
        elif args.mode == 'test':
            # 测试模式 - 测试现有模型
            print("🧪 测试模式...")
            
            if args.model_path and os.path.exists(args.model_path):
                inference = LightASRInference(args.model_path)
                print(f"✅ 已加载模型: {args.model_path}")
            else:
                print("⚠️ 未指定模型路径或文件不存在，使用未训练模型")
                inference = LightASRInference()
            
            # 运行测试
            result = test_inference()
            
        elif args.mode == 'inference':
            # 推理模式 - 对指定音频文件进行推理
            print("🔍 推理模式...")
            
            if not args.audio_file:
                print("❌ 推理模式需要指定音频文件路径 (--audio_file)")
                return
            
            if not os.path.exists(args.audio_file):
                print(f"❌ 音频文件不存在: {args.audio_file}")
                return
            
            # 加载模型
            if args.model_path and os.path.exists(args.model_path):
                inference = LightASRInference(args.model_path)
                print(f"✅ 已加载模型: {args.model_path}")
            else:
                print("⚠️ 未指定模型路径，使用默认模型")
                default_model = os.path.join(
                    os.path.dirname(__file__), 'model', 'light_asr_demo.pth'
                )
                if os.path.exists(default_model):
                    inference = LightASRInference(default_model)
                else:
                    inference = LightASRInference()
            
            # 进行推理
            print(f"🎤 分析音频文件: {args.audio_file}")
            result = inference.predict_from_file(args.audio_file)
            
            print(f"\n📊 推理结果:")
            print(f"分类预测: {result['class_prediction']}")
            print(f"分类置信度: {result['class_confidence']:.4f}")
            print(f"特征维度: {result['features'].shape}")
            
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断程序")
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ 程序执行完成")

def show_model_info():
    """显示模型信息"""
    print("\n📋 模型架构信息:")
    print("=" * 40)
    
    vocab = SmartHomeVocab()
    model = LightASRModel(vocab_size=vocab.vocab_size)
    
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    print(f"词汇表大小: {vocab.vocab_size}")
    print(f"总参数数量: {total_params:,}")
    print(f"可训练参数: {trainable_params:,}")
    print(f"模型大小: ~{total_params * 4 / 1024 / 1024:.2f} MB")
    
    print(f"\n🎯 支持的智能家居指令类型:")
    for i, (command, _) in enumerate(vocab.command_patterns):
        print(f"  {i+1}. {command}")

def benchmark_model():
    """模型性能基准测试"""
    print("\n⚡ 模型性能基准测试:")
    print("=" * 40)
    
    vocab = SmartHomeVocab()
    model = LightASRModel(vocab_size=vocab.vocab_size, hidden_dim=128)
    
    # 测试推理速度
    import time
    
    # 创建测试输入
    batch_size = 1
    seq_length = 100
    feature_dim = 80
    
    test_input = torch.randn(batch_size, 1, feature_dim, seq_length)
    
    # 预热
    with torch.no_grad():
        for _ in range(10):
            _ = model(test_input)
    
    # 计时测试
    num_iterations = 100
    start_time = time.time()
    
    with torch.no_grad():
        for _ in range(num_iterations):
            _ = model(test_input)
    
    end_time = time.time()
    avg_time = (end_time - start_time) / num_iterations
    
    print(f"平均推理时间: {avg_time*1000:.2f} ms")
    print(f"推理速度: {1/avg_time:.1f} FPS")
    print(f"内存使用: ~{torch.cuda.memory_allocated() / 1024 / 1024:.2f} MB" if torch.cuda.is_available() else "CPU模式")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # 如果没有命令行参数，显示帮助信息
        print("🏠 智能家居轻量级语音识别模型")
        print("=" * 50)
        print("\n📖 使用方法:")
        print("python train_model.py --mode demo                    # 运行演示")
        print("python train_model.py --mode train --epochs 50      # 自定义训练")
        print("python train_model.py --mode test                   # 测试模型")
        print("python train_model.py --mode inference --audio_file audio.wav  # 推理")
        print("\n🔧 可选参数:")
        print("--epochs        训练轮数 (默认: 20)")
        print("--batch_size    批次大小 (默认: 8)")
        print("--learning_rate 学习率 (默认: 1e-3)")
        print("--hidden_dim    隐藏层维度 (默认: 128)")
        print("--num_layers    RNN层数 (默认: 1)")
        print("--model_path    模型路径")
        print("--save_name     保存文件名")
        
        show_model_info()
        benchmark_model()
        
        print("\n💡 快速开始: python train_model.py --mode demo")
    else:
        main()
