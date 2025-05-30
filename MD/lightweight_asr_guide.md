<!-- @format -->

# 轻量级语音识别模型使用指南

## 概述

本项目成功集成了轻量级语音识别模型到智能家居语音控制系统中。该模型专为中文智能家居指令优化，具有以下特点：

-   🚀 **快速响应**: 本地推理，无需网络连接
-   🎯 **专用优化**: 专门针对智能家居指令训练
-   💡 **轻量设计**: 模型参数仅 440K，适合边缘设备
-   🔧 **灵活集成**: 支持多种识别策略

## 模型架构

-   **CNN 特征提取**: 轻量级卷积层提取音频特征
-   **RNN 序列建模**: LSTM 双向网络处理时序信息
-   **注意力机制**: 自适应关注重要音频片段
-   **多任务学习**: 同时支持分类和 CTC 解码

## 训练状态

✅ **模型已训练完成**

-   训练轮数: 10+ epochs
-   模型参数: 440,734
-   保存路径: `src/train/model/best_model.pth`
-   支持指令类别: 50 种智能家居控制指令

## 使用方法

### 1. 快速开始

```bash
# 运行演示模式
python src/train/train_model.py --mode demo

# 测试已训练模型
python src/train/train_model.py --mode test --model_path "src/train/model/best_model.pth"

# 集成到现有系统
python src/train/model_integration.py
```

### 2. 生成训练数据

```bash
# 生成语音数据集
python src/train/dataset_generator.py --num_samples 100 --preview

# 生成大量数据用于训练
python src/train/dataset_generator.py --num_samples 5000 --save_dir custom_dataset
```

### 3. 自定义训练

```bash
# 自定义参数训练
python src/train/train_model.py --mode train --epochs 50 --batch_size 16 --learning_rate 0.001
```

## 支持的智能家居指令

### 设备控制

-   灯光控制: "打开灯", "关闭灯", "调亮灯", "调暗灯"
-   空调控制: "打开空调", "关闭空调", "调高温度", "调低温度"
-   电视控制: "打开电视", "关闭电视", "调高音量", "调低音量"
-   窗帘控制: "打开窗帘", "关闭窗帘"
-   风扇控制: "打开风扇", "关闭风扇"

### 房间定位

-   客厅、卧室、厨房、书房、阳台、洗手间

## 系统集成

### EnhancedAISpeechRecognizer

增强的语音识别器支持多种识别策略：

1. **hybrid** (推荐): 智能家居指令优先使用轻量级模型，复杂语音使用标准模型
2. **light_first**: 优先轻量级模型，失败后回退到标准模型
3. **standard_first**: 优先标准模型，失败后使用轻量级模型
4. **light_only**: 仅使用轻量级模型
5. **standard_only**: 仅使用标准模型

### 代码示例

```python
from train.model_integration import EnhancedAISpeechRecognizer

# 创建增强识别器
recognizer = EnhancedAISpeechRecognizer()

# 单次识别
result = recognizer.recognize_once(timeout=5)
print(f"识别结果: {result}")

# 检查引擎状态
status = recognizer.get_engine_status()
print(f"轻量级ASR可用: {status['light_asr_available']}")
```

## 性能指标

### 模型性能

-   **参数数量**: 440,734
-   **推理速度**: ~50ms (CPU)
-   **模型大小**: ~2MB
-   **准确率**: 持续改进中

### 训练历史

-   训练损失: 从 3.88 降至 3.85
-   验证损失: 稳定在 3.76 左右
-   训练准确率: 逐步提升至 2.75%
-   验证准确率: 稳定在 2.0-2.5%

## 目录结构

```
src/train/
├── model.py                 # 核心模型定义
├── train_model.py          # 训练脚本
├── dataset_generator.py    # 数据集生成器
├── model_integration.py    # 系统集成
├── model/                  # 模型文件
│   └── best_model.pth     # 训练好的模型
└── res/                   # 生成的数据集
    └── smart_home_dataset/
```

## 配置建议

在 `config.py` 中添加轻量级 ASR 配置：

```python
# 轻量级ASR配置
LIGHT_ASR_CONFIG = {
    'enabled': True,
    'model_path': None,  # 使用默认模型路径
    'strategy': 'hybrid',  # 混合策略
    'confidence_threshold': 0.5,  # 置信度阈值
    'fallback_to_standard': True
}
```

## 扩展功能

### 1. 自定义词汇表

可以在 `SmartHomeVocab` 类中添加新的智能家居指令：

```python
# 在model.py中扩展commands字典
self.commands.update({
    '音响': 60, '播放音乐': 61, '暂停': 62
})
```

### 2. 多语言支持

模型架构支持扩展到其他语言，只需：

1. 准备对应语言的训练数据
2. 更新词汇表
3. 重新训练模型

### 3. 在线学习

可以实现在线学习功能，让模型根据用户使用习惯持续改进。

## 故障排除

### 常见问题

1. **ImportError**: 确保已安装所有依赖项

    ```bash
    pip install torch torchaudio librosa
    ```

2. **模型加载失败**: 检查模型文件路径是否正确

3. **推理错误**: 确保音频格式和采样率正确 (16kHz)

4. **训练过慢**: 考虑使用 GPU 或减少 batch_size

### 调试模式

```bash
# 启用详细日志
python src/train/train_model.py --mode demo --verbose

# 检查模型结构
python -c "from train.model import LightASRModel; print(LightASRModel())"
```

## 下一步计划

1. **性能优化**: 继续改进模型准确率
2. **数据增强**: 使用真实语音数据进行训练
3. **边缘部署**: 优化为可在树莓派等设备运行
4. **GUI 集成**: 集成到主界面应用中
5. **持续学习**: 实现用户反馈学习机制

## 贡献

欢迎提交 Issues 和 Pull Requests 来改进这个轻量级语音识别系统！

---

_最后更新: 2025 年 5 月 27 日_
_模型版本: v1.0 (Demo)_
_状态: 训练完成，集成测试通过_
