# 🏠 智能语音控制家居系统 (SHCH)

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

> 一个功能强大的智能语音家居控制系统，支持实时语音识别、AI语音助手和MQTT物联网通信

## 🌟 项目亮点

基于Python开发的现代化智能家居控制系统，集成了多种先进技术：
- **多重语音识别引擎**: 支持Google、百度、Whisper等多种语音识别方案
- **AI智能对话**: 集成ChatGPT等AI模型，实现自然语言交互
- **实时唤醒词检测**: 支持自定义唤醒词，无需手动激活
- **MQTT物联网通信**: 与巴法云平台无缝集成，控制真实设备
- **现代化GUI界面**: 美观易用的图形界面，支持主题切换

## ✨ 核心功能

### 🎤 语音识别技术
- **实时语音监听**: 持续监听环境中的语音指令
- **多引擎支持**: Google、百度AI、Whisper本地识别
- **🆕 轻量级ASR**: 自研的智能家居专用轻量级语音识别模型
- **唤醒词检测**: 自定义唤醒词，如"小助手"、"智能家居"
- **噪音过滤**: 智能过滤环境噪音，提高识别准确率
- **混合识别策略**: 智能选择最适合的识别引擎

### 🧠 AI智能助手
- **自然语言理解**: 基于AI模型的语义分析
- **上下文记忆**: 支持多轮对话和上下文理解
- **智能推理**: 根据环境和历史数据做出智能决策
- **个性化学习**: 学习用户习惯，提供个性化服务

### 🏡 设备控制
- 💡 **智能照明**: 客厅灯、卧室灯、书房灯等多区域控制
- ❄️ **空调系统**: 温度调节、模式切换、定时功能
- 📺 **娱乐设备**: 电视、音响、投影仪控制
- 🪟 **遮阳系统**: 电动窗帘、百叶窗控制
- 🌀 **通风设备**: 风扇、新风系统、空气净化器
- 🔒 **安防系统**: 智能门锁、摄像头、报警器

### 📊 数据监控
- **实时状态显示**: 设备状态、系统运行情况
- **历史数据分析**: 使用统计、能耗分析
- **日志记录**: 详细的操作日志和错误追踪
- **可视化图表**: 直观的数据展示和趋势分析

## 🚀 快速开始

### 方式一：一键启动 (推荐 Windows 用户)

```powershell
# 1. 克隆项目
git clone [项目地址]
cd SHCH

# 2. 一键安装依赖
.\install.bat

# 3. 快速配置
.\config.bat

# 4. 启动系统
.\start.bat
```

### 方式二：演示模式 (无需配置)

快速体验系统功能，无需安装任何依赖：

```powershell
# 直接运行演示版本
python demo.py

# 或使用AI演示版本
python demo_ai.py
```

**演示模式特色**:
- ✅ 零配置启动
- ✅ 模拟所有功能
- ✅ 完整UI展示
- ✅ 适合演示和学习

### 方式三：手动安装

#### 1. 环境要求
- **Python**: 3.8+ (推荐3.10+)
- **操作系统**: Windows 10/11
- **音频设备**: 麦克风和扬声器
- **网络**: 稳定的互联网连接

#### 2. 安装依赖

```powershell
# 基础安装
pip install -r requirements.txt

# 如果遇到pyaudio安装问题 (Windows)
pip install pipwin
pipwin install pyaudio

# 或者使用conda (推荐)
conda install pyaudio
```

#### 3. 环境测试

```powershell
# 运行系统测试
python test_system.py

# 测试语音识别
python test_ai_speech.py

# 测试唤醒词功能
python test_wake_word.py
```

## ⚙️ 配置指南

### 🔧 自动配置 (推荐)

使用AI配置向导进行智能配置：

```powershell
# 启动AI配置向导
python ai_config_wizard.py
```

AI向导将帮您：
- 🤖 自动检测系统环境
- 🔑 配置API密钥
- 🎙️ 测试音频设备
- 📡 设置MQTT连接
- 🎯 优化唤醒词

### 🔐 MQTT连接配置

#### 方式1：私钥登录 (推荐)

```python
# src/config.py
MQTT_CONFIG = {
    'broker': 'bemfa.com',
    'port': 9501,
    'client_id': 'your_private_key_here',
    'username': '',
    'password': '',
    'keep_alive': 60,
    'use_private_key': True
}
```

