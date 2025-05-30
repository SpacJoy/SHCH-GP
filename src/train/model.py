# -*- coding: utf-8 -*-
"""
轻量级语音识别模型
专为智能家居语音控制优化的轻量级深度学习模型
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchaudio
import librosa
import numpy as np
import os
import json
import pickle
from typing import List, Tuple, Optional, Dict
import warnings
warnings.filterwarnings("ignore")

class LightASRModel(nn.Module):
    """
    轻量级自动语音识别模型
    使用CNN+RNN架构，专门优化用于智能家居语音控制指令识别
    """
    
    def __init__(self, 
                 vocab_size: int = 1000,
                 input_dim: int = 80,  # MFCC特征维度
                 hidden_dim: int = 256,
                 num_layers: int = 2,
                 num_classes: int = 50,  # 智能家居指令类别数
                 dropout: float = 0.1):
        super(LightASRModel, self).__init__()
        
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.vocab_size = vocab_size
        self.num_classes = num_classes
        
        # CNN特征提取层 - 轻量级设计
        self.conv_layers = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1)),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=(2, 2)),
            
            nn.Conv2d(32, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1)),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=(2, 2)),
            
            nn.Conv2d(64, 128, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1)),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.AdaptiveAvgPool2d((1, None))  # 全局平均池化
        )
        
        # RNN序列建模层
        self.rnn = nn.LSTM(
            input_size=128,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=True
        )
        
        # 注意力机制 - 轻量级
        self.attention = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, 1),
            nn.Softmax(dim=1)
        )
        
        # 分类器
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, num_classes)
        )
        
        # CTC解码器（用于序列到序列）
        self.ctc_layer = nn.Linear(hidden_dim * 2, vocab_size)
        
    def forward(self, x: torch.Tensor, lengths: Optional[torch.Tensor] = None):
        """
        前向传播
        
        Args:
            x: 输入特征 [batch_size, 1, time, freq]
            lengths: 序列长度 [batch_size]
        
        Returns:
            dict: 包含分类和CTC输出的字典
        """
        batch_size = x.size(0)
          # CNN特征提取
        conv_out = self.conv_layers(x)  # [batch_size, 128, 1, time']
        conv_out = conv_out.squeeze(2).transpose(1, 2)  # [batch_size, time', 128]
        
        # RNN序列建模
        if lengths is not None:
            # 调整lengths以匹配CNN输出的时间维度
            # CNN有两个MaxPool2d(2,2)，所以时间维度被下采样4倍
            adjusted_lengths = torch.clamp(lengths // 4, min=1, max=conv_out.size(1))
            conv_out = nn.utils.rnn.pack_padded_sequence(
                conv_out, adjusted_lengths.cpu(), batch_first=True, enforce_sorted=False
            )
        
        rnn_out, _ = self.rnn(conv_out)
        
        if lengths is not None:
            rnn_out, _ = nn.utils.rnn.pad_packed_sequence(rnn_out, batch_first=True)
        
        # 注意力机制
        attention_weights = self.attention(rnn_out)  # [batch_size, time, 1]
        attended_features = torch.sum(rnn_out * attention_weights, dim=1)  # [batch_size, hidden_dim*2]
        
        # 分类输出（用于意图识别）
        class_output = self.classifier(attended_features)
        
        # CTC输出（用于语音识别）
        ctc_output = self.ctc_layer(rnn_out)
        ctc_output = F.log_softmax(ctc_output, dim=-1)
        
        return {
            'classification': class_output,
            'ctc': ctc_output,
            'attention_weights': attention_weights,
            'features': attended_features
        }

class AudioFeatureExtractor:
    """
    音频特征提取器
    提取MFCC、梅尔频谱等特征
    """
    
    def __init__(self, 
                 sample_rate: int = 16000,
                 n_mfcc: int = 80,
                 n_fft: int = 512,
                 hop_length: int = 160,
                 n_mels: int = 80):
        self.sample_rate = sample_rate
        self.n_mfcc = n_mfcc
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.n_mels = n_mels
        
        # 预计算梅尔滤波器组
        self.mel_transform = torchaudio.transforms.MelSpectrogram(
            sample_rate=sample_rate,
            n_fft=n_fft,
            hop_length=hop_length,
            n_mels=n_mels,
            f_min=0,
            f_max=sample_rate // 2
        )
        
        self.mfcc_transform = torchaudio.transforms.MFCC(
            sample_rate=sample_rate,
            n_mfcc=n_mfcc,
            melkwargs={
                'n_fft': n_fft,
                'hop_length': hop_length,
                'n_mels': n_mels,
                'f_min': 0,
                'f_max': sample_rate // 2
            }
        )
    
    def extract_features(self, audio: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        提取音频特征
        
        Args:
            audio: 音频信号 [batch_size, samples] 或 [samples]
        
        Returns:
            dict: 包含各种特征的字典
        """
        if audio.dim() == 1:
            audio = audio.unsqueeze(0)
        
        # 确保音频长度
        if audio.size(-1) < self.n_fft:
            padding = self.n_fft - audio.size(-1)
            audio = F.pad(audio, (0, padding))
        
        # 提取MFCC特征
        mfcc = self.mfcc_transform(audio)
        
        # 提取梅尔频谱
        mel_spec = self.mel_transform(audio)
        mel_spec = torch.log(mel_spec + 1e-8)  # 对数变换
        
        # 特征归一化
        mfcc = (mfcc - mfcc.mean(dim=-1, keepdim=True)) / (mfcc.std(dim=-1, keepdim=True) + 1e-8)
        mel_spec = (mel_spec - mel_spec.mean(dim=-1, keepdim=True)) / (mel_spec.std(dim=-1, keepdim=True) + 1e-8)
        
        return {
            'mfcc': mfcc,
            'mel_spectrogram': mel_spec,
            'raw_audio': audio
        }

