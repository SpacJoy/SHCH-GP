# -*- coding: utf-8 -*-
"""
轻量级语音识别模型集成器
将自训练的轻量级模型集成到现有的语音识别系统中
"""

import os
import sys
import numpy as np
import torch
import speech_recognition as sr
from typing import Optional, Dict, Any
import tempfile
import warnings
warnings.filterwarnings("ignore")

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from train.model import LightASRInference, AudioFeatureExtractor
from config import AI_SPEECH_CONFIG, SPEECH_CONFIG

class LightASREngine:
    """
    轻量级ASR引擎
    集成到现有的AI语音识别系统中
    """
    
    def __init__(self, model_path: Optional[str] = None, device: str = 'auto'):
        """
        初始化轻量级ASR引擎
        
        Args:
            model_path: 模型文件路径
            device: 计算设备 ('auto', 'cpu', 'cuda')
        """
        self.model_path = model_path
        
        # 设置设备
        if device == 'auto':
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)
        
        # 初始化推理器
        self.inference = None
        self.is_loaded = False
        self.feature_extractor = AudioFeatureExtractor()
          # 智能家居指令映射 - 扩展到50个类别
        self.command_mapping = {
            # 基本灯光控制
            0: "打开灯", 1: "关闭灯", 2: "调亮灯", 3: "调暗灯",
            4: "打开客厅灯", 5: "关闭客厅灯", 6: "打开卧室灯", 7: "关闭卧室灯",
            8: "打开厨房灯", 9: "关闭厨房灯", 10: "打开台灯", 11: "关闭台灯",
            
            # 空调控制
            12: "打开空调", 13: "关闭空调", 14: "调高温度", 15: "调低温度",
            16: "打开制冷", 17: "打开制热", 18: "调节风速", 19: "设置温度",
            
            # 电视控制
            20: "打开电视", 21: "关闭电视", 22: "调高音量", 23: "调低音量",
            24: "换频道", 25: "静音", 26: "取消静音", 27: "播放",
            
            # 窗帘控制
            28: "打开窗帘", 29: "关闭窗帘", 30: "拉上窗帘", 31: "拉开窗帘",
            
            # 风扇控制
            32: "打开风扇", 33: "关闭风扇", 34: "调节风扇", 35: "风扇加速",
            
            # 音乐控制
            36: "播放音乐", 37: "停止音乐", 38: "暂停音乐", 39: "下一首",
            40: "上一首", 41: "随机播放", 42: "循环播放", 43: "关闭音乐",
            
            # 其他设备
            44: "打开加湿器", 45: "关闭加湿器", 46: "打开净化器", 47: "关闭净化器",
            48: "打开热水器", 49: "关闭热水器"
        }
        
        # 尝试加载模型
        self._load_model()
    
    def _load_model(self):
        """加载模型"""
        try:
            if self.model_path and os.path.exists(self.model_path):
                self.inference = LightASRInference(self.model_path)
                self.is_loaded = True
                print(f"✅ 轻量级ASR模型已加载: {self.model_path}")
            else:
                # 尝试加载默认模型
                default_model_path = os.path.join(
                    os.path.dirname(__file__), 'model', 'best_model.pth'
                )
                if os.path.exists(default_model_path):
                    self.inference = LightASRInference(default_model_path)
                    self.is_loaded = True
                    print(f"✅ 已加载默认轻量级ASR模型: {default_model_path}")
                else:
                    print("⚠️ 未找到轻量级ASR模型，将使用未训练模型")
                    self.inference = LightASRInference()
                    self.is_loaded = False
        except Exception as e:
            print(f"❌ 轻量级ASR模型加载失败: {e}")
            self.inference = None
            self.is_loaded = False
    
    def recognize(self, audio: sr.AudioData) -> Optional[str]:
        """
        识别语音
        
        Args:
            audio: 语音数据
        
        Returns:
            Optional[str]: 识别结果文本
        """
        if not self.inference:
            return None
        
        try:
            # 转换音频格式
            wav_data = audio.get_wav_data()
            
            # 保存到临时文件
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_file.write(wav_data)
                tmp_path = tmp_file.name
            
            try:                # 使用模型进行推理
                result = self.inference.predict_from_file(tmp_path)
                
                # 获取预测结果
                class_pred = result['class_prediction']
                confidence = result['class_confidence']
                
                # 映射到文本 - 降低置信度阈值用于测试
                if class_pred in self.command_mapping and confidence > 0.02:
                    recognized_text = self.command_mapping[class_pred]
                    return recognized_text
                else:
                    return None
                    
            finally:
                # 清理临时文件
                os.unlink(tmp_path)
                
        except Exception as e:
            print(f"❌ 轻量级ASR识别失败: {e}")
            return None

    def recognize_file(self, file_path: str) -> Optional[str]:
        """
        从音频文件识别语音
        
        Args:
            file_path: 音频文件路径
        
        Returns:
            Optional[str]: 识别结果文本
        """
        if not self.inference:
            return None
        
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                print(f"❌ 音频文件不存在: {file_path}")
                return None
              # 直接使用模型进行推理
            result = self.inference.predict_from_file(file_path)
            
            # 获取预测结果
            class_pred = result['class_prediction']
            confidence = result['class_confidence']
            
            # 映射到文本 - 降低置信度阈值用于测试
            if class_pred in self.command_mapping and confidence > 0.02:
                recognized_text = self.command_mapping[class_pred]
                return recognized_text
            else:
                return None
                
        except Exception as e:
            print(f"❌ 轻量级ASR文件识别失败: {e}")
            return None
    
    def is_available(self) -> bool:
        """检查引擎是否可用"""
        return self.inference is not None
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        if not self.inference:
            return {"status": "not_loaded"}
        
        return {
            "status": "loaded" if self.is_loaded else "default",
            "device": str(self.device),
            "model_path": self.model_path,
            "commands": list(self.command_mapping.values())
        }

class EnhancedAISpeechRecognizer:
    """
    增强的AI语音识别器
    集成轻量级本地模型
    """
    
    def __init__(self, status_callback=None, use_light_asr=True):
        """
        初始化增强语音识别器
        
        Args:
            status_callback: 状态回调函数
            use_light_asr: 是否使用轻量级ASR
        """
        # 导入原有的AI语音识别器
        from ai_speech_recognition import AISpeechRecognizer
        
        # 初始化基础识别器
        self.base_recognizer = AISpeechRecognizer(status_callback)
        self.status_callback = status_callback
        
        # 初始化轻量级ASR引擎
        self.light_asr = None
        if use_light_asr:
            try:
                self.light_asr = LightASREngine()
                if self.light_asr.is_available():
                    self._update_status("✅ 轻量级ASR引擎已启用")
                else:
                    self._update_status("⚠️ 轻量级ASR引擎不可用，使用标准引擎")
            except Exception as e:
                self._update_status(f"⚠️ 轻量级ASR初始化失败: {e}")
                self.light_asr = None
        
        # 识别策略配置
        self.recognition_strategy = AI_SPEECH_CONFIG.get('strategy', 'hybrid')
        # 可选: 'light_first', 'standard_first', 'hybrid', 'light_only', 'standard_only'
    
    def _update_status(self, message: str):
        """更新状态"""
        if self.status_callback:
            self.status_callback(message)
        print(f"[Enhanced ASR] {message}")
    
    def _recognize_with_light_asr(self, audio: sr.AudioData) -> Optional[str]:
        """使用轻量级ASR识别"""
        if not self.light_asr or not self.light_asr.is_available():
            return None
        
        try:
            self._update_status("🔬 尝试轻量级ASR识别...")
            result = self.light_asr.recognize(audio)
            if result:
                self._update_status(f"✅ 轻量级ASR识别成功: {result}")
                return result
            else:
                self._update_status("⚠️ 轻量级ASR未识别到内容")
                return None
        except Exception as e:
            self._update_status(f"❌ 轻量级ASR识别异常: {e}")
            return None
    
    def _recognize_with_standard_asr(self, audio: sr.AudioData) -> Optional[str]:
        """使用标准ASR识别"""
        try:
            self._update_status("🌐 使用标准ASR识别...")
            result = self.base_recognizer._recognize_with_ai(audio)
            if result:
                self._update_status(f"✅ 标准ASR识别成功: {result}")
                return result
            else:
                self._update_status("⚠️ 标准ASR未识别到内容")
                return None
        except Exception as e:
            self._update_status(f"❌ 标准ASR识别异常: {e}")
            return None
    
    def recognize_with_strategy(self, audio: sr.AudioData) -> Optional[str]:
        """
        根据策略进行识别
        
        Args:
            audio: 音频数据
        
        Returns:
            Optional[str]: 识别结果
        """
        if self.recognition_strategy == 'light_only':
            # 仅使用轻量级ASR
            return self._recognize_with_light_asr(audio)
            
        elif self.recognition_strategy == 'standard_only':
            # 仅使用标准ASR
            return self._recognize_with_standard_asr(audio)
            
        elif self.recognition_strategy == 'light_first':
            # 优先使用轻量级ASR，失败后使用标准ASR
            result = self._recognize_with_light_asr(audio)
            if result:
                return result
            return self._recognize_with_standard_asr(audio)
            
        elif self.recognition_strategy == 'standard_first':
            # 优先使用标准ASR，失败后使用轻量级ASR
            result = self._recognize_with_standard_asr(audio)
            if result:
                return result
            return self._recognize_with_light_asr(audio)
            
        elif self.recognition_strategy == 'hybrid':
            # 混合策略：对于简单指令使用轻量级，复杂指令使用标准
            # 先尝试轻量级ASR
            light_result = self._recognize_with_light_asr(audio)
            if light_result:
                # 检查是否为智能家居指令
                smart_home_keywords = ['灯', '空调', '电视', '窗帘', '风扇', '打开', '关闭']
                if any(keyword in light_result for keyword in smart_home_keywords):
                    self._update_status("🎯 检测到智能家居指令，使用轻量级ASR结果")
                    return light_result
            
            # 使用标准ASR进行更准确的识别
            standard_result = self._recognize_with_standard_asr(audio)
            if standard_result:
                return standard_result
                
            # 如果标准ASR也失败，返回轻量级ASR的结果
            return light_result
        
        else:
            # 默认策略
            return self._recognize_with_standard_asr(audio)
    
    def recognize_once(self, timeout: int = 5) -> Optional[str]:
        """
        单次语音识别
        
        Args:
            timeout: 超时时间
        
        Returns:
            Optional[str]: 识别结果
        """
        try:
            self._update_status("🎤 开始增强语音识别...")
            
            # 录音
            with self.base_recognizer.microphone as source:
                audio = self.base_recognizer.recognizer.listen(source, timeout=timeout, phrase_time_limit=5)
            
            # 使用策略进行识别
            result = self.recognize_with_strategy(audio)
            
            if result:
                self._update_status(f"✅ 识别完成: {result}")
                return result
            else:
                self._update_status("❌ 识别失败")
                return None
                
        except sr.WaitTimeoutError:
            self._update_status("⏰ 录音超时")
            return None
        except Exception as e:
            self._update_status(f"❌ 识别异常: {e}")
            return None
    
    def listen_continuous(self) -> Optional[str]:
        """持续监听（单次调用）"""
        return self.base_recognizer.listen_continuous()
    
    def listen_with_wake_word(self) -> Optional[str]:
        """带唤醒词的监听"""
        return self.base_recognizer.listen_with_wake_word()
    
    def is_microphone_available(self) -> bool:
        """检查麦克风是否可用"""
        return self.base_recognizer.is_microphone_available()
    
    def get_engine_status(self) -> Dict[str, Any]:
        """获取引擎状态"""
        status = {
            'base_engine': self.base_recognizer.engine,
            'light_asr_available': self.light_asr.is_available() if self.light_asr else False,
            'recognition_strategy': self.recognition_strategy
        }
        
        if self.light_asr:
            status['light_asr_info'] = self.light_asr.get_model_info()
        
        return status