#### 方式2：账号密码登录

```python
MQTT_CONFIG = {
    'broker': 'bemfa.com',
    'port': 9501,
    'client_id': 'your_client_id',
    'username': 'your_username',
    'password': 'your_password',
    'keep_alive': 60,
    'use_private_key': False
}
```

### 🤖 AI配置

```python
# AI语音识别配置
AI_CONFIG = {
    'provider': 'openai',  # openai, azure, baidu
    'api_key': 'your_api_key_here',
    'model': 'gpt-3.5-turbo',
    'temperature': 0.7,
    'max_tokens': 1000
}

# 百度AI配置
BAIDU_CONFIG = {
    'app_id': 'your_app_id',
    'api_key': 'your_api_key',
    'secret_key': 'your_secret_key'
}
```

### 🎙️ 唤醒词配置

```python
# 唤醒词设置
WAKE_WORD_CONFIG = {
    'enabled': True,
    'wake_words': ['小助手', '智能家居', 'Hello智能'],
    'sensitivity': 0.7,
    'timeout': 5.0
}
```

## 📚 使用教程

### 🎯 语音控制使用

#### 基础语音指令
```
💡 照明控制:
"打开客厅的灯" | "关闭卧室灯" | "调亮书房灯"

❄️ 空调控制:
"开空调" | "关空调" | "空调温度调到25度" | "空调切换制冷模式"

📺 娱乐设备:
"打开电视" | "关闭电视" | "音量调大" | "切换频道"

🪟 窗帘控制:
"拉开窗帘" | "关闭窗帘" | "窗帘开一半"

🌀 风扇控制:
"开风扇" | "关风扇" | "风扇调到2档" | "风扇摆头"
```

#### AI智能对话
```
🤖 自然语言交互:
"现在家里有点热，帮我调节一下"
"我要睡觉了，帮我关掉所有不必要的设备"
"晚上看电影的时候应该怎么调节灯光？"
"帮我设置一个舒适的居家环境"
```

#### 唤醒词使用
1. **设置唤醒词**: 在配置中设置"小助手"、"智能家居"等
2. **激活语音**: 说出唤醒词后，系统进入监听状态
3. **发出指令**: 在提示音后说出控制指令
4. **确认执行**: 系统确认并执行指令

### 🖥️ GUI界面操作

#### 主控制面板
- **连接状态**: 显示MQTT和AI服务连接状态
- **设备控制**: 手动选择设备和操作
- **语音控制**: 启动/停止语音监听
- **系统日志**: 查看实时操作日志

#### 高级功能
- **场景模式**: 预设的智能场景(如观影模式、睡眠模式)
- **定时任务**: 设置设备定时开关
- **数据统计**: 查看设备使用统计和能耗分析
- **设备管理**: 添加、删除、配置智能设备

## 🏗️ 项目架构

```
SHCH/                                   # 🏠 项目根目录
├── 📁 src/                            # 💻 核心源码目录
│   ├── 🔧 config.py                   # ⚙️ 系统配置管理
│   ├── 📡 mqtt_client.py              # 🌐 MQTT通信模块
│   ├── 🎤 speech_recognition_module.py # 🗣️ 传统语音识别
│   ├── 🤖 ai_speech_recognition.py    # 🧠 AI语音识别
│   ├── 🎯 intent_recognition.py       # 💭 意图识别引擎
│   └── 🖥️ main_gui.py                 # 🎨 主界面程序
├── 📁 MD/                             # 📚 文档目录
│   ├── 📖 README.md                   # 📄 项目说明文档
│   ├── 📝 dome.txt                    # 📋 需求文档
│   └── 📓 *.md                        # 📑 其他文档
├── 🚀 启动脚本
│   ├── ▶️ start.bat                   # 🎯 主程序启动
│   ├── 🎭 demo_ai.bat                 # 🤖 AI演示启动
│   ├── ⚙️ config.bat                  # 🔧 配置向导启动
│   └── 🧪 test_*.bat                  # 🔬 测试脚本集合
├── 🔧 配置和测试
│   ├── 📦 requirements.txt            # 📋 依赖包清单
│   ├── 🏗️ install.bat                # 📥 一键安装脚本
│   ├── ⚙️ config_helper.py            # 🛠️ 配置助手
│   ├── 🤖 ai_config_wizard.py         # 🧙 AI配置向导
│   └── 🧪 test_*.py                   # 🔬 系统测试模块
└── 🎭 演示和工具
    ├── 🎪 demo.py                     # 🎨 基础演示版本
    ├── 🗣️ wake_word_*.py              # 👂 唤醒词相关工具
    └── 🎛️ *_optimizer.py              # ⚡ 性能优化工具
```

