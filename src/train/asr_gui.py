# -*- coding: utf-8 -*-
"""
轻量级ASR GUI集成模块
将轻量级语音识别集成到主界面中
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
from typing import Optional, Callable
import warnings
warnings.filterwarnings("ignore")

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class LightASRControlPanel:
    """轻量级ASR控制面板"""
    
    def __init__(self, parent_frame, status_callback: Optional[Callable] = None):
        """
        初始化控制面板
        
        Args:
            parent_frame: 父容器
            status_callback: 状态回调函数
        """
        self.parent_frame = parent_frame
        self.status_callback = status_callback
        self.light_asr = None
        self.enhanced_asr = None
        self.is_listening = False
        self.recognition_thread = None
        
        # 创建界面
        self.create_widgets()
        
        # 初始化ASR
        self.init_asr()
    
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        self.main_frame = ttk.LabelFrame(self.parent_frame, text="轻量级语音识别", padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 状态显示区域
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(status_frame, text="系统状态:").pack(side=tk.LEFT)
        self.status_var = tk.StringVar(value="初始化中...")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                                     foreground="orange")
        self.status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 模型信息区域
        info_frame = ttk.LabelFrame(self.main_frame, text="模型信息", padding=5)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.info_text = scrolledtext.ScrolledText(info_frame, height=4, state=tk.DISABLED)
        self.info_text.pack(fill=tk.BOTH, expand=True)
        
        # 控制按钮区域
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.listen_btn = ttk.Button(control_frame, text="开始监听", 
                                    command=self.toggle_listening)
        self.listen_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.test_btn = ttk.Button(control_frame, text="测试识别", 
                                  command=self.test_recognition)
        self.test_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.reload_btn = ttk.Button(control_frame, text="重新加载", 
                                    command=self.reload_model)
        self.reload_btn.pack(side=tk.LEFT)
        
        # 识别策略选择
        strategy_frame = ttk.Frame(self.main_frame)
        strategy_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(strategy_frame, text="识别策略:").pack(side=tk.LEFT)
        self.strategy_var = tk.StringVar(value="hybrid")
        strategy_combo = ttk.Combobox(strategy_frame, textvariable=self.strategy_var,
                                     values=["light_only", "standard_only", "hybrid"],
                                     state="readonly", width=15)
        strategy_combo.pack(side=tk.LEFT, padx=(10, 0))
        strategy_combo.bind('<<ComboboxSelected>>', self.on_strategy_change)
        
        # 识别结果区域
        result_frame = ttk.LabelFrame(self.main_frame, text="识别结果", padding=5)
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        self.result_text = scrolledtext.ScrolledText(result_frame, height=8)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        # 清除按钮
        clear_btn = ttk.Button(result_frame, text="清除日志", 
                              command=self.clear_results)
        clear_btn.pack(anchor=tk.E, pady=(5, 0))
    
    def init_asr(self):
        """初始化ASR系统"""
        def init_worker():
            try:
                from train.model_integration import LightASREngine, EnhancedAISpeechRecognizer
                
                self.update_status("正在初始化轻量级ASR...", "orange")
                
                # 初始化轻量级引擎
                self.light_asr = LightASREngine()
                
                # 初始化增强识别器
                self.enhanced_asr = EnhancedAISpeechRecognizer(
                    status_callback=self.log_result,
                    use_light_asr=True
                )
                
                # 更新界面信息
                if self.light_asr.is_available():
                    model_info = self.light_asr.get_model_info()
                    self.update_model_info(model_info)
                    self.update_status("✅ 轻量级ASR已就绪", "green")
                else:
                    self.update_status("⚠️ 轻量级ASR不可用", "red")
                
                # 启用按钮
                self.test_btn.config(state=tk.NORMAL)
                self.listen_btn.config(state=tk.NORMAL)
                
            except Exception as e:
                self.update_status(f"❌ 初始化失败: {e}", "red")
                self.log_result(f"错误: {e}")
        
        # 在后台线程中初始化
        init_thread = threading.Thread(target=init_worker, daemon=True)
        init_thread.start()
    
    def update_status(self, message: str, color: str = "black"):
        """更新状态显示"""
        self.status_var.set(message)
        self.status_label.config(foreground=color)
        
        if self.status_callback:
            self.status_callback(message)
    
    def update_model_info(self, info: dict):
        """更新模型信息显示"""
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        
        info_text = f"状态: {info.get('status', 'unknown')}\n"
        info_text += f"设备: {info.get('device', 'unknown')}\n"
        info_text += f"模型路径: {info.get('model_path', 'default')}\n"
        info_text += f"支持指令数: {len(info.get('commands', []))}"
        
        self.info_text.insert(tk.END, info_text)
        self.info_text.config(state=tk.DISABLED)
    
    def log_result(self, message: str):
        """记录识别结果"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.result_text.insert(tk.END, log_entry)
        self.result_text.see(tk.END)
    
    def toggle_listening(self):
        """切换监听状态"""
        if not self.enhanced_asr:
            messagebox.showerror("错误", "ASR系统未初始化")
            return
        
        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()
    
    def start_listening(self):
        """开始监听"""
        if not self.enhanced_asr.is_microphone_available():
            messagebox.showerror("错误", "麦克风不可用")
            return
        
        self.is_listening = True
        self.listen_btn.config(text="停止监听", style="Accent.TButton")
        self.update_status("🎤 正在监听...", "blue")
        
        def listen_worker():
            try:
                while self.is_listening:
                    self.log_result("等待语音输入...")
                    result = self.enhanced_asr.recognize_once(timeout=5)
                    
                    if result:
                        self.log_result(f"✅ 识别结果: {result}")
                        
                        # 如果识别到指令，可以在这里触发相应的智能家居操作
                        self.process_command(result)
                    else:
                        self.log_result("⏰ 未检测到语音")
                    
                    time.sleep(0.5)  # 短暂停顿
                    
            except Exception as e:
                self.log_result(f"❌ 监听错误: {e}")
            
            self.is_listening = False
            self.listen_btn.config(text="开始监听")
            self.update_status("监听已停止", "black")
        
        self.recognition_thread = threading.Thread(target=listen_worker, daemon=True)
        self.recognition_thread.start()
    
    def stop_listening(self):
        """停止监听"""
        self.is_listening = False
        self.listen_btn.config(text="开始监听")
        self.update_status("正在停止监听...", "orange")
    
    def test_recognition(self):
        """测试识别功能"""
        if not self.enhanced_asr:
            messagebox.showerror("错误", "ASR系统未初始化")
            return
        
        def test_worker():
            try:
                self.update_status("🎤 准备录音测试...", "blue")
                self.log_result("请说话进行测试...")
                
                result = self.enhanced_asr.recognize_once(timeout=10)
                
                if result:
                    self.log_result(f"✅ 测试成功: {result}")
                    self.update_status("✅ 测试完成", "green")
                else:
                    self.log_result("❌ 测试失败: 未识别到语音")
                    self.update_status("❌ 测试失败", "red")
                    
            except Exception as e:
                self.log_result(f"❌ 测试错误: {e}")
                self.update_status("❌ 测试错误", "red")
        
        test_thread = threading.Thread(target=test_worker, daemon=True)
        test_thread.start()
    
    def reload_model(self):
        """重新加载模型"""
        self.update_status("正在重新加载模型...", "orange")
        
        def reload_worker():
            try:
                # 重新初始化
                if self.light_asr:
                    self.light_asr = None
                if self.enhanced_asr:
                    self.enhanced_asr = None
                
                self.init_asr()
                self.log_result("模型已重新加载")
                
            except Exception as e:
                self.update_status(f"❌ 重新加载失败: {e}", "red")
                self.log_result(f"重新加载失败: {e}")
        
        reload_thread = threading.Thread(target=reload_worker, daemon=True)
        reload_thread.start()
    
    def on_strategy_change(self, event):
        """识别策略改变"""
        strategy = self.strategy_var.get()
        self.log_result(f"识别策略已切换为: {strategy}")
        
        # 这里可以更新enhanced_asr的策略配置
        # self.enhanced_asr.set_strategy(strategy)
    
    def process_command(self, command: str):
        """处理识别到的指令"""
        # 这里可以集成到智能家居控制系统
        self.log_result(f"🏠 处理指令: {command}")
        
        # 示例：解析指令并执行相应操作
        if "打开" in command and "灯" in command:
            self.log_result("💡 执行: 打开灯光")
        elif "关闭" in command and "灯" in command:
            self.log_result("💡 执行: 关闭灯光")
        elif "空调" in command:
            self.log_result("❄️ 执行: 空调控制")
        elif "音乐" in command:
            self.log_result("🎵 执行: 音乐控制")
        else:
            self.log_result("❓ 未知指令类型")
    
    def clear_results(self):
        """清除结果日志"""
        self.result_text.delete(1.0, tk.END)
        self.log_result("日志已清除")