class SmartHomeVocab:
    """
    智能家居专用词汇表
    """
    
    def __init__(self):
        self.commands = {
            # 设备控制
            '打开': 0, '关闭': 1, '开启': 2, '关闭': 3,
            '调节': 4, '设置': 5, '调到': 6, '调整': 7,
            
            # 设备名称
            '灯': 10, '电灯': 11, '台灯': 12, '吊灯': 13,
            '空调': 20, '冷气': 21, '暖气': 22,
            '电视': 30, '电视机': 31,
            '窗帘': 40, '百叶窗': 41,
            '风扇': 50, '吊扇': 51,
            
            # 房间位置
            '客厅': 100, '卧室': 101, '厨房': 102, '书房': 103,
            '阳台': 104, '洗手间': 105, '卫生间': 106,
            
            # 数值和状态
            '一': 200, '二': 201, '三': 202, '四': 203, '五': 204,
            '低': 210, '中': 211, '高': 212,
            '亮': 220, '暗': 221, '明亮': 222, '昏暗': 223,
            
            # 特殊标记
            '<PAD>': 300, '<UNK>': 301, '<START>': 302, '<END>': 303
        }
        
        self.id_to_token = {v: k for k, v in self.commands.items()}
        self.vocab_size = len(self.commands)
        
        # 预定义的智能家居指令模式
        self.command_patterns = [
            ('打开客厅的灯', [0, 100, 10]),
            ('关闭卧室的灯', [1, 101, 10]),
            ('开启空调', [2, 20]),
            ('调节空调温度', [4, 20]),
            ('打开电视', [0, 30]),
            ('关闭窗帘', [1, 40]),
            ('开启风扇', [2, 50])
        ]
    
    def encode(self, text: str) -> List[int]:
        """将文本编码为token ID列表"""
        tokens = []
        for char in text:
            if char in self.commands:
                tokens.append(self.commands[char])
            else:
                tokens.append(self.commands['<UNK>'])
        return tokens
    
    def decode(self, token_ids: List[int]) -> str:
        """将token ID列表解码为文本"""
        text = ""
        for token_id in token_ids:
            if token_id in self.id_to_token:
                text += self.id_to_token[token_id]
            else:
                text += '<UNK>'
        return text