### 🔗 核心模块说明

#### 🧠 AI语音识别模块 (`ai_speech_recognition.py`)
- 集成多种AI语音识别引擎
- 支持实时语音转文本
- 智能噪音过滤和语音增强
- 多语言支持和方言识别

#### 💭 意图识别引擎 (`intent_recognition.py`)
- 基于AI的自然语言理解
- 上下文感知和多轮对话
- 设备和操作的智能映射
- 模糊匹配和纠错能力

#### 📡 MQTT通信模块 (`mqtt_client.py`)
- 与巴法云平台的稳定连接
- 设备状态实时同步
- 消息队列和重试机制
- 安全认证和加密传输

#### 🎨 图形界面 (`main_gui.py`)
- 现代化Material Design风格
- 响应式布局和主题切换
- 实时数据可视化
- 多语言界面支持

## 🛠️ 技术栈

### 🐍 核心技术
| 技术 | 版本 | 用途 | 特色 |
|------|------|------|------|
| **Python** | 3.8+ | 主开发语言 | 跨平台、丰富生态 |
| **tkinter** | 内置 | GUI界面开发 | 原生支持、轻量级 |
| **paho-mqtt** | 1.6.1+ | MQTT通信 | 稳定可靠、标准协议 |
| **SpeechRecognition** | 3.10.0+ | 语音识别 | 多引擎支持 |
| **PyAudio** | 0.2.11+ | 音频处理 | 实时音频流处理 |

### 🤖 AI技术栈
| 组件 | 技术选型 | 功能描述 |
|------|----------|----------|
| **语音识别** | Google Speech API, 百度AI, Whisper | 高精度语音转文本 |
| **自然语言处理** | OpenAI GPT, Azure Cognitive | 智能意图理解 |
| **唤醒词检测** | 自研算法 + Porcupine | 低功耗实时检测 |
| **语音合成** | Azure TTS, 百度TTS | 自然语音反馈 |

### 📊 数据处理
| 库名 | 用途 | 优势 |
|------|------|------|
| **pandas** | 数据分析 | 高效数据处理 |
| **numpy** | 数值计算 | 快速数组运算 |
| **matplotlib** | 数据可视化 | 专业图表生成 |
| **librosa** | 音频分析 | 专业音频处理 |

## 🚨 故障排除

### 🎤 音频设备问题

#### 问题：麦克风无法识别
```powershell
# 1. 检测音频设备
python -c "import pyaudio; p=pyaudio.PyAudio(); [print(f'{i}: {p.get_device_info_by_index(i)[\"name\"]}') for i in range(p.get_device_count())]"

# 2. 测试麦克风
python test_ai_speech.py

# 3. 重新安装音频库
pip uninstall pyaudio
pip install pipwin
pipwin install pyaudio
```

#### 问题：权限不足
```powershell
# Windows: 检查麦克风权限
# 设置 > 隐私 > 麦克风 > 允许应用访问麦克风

# 以管理员权限运行
# 右键点击 PowerShell > 以管理员身份运行
```

### 📡 网络连接问题

#### MQTT连接失败
```powershell
# 1. 测试网络连接
ping bemfa.com

# 2. 检查防火墙设置
# Windows Defender > 允许应用通过防火墙

# 3. 验证配置
python test_complete.py

# 4. 查看详细日志
python run.py --debug
```

#### API调用失败
```powershell
# 1. 检查API密钥
python config_helper.py --verify-api

# 2. 测试网络连接
curl -I https://api.openai.com

# 3. 检查代理设置
echo $HTTP_PROXY
echo $HTTPS_PROXY
```

### 🧠 语音识别问题

#### 识别准确率低
```powershell
# 1. 环境噪音测试
python test_wake_word.py --noise-test

# 2. 调整灵敏度
python wake_word_optimizer.py

# 3. 重新训练唤醒词
python wake_word_tuning.py
```

