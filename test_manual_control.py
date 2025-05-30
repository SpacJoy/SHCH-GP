# -*- coding: utf-8 -*-
"""
测试手动控制功能修复
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from mqtt_client import control_device
from config import DEVICE_COMMANDS

class MockMQTTClient:
    """模拟MQTT客户端用于测试"""
    def __init__(self):
        self.is_connected = True
        self.published_messages = []
    
    def publish_message(self, topic, command):
        """模拟发布消息"""
        self.published_messages.append((topic, command))
        print(f"✅ 发布消息: 主题={topic}, 指令={command}")
        return True

def test_manual_control():
    """测试手动控制功能"""
    print("=== 测试手动控制功能修复 ===\n")
    
    # 创建模拟MQTT客户端
    mock_client = MockMQTTClient()
    
    # 测试中文设备名称
    test_devices = ["灯", "空调", "电视", "窗帘", "风扇"]
    test_actions = ["on", "off"]
    
    print("1. 测试中文设备名称控制:")
    for device in test_devices:
        for action in test_actions:
            print(f"\n测试: {device} - {action}")
            result = control_device(mock_client, device, action)
            if result:
                print(f"✅ 成功: {device} {action}")
            else:
                print(f"❌ 失败: {device} {action}")
    
    print(f"\n2. 总共发布的消息数量: {len(mock_client.published_messages)}")
    print("\n3. 发布的消息详情:")
    for i, (topic, command) in enumerate(mock_client.published_messages, 1):
        print(f"   {i}. 主题: {topic}, 指令: {command}")
    
    print(f"\n4. 配置的设备:")
    for device in DEVICE_COMMANDS.keys():
        config = DEVICE_COMMANDS[device]
        topics = config['topics']
        print(f"   {device}: 主题={topics}")

if __name__ == "__main__":
    test_manual_control()
