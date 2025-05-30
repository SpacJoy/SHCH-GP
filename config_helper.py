# -*- coding: utf-8 -*-
"""
巴法云MQTT配置助手
帮助用户快速配置MQTT连接参数
"""

import os
import sys

def print_banner():
    """打印欢迎界面"""
    print("=" * 60)
    print("    智能家居系统 - 巴法云MQTT配置助手")
    print("=" * 60)
    print()

def print_login_methods():
    """显示登录方式说明"""
    print("📋 支持的登录方式：")
    print()
    print("方式1：私钥登录（推荐）")
    print("  ✅ 简单便捷，只需要私钥")
    print("  ✅ 无需记住用户名密码")
    print("  ✅ 更安全的认证方式")
    print()
    print("方式2：传统账号密码登录")
    print("  ⚠️  需要提供完整的账号信息")
    print("  ⚠️  需要客户端ID、用户名、密码")
    print()

def configure_private_key_login():
    """配置私钥登录"""
    print("🔑 配置私钥登录")
    print("-" * 40)
    print("请从巴法云控制台获取您的私钥（Secret Key）")
    print("通常是一个较长的字符串，例如：abcd1234efgh5678...")
    print()
    
    private_key = input("请输入您的私钥: ").strip()
    
    if not private_key:
        print("❌ 私钥不能为空！")
        return None
    
    if private_key.startswith('your_'):
        print("❌ 请输入实际的私钥，不要使用占位符！")
        return None
    
    config = {
        'client_id': private_key,
        'username': '',
        'password': '',
        'use_private_key': True
    }
    
    print(f"✅ 私钥配置完成！")
    print(f"   私钥: {private_key[:10]}...")
    return config

def configure_traditional_login():
    """配置传统账号密码登录"""
    print("👤 配置传统账号密码登录")
    print("-" * 40)
    
    client_id = input("请输入客户端ID: ").strip()
    username = input("请输入用户名: ").strip()
    password = input("请输入密码: ").strip()
    
    if not all([client_id, username, password]):
        print("❌ 所有字段都必须填写！")
        return None
    
    if any(field.startswith('your_') for field in [client_id, username, password]):
        print("❌ 请输入实际值，不要使用占位符！")
        return None
    
    config = {
        'client_id': client_id,
        'username': username,
        'password': password,
        'use_private_key': False
    }
    
    print(f"✅ 传统登录配置完成！")
    print(f"   客户端ID: {client_id}")
    print(f"   用户名: {username}")
    return config

def update_config_file(config):
    """更新配置文件"""
    config_path = os.path.join('src', 'config.py')
    
    if not os.path.exists(config_path):
        print(f"❌ 配置文件不存在: {config_path}")
        return False
    
    try:
        # 读取原始配置文件
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 更新MQTT配置部分
        lines = content.split('\n')
        new_lines = []
        in_mqtt_config = False
        
        for line in lines:
            if 'MQTT_CONFIG = {' in line:
                in_mqtt_config = True
                new_lines.append(line)
                new_lines.append("    'broker': 'bemfa.com',  # 巴法云MQTT服务器地址")
                new_lines.append("    'port': 9501,           # 巴法云MQTT端口")
                new_lines.append(f"    'client_id': '{config['client_id']}',  # 巴法云私钥或客户端ID")
                new_lines.append(f"    'username': '{config['username']}',    # 用户名")
                new_lines.append(f"    'password': '{config['password']}',    # 密码")
                new_lines.append("    'keep_alive': 60,")
                new_lines.append(f"    'use_private_key': {config['use_private_key']}  # 是否使用私钥登录")
            elif in_mqtt_config and line.strip() == '}':
                in_mqtt_config = False
                new_lines.append(line)
            elif not in_mqtt_config:
                new_lines.append(line)
        
        # 写入更新后的配置
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print(f"✅ 配置文件已更新: {config_path}")
        return True
        
    except Exception as e:
        print(f"❌ 更新配置文件失败: {e}")
        return False

def test_config():
    """测试配置"""
    print("\n🧪 测试MQTT配置...")
    
    try:
        # 临时导入配置
        sys.path.insert(0, 'src')
        from config import MQTT_CONFIG
        
        print(f"✅ 配置加载成功")
        print(f"   服务器: {MQTT_CONFIG['broker']}:{MQTT_CONFIG['port']}")
        print(f"   客户端ID: {MQTT_CONFIG['client_id']}")
        
        if MQTT_CONFIG.get('use_private_key', True):
            print(f"   登录方式: 私钥登录")
        else:
            print(f"   登录方式: 账号密码登录")
            print(f"   用户名: {MQTT_CONFIG['username']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

def main():
    """主函数"""
    print_banner()
    print_login_methods()
    
    while True:
        print("请选择登录方式：")
        print("1. 私钥登录（推荐）")
        print("2. 传统账号密码登录")
        print("3. 退出")
        print()
        
        choice = input("请输入选择 (1-3): ").strip()
        
        if choice == '1':
            config = configure_private_key_login()
            if config:
                if update_config_file(config):
                    test_config()
                    print("\n🎉 配置完成！现在可以运行系统了。")
                    break
        elif choice == '2':
            config = configure_traditional_login()
            if config:
                if update_config_file(config):
                    test_config()
                    print("\n🎉 配置完成！现在可以运行系统了。")
                    break
        elif choice == '3':
            print("👋 再见！")
            break
        else:
            print("❌ 无效选择，请重新输入！")
        
        print()

if __name__ == "__main__":
    main()
