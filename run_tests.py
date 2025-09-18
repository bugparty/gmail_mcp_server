#!/usr/bin/env python3
"""
Gmail MCP Server 测试运行器

使用pytest框架运行各种类型的测试
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def check_dependencies():
    """检查测试依赖是否安装"""
    try:
        import pytest
        import requests
        from dotenv import load_dotenv
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False


def check_environment():
    """检查环境配置"""
    from dotenv import load_dotenv
    load_dotenv()
    
    token = os.getenv('TEST_ACCESS_TOKEN')
    if not token:
        print("⚠️  警告: 未找到 TEST_ACCESS_TOKEN 环境变量")
        print("请设置访问令牌:")
        print("  export TEST_ACCESS_TOKEN='your_token_here'")
        print("  或在 .env 文件中添加: TEST_ACCESS_TOKEN=your_token_here")
        return False
    
    server_url = os.getenv('TEST_SERVER_URL', 'http://localhost:12000')
    print(f"🌐 测试服务器: {server_url}")
    print(f"🔑 访问令牌: {token[:20]}...")
    
    return True


def check_server():
    """检查服务器是否运行"""
    import requests
    from dotenv import load_dotenv
    
    load_dotenv()
    server_url = os.getenv('TEST_SERVER_URL', 'http://localhost:12000')
    
    try:
        response = requests.get(f"{server_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'healthy':
                print(f"✅ 服务器运行正常")
                return True
    except Exception as e:
        pass
    
    print(f"❌ 服务器未运行或不健康")
    print(f"请先启动服务器: python start_server.py")
    return False


def run_pytest(args):
    """运行pytest"""
    cmd = ['python', '-m', 'pytest'] + args
    print(f"🚀 运行命令: {' '.join(cmd)}")
    print("=" * 60)
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description='Gmail MCP Server 测试运行器')
    parser.add_argument('--quick', action='store_true', help='快速测试（只运行基本功能）')
    parser.add_argument('--smoke', action='store_true', help='冒烟测试（最基本的功能验证）')
    parser.add_argument('--integration', action='store_true', help='集成测试')
    parser.add_argument('--slow', action='store_true', help='包含慢速测试')
    parser.add_argument('--destructive', action='store_true', help='包含破坏性测试（会修改Gmail数据）')
    parser.add_argument('--coverage', action='store_true', help='生成覆盖率报告')
    parser.add_argument('--html', action='store_true', help='生成HTML测试报告')
    parser.add_argument('--parallel', '-n', type=int, help='并行运行测试（指定进程数）')
    parser.add_argument('--verbose', '-v', action='count', default=1, help='详细输出')
    parser.add_argument('--filter', '-k', help='过滤测试（pytest -k 参数）')
    parser.add_argument('--file', help='运行特定测试文件')
    parser.add_argument('--skip-checks', action='store_true', help='跳过环境检查')
    
    args = parser.parse_args()
    
    print("🧪 Gmail MCP Server 测试运行器")
    print("=" * 60)
    
    # 检查依赖
    if not check_dependencies():
        return 1
    
    # 检查环境（除非跳过）
    if not args.skip_checks:
        if not check_environment():
            return 1
        
        if not check_server():
            return 1
    
    # 构建pytest参数
    pytest_args = []
    
    # 详细程度
    if args.verbose:
        pytest_args.extend(['-' + 'v' * args.verbose])
    
    # 测试选择
    if args.quick:
        pytest_args.extend(['-m', 'not slow and not destructive'])
        pytest_args.extend(['tests/test_health.py', 'tests/test_messages.py::TestMessages::test_get_messages_list'])
    elif args.smoke:
        pytest_args.extend(['tests/test_health.py'])
    elif args.integration:
        pytest_args.extend(['tests/test_integration.py'])
    elif args.file:
        pytest_args.append(f'tests/{args.file}' if not args.file.startswith('tests/') else args.file)
    else:
        # 默认运行所有测试，但排除慢速和破坏性测试
        if not args.slow:
            if not args.destructive:
                pytest_args.extend(['-m', 'not slow and not destructive'])
            else:
                pytest_args.extend(['-m', 'not slow'])
        elif not args.destructive:
            pytest_args.extend(['-m', 'not destructive'])
    
    # 过滤器
    if args.filter:
        pytest_args.extend(['-k', args.filter])
    
    # 覆盖率
    if args.coverage:
        pytest_args.extend(['--cov=.', '--cov-report=term-missing', '--cov-report=html'])
    
    # HTML报告
    if args.html:
        pytest_args.extend(['--html=test_report.html', '--self-contained-html'])
    
    # 并行执行
    if args.parallel:
        pytest_args.extend(['-n', str(args.parallel)])
    
    # 运行测试
    return run_pytest(pytest_args)


if __name__ == '__main__':
    sys.exit(main())