#### 唤醒词不响应
```powershell
# 1. 运行唤醒词测试套件
.\test_wake_word_suite.bat

# 2. 调试唤醒词检测
python test_wake_word_advanced.py --debug

# 3. 优化参数
python wake_word_optimizer.py --auto-tune
```

### 🔧 系统问题

#### Python环境问题
```powershell
# 1. 检查Python版本
python --version  # 应该是 3.8+

# 2. 修复Python 3.12兼容性
.\fix_python312.bat

# 3. 重建虚拟环境
python -m venv smart_home_env
smart_home_env\Scripts\activate
pip install -r requirements.txt
```

#### 依赖包冲突
```powershell
# 1. 清理旧依赖
pip freeze > old_requirements.txt
pip uninstall -r old_requirements.txt -y

# 2. 重新安装
pip install -r requirements.txt

# 3. 检查冲突
pip check
```

## 📈 性能优化

### ⚡ 系统优化建议

#### 硬件要求
| 组件 | 最低配置 | 推荐配置 |
|------|----------|----------|
| **CPU** | 双核 2.0GHz | 四核 3.0GHz+ |
| **内存** | 4GB RAM | 8GB+ RAM |
| **存储** | 2GB 可用空间 | SSD 5GB+ |
| **网络** | 宽带连接 | 稳定低延迟网络 |

#### 软件优化
```powershell
# 1. 启用性能模式
python run.py --performance-mode

# 2. 优化唤醒词检测
python wake_word_optimizer.py --optimize-cpu

# 3. 调整缓存设置
python config_helper.py --optimize-cache
```

### 🔋 电源管理
```powershell
# 设置为高性能模式
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c

# 关闭USB选择性挂起
powercfg /setacvalueindex SCHEME_CURRENT 2a737441-1930-4402-8d77-b2bebba308a3 48e6b7a6-50f5-4782-a5d4-53bb8f07e226 0
```

## 🔐 安全与隐私

### 🛡️ 数据保护
- **本地处理**: 核心算法本地运行，减少数据传输
- **加密传输**: MQTT和API通信采用TLS加密
- **隐私模式**: 可选择完全离线运行模式
- **数据控制**: 用户完全控制语音数据的存储和使用

### 🔑 安全配置
```python
# 启用安全模式
SECURITY_CONFIG = {
    'encrypt_local_data': True,
    'use_https_only': True,
    'enable_ssl_verification': True,
    'offline_mode': False,  # 完全离线模式
    'data_retention_days': 7  # 数据保留天数
}
```

## 🤝 贡献指南

### 📝 如何贡献

1. **Fork项目** 📌
   ```powershell
   git clone https://github.com/your-username/SHCH.git
   cd SHCH
   ```

2. **创建分支** 🌿
   ```powershell
   git checkout -b feature/amazing-feature
   ```

3. **提交更改** 💾
   ```powershell
   git commit -m "Add amazing feature"
   git push origin feature/amazing-feature
   ```

4. **创建Pull Request** 🚀

### 🐛 问题报告

请包含以下信息：
- 📋 系统信息 (OS, Python版本)
- 🔍 详细错误描述
- 📝 复现步骤
- 📊 相关日志文件

### 💡 功能建议

欢迎提出新功能建议：
- 🎯 描述使用场景
- 💭 提供实现思路
- 🔧 技术可行性分析

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

```
MIT License

Copyright (c) 2024 Smart Home Control Hub

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

## 🙏 致谢

感谢以下开源项目和服务提供商：

| 项目/服务 | 贡献 |
|-----------|------|
| **Python** | 强大的编程语言基础 |
| **OpenAI** | AI语言模型支持 |
| **巴法云** | MQTT物联网平台 |
| **Google Speech API** | 语音识别服务 |
| **百度AI** | 本土化AI服务 |
| **OpenSource Community** | 各种优秀的开源库 |

## 📞 联系我们

- 📧 **邮箱**: [项目邮箱]
- 💬 **QQ群**: [QQ群号]
- 🐦 **微信群**: [微信群二维码]
- 🌐 **官网**: [项目官网]
- 📱 **GitHub**: [GitHub地址]

---

<div align="center">

### 🌟 如果这个项目对您有帮助，请给我们一个 Star ⭐

**让智能家居走进千家万户！**

</div>
