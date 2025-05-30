# -*- coding: utf-8 -*-
"""
智能语音控制家居系统启动脚本
"""

import sys
import os

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

try:
    from src.main_gui import main
    
    if __name__ == "__main__":
        print("启动智能语音控制家居系统...")
        main()
        
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保安装了所需的依赖包:")
    print("pip install -r requirements.txt")
except Exception as e:
    print(f"启动失败: {e}")
    input("按回车键退出...")
