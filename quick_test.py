#!/usr/bin/env python3
"""
Gmail MCP Server 快速测试脚本

这是一个简化版的测试脚本，用于快速验证服务器是否正常工作。

使用方法:
    python quick_test.py [access_token]
    
如果不提供access_token，会从环境变量或.env文件中读取。
"""

import os
import sys
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def quick_test(access_token=None, base_url="http://localhost:12000"):
    """快速测试所有主要功能"""
    
    # 获取访问令牌
    if not access_token:
        access_token = os.getenv('TEST_ACCESS_TOKEN')
    
    if not access_token:
        print("❌ 错误: 未找到访问令牌")
        print("使用方法: python quick_test.py [access_token]")
        print("或设置环境变量 TEST_ACCESS_TOKEN")
        return False
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    print("🚀 Gmail MCP Server 快速测试")
    print(f"服务器: {base_url}")
    print(f"令牌: {access_token[:20]}...")
    print()
    
    try:
        # 1. 健康检查
        print("1️⃣ 健康检查...", end=" ")
        response = requests.get(f"{base_url}/health", headers=headers, timeout=10)
        if response.status_code == 200 and response.json().get('status') == 'healthy':
            print("✅")
        else:
            print("❌")
            return False
            
        # 2. 获取邮件列表
        print("2️⃣ 获取邮件列表...", end=" ")
        response = requests.get(f"{base_url}/api/messages?max_results=3", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'messages' in data and len(data['messages']) > 0:
                print(f"✅ ({len(data['messages'])} 封邮件)")
                message_id = data['messages'][0]['id']
            else:
                print("❌ 无邮件")
                return False
        else:
            print("❌")
            return False
            
        # 3. 获取单个邮件
        print("3️⃣ 获取邮件详情...", end=" ")
        response = requests.get(f"{base_url}/api/messages/{message_id}", headers=headers, timeout=10)
        if response.status_code == 200 and 'id' in response.json():
            print("✅")
        else:
            print("❌")
            return False
            
        # 4. 获取标签列表
        print("4️⃣ 获取标签列表...", end=" ")
        response = requests.get(f"{base_url}/api/labels", headers=headers, timeout=10)
        if response.status_code == 200:
            labels = response.json()
            if isinstance(labels, list) and len(labels) > 0:
                print(f"✅ ({len(labels)} 个标签)")
            else:
                print("❌ 无标签")
                return False
        else:
            print("❌")
            return False
            
        # 5. MCP工具
        print("5️⃣ MCP工具定义...", end=" ")
        response = requests.get(f"{base_url}/mcp/tools", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'tools' in data and len(data['tools']) > 0:
                print(f"✅ ({len(data['tools'])} 个工具)")
            else:
                print("❌ 无工具")
                return False
        else:
            print("❌")
            return False
            
        print()
        print("🎉 所有测试通过！服务器运行正常。")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def main():
    """主函数"""
    access_token = None
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print(__doc__)
            return
        access_token = sys.argv[1]
    
    # 运行快速测试
    success = quick_test(access_token)
    
    if not success:
        print()
        print("💡 故障排除建议:")
        print("- 确保服务器正在运行 (python start_server.py)")
        print("- 检查访问令牌是否有效")
        print("- 验证网络连接")
        print("- 查看服务器日志")
        sys.exit(1)

if __name__ == "__main__":
    main()