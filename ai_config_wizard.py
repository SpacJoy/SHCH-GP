# -*- coding: utf-8 -*-
"""
AI语音识别配置向导
帮助用户配置各种AI语音识别引擎
"""

import os
import sys
import json
import requests
from datetime import datetime

def show_welcome():
    """显示欢迎信息"""
    print("🤖 AI语音识别配置向导")
    print("=" * 50)
    print("本向导将帮助您配置AI语音识别引擎")
    print("支持的引擎：百度AI、Whisper、Google等")
    print()

def test_baidu_api(app_id, api_key, secret_key):
    """测试百度API配置"""
    try:
        # 获取访问令牌
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            'grant_type': 'client_credentials',
            'client_id': api_key,
            'client_secret': secret_key
        }
        
        print("🔍 正在验证百度API配置...")
        response = requests.get(url, params=params, timeout=10)
        result = response.json()
        
        if 'access_token' in result:
            print("✅ 百度API配置验证成功")
            return True
        else:
            print(f"❌ 百度API配置验证失败: {result.get('error_description', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"❌ 百度API测试失败: {e}")
        return False

def configure_baidu():
    """配置百度AI语音识别"""
    print("🔧 配置百度AI语音识别")
    print("-" * 30)
    print("需要以下信息（在百度AI开放平台获取）:")
    print("1. APP ID")
    print("2. API Key") 
    print("3. Secret Key")
    print()
    print("💡 获取步骤:")
    print("   1. 访问 https://ai.baidu.com/")
    print("   2. 注册并登录")
    print("   3. 创建语音识别应用")
    print("   4. 获取密钥信息")
    print()
    
    app_id = input("请输入 APP ID: ").strip()
    if not app_id:
        print("❌ APP ID 不能为空")
        return None
    
    api_key = input("请输入 API Key: ").strip()
    if not api_key:
        print("❌ API Key 不能为空")
        return None
    
    secret_key = input("请输入 Secret Key: ").strip()
    if not secret_key:
        print("❌ Secret Key 不能为空")
        return None
    
    # 测试配置
    if test_baidu_api(app_id, api_key, secret_key):
        return {
            'engine': 'baidu',
            'baidu': {
                'app_id': app_id,
                'api_key': api_key,
                'secret_key': secret_key,
            }
        }
    else:
        print("❌ 配置验证失败，请检查密钥是否正确")
        return None

def configure_whisper():
    """配置Whisper本地识别"""
    print("🔧 配置Whisper本地识别")
    print("-" * 30)
    
    try:
        import whisper
        print("✅ Whisper已安装")
    except ImportError:
        print("⚠️ Whisper未安装")
        install = input("是否现在安装Whisper? (y/n): ").strip().lower()
        if install == 'y':
            print("📦 正在安装Whisper...")
            os.system("pip install openai-whisper")
            try:
                import whisper
                print("✅ Whisper安装成功")
            except ImportError:
                print("❌ Whisper安装失败")
                return None
        else:
            return None
    
    print("\n可用的模型大小:")
    print("1. tiny   - 最小最快，准确率较低")
    print("2. base   - 平衡选择（推荐）")
    print("3. small  - 较好准确率")
    print("4. medium - 高准确率，较慢")
    print("5. large  - 最高准确率，最慢")
    
    choice = input("\n请选择模型 (1-5，默认2): ").strip()
    model_map = {'1': 'tiny', '2': 'base', '3': 'small', '4': 'medium', '5': 'large'}
    model_size = model_map.get(choice, 'base')
    
    print(f"📥 准备下载 {model_size} 模型...")
    try:
        model = whisper.load_model(model_size)
        print(f"✅ {model_size} 模型加载成功")
        
        return {
            'engine': 'whisper',
            'whisper': {
                'model_size': model_size,
                'local': True,
            }
        }
    except Exception as e:
        print(f"❌ 模型加载失败: {e}")
        return None

def configure_google():
    """配置Google识别（默认）"""
    print("🔧 配置Google语音识别")
    print("-" * 30)
    print("Google识别使用免费服务，无需额外配置")
    print("⚠️ 注意：可能有频率限制，稳定性一般")
    
    return {
        'engine': 'google'
    }

def update_config_file(ai_config):
    """更新配置文件"""
    config_path = os.path.join('src', 'config.py')
    
    if not os.path.exists(config_path):
        print(f"❌ 配置文件不存在: {config_path}")
        return False
    
    try:
        # 读取现有配置
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找AI_SPEECH_CONFIG的位置
        start_marker = "AI_SPEECH_CONFIG = {"
        end_marker = "}"
        
        start_pos = content.find(start_marker)
        if start_pos == -1:
            print("❌ 未找到AI_SPEECH_CONFIG配置段")
            return False
        
        # 查找配置段的结束位置
        brace_count = 0
        end_pos = start_pos
        in_config = False
        
        for i, char in enumerate(content[start_pos:], start_pos):
            if char == '{':
                brace_count += 1
                in_config = True
            elif char == '}':
                brace_count -= 1
                if in_config and brace_count == 0:
                    end_pos = i + 1
                    break
        
        # 生成新的配置内容
        new_config = "AI_SPEECH_CONFIG = " + json.dumps(ai_config, indent=4, ensure_ascii=False)
        
        # 替换配置段
        new_content = content[:start_pos] + new_config + content[end_pos:]
        
        # 备份原文件
        backup_path = config_path + f".backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"📋 原配置已备份到: {backup_path}")
        
        # 写入新配置
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ 配置已更新到: {config_path}")
        return True
        
    except Exception as e:
        print(f"❌ 更新配置文件失败: {e}")
        return False

def main():
    """主函数"""
    show_welcome()
    
    print("请选择要配置的AI引擎:")
    print("1. 百度AI语音识别（推荐，高精度）")
    print("2. Whisper本地识别（离线可用）")
    print("3. Google识别（默认，免费但有限制）")
    print("4. 查看当前配置")
    print("5. 退出")
    
    while True:
        choice = input("\n请选择 (1-5): ").strip()
        
        if choice == '1':
            config = configure_baidu()
            if config:
                if update_config_file(config):
                    print("\n🎉 百度AI配置完成！")
                    print("请重新启动程序以使用新配置")
                break
            else:
                continue
                
        elif choice == '2':
            config = configure_whisper()
            if config:
                if update_config_file(config):
                    print("\n🎉 Whisper配置完成！")
                    print("请重新启动程序以使用新配置")
                break
            else:
                continue
                
        elif choice == '3':
            config = configure_google()
            if update_config_file(config):
                print("\n🎉 Google配置完成！")
                print("请重新启动程序以使用新配置")
            break
            
        elif choice == '4':
            # 显示当前配置
            try:
                sys.path.insert(0, 'src')
                from config import AI_SPEECH_CONFIG
                print("\n📋 当前AI语音配置:")
                print(json.dumps(AI_SPEECH_CONFIG, indent=2, ensure_ascii=False))
            except Exception as e:
                print(f"❌ 读取配置失败: {e}")
            continue
            
        elif choice == '5':
            print("👋 退出配置向导")
            break
            
        else:
            print("❌ 无效选择，请重新输入")
            continue

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 配置被用户中断")
    except Exception as e:
        print(f"\n💥 配置过程出现错误: {e}")
    
    input("\n按回车键退出...")
