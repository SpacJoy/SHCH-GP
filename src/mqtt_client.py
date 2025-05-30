# -*- coding: utf-8 -*-
"""
MQTT通信模块
用于与巴法云进行MQTT通信
"""

import paho.mqtt.client as mqtt
from datetime import datetime
from config import MQTT_CONFIG, MQTT_TOPICS

class MQTTClient:
    def __init__(self, on_message_callback=None):
        # 验证配置
        if not self._validate_config():
            raise ValueError("MQTT配置无效，请检查config.py中的配置信息")
        
        self.client = mqtt.Client(MQTT_CONFIG['client_id'])
        
        # 根据配置决定是否设置用户名密码
        if self._should_use_credentials():
            print(f"✅ 使用私钥登录模式 (client_id: {MQTT_CONFIG['client_id']})")
        else:
            self.client.username_pw_set(MQTT_CONFIG['username'], MQTT_CONFIG['password'])
            print(f"✅ 使用账号密码登录模式")
        
        # 设置回调函数
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        self.on_message_callback = on_message_callback
        self.is_connected = False
        self.message_log = []
        
    def _validate_config(self):
        """验证MQTT配置是否有效"""
        required_fields = ['client_id', 'broker', 'port']
        for field in required_fields:
            if field not in MQTT_CONFIG:
                print(f"❌ 配置错误：缺少必需字段 '{field}'")
                return False
        
        # 检查client_id是否为占位符
        if MQTT_CONFIG['client_id'].startswith('your_'):
            print(f"❌ 配置错误：请替换client_id中的占位符为实际值")
            print(f"   当前值: {MQTT_CONFIG['client_id']}")
            return False
        
        # 如果使用传统登录模式，检查用户名密码
        if MQTT_CONFIG.get('use_private_key', True) == False:
            if (MQTT_CONFIG.get('username', '').startswith('your_') or 
                MQTT_CONFIG.get('password', '').startswith('your_')):
                print(f"❌ 配置错误：传统登录模式需要有效的用户名和密码")
                return False
        
        print(f"✅ MQTT配置验证通过")
        print(f"   服务器: {MQTT_CONFIG['broker']}:{MQTT_CONFIG['port']}")
        return True
    
    def _should_use_credentials(self):
        """判断是否需要使用用户名密码"""
        # 如果明确设置不使用私钥，则使用用户名密码
        if MQTT_CONFIG.get('use_private_key', True) == False:
            return True
        
        # 如果用户名密码不为空且不是占位符，则使用用户名密码
        username = MQTT_CONFIG.get('username', '')
        password = MQTT_CONFIG.get('password', '')
        
        if (username and not username.startswith('your_') and 
            password and not password.startswith('your_')):
            return True
        
        # 否则使用私钥模式（不设置用户名密码）
        return False
        
    def on_connect(self, client, userdata, flags, rc):
        """连接回调"""
        if rc == 0:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] MQTT连接成功")
            self.is_connected = True
            # 订阅所有设备主题
            for topic in MQTT_TOPICS.values():
                client.subscribe(topic)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 订阅主题: {topic}")
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] MQTT连接失败，错误代码: {rc}")
            self.is_connected = False
    
    def on_message(self, client, userdata, msg):
        """消息接收回调"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            message_info = {
                'timestamp': timestamp,
                'topic': topic,
                'payload': payload,
                'type': 'received'
            }
            
            self.message_log.append(message_info)
            print(f"[{timestamp}] 收到消息 - 主题: {topic}, 内容: {payload}")
            
            # 调用外部回调函数
            # if self.on_message_callback:
            #     self.on_message_callback(message_info)
                
        except Exception as e:
            print(f"处理接收消息时出错: {e}")
    
    def on_disconnect(self, client, userdata, rc):
        """断开连接回调"""
        self.is_connected = False
        print(f"[{datetime.now().strftime('%H:%M:%S')}] MQTT连接断开")
    
    def connect(self):
        """连接到MQTT服务器"""
        try:
            self.client.connect(MQTT_CONFIG['broker'], MQTT_CONFIG['port'], MQTT_CONFIG['keep_alive'])
            self.client.loop_start()
            return True
        except Exception as e:
            print(f"MQTT连接错误: {e}")
            return False
    
    def disconnect(self):
        """断开MQTT连接"""
        if self.is_connected:
            self.client.loop_stop()
            self.client.disconnect()
    
    def publish_message(self, topic, message):
        """发布消息"""
        if not self.is_connected:
            print("MQTT未连接，无法发送消息")
            return False
        
        try:
            result = self.client.publish(topic, message)
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            message_info = {
                'timestamp': timestamp,
                'topic': topic,
                'payload': message,
                'type': 'sent'
            }
            
            self.message_log.append(message_info)
            
            if result.rc == 0:
                print(f"[{timestamp}] 发送消息成功 - 主题: {topic}, 内容: {message}")
                return True
            else:
                print(f"[{timestamp}] 发送消息失败 - 主题: {topic}, 错误代码: {result.rc}")
                return False
                
        except Exception as e:
            print(f"发送消息时出错: {e}")
            return False
    
    def get_message_log(self):
        """获取消息日志"""
        return self.message_log.copy()
    
    def clear_message_log(self):
        """清空消息日志"""
        self.message_log.clear()

# 设备控制函数
def control_device(mqtt_client, device_type, action, room=None):
    """
    控制设备
    :param mqtt_client: MQTT客户端实例
    :param device_type: 设备类型 (支持中文和英文，如: '灯'/'light', '空调'/'aircon', '电视'/'tv')
    :param action: 操作 ('on' 或 'off')
    :param room: 房间 (可选，如: 'living_room', 'bedroom')
    """
    if not mqtt_client.is_connected:
        return False
    
    # 导入设备配置
    from config import DEVICE_COMMANDS
    
    # 中文设备名称到英文的映射
    device_name_map = {
        '灯': 'light',
        '空调': 'aircon', 
        '电视': 'tv',
        '窗帘': 'curtain',
        '风扇': 'fan'
    }
    
    # 如果是中文设备名称，先转换为英文
    if device_type in device_name_map:
        english_device = device_name_map[device_type]
    else:
        english_device = device_type
    
    # 如果在DEVICE_COMMANDS中有配置，优先使用配置
    if device_type in DEVICE_COMMANDS:
        device_config = DEVICE_COMMANDS[device_type]
        topics = device_config['topics']
        
        if action == 'on':
            commands = device_config['on_commands']
        elif action == 'off':
            commands = device_config['off_commands']
        else:
            return False
        
        # 使用第一个主题和第一个指令
        if topics and commands:
            topic = topics[0]
            command = commands[0]
            return mqtt_client.publish_message(topic, command)
    
    # 回退到原来的英文映射逻辑
    topic_map = {
        'light': {
            'living_room': 'light001',
            'bedroom': 'light002',
            'default': 'light001'
        },
        'aircon': {'default': 'aircon001'},
        'tv': {'default': 'tv001'},
        'curtain': {'default': 'curtain001'},
        'fan': {'default': 'fan001'}
    }
    
    if english_device in topic_map:
        if room and room in topic_map[english_device]:
            topic = topic_map[english_device][room]
        else:
            topic = topic_map[english_device]['default']
        
        # 发送控制指令
        command = '1' if action == 'on' else '0'
        return mqtt_client.publish_message(topic, command)
    
    return False