class LightASRTrainer:
    """
    轻量级ASR模型训练器
    """
    
    def __init__(self, 
                 model: LightASRModel,
                 device: Optional[torch.device] = None,
                 learning_rate: float = 1e-3,
                 weight_decay: float = 1e-5):
        
        self.model = model
        self.device = device if device else torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
        self.feature_extractor = AudioFeatureExtractor()
        self.vocab = SmartHomeVocab()
        
        # 优化器
        self.optimizer = torch.optim.AdamW(
            model.parameters(), 
            lr=learning_rate, 
            weight_decay=weight_decay
        )
          # 学习率调度器
        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode='min', factor=0.5, patience=5
        )
        
        # 损失函数
        self.ctc_loss = nn.CTCLoss(blank=self.vocab.commands['<PAD>'], reduction='mean')
        self.classification_loss = nn.CrossEntropyLoss()
        
        # 训练历史
        self.train_history = {
            'train_loss': [],
            'val_loss': [],
            'train_acc': [],
            'val_acc': []
        }
    
    def create_synthetic_data(self, num_samples: int = 1000) -> Tuple[List, List]:
        """
        创建合成训练数据
        用于演示和初步训练
        """
        print("🔧 创建合成训练数据...")
        
        audio_data = []
        labels = []
        
        for i in range(num_samples):
            # 生成随机音频信号（模拟语音）
            duration = np.random.uniform(1.0, 3.0)  # 1-3秒
            samples = int(duration * self.feature_extractor.sample_rate)
            
            # 生成基频和谐波（模拟人声）
            t = np.linspace(0, duration, samples)
            f0 = np.random.uniform(80, 300)  # 基频80-300Hz
            
            # 合成语音信号
            signal = np.zeros_like(t)
            for harmonic in range(1, 6):  # 前5个谐波
                amplitude = 1.0 / harmonic
                signal += amplitude * np.sin(2 * np.pi * f0 * harmonic * t)
            
            # 添加噪声
            noise = np.random.normal(0, 0.1, samples)
            signal += noise
            
            # 添加包络
            envelope = np.exp(-t * 2)  # 指数衰减包络
            signal *= envelope
            
            # 随机选择一个指令模式
            pattern = self.vocab.command_patterns[i % len(self.vocab.command_patterns)]
            command_text, token_ids = pattern
            
            audio_data.append(signal.astype(np.float32))
            labels.append({
                'text': command_text,
                'tokens': token_ids,
                'class_label': i % self.model.num_classes
            })
        
        print(f"✅ 创建了 {num_samples} 个合成样本")
        return audio_data, labels
    
    def prepare_batch(self, audio_batch: List[np.ndarray], label_batch: List[Dict]) -> Tuple[torch.Tensor, Dict]:
        """
        准备训练批次
        """
        batch_features = []
        batch_lengths = []
        batch_tokens = []
        batch_classes = []
        
        for audio, label in zip(audio_batch, label_batch):
            # 转换为PyTorch张量
            audio_tensor = torch.from_numpy(audio).float()
            
            # 提取特征
            features = self.feature_extractor.extract_features(audio_tensor)
            mfcc = features['mfcc']  # [1, n_mfcc, time]
            
            # 添加批次维度和通道维度
            mfcc = mfcc.unsqueeze(0)  # [1, 1, n_mfcc, time]
            
            batch_features.append(mfcc)
            batch_lengths.append(mfcc.size(-1))
            batch_tokens.append(label['tokens'])
            batch_classes.append(label['class_label'])
        
        # 填充到相同长度
        max_length = max(batch_lengths)
        padded_features = []
        
        for features in batch_features:
            if features.size(-1) < max_length:
                padding = max_length - features.size(-1)
                features = F.pad(features, (0, padding))
            padded_features.append(features)
        
        # 合并批次
        batch_tensor = torch.cat(padded_features, dim=0)  # [batch_size, 1, n_mfcc, max_time]
        lengths_tensor = torch.tensor(batch_lengths)
        classes_tensor = torch.tensor(batch_classes)
        
        return batch_tensor.to(self.device), {
            'lengths': lengths_tensor.to(self.device),
            'tokens': batch_tokens,
            'classes': classes_tensor.to(self.device)
        }
    
    def train_epoch(self, audio_data: List, labels: List, batch_size: int = 16):
        """
        训练一个epoch
        """
        self.model.train()
        total_loss = 0.0
        total_correct = 0
        total_samples = 0
        
        # 随机打乱数据
        indices = np.random.permutation(len(audio_data))
        
        for i in range(0, len(indices), batch_size):
            batch_indices = indices[i:i + batch_size]
            batch_audio = [audio_data[idx] for idx in batch_indices]
            batch_labels = [labels[idx] for idx in batch_indices]
            
            # 准备批次
            batch_features, batch_targets = self.prepare_batch(batch_audio, batch_labels)
            
            # 前向传播
            outputs = self.model(batch_features, batch_targets['lengths'])
            
            # 计算损失
            classification_loss = self.classification_loss(
                outputs['classification'], 
                batch_targets['classes']
            )
            
            # CTC损失（简化版，仅用于演示）
            ctc_loss = torch.tensor(0.0, device=self.device)
            
            # 总损失
            loss = classification_loss + 0.1 * ctc_loss
            
            # 反向传播
            self.optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            self.optimizer.step()
            
            # 计算准确率
            _, predicted = torch.max(outputs['classification'], 1)
            correct = (predicted == batch_targets['classes']).sum().item()
            
            total_loss += loss.item()
            total_correct += correct
            total_samples += len(batch_labels)
        
        epoch_loss = total_loss / (len(indices) // batch_size + 1)
        epoch_acc = total_correct / total_samples
        
        return epoch_loss, epoch_acc
    
    def evaluate(self, audio_data: List, labels: List, batch_size: int = 16):
        """
        评估模型
        """
        self.model.eval()
        total_loss = 0.0
        total_correct = 0
        total_samples = 0
        
        with torch.no_grad():
            for i in range(0, len(audio_data), batch_size):
                batch_audio = audio_data[i:i + batch_size]
                batch_labels = labels[i:i + batch_size]
                
                batch_features, batch_targets = self.prepare_batch(batch_audio, batch_labels)
                outputs = self.model(batch_features, batch_targets['lengths'])
                
                classification_loss = self.classification_loss(
                    outputs['classification'], 
                    batch_targets['classes']
                )
                
                _, predicted = torch.max(outputs['classification'], 1)
                correct = (predicted == batch_targets['classes']).sum().item()
                
                total_loss += classification_loss.item()
                total_correct += correct
                total_samples += len(batch_labels)
        
        avg_loss = total_loss / (len(audio_data) // batch_size + 1)
        accuracy = total_correct / total_samples
        
        return avg_loss, accuracy
    
    def train(self, num_epochs: int = 50, batch_size: int = 16, validation_split: float = 0.2):
        """
        训练模型
        """
        print("🚀 开始训练轻量级语音识别模型...")
        print(f"设备: {self.device}")
        print(f"模型参数数量: {sum(p.numel() for p in self.model.parameters()):,}")
        
        # 创建训练数据
        audio_data, labels = self.create_synthetic_data(num_samples=1000)
        
        # 划分训练集和验证集
        split_idx = int(len(audio_data) * (1 - validation_split))
        train_audio, val_audio = audio_data[:split_idx], audio_data[split_idx:]
        train_labels, val_labels = labels[:split_idx], labels[split_idx:]
        
        print(f"训练样本: {len(train_audio)}, 验证样本: {len(val_audio)}")
        
        best_val_loss = float('inf')
        patience_counter = 0
        
        for epoch in range(num_epochs):
            # 训练
            train_loss, train_acc = self.train_epoch(train_audio, train_labels, batch_size)
            
            # 验证
            val_loss, val_acc = self.evaluate(val_audio, val_labels, batch_size)
            
            # 更新学习率
            self.scheduler.step(val_loss)
            
            # 记录历史
            self.train_history['train_loss'].append(train_loss)
            self.train_history['val_loss'].append(val_loss)
            self.train_history['train_acc'].append(train_acc)
            self.train_history['val_acc'].append(val_acc)
            
            # 早停
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                self.save_model('best_model.pth')
            else:
                patience_counter += 1
            
            # 打印进度
            if epoch % 5 == 0:
                print(f"Epoch {epoch:3d}/{num_epochs}: "
                      f"训练损失={train_loss:.4f}, 训练准确率={train_acc:.4f}, "
                      f"验证损失={val_loss:.4f}, 验证准确率={val_acc:.4f}")
            
            # 早停检查
            if patience_counter >= 10:
                print(f"早停于第 {epoch} 轮")
                break
        
        print("✅ 训练完成!")
        return self.train_history
    
    def save_model(self, path: str):
        """保存模型"""
        model_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(model_dir, 'model', path)
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'train_history': self.train_history,
            'vocab': self.vocab.commands,
            'model_config': {
                'vocab_size': self.model.vocab_size,
                'input_dim': self.model.input_dim,
                'hidden_dim': self.model.hidden_dim,
                'num_layers': self.model.num_layers,
                'num_classes': self.model.num_classes
            }
        }, model_path)
        
        print(f"💾 模型已保存到: {model_path}")

