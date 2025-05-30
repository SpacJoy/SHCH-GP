# -*- coding: utf-8 -*-
"""
智能语音控制家居系统配置文件
"""

# MQTT配置 - 巴法云配置
# 支持两种登录方式：
# 方式1：使用私钥登录（推荐）- 只需填写client_id为你的私钥，username和password可以留空或填any
# 方式2：传统账号密码登录 - 需要填写完整的client_id、username、password
# 
# ⚠️ 重要：请在下面填写你的巴法云私钥或完整登录信息
# 如需配置帮助，请运行 config.bat 或 python config_helper.py
MQTT_CONFIG = {
    'broker': 'bemfa.com',  # 巴法云MQTT服务器地址
    'port': 9501,           # 巴法云MQTT端口
    'client_id': '',  # 请替换为你的巴法云私钥或客户端ID
    'username': 'any',    # 使用私钥时可填any，传统登录时填实际用户名
    'password': 'any',    # 使用私钥时可填any，传统登录时填实际密码
    'keep_alive': 60,
    'use_private_key': True  # 是否使用私钥登录
}

# 主题配置
MQTT_TOPICS = {
    'light_living_room': 'light001',    # 客厅灯光
    'light_bedroom': 'light002',        # 卧室灯光
    'air_conditioner': 'aircon001',     # 空调
    'tv': 'tv001',                      # 电视
    'curtain': 'curtain001',            # 窗帘
    'fan': 'fan001',                    # 风扇
}

# 语音识别配置
SPEECH_CONFIG = {
    'language': 'zh-CN',  # 中文语音识别
    'timeout': 1,         # 超时时间
    'phrase_timeout': 1,  # 短语超时时间
}

# 唤醒词配置
WAKE_WORD_CONFIG = {
    'enabled': True,  # 是否启用唤醒词功能
    'keywords': ['小智', '智能助手','你好小智'],  # 唤醒词列表
    'timeout': 5,  # 唤醒词检测超时时间（秒）
    'phrase_timeout': 2,  # 唤醒词短语超时时间（秒）
    'sensitivity': 0.8,  # 唤醒词匹配敏感度（0-1）
    'command_timeout': 10,  # 检测到唤醒词后，等待命令的超时时间（秒）
    'energy_threshold': 300,  # 音频能量阈值
    'use_lightweight_detection': True,  # 使用轻量级检测模式
    
    # 高级配置
    'fallback_detection': True,  # 启用备用检测机制
    'offline_detection': False,  # 离线检测（需要额外库支持）
    'confidence_threshold': 0.6,  # 唤醒词置信度阈值
    'retry_count': 3,  # 检测失败重试次数
    'audio_feedback': True,  # 音频反馈（检测到唤醒词时播放提示音）
    
    # 性能优化
    'adaptive_threshold': True,  # 自适应能量阈值
    'noise_reduction': True,  # 噪音降低
    'continuous_adjustment': True,  # 持续调整麦克风参数
}

# AI语音识别配置
AI_SPEECH_CONFIG = {
    'engine': 'baidu',  # 可选: 'baidu', 'whisper', 'google', 'azure'
    'baidu': {
        'app_id': '',  # 百度语音识别APP ID
        'api_key': '',  # 百度语音识别API Key
        'secret_key': '',  # 百度语音识别Secret Key
    },
    'whisper': {
        'model_size': 'base',  # 可选: tiny, base, small, medium, large
        'local': True,  # 是否使用本地模型
    },
    'azure': {
        'key': '',  # Azure语音服务密钥
        'region': '',  # Azure服务区域
    },
    'google': {
        'credentials_path': '',  # Google Cloud凭证文件路径
    }
}

# 设备控制指令映射
DEVICE_COMMANDS = {
    '灯': {
        'topics': ['light001', 'light002'],
        'on_commands': ['on', '1'],
        'off_commands': ['off', '0'],
        'keywords': ['灯', '灯光', '照明']
    },
    '空调': {
        'topics': ['aircon001'],
        'on_commands': ['on', '1'],
        'off_commands': ['off', '0'],
        'keywords': ['空调', '制冷', '制热']
    },
    '电视': {
        'topics': ['tv001'],
        'on_commands': ['on', '1'],
        'off_commands': ['off', '0'],
        'keywords': ['电视', 'TV', '电视机']
    },
    '窗帘': {
        'topics': ['curtain001'],
        'on_commands': ['open', '1'],
        'off_commands': ['close', '0'],
        'keywords': ['窗帘', '拉开窗帘', '关闭窗帘']
    },
    '风扇': {
        'topics': ['fan001'],
        'on_commands': ['on', '1'],
        'off_commands': ['off', '0'],
        'keywords': ['风扇', '电扇']
    }
}

# 操作关键词
ACTION_KEYWORDS = {
    'on': ['打开', '开启', '启动', '开', '亮'],
    'off': ['关闭', '关', '熄灭', '停止', '灭']
}

# GUI配置
GUI_CONFIG = {
    'title': '智能语音控制家居系统',
    'width': 800,
    'height': 600,
    'font_family': 'Microsoft YaHei',
    'font_size': 10
}
