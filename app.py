import os
from src.main import start

# 程序版本信息
__version__ = "1.0.0"

def print_version():
    """打印程序版本信息（带水印格式）"""
    watermark = """
╔═══════════════════════════════════════════════════════════════
║            🚀 Diskless Management System 🚀                  
║                                                               
║  Version: {version}                                          
║  Build Date: 2025-12-26                                      
║  Author: AisDanny                            
║  License: MIT Open Source                                    
║                                               
║  Copyright © 2025 Diskless Management System                 
║                                                               
║  ✨ 专业的无盘管理系统 ✨                                     
║  📁 支持 TrueNAS 集成 | 🔧 PVE 配置管理 | 🌐 NFS 共享服务    
║                                                               
║  🔗 GitHub: https://github.com/Ais-Danny/diskless-api         
╚═══════════════════════════════════════════════════════════════
""".format(version=__version__)
    
    print(watermark)
    print("=" * 65)

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print_version()
    start()