class LightASRInference:
    """
    轻量级ASR模型推理器
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.feature_extractor = AudioFeatureExtractor()
        self.vocab = SmartHomeVocab()
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            # 创建默认模型
            self.model = LightASRModel(
                vocab_size=self.vocab.vocab_size,
                num_classes=50
            )
            self.model.to(self.device)
            print("⚠️ 使用未训练的模型，建议先进行训练")
    
    def load_model(self, model_path: str):
        """加载训练好的模型"""
        checkpoint = torch.load(model_path, map_location=self.device)
        
        model_config = checkpoint['model_config']
        self.model = LightASRModel(**model_config)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.to(self.device)
        self.model.eval()
        
        print(f"✅ 模型已从 {model_path} 加载")
    
    def predict(self, audio: np.ndarray) -> Dict:
        """
        对音频进行预测
        
        Args:
            audio: 音频信号数组
        
        Returns:
            dict: 预测结果
        """
        self.model.eval()
        
        with torch.no_grad():            # 预处理音频
            audio_tensor = torch.from_numpy(audio).float()
            features = self.feature_extractor.extract_features(audio_tensor)
            mfcc = features['mfcc']  # [1, n_mfcc, time]
            mfcc = mfcc.unsqueeze(0)  # [1, 1, n_mfcc, time] - 添加通道维度
            mfcc = mfcc.to(self.device)
            
            # 模型推理
            outputs = self.model(mfcc)            # 分类预测
            class_probs = F.softmax(outputs['classification'], dim=1)
            class_pred_tensor = torch.argmax(class_probs, dim=1)
            class_pred = int(class_pred_tensor.item())
            class_conf = class_probs[0][class_pred].item()
            
            # CTC预测（简化版）
            ctc_probs = F.softmax(outputs['ctc'], dim=2)
            ctc_pred = torch.argmax(ctc_probs, dim=2).squeeze().cpu().numpy()
            
            return {
                'class_prediction': class_pred,
                'class_confidence': class_conf,
                'ctc_prediction': ctc_pred.tolist(),
                'attention_weights': outputs['attention_weights'].cpu().numpy(),
                'features': outputs['features'].cpu().numpy()
            }
    
    def predict_from_file(self, audio_file: str) -> Dict:
        """
        从音频文件进行预测
        
        Args:
            audio_file: 音频文件路径
        
        Returns:
            dict: 预测结果
        """
        # 加载音频文件
        audio, sr = librosa.load(audio_file, sr=self.feature_extractor.sample_rate)
        return self.predict(audio)

def create_demo_model():
    """
    创建演示模型并进行简单训练
    """
    print("🎯 创建轻量级语音识别演示模型")
    print("=" * 50)
    
    # 创建模型
    vocab = SmartHomeVocab()
    model = LightASRModel(
        vocab_size=vocab.vocab_size,
        num_classes=50,
        hidden_dim=128,  # 更小的隐藏层，提高训练速度
        num_layers=1     # 减少层数，提高训练速度
    )
    
    # 创建训练器
    trainer = LightASRTrainer(model, learning_rate=1e-3)
    
    # 开始训练
    history = trainer.train(num_epochs=20, batch_size=8)
    
    # 保存模型
    trainer.save_model('light_asr_demo.pth')
    
    print("\n📊 训练历史:")
    print(f"最终训练准确率: {history['train_acc'][-1]:.4f}")
    print(f"最终验证准确率: {history['val_acc'][-1]:.4f}")
    
    return model, trainer

def test_inference():
    """
    测试模型推理
    """
    print("\n🧪 测试模型推理")
    print("=" * 30)
    
    # 创建推理器
    model_path = os.path.join(os.path.dirname(__file__), 'model', 'light_asr_demo.pth')
    if os.path.exists(model_path):
        inference = LightASRInference(model_path)
    else:
        print("⚠️ 未找到训练好的模型，使用未训练模型进行演示")
        inference = LightASRInference()
    
    # 创建测试音频
    duration = 2.0
    sample_rate = 16000
    samples = int(duration * sample_rate)
    t = np.linspace(0, duration, samples)
    
    # 生成测试信号
    f0 = 150  # 基频
    test_audio = np.sin(2 * np.pi * f0 * t) * np.exp(-t * 2)
    test_audio += np.random.normal(0, 0.05, samples)  # 添加噪声
    
    # 进行预测
    result = inference.predict(test_audio.astype(np.float32))
    
    print(f"分类预测: {result['class_prediction']}")
    print(f"分类置信度: {result['class_confidence']:.4f}")
    print(f"特征维度: {result['features'].shape}")
    print(f"注意力权重维度: {result['attention_weights'].shape}")
    
    return result

if __name__ == "__main__":
    print("🏠 智能家居轻量级语音识别模型")
    print("=" * 50)
    
    try:
        # 创建并训练演示模型
        model, trainer = create_demo_model()
        
        # 测试推理
        test_result = test_inference()
        
        print("\n✅ 演示完成!")
        print("\n📝 使用说明:")
        print("1. 模型已保存到 src/train/model/ 目录")
        print("2. 可以通过 LightASRInference 类进行推理")
        print("3. 支持从音频文件或numpy数组进行预测")
        print("4. 模型专门针对智能家居指令进行优化")
        
    except Exception as e:
        print(f"❌ 运行出错: {e}")
        import traceback
        traceback.print_exc()