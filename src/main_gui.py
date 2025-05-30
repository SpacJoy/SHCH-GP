# -*- coding: utf-8 -*-
"""
智能语音控制家居系统主界面 - AI语音识别版本
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from datetime import datetime

from mqtt_client import MQTTClient, control_device
from ai_speech_recognition import AISpeechRecognizer
from intent_recognition import IntentRecognizer, EXAMPLE_COMMANDS
from config import GUI_CONFIG, MQTT_TOPICS, DEVICE_COMMANDS

class SmartHomeGUI:
    def __init__(self, root):
        self.root = root        
        self.setup_window()
        
        # 初始化组件
        self.mqtt_client = None
        self.speech_recognizer = None
        self.intent_recognizer = IntentRecognizer()
        
        # 状态变量
        self.is_speech_listening = False
        self.is_mqtt_connected = False
        
        # 创建界面
        self.create_widgets()
        
        # 初始化组件（带错误处理）
        self.initialize_components()
    
    def initialize_components(self):
        """初始化系统组件"""
        # 初始化MQTT客户端
        try:
            self.mqtt_client = MQTTClient(on_message_callback=self.on_mqtt_message)
            self.log_message("系统", "MQTT模块初始化成功")
            # 自动连接MQTT
            self.connect_mqtt()
        except ValueError as e:
            error_msg = str(e)
            if "配置无效" in error_msg:
                self.log_message("配置错误", "MQTT配置无效，请运行 config.bat 进行配置")
                messagebox.showwarning("配置提醒", 
                    "MQTT配置需要设置！\n\n请运行 config.bat 配置巴法云连接信息，\n或手动编辑 src/config.py 文件。")
            else:
                self.log_message("错误", f"MQTT初始化失败: {error_msg}")
        except Exception as e:
            self.log_message("错误", f"MQTT初始化异常: {str(e)}")
          # 初始化AI语音识别器
        try:
            self.speech_recognizer = AISpeechRecognizer(status_callback=self.update_speech_status)
            self.log_message("系统", "AI语音识别模块初始化成功")
        except RuntimeError as e:
            self.speech_recognizer = None
            if "setuptools" in str(e) or "distutils" in str(e):
                self.log_message("依赖错误", 
                    "语音识别需要setuptools支持，请运行: pip install setuptools>=65.0.0")
                messagebox.showerror("依赖错误", 
                    "语音识别功能需要setuptools支持！\n\n请运行以下命令修复：\npip install setuptools>=65.0.0\n\n或运行 fix_python312.bat")
            else:
                self.log_message("错误", f"AI语音识别初始化失败: {str(e)}")
        except Exception as e:
            self.speech_recognizer = None
            self.log_message("错误", f"AI语音识别初始化异常: {str(e)}")
    def setup_window(self):
        """设置主窗口"""
        self.root.title(GUI_CONFIG["title"])
        # 增加窗口宽度以适应左右分栏布局
        window_width = GUI_CONFIG.get("width", 800) + 200
        window_height = GUI_CONFIG.get("height", 600)
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.resizable(True, True)
        self.root.minsize(900, 500)  # 设置最小窗口大小
        
        # 设置字体
        self.font = ("Microsoft YaHei", 9)
        
        # 设置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    def create_widgets(self):
        """创建界面控件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)  # 右侧权重更大
        main_frame.rowconfigure(0, weight=1)
        
        # 左侧面板：控制区域
        left_panel = ttk.Frame(main_frame)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(1, weight=1)
        
        # 右侧面板：日志和信息区域
        right_panel = ttk.Frame(main_frame)
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=1)
        
        # 创建各个组件
        self.create_control_panel(left_panel)
        self.create_status_panel(left_panel)
        self.create_message_panel(right_panel)
        self.create_example_panel(right_panel)
    def create_control_panel(self, parent):
        """创建控制面板"""
        # 控制面板框架
        control_frame = ttk.LabelFrame(parent, text="🎛️ 控制面板", padding="10")
        control_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        control_frame.columnconfigure(0, weight=1)
        
        # 语音控制区域
        voice_frame = ttk.LabelFrame(control_frame, text="🎤 AI语音控制", padding="8")
        voice_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        voice_frame.columnconfigure(0, weight=1)
        voice_frame.columnconfigure(1, weight=1)
        
        # 语音控制按钮区域
        voice_btn_frame = ttk.Frame(voice_frame)
        voice_btn_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        voice_btn_frame.columnconfigure(0, weight=1)
        voice_btn_frame.columnconfigure(1, weight=1)
        
        self.voice_btn = ttk.Button(voice_btn_frame, text="🎧 开始语音监听", 
                                   command=self.toggle_voice_listening)
        self.voice_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        self.once_voice_btn = ttk.Button(voice_btn_frame, text="🔍 单次AI识别", 
                                        command=self.recognize_once)
        self.once_voice_btn.grid(row=0, column=1, padx=(5, 0), sticky="ew")
        
        # 唤醒词开关
        wake_word_frame = ttk.Frame(voice_frame)
        wake_word_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5, 5))
        
        self.wake_word_var = tk.BooleanVar(value=True)
        self.wake_word_check = ttk.Checkbutton(wake_word_frame, text="🔊 启用唤醒词功能", 
                                             variable=self.wake_word_var,
                                             command=self.toggle_wake_word)
        self.wake_word_check.grid(row=0, column=0, sticky="w")
        
        # 语音状态显示
        self.voice_status_label = ttk.Label(voice_frame, text="📴 语音监听: 关闭", 
                                          font=self.font, foreground="gray")
        self.voice_status_label.grid(row=2, column=0, columnspan=2, pady=(5, 0), sticky="w")
        
        # 手动控制区域
        manual_frame = ttk.LabelFrame(control_frame, text="⚙️ 手动控制", padding="8")
        manual_frame.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        manual_frame.columnconfigure(1, weight=1)
        manual_frame.columnconfigure(3, weight=1)
        
        # 设备选择
        ttk.Label(manual_frame, text="设备:", font=self.font).grid(row=0, column=0, sticky="w", pady=2)
        self.device_var = tk.StringVar(value="灯")
        device_combo = ttk.Combobox(manual_frame, textvariable=self.device_var,
                                  values=["💡 灯", "🌪️ 风扇", "❄️ 空调", "📺 电视", "🪟 窗帘"], 
                                  state="readonly", width=12)
        device_combo.grid(row=0, column=1, padx=(5, 10), sticky="ew", pady=2)
        
        # 操作选择
        ttk.Label(manual_frame, text="操作:", font=self.font).grid(row=0, column=2, sticky="w", pady=2)
        self.action_var = tk.StringVar(value="on")
        action_combo = ttk.Combobox(manual_frame, textvariable=self.action_var,
                                  values=["✅ 开启", "❌ 关闭"], state="readonly", width=10)
        action_combo.grid(row=0, column=3, padx=(5, 10), sticky="ew", pady=2)
        
        # 执行按钮
        execute_btn = ttk.Button(manual_frame, text="▶️ 执行", 
                               command=self.execute_manual_command)
        execute_btn.grid(row=0, column=4, padx=(5, 0), pady=2)
        
        # MQTT连接区域
        mqtt_frame = ttk.LabelFrame(control_frame, text="🌐 MQTT连接", padding="8")
        mqtt_frame.grid(row=2, column=0, sticky="ew")
        mqtt_frame.columnconfigure(0, weight=1)
        
        # MQTT按钮区域
        mqtt_btn_frame = ttk.Frame(mqtt_frame)
        mqtt_btn_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        mqtt_btn_frame.columnconfigure(0, weight=1)
        mqtt_btn_frame.columnconfigure(1, weight=1)
        
        self.mqtt_btn = ttk.Button(mqtt_btn_frame, text="🔗 连接MQTT", 
                                 command=self.toggle_mqtt_connection)
        self.mqtt_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        clear_btn = ttk.Button(mqtt_btn_frame, text="🗑️ 清除日志", 
                             command=self.clear_message_log)
        clear_btn.grid(row=0, column=1, padx=(5, 0), sticky="ew")
        
        # MQTT状态显示
        self.mqtt_status_label = ttk.Label(mqtt_frame, text="🔴 MQTT: 未连接", 
                                         font=self.font, foreground="red")
        self.mqtt_status_label.grid(row=1, column=0, pady=(5, 0), sticky="w")
    def create_message_panel(self, parent):
        """创建消息显示面板"""
        message_frame = ttk.LabelFrame(parent, text="📝 系统日志", padding="10")
        message_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 8))
        message_frame.columnconfigure(0, weight=1)
        message_frame.rowconfigure(0, weight=1)
        
        # 创建工具栏
        toolbar_frame = ttk.Frame(message_frame)
        toolbar_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        toolbar_frame.columnconfigure(0, weight=1)
        
        # 日志控制按钮
        log_controls = ttk.Frame(toolbar_frame)
        log_controls.grid(row=0, column=1, sticky="e")
        
        auto_scroll_var = tk.BooleanVar(value=True)
        auto_scroll_check = ttk.Checkbutton(log_controls, text="📜 自动滚动", 
                                           variable=auto_scroll_var)
        auto_scroll_check.grid(row=0, column=0, padx=(0, 5))
        
        # 日志文本区域
        self.message_text = scrolledtext.ScrolledText(message_frame, height=12, width=50, 
                                                    font=self.font, wrap=tk.WORD)
        self.message_text.grid(row=1, column=0, sticky="nsew")
        
        # 设置文本区域的样式
        self.message_text.configure(bg="#f8f9fa", fg="#212529", 
                                  selectbackground="#007bff", 
                                  selectforeground="white")
    def create_example_panel(self, parent):
        """创建示例命令面板"""
        example_frame = ttk.LabelFrame(parent, text="💬 AI语音命令示例", padding="10")
        example_frame.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        example_frame.columnconfigure(0, weight=1)
        
        # 创建Notebook来组织示例
        notebook = ttk.Notebook(example_frame)
        notebook.grid(row=0, column=0, sticky="ew")
        
        # 基础命令选项卡
        basic_frame = ttk.Frame(notebook)
        notebook.add(basic_frame, text="📋 基础命令")
        
        basic_text = tk.Text(basic_frame, height=4, width=40, font=self.font, wrap=tk.WORD,
                           bg="#f8f9fa", relief=tk.FLAT, bd=0, cursor="arrow")
        basic_text.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        basic_frame.columnconfigure(0, weight=1)
        
        # 高级命令选项卡
        advanced_frame = ttk.Frame(notebook)
        notebook.add(advanced_frame, text="🚀 高级命令")
        
        advanced_text = tk.Text(advanced_frame, height=4, width=40, font=self.font, wrap=tk.WORD,
                              bg="#f8f9fa", relief=tk.FLAT, bd=0, cursor="arrow")
        advanced_text.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        advanced_frame.columnconfigure(0, weight=1)
        
        # 分类显示示例命令
        basic_commands = [
            "💡 打开灯", "💡 关闭灯", "🌪️ 打开风扇", "❄️ 关闭空调"
        ]
        advanced_commands = [
            "🏠 打开客厅的灯", "🛏️ 关闭卧室的空调", "📺 打开电视", "🪟 关闭窗帘"
        ]
        
        basic_examples = "\n".join([f"• {cmd}" for cmd in basic_commands])
        advanced_examples = "\n".join([f"• {cmd}" for cmd in advanced_commands])
        
        basic_text.insert(tk.END, basic_examples)
        basic_text.config(state=tk.DISABLED)
        
        advanced_text.insert(tk.END, advanced_examples)
        advanced_text.config(state=tk.DISABLED)
    def create_status_panel(self, parent):
        """创建状态面板"""
        status_frame = ttk.LabelFrame(parent, text="📊 系统状态", padding="10")
        status_frame.grid(row=1, column=0, sticky="ew")
        status_frame.columnconfigure(1, weight=1)
        
        # 创建状态显示区域
        status_container = ttk.Frame(status_frame)
        status_container.grid(row=0, column=0, sticky="ew")
        status_container.columnconfigure(1, weight=1)
        
        # 系统状态行
        system_frame = ttk.Frame(status_container)
        system_frame.grid(row=0, column=0, sticky="ew", pady=2)
        system_frame.columnconfigure(1, weight=1)
        
        ttk.Label(system_frame, text="🖥️ 系统:", font=self.font).grid(row=0, column=0, sticky="w")
        self.status_label = ttk.Label(system_frame, text="✅ 就绪", font=self.font, foreground="green")
        self.status_label.grid(row=0, column=1, sticky="w", padx=(10, 0))
        
        # AI语音识别状态行
        speech_frame = ttk.Frame(status_container)
        speech_frame.grid(row=1, column=0, sticky="ew", pady=2)
        speech_frame.columnconfigure(1, weight=1)
        
        ttk.Label(speech_frame, text="🎤 语音:", font=self.font).grid(row=0, column=0, sticky="w")
        self.speech_status_label = ttk.Label(speech_frame, text="💤 待机中", font=self.font, foreground="blue")
        self.speech_status_label.grid(row=0, column=1, sticky="w", padx=(10, 0))
        
        # MQTT连接状态行
        mqtt_frame = ttk.Frame(status_container)
        mqtt_frame.grid(row=2, column=0, sticky="ew", pady=2)
        mqtt_frame.columnconfigure(1, weight=1)
        
        ttk.Label(mqtt_frame, text="🌐 MQTT:", font=self.font).grid(row=0, column=0, sticky="w")
        self.mqtt_status_detailed = ttk.Label(mqtt_frame, text="⚪ 未连接", font=self.font, foreground="gray")
        self.mqtt_status_detailed.grid(row=0, column=1, sticky="w", padx=(10, 0))
    
    def update_speech_status(self, message):
        """更新AI语音识别状态显示"""
        if hasattr(self, 'speech_status_label'):
            # 根据消息类型设置不同颜色
            if "错误" in message or "❌" in message:
                color = "red"
            elif "成功" in message or "✅" in message:
                color = "green"
            elif "正在" in message or "🔄" in message or "🎤" in message:
                color = "orange"
            else:
                color = "blue"
            
            self.speech_status_label.config(text=message, foreground=color)
    
    def toggle_voice_listening(self):
        """切换语音监听状态"""
        if not self.speech_recognizer:
            messagebox.showerror("错误", "AI语音识别器未初始化")
            return
            
        if self.is_speech_listening:
            self.stop_voice_listening()
        else:
            self.start_voice_listening()
    def start_voice_listening(self):
        """开始语音监听"""
        try:
            self.is_speech_listening = True
            self.voice_btn.config(text="⏹️ 停止语音监听")
            self.voice_status_label.config(text="🎧 语音监听: 开启", foreground="green")
            self.update_speech_status("🎧 开始持续AI语音监听...")
            self.log_message("AI语音", "开始持续语音监听...")
            
            # 在新线程中运行语音识别
            self.voice_thread = threading.Thread(target=self.continuous_voice_recognition, daemon=True)
            self.voice_thread.start()
        except Exception as e:
            self.log_message("错误", f"启动语音监听失败: {str(e)}")
            self.update_speech_status(f"❌ 启动失败: {str(e)}")
            self.is_speech_listening = False
            self.voice_btn.config(text="🎧 开始语音监听")
            self.voice_status_label.config(text="📴 语音监听: 关闭", foreground="gray")
    def stop_voice_listening(self):
        """停止语音监听"""
        self.is_speech_listening = False
        self.voice_btn.config(text="🎧 开始语音监听")
        self.voice_status_label.config(text="📴 语音监听: 关闭", foreground="gray")
        self.update_speech_status("⏹️ 语音监听已停止")
        self.log_message("AI语音", "语音监听已停止")
    
    def continuous_voice_recognition(self):
        """持续语音识别（在后台线程中运行）"""
        while self.is_speech_listening:
            try:
                if self.speech_recognizer:
                    # 使用唤醒词功能或直接识别
                    if self.speech_recognizer.wake_word_enabled:
                        result = self.speech_recognizer.listen_with_wake_word()
                    else:
                        result = self.speech_recognizer.listen_continuous()
                    
                    if result:
                        # 在主线程中处理识别结果
                        self.root.after(0, self.process_voice_command, result)
                else:
                    # 如果语音识别器未初始化，停止监听
                    self.root.after(0, self.log_message, "错误", "语音识别器未初始化，停止监听")
                    break
            except Exception as e:
                self.root.after(0, self.log_message, "AI语音错误", f"语音识别异常: {str(e)}")
                self.root.after(0, self.update_speech_status, f"❌ 识别异常: {str(e)}")
                break
    
    def recognize_once(self):
        """单次AI语音识别"""
        if not self.speech_recognizer:
            messagebox.showerror("错误", "AI语音识别器未初始化")
            return
            
        def recognize():
            try:
                self.log_message("AI语音", "开始单次AI语音识别...")
                result = self.speech_recognizer.recognize_once() # type: ignore
                if result:
                    self.root.after(0, self.process_voice_command, result)
                else:
                    self.root.after(0, self.log_message, "AI语音", "未识别到语音或识别失败")
            except Exception as e:
                self.root.after(0, self.log_message, "AI语音错误", f"单次识别失败: {str(e)}")
                self.root.after(0, self.update_speech_status, f"❌ 识别失败: {str(e)}")
        
        # 在新线程中执行语音识别
        threading.Thread(target=recognize, daemon=True).start()
    
    def process_voice_command(self, voice_text):
        """处理语音命令"""
        self.log_message("AI识别结果", f"识别到: {voice_text}")
        
        # 意图识别
        intent = self.intent_recognizer.recognize_intent(voice_text)
        if intent:
            device = intent.get("device")
            action = intent.get("action")
            self.log_message("意图识别", f"设备: {device}, 操作: {action}")
            
            # 执行控制命令
            if self.mqtt_client and self.is_mqtt_connected:
                self.execute_device_control(device, action)
            else:
                self.log_message("错误", "MQTT未连接，无法执行设备控制")
                self.update_speech_status("⚠️ MQTT未连接")
        else:
            self.log_message("意图识别", "未识别到有效的控制意图")
            self.update_speech_status("⚠️ 未识别到有效指令")
    
    def toggle_mqtt_connection(self):
        """切换MQTT连接状态"""
        if not self.mqtt_client:
            messagebox.showerror("错误", "MQTT客户端未初始化")
            return
            
        if self.is_mqtt_connected:
            self.disconnect_mqtt()
        else:
            self.connect_mqtt()
    def connect_mqtt(self):
        """连接MQTT"""
        if self.mqtt_client:
            try:
                if self.mqtt_client.connect():
                    self.is_mqtt_connected = True
                    self.mqtt_btn.config(text="🔌 断开MQTT")
                    self.mqtt_status_label.config(text="🟢 MQTT: 已连接", foreground="green")
                    if hasattr(self, 'mqtt_status_detailed'):
                        self.mqtt_status_detailed.config(text="🟢 已连接", foreground="green")
                    self.log_message("MQTT", "连接成功")
                else:
                    self.log_message("MQTT", "连接失败")
            except Exception as e:
                self.log_message("MQTT错误", f"连接异常: {str(e)}")
    def disconnect_mqtt(self):
        """断开MQTT连接"""
        if self.mqtt_client:
            self.mqtt_client.disconnect()
        self.is_mqtt_connected = False
        self.mqtt_btn.config(text="🔗 连接MQTT")
        self.mqtt_status_label.config(text="🔴 MQTT: 未连接", foreground="red")
        if hasattr(self, 'mqtt_status_detailed'):
            self.mqtt_status_detailed.config(text="⚪ 未连接", foreground="gray")
        self.log_message("MQTT", "连接已断开")
    def execute_manual_command(self):
        """执行手动控制命令"""
        device_display = self.device_var.get()
        action_display = self.action_var.get()
        
        # 提取实际的设备名称和操作（去掉emoji）
        device_map = {
            "💡 灯": "灯",
            "🌪️ 风扇": "风扇", 
            "❄️ 空调": "空调",
            "📺 电视": "电视",
            "🪟 窗帘": "窗帘"
        }
        action_map = {
            "✅ 开启": "on",
            "❌ 关闭": "off"
        }
        
        device = device_map.get(device_display, device_display)
        action = action_map.get(action_display, action_display)
        
        self.log_message("手动控制", f"用户选择: 设备={device}, 操作={action}")
        
        if self.mqtt_client and self.is_mqtt_connected:
            self.execute_device_control(device, action)
        else:
            self.log_message("错误", "MQTT未连接，无法执行设备控制")
    
    def execute_device_control(self, device, action):
        """执行设备控制"""
        try:
            self.log_message("设备控制", f"准备执行: 设备={device}, 操作={action}")
            success = control_device(self.mqtt_client, device, action)
            if success:
                self.log_message("设备控制", f"✅ 成功执行: {device} {action}")
                self.update_speech_status(f"✅ {device} {action} 成功")
            else:
                self.log_message("设备控制", f"❌ 执行失败: {device} {action}")
                self.update_speech_status(f"❌ {device} {action} 失败")
        except Exception as e:
            self.log_message("控制错误", f"设备控制异常: {str(e)}")
            self.update_speech_status(f"❌ 控制异常: {str(e)}")
    
    def on_mqtt_message(self, client, userdata, message):
        """MQTT消息回调"""
        try:
            topic = message.topic
            payload = message.payload.decode('utf-8')
            self.log_message("MQTT接收", f"主题: {topic}, 消息: {payload}")
        except Exception as e:
            self.log_message("MQTT错误", f"消息处理异常: {str(e)}")
    
    def log_message(self, sender, message):
        """记录消息到日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {sender}: {message}\n"
        
        # 在主线程中更新界面
        if hasattr(self, 'message_text'):
            self.message_text.insert(tk.END, log_entry)
            self.message_text.see(tk.END)
    
    def clear_message_log(self):
        """清除消息日志"""
        if hasattr(self, 'message_text'):
            self.message_text.delete(1.0, tk.END)
            self.log_message("系统", "日志已清除")
    
    def toggle_wake_word(self):
        """切换唤醒词启用状态"""
        try:
            if self.speech_recognizer:
                # 更新语音识别器的唤醒词设置
                self.speech_recognizer.wake_word_enabled = self.wake_word_var.get()
                
                status = "启用" if self.wake_word_var.get() else "禁用"
                self.log_message("设置", f"唤醒词功能已{status}")
                
                # 如果正在监听，重新启动以应用新设置
                if self.is_speech_listening:
                    self.log_message("系统", "重新启动语音监听以应用设置...")
                    self.stop_voice_listening()
                    import time
                    time.sleep(0.5)  # 短暂延迟
                    self.start_voice_listening()
            else:
                self.log_message("错误", "语音识别器未初始化")
        except Exception as e:
            self.log_message("错误", f"切换唤醒词设置失败: {str(e)}")

def main():
    """主函数"""
    root = tk.Tk()
    app = SmartHomeGUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序异常: {e}")
    finally:
        # 清理资源
        if hasattr(app, 'mqtt_client') and app.mqtt_client:
            app.mqtt_client.disconnect()
        root.quit()

if __name__ == "__main__":
    main()
