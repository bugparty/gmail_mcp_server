#!/usr/bin/env python3
"""
Gmail MCP Server 启动脚本
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_environment():
    """检查环境配置"""
    required_vars = [
        'GOOGLE_CLIENT_ID',
        'GOOGLE_CLIENT_SECRET'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ 缺少必要的环境变量:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n请设置这些环境变量或创建 .env 文件")
        print("参考 .env.example 文件进行配置")
        return False
    
    print("✅ 环境配置检查通过")
    return True

def main():
    """主函数"""
    print("🚀 启动 Gmail MCP Server...")
    
    # 加载环境变量（如果存在.env文件）
    env_file = project_root / '.env'
    if env_file.exists():
        print(f"📄 加载环境变量文件: {env_file}")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    
    # 检查环境配置
    if not check_environment():
        sys.exit(1)
    
    # 启动服务器
    try:
        import uvicorn
        from main import app
        from config.settings import settings
        
        print(f"🌐 服务器将在 http://{settings.HOST}:{settings.PORT} 启动")
        print(f"📧 访问 http://localhost:{settings.PORT} 开始使用")
        print("按 Ctrl+C 停止服务器")
        
        uvicorn.run(
            "main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            access_log=True
        )
        
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()