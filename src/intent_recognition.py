# -*- coding: utf-8 -*-
"""
意图识别模块
分析用户语音指令并识别意图
"""

import re
from config import DEVICE_COMMANDS, ACTION_KEYWORDS

class IntentRecognizer:
    def __init__(self):
        self.device_patterns = self._build_device_patterns()
        self.action_patterns = self._build_action_patterns()
    
    def _build_device_patterns(self):
        """构建设备识别模式"""
        patterns = {}
        for device, config in DEVICE_COMMANDS.items():
            keywords = config['keywords']
            pattern = '|'.join(keywords)
            patterns[device] = re.compile(f'({pattern})', re.IGNORECASE)
        return patterns
    
    def _build_action_patterns(self):
        """构建动作识别模式"""
        patterns = {}
        for action, keywords in ACTION_KEYWORDS.items():
            pattern = '|'.join(keywords)
            patterns[action] = re.compile(f'({pattern})', re.IGNORECASE)
        return patterns
    
    def recognize_intent(self, text):
        """
        识别用户意图
        返回: {
            'device': 设备类型,
            'action': 操作类型,
            'room': 房间 (可选),
            'confidence': 置信度,
            'original_text': 原始文本
        }
        """
        result = {
            'device': None,
            'action': None,
            'room': None,
            'confidence': 0.0,
            'original_text': text
        }
        
        # 识别设备
        device_matches = []
        for device, pattern in self.device_patterns.items():
            if pattern.search(text):
                device_matches.append(device)
        
        # 识别动作
        action_matches = []
        for action, pattern in self.action_patterns.items():
            if pattern.search(text):
                action_matches.append(action)
        
        # 识别房间
        room = self._recognize_room(text)
        
        # 确定最终意图
        if device_matches and action_matches:
            result['device'] = device_matches[0]  # 取第一个匹配的设备
            result['action'] = action_matches[0]  # 取第一个匹配的动作
            result['room'] = room
            result['confidence'] = self._calculate_confidence(text, device_matches, action_matches, room)
        
        return result
    
    def _recognize_room(self, text):
        """识别房间"""
        room_keywords = {
            'living_room': ['客厅', '大厅', '起居室'],
            'bedroom': ['卧室', '睡房', '房间'],
            'kitchen': ['厨房'],
            'bathroom': ['浴室', '卫生间', '厕所'],
            'study': ['书房', '工作室']
        }
        
        for room, keywords in room_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return room
        return None
    
    def _calculate_confidence(self, text, device_matches, action_matches, room):
        """计算置信度"""
        base_confidence = 0.5
        
        # 有设备和动作匹配
        if device_matches and action_matches:
            base_confidence += 0.3
        
        # 有房间信息
        if room:
            base_confidence += 0.1
        
        # 文本长度适中 (不太短也不太长)
        if 3 <= len(text) <= 20:
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def get_device_command(self, device, action):
        """
        获取设备控制指令
        返回主题和指令内容
        """
        if device not in DEVICE_COMMANDS:
            return None, None
        
        device_config = DEVICE_COMMANDS[device]
        topics = device_config['topics']
        
        if action == 'on':
            commands = device_config['on_commands']
        elif action == 'off':
            commands = device_config['off_commands']
        else:
            return None, None
        
        # 返回第一个主题和第一个指令
        if topics and commands:
            return topics[0], commands[0]
        
        return None, None
    
    def analyze_speech_text(self, text):
        """
        分析语音文本并返回详细信息
        """
        intent = self.recognize_intent(text)
        analysis = {
            'intent': intent,
            'is_valid': intent['device'] is not None and intent['action'] is not None,
            'device_topic': None,
            'command': None,
            'description': self._generate_description(intent)
        }
        
        if analysis['is_valid']:
            topic, command = self.get_device_command(intent['device'], intent['action'])
            analysis['device_topic'] = topic
            analysis['command'] = command
        
        return analysis
    
    def _generate_description(self, intent):
        """生成意图描述"""
        if not intent['device'] or not intent['action']:
            return "无法识别有效的控制指令"
        
        device_name = intent['device']
        action_desc = "打开" if intent['action'] == 'on' else "关闭"
        room_desc = f"{intent['room']}" if intent['room'] else ""
        
        if room_desc:
            return f"{action_desc}{room_desc}的{device_name}"
        else:
            return f"{action_desc}{device_name}"

# 预定义的常用指令示例
EXAMPLE_COMMANDS = [
    "【唤醒词使用说明】",
    "先说唤醒词：小智、智能助手、小助手、语音助手、你好智能",
    "然后说具体指令：",
    "",
    "【控制指令示例】",
    "打开客厅的灯",
    "关闭卧室的灯",
    "开空调",
    "关空调",
    "打开电视",
    "关闭电视",
    "拉开窗帘",
    "关闭窗帘",
    "开风扇",
    "关风扇",
    "",
    "【完整使用示例】",
    "1. 先说：'小智'",
    "2. 听到提示后说：'打开客厅的灯'"
]
