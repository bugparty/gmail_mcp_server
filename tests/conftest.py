"""
pytest配置文件

定义测试fixtures和全局配置
"""

import os
import pytest
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

@pytest.fixture(scope="session")
def base_url():
    """测试服务器基础URL"""
    return os.getenv('TEST_SERVER_URL', 'http://localhost:12000')

@pytest.fixture(scope="session")
def google_access_token():
    """Google访问令牌"""
    token = os.getenv('TEST_ACCESS_TOKEN')
    if not token:
        pytest.skip("未找到访问令牌，请设置 TEST_ACCESS_TOKEN 环境变量")
    return token

@pytest.fixture(scope="session")
def jwt_token(google_access_token):
    """JWT访问令牌"""
    from tests.test_utils import create_test_jwt_token, register_test_token_in_manager
    
    # 创建JWT token
    jwt_token = create_test_jwt_token(google_access_token)
    
    # 在token manager中注册
    register_test_token_in_manager(jwt_token, google_access_token)
    
    return jwt_token

@pytest.fixture(scope="session")
def auth_headers(jwt_token):
    """认证请求头"""
    return {
        'Authorization': f'Bearer {jwt_token}',
        'Content-Type': 'application/json'
    }

@pytest.fixture(scope="session")
def api_client(base_url, auth_headers):
    """API客户端"""
    class APIClient:
        def __init__(self, base_url, headers):
            self.base_url = base_url
            self.headers = headers
            self.session = requests.Session()
            self.session.headers.update(headers)
            
        def get(self, endpoint, **kwargs):
            """GET请求"""
            url = f"{self.base_url}{endpoint}"
            return self.session.get(url, timeout=30, **kwargs)
            
        def post(self, endpoint, **kwargs):
            """POST请求"""
            url = f"{self.base_url}{endpoint}"
            return self.session.post(url, timeout=30, **kwargs)
            
        def delete(self, endpoint, **kwargs):
            """DELETE请求"""
            url = f"{self.base_url}{endpoint}"
            return self.session.delete(url, timeout=30, **kwargs)
    
    return APIClient(base_url, auth_headers)

@pytest.fixture(scope="session")
def server_health_check(base_url):
    """服务器健康检查"""
    import requests
    try:
        response = requests.get(f'{base_url}/health', timeout=10)
        if response.status_code != 200 or response.json().get('status') != 'healthy':
            pytest.skip("服务器未运行或不健康，请先启动服务器")
        return True
    except Exception as e:
        pytest.skip(f"无法连接到服务器: {e}")

@pytest.fixture(scope="session")
def sample_messages(api_client, server_health_check):
    """获取示例邮件数据"""
    response = api_client.get('/api/messages?max_results=5')
    if response.status_code != 200:
        pytest.skip("无法获取邮件列表")
    
    data = response.json()
    messages = data.get('messages', [])
    if not messages:
        pytest.skip("邮箱中没有邮件")
    
    return messages

@pytest.fixture(scope="session")
def sample_message_id(sample_messages):
    """获取示例邮件ID"""
    return sample_messages[0]['id']

@pytest.fixture(scope="session")
def gmail_labels(api_client, server_health_check):
    """获取Gmail标签列表"""
    response = api_client.get('/api/labels')
    if response.status_code != 200:
        pytest.skip("无法获取标签列表")
    
    return response.json()

# pytest配置
def pytest_configure(config):
    """pytest配置"""
    config.addinivalue_line(
        "markers", "slow: 标记测试为慢速测试"
    )
    config.addinivalue_line(
        "markers", "integration: 标记测试为集成测试"
    )
    config.addinivalue_line(
        "markers", "destructive: 标记测试为破坏性测试（会修改数据）"
    )

def pytest_collection_modifyitems(config, items):
    """修改测试收集"""
    # 为所有测试添加integration标记
    for item in items:
        item.add_marker(pytest.mark.integration)