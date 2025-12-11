#!/usr/bin/env python3
"""
Web应用启动脚本
"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from web_app import app

if __name__ == '__main__':
    # 创建必要的目录
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('results', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    print("🚀 启动Word文档审核Web应用...")
    print("📍 访问地址: http://localhost:5000")
    print("📁 上传目录: uploads/")
    print("📄 结果目录: results/")
    print("⚠️  请确保已配置AWS凭证")
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )