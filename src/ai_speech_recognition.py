# -*- coding: utf-8 -*-
"""
AI语音识别模块
支持多种AI语音识别引擎：百度、Whisper、Azure等
支持唤醒词功能，避免频繁调用AI识别
"""

import speech_recognition as sr
import tempfile
import os
# import whisper
import requests
import base64
from datetime import datetime
from config import SPEECH_CONFIG, AI_SPEECH_CONFIG, WAKE_WORD_CONFIG

class AISpeechRecognizer:
    def __init__(self, status_callback=None):
        """初始化AI语音识别器
        
        Args:
            status_callback: 状态回调函数，用于更新GUI状态显示
        """
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            self.is_listening = False
            self.listen_thread = None
            self.status_callback = status_callback
            self.engine = AI_SPEECH_CONFIG.get('engine', 'baidu')
            
            # 唤醒词相关属性
            self.wake_word_enabled = WAKE_WORD_CONFIG.get('enabled', True)
            self.wake_words = WAKE_WORD_CONFIG.get('keywords', ['小智'])
            self.wake_word_timeout = WAKE_WORD_CONFIG.get('timeout', 3)
            self.command_timeout = WAKE_WORD_CONFIG.get('command_timeout', 10)
            self.wake_sensitivity = WAKE_WORD_CONFIG.get('sensitivity', 0.7)
            
            # 高级唤醒词配置
            self.fallback_detection = WAKE_WORD_CONFIG.get('fallback_detection', True)
            self.confidence_threshold = WAKE_WORD_CONFIG.get('confidence_threshold', 0.6)
            self.retry_count = WAKE_WORD_CONFIG.get('retry_count', 3)
            self.audio_feedback = WAKE_WORD_CONFIG.get('audio_feedback', True)
            self.adaptive_threshold = WAKE_WORD_CONFIG.get('adaptive_threshold', True)
            self.noise_reduction = WAKE_WORD_CONFIG.get('noise_reduction', True)
            
            # 动态调整参数
            self.dynamic_energy_threshold = WAKE_WORD_CONFIG.get('energy_threshold', 300)
            self.background_noise_samples = []
            self.wake_word_detections = 0
            self.false_positives = 0
            
            # 更新状态
            self._update_status("正在初始化语音识别...")
            
            # 调整麦克风噪音
            self._update_status("正在调整麦克风，请保持安静...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                # 设置能量阈值
                self.recognizer.energy_threshold = WAKE_WORD_CONFIG.get('energy_threshold', 300)
            
            # 初始化AI引擎
            self._init_ai_engine()
            
            wake_status = "已启用" if self.wake_word_enabled else "已禁用"
            wake_words_str = "、".join(self.wake_words)
            self._update_status(f"语音识别初始化完成，唤醒词功能{wake_status}，支持唤醒词：{wake_words_str}")
            
        except ModuleNotFoundError as e:
            if "distutils" in str(e):
                error_msg = "需要安装setuptools以兼容Python 3.12+"
                self._update_status(f"错误: {error_msg}")
                raise RuntimeError(error_msg) from e
            else:
                raise e
        except Exception as e:
            error_msg = f"语音识别模块初始化失败: {e}"
            self._update_status(f"错误: {error_msg}")
            raise e
    
    def _init_ai_engine(self):
        """初始化AI识别引擎"""
        if self.engine == 'baidu':
            self._init_baidu_engine()
        elif self.engine == 'whisper':
            self._init_whisper_engine()
        else:
            self._update_status(f"使用默认引擎: {self.engine}")
    
    def _init_baidu_engine(self):
        """初始化百度语音识别引擎"""
        config = AI_SPEECH_CONFIG.get('baidu', {})
        self.baidu_app_id = config.get('app_id', '')
        self.baidu_api_key = config.get('api_key', '')
        self.baidu_secret_key = config.get('secret_key', '')
        
        if not all([self.baidu_app_id, self.baidu_api_key, self.baidu_secret_key]):
            self._update_status("警告: 百度语音识别未配置，将使用默认引擎")
            self.engine = 'google'
        else:
            self._update_status("百度语音识别引擎已配置")
    
    def _init_whisper_engine(self):
        """初始化Whisper引擎"""
        try:
            model_size = AI_SPEECH_CONFIG.get('whisper', {}).get('model_size', 'base')
            self.whisper_model = whisper.load_model(model_size) # type: ignore
            self._update_status(f"Whisper {model_size} 模型加载完成")
        except ImportError:
            self._update_status("Whisper未安装，将使用默认引擎")
            self.engine = 'google'
        except Exception as e:
            self._update_status(f"Whisper加载失败: {e}")
            self.engine = 'google'
    
    def _update_status(self, message):
        """更新状态显示"""
        if self.status_callback:
            self.status_callback(message)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
    
    def listen_continuous(self):
        """持续语音监听（单次调用）"""
        try:
            self._update_status("🎤 正在监听语音...")
            
            with self.microphone as source:
                # 监听音频
                audio = self.recognizer.listen(
                    source, 
                    timeout=SPEECH_CONFIG['timeout'],
                    phrase_time_limit=SPEECH_CONFIG['phrase_timeout']
                )
            
            self._update_status("🔄 正在识别语音...")
            
            # 使用AI模型识别语音
            text = self._recognize_with_ai(audio)
            
            if text and text.strip(): # type: ignore
                self._update_status(f"✅ 识别结果: {text}")
                return text
            else:
                self._update_status("⚠️ 未识别到有效语音")
                return None
                
        except sr.WaitTimeoutError:
            # 超时，正常情况
            return None
        except sr.UnknownValueError:
            self._update_status("⚠️ 语音不清晰，请重新说话")
            return None
        except sr.RequestError as e:
            self._update_status(f"❌ 识别服务错误: {e}")
            return None
        except Exception as e:
            self._update_status(f"❌ 识别异常: {e}")
            return None
    
    def recognize_once(self, timeout=5):
        """单次语音识别"""
        try:
            self._update_status("🎤 请开始说话...")
            
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=5)
            
            self._update_status("🔄 正在使用AI模型识别...")
            
            # 使用AI模型识别
            text = self._recognize_with_ai(audio)
            
            if text and text.strip(): # type: ignore
                self._update_status(f"✅ 识别成功: {text}")
                return text
            else:
                self._update_status("⚠️ 未识别到有效内容")
                return None
                
        except sr.WaitTimeoutError:
            self._update_status("⏰ 等待超时，未检测到语音")
            return None
        except sr.UnknownValueError:
            self._update_status("⚠️ 无法识别语音内容")
            return None
        except sr.RequestError as e:
            self._update_status(f"❌ 识别服务错误: {e}")
            return None
        except Exception as e:
            self._update_status(f"❌ 识别出错: {e}")
            return None
    
    def _recognize_with_ai(self, audio):
        """使用AI模型识别语音"""
        if self.engine == 'baidu' and hasattr(self, 'baidu_api_key'):
            return self._recognize_with_baidu(audio)
        elif self.engine == 'whisper' and hasattr(self, 'whisper_model'):
            return self._recognize_with_whisper(audio)
        else:
            # 默认使用Google识别
            return self._recognize_with_google(audio)
    
    def _recognize_with_baidu(self, audio):
        """使用百度AI识别"""
        try:
            # 获取访问令牌
            token = self._get_baidu_token()
            if not token:
                return self._recognize_with_google(audio)
            
            # 转换音频格式
            wav_data = audio.get_wav_data()
            
            # 调用百度API
            url = f"https://vop.baidu.com/server_api"
            headers = {'Content-Type': 'application/json'}
            
            data = {
                'format': 'wav',
                'rate': 16000,
                'channel': 1,
                'cuid': 'python_client',
                'token': token,
                'speech': base64.b64encode(wav_data).decode('utf-8'),
                'len': len(wav_data)
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=10)
            result = response.json()
            
            if result.get('err_no') == 0:
                return result.get('result', [''])[0]
            else:
                self._update_status(f"百度识别错误: {result.get('err_msg', '未知错误')}")
                return self._recognize_with_google(audio)
                
        except Exception as e:
            self._update_status(f"百度识别异常: {e}")
            return self._recognize_with_google(audio)
    
    def _get_baidu_token(self):
        """获取百度访问令牌"""
        try:
            url = "https://aip.baidubce.com/oauth/2.0/token"
            params = {
                'grant_type': 'client_credentials',
                'client_id': self.baidu_api_key,
                'client_secret': self.baidu_secret_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            result = response.json()
            
            return result.get('access_token')
        except Exception as e:
            self._update_status(f"获取百度令牌失败: {e}")
            return None
    
    def _recognize_with_whisper(self, audio):
        """使用Whisper模型识别"""
        try:
            # 保存音频到临时文件
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_file.write(audio.get_wav_data())
                tmp_path = tmp_file.name
            
            # 使用Whisper识别
            result = self.whisper_model.transcribe(tmp_path, language='zh')
            
            # 清理临时文件
            os.unlink(tmp_path)
            
            return result.get('text', '').strip() # type: ignore
            
        except Exception as e:
            self._update_status(f"Whisper识别异常: {e}")
            return self._recognize_with_google(audio)
    
    def _recognize_with_google(self, audio):
        """使用Google识别（备用）"""
        try:
            return self.recognizer.recognize_google(audio, language=SPEECH_CONFIG['language'])
        except Exception as e:
            self._update_status(f"Google识别失败: {e}")
            return None
    
    def is_microphone_available(self):
        """检查麦克风是否可用"""
        try:
            with self.microphone as source:
                pass
            return True
        except Exception as e:
            self._update_status(f"麦克风不可用: {e}")
            return False
    
    def listen_with_wake_word(self):
        """带唤醒词的持续监听（单次调用）"""
        if not self.wake_word_enabled:
            # 如果唤醒词未启用，直接进行正常识别
            return self.listen_continuous()
        
        try:
            # 第一阶段：检测唤醒词
            wake_detected = self._detect_wake_word()
            if not wake_detected:
                return None
            
            # 第二阶段：识别具体命令
            self._update_status("🟢 检测到唤醒词，请说出您的指令...")
            command = self._listen_for_command()
            return command
            
        except Exception as e:
            self._update_status(f"❌ 唤醒词检测异常: {e}")
            return None
    
    def _detect_wake_word(self):
        """检测唤醒词"""
        try:
            self._update_status("👂 等待唤醒词...")
            
            with self.microphone as source:
                # 监听音频，使用较短的超时时间
                audio = self.recognizer.listen(
                    source, 
                    timeout=self.wake_word_timeout,
                    phrase_time_limit=WAKE_WORD_CONFIG.get('phrase_timeout', 2)
                )
            
            # 使用轻量级识别检测唤醒词（使用Google引擎，速度快）
            try:
                text = self.recognizer.recognize_google(audio, language=SPEECH_CONFIG['language'])
                if text:
                    self._update_status(f"🔍 检测内容: {text}")
                    return self._check_wake_word_match(text)
            except sr.UnknownValueError:
                # 无法识别，继续等待
                return False
            except sr.RequestError:
                # 网络错误，尝试本地检测
                return self._simple_wake_word_check(audio) # type: ignore
                
        except sr.WaitTimeoutError:
            # 超时，正常情况
            return False
        except Exception as e:
            self._update_status(f"⚠️ 唤醒词检测出错: {e}")
            return False
    
    def _check_wake_word_match(self, text):
        """检查文本是否包含唤醒词"""
        text_lower = text.lower()
        for wake_word in self.wake_words:
            if wake_word.lower() in text_lower:
                self._update_status(f"✅ 检测到唤醒词: {wake_word}")
                self.wake_word_detections += 1
                self._adaptive_threshold_adjustment(True)
                
                # 音频反馈
                if self.audio_feedback:
                    self._play_wake_word_feedback()
                
                return True
        
        # 如果没有检测到唤醒词，可能是误检
        if len(text_lower) > 0:
            self.false_positives += 1
            self._adaptive_threshold_adjustment(False)
            
        return False
    
    def _adaptive_threshold_adjustment(self, wake_word_detected):
        """自适应阈值调整"""
        if not self.adaptive_threshold:
            return
            
        try:
            if wake_word_detected:
                # 检测到唤醒词，可以适当降低阈值以提高灵敏度
                if self.dynamic_energy_threshold > 200:
                    self.dynamic_energy_threshold *= 0.95
            else:
                # 误检，提高阈值以减少误报
                if self.dynamic_energy_threshold < 500:
                    self.dynamic_energy_threshold *= 1.05
            
            # 更新识别器阈值
            self.recognizer.energy_threshold = self.dynamic_energy_threshold
            
        except Exception as e:
            self._update_status(f"阈值调整出错: {e}")
    
    def _play_wake_word_feedback(self):
        """播放唤醒词检测反馈音效"""
        try:
            # 这里可以添加系统提示音或自定义音效
            # 由于避免依赖额外库，暂时使用系统beep
            import winsound
            winsound.Beep(800, 200)  # 800Hz, 200ms
        except ImportError:
            # 如果winsound不可用，跳过音效
            pass
        except Exception:
            # 忽略音效播放错误
            pass
    
    def get_wake_word_stats(self):
        """获取唤醒词检测统计信息"""
        return {
            'detections': self.wake_word_detections,
            'false_positives': self.false_positives,
            'current_threshold': self.dynamic_energy_threshold,
            'detection_rate': self.wake_word_detections / max(1, self.wake_word_detections + self.false_positives)
        }
    
    def reset_wake_word_stats(self):
        """重置唤醒词统计"""
        self.wake_word_detections = 0
        self.false_positives = 0
        self.dynamic_energy_threshold = WAKE_WORD_CONFIG.get('energy_threshold', 300)
    
    def _listen_for_command(self):
        """监听用户命令"""
        try:
            with self.microphone as source:
                # 监听用户命令，使用较长的超时时间
                audio = self.recognizer.listen(
                    source, 
                    timeout=self.command_timeout,
                    phrase_time_limit=8
                )
            
            self._update_status("🔄 正在识别指令...")
            
            # 使用AI模型识别用户命令
            text = self._recognize_with_ai(audio)
            
            if text and text.strip(): # type: ignore
                self._update_status(f"✅ 识别到指令: {text}")
                return text
            else:
                self._update_status("⚠️ 未识别到有效指令")
                return None
                
        except sr.WaitTimeoutError:
            self._update_status("⏰ 等待指令超时")
            return None
        except Exception as e:
            self._update_status(f"❌ 指令识别异常: {e}")
            return None

# 为了兼容性，保留原来的类名
class SpeechRecognizer(AISpeechRecognizer):
    """兼容性别名"""
    pass