def integrate_light_asr():
    """
    集成轻量级ASR到现有系统
    """
    print("🔗 集成轻量级ASR到现有语音识别系统")
    print("=" * 50)
    
    # 修改AI语音识别配置
    config_updates = {
        'light_asr': {
            'enabled': True,
            'model_path': None,  # 使用默认模型
            'strategy': 'hybrid',  # 混合策略
            'fallback_to_standard': True
        }
    }
    
    # 更新配置文件
    config_file = os.path.join(os.path.dirname(__file__), '..', 'config.py')
    
    print(f"📝 建议配置更新:")
    print("在 config.py 中添加以下配置:")
    print(f"LIGHT_ASR_CONFIG = {config_updates}")
    
    # 创建测试实例
    try:
        enhanced_recognizer = EnhancedAISpeechRecognizer()
        status = enhanced_recognizer.get_engine_status()
        
        print(f"\n📊 引擎状态:")
        print(f"基础引擎: {status['base_engine']}")
        print(f"轻量级ASR可用: {status['light_asr_available']}")
        print(f"识别策略: {status['recognition_strategy']}")
        
        if status['light_asr_available']:
            light_info = status['light_asr_info']
            print(f"轻量级ASR状态: {light_info['status']}")
            print(f"支持指令数: {len(light_info['commands'])}")
        
        print("\n✅ 集成完成!")
        return enhanced_recognizer
        
    except Exception as e:
        print(f"❌ 集成失败: {e}")
        return None

if __name__ == "__main__":
    # 集成测试
    enhanced_recognizer = integrate_light_asr()
    
    if enhanced_recognizer:
        print("\n🧪 运行集成测试...")
        
        # 测试麦克风
        if enhanced_recognizer.is_microphone_available():
            print("🎤 麦克风可用")
            
            # 可以添加实际的语音识别测试
            # result = enhanced_recognizer.recognize_once(timeout=10)
            # print(f"识别结果: {result}")
        else:
            print("❌ 麦克风不可用")
        
        print("✅ 集成测试完成")
    else:
        print("❌ 集成测试失败")