def create_light_asr_window():
    """创建独立的轻量级ASR窗口"""
    root = tk.Tk()
    root.title("轻量级语音识别控制台")
    root.geometry("600x700")
    
    # 设置样式
    style = ttk.Style()
    style.theme_use('clam')
    
    # 创建控制面板
    control_panel = LightASRControlPanel(root)
    
    # 添加菜单栏
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    
    # 文件菜单
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="文件", menu=file_menu)
    file_menu.add_command(label="导出日志", command=lambda: export_logs(control_panel))
    file_menu.add_separator()
    file_menu.add_command(label="退出", command=root.quit)
    
    # 工具菜单
    tools_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="工具", menu=tools_menu)
    tools_menu.add_command(label="性能测试", command=lambda: run_benchmark())
    tools_menu.add_command(label="模型训练", command=lambda: run_training())
    
    return root, control_panel

def export_logs(control_panel):
    """导出日志"""
    try:
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            title="保存日志",
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if filename:
            content = control_panel.result_text.get(1.0, tk.END)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            control_panel.log_result(f"日志已导出到: {filename}")
            
    except Exception as e:
        messagebox.showerror("错误", f"导出失败: {e}")

def run_benchmark():
    """运行性能测试"""
    try:
        import subprocess
        script_path = os.path.join(os.path.dirname(__file__), 'simple_test.py')
        subprocess.Popen(['python', script_path], creationflags=subprocess.CREATE_NEW_CONSOLE)
    except Exception as e:
        messagebox.showerror("错误", f"无法启动性能测试: {e}")

def run_training():
    """运行模型训练"""
    try:
        import subprocess
        script_path = os.path.join(os.path.dirname(__file__), 'train_model.py')
        subprocess.Popen(['python', script_path, '--mode', 'train'], 
                        creationflags=subprocess.CREATE_NEW_CONSOLE)
    except Exception as e:
        messagebox.showerror("错误", f"无法启动训练: {e}")

def main():
    """主函数"""
    root, control_panel = create_light_asr_window()
    
    # 设置关闭事件
    def on_closing():
        if control_panel.is_listening:
            control_panel.stop_listening()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 启动界面
    root.mainloop()

if __name__ == "__main__":
    main()
