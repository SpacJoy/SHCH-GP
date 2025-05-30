# -*- coding: utf-8 -*-
"""
语音识别模块
使用AI模型进行语音识别（支持多种AI引擎）
"""

import speech_recognition as sr
import threading
import time
from datetime import datetime
from config import SPEECH_CONFIG, AI_SPEECH_CONFIG

class SpeechRecognizer:
    def __init__(self, on_speech_callback=None):
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            self.is_listening = False
            self.listen_thread = None
            self.on_speech_callback = on_speech_callback
            
            # 调整麦克风噪音
            print("正在调整麦克风噪音，请保持安静...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
            print("麦克风噪音调整完成")
        except ModuleNotFoundError as e:
            if "distutils" in str(e):
                error_msg = """
❌ Python 3.12兼容性问题: distutils模块未找到
📋 解决方案:
1. 运行 install.bat 重新安装依赖（会自动安装setuptools）
2. 或手动执行: pip install setuptools>=65.0.0
3. 然后重新启动程序
"""
                print(error_msg)
                raise RuntimeError("需要安装setuptools以兼容Python 3.12+") from e
            else:
                raise e
        except Exception as e:
            print(f"❌ 语音识别模块初始化失败: {e}")
            raise e
    
    def start_listening(self):
        """开始语音监听"""
        if not self.is_listening:
            self.is_listening = True
            self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.listen_thread.start()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 开始语音监听...")
    
    def stop_listening(self):
        """停止语音监听"""
        self.is_listening = False
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=2)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 停止语音监听")
    
    def _listen_loop(self):
        """语音监听循环"""
        while self.is_listening:
            try:
                # 监听音频
                with self.microphone as source:
                    # 设置超时时间，避免长时间阻塞
                    audio = self.recognizer.listen(
                        source, 
                        timeout=SPEECH_CONFIG['timeout'],
                        phrase_time_limit=SPEECH_CONFIG['phrase_timeout']
                    )
                
                # 识别语音
                text = self.recognizer.recognize_google(
                    audio, 
                    language=SPEECH_CONFIG['language']
                )
                
                if text:
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    print(f"[{timestamp}] 识别到语音: {text}")
                    
                    # 调用回调函数
                    if self.on_speech_callback:
                        self.on_speech_callback(text, timestamp)
                        
            except sr.WaitTimeoutError:
                # 超时，继续监听
                pass
            except sr.UnknownValueError:
                # 无法识别语音
                pass
            except sr.RequestError as e:
                print(f"语音识别服务错误: {e}")
                time.sleep(1)  # 等待一秒后重试
            except Exception as e:
                print(f"语音识别出错: {e}")
                time.sleep(1)
    
    def recognize_once(self, timeout=5):
        """单次语音识别"""
        try:
            with self.microphone as source:
                print("请说话...")
                audio = self.recognizer.listen(source, timeout=timeout)
            
            text = self.recognizer.recognize_google(audio, language=SPEECH_CONFIG['language'])
            return text
            
        except sr.WaitTimeoutError:
            return "超时，未检测到语音"
        except sr.UnknownValueError:
            return "无法识别语音内容"
        except sr.RequestError as e:
            return f"语音识别服务错误: {e}"
        except Exception as e:
            return f"识别出错: {e}"
    
    def is_microphone_available(self):
        """检查麦克风是否可用"""
        try:
            with self.microphone as source:
                pass
            return True
        except Exception as e:
            print(f"麦克风不可用: {e}")
            return False
