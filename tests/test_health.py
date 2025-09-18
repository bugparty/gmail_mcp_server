"""
健康检查测试

测试服务器基本健康状态和连通性
"""

import pytest


class TestHealth:
    """健康检查测试类"""
    
    def test_server_health(self, api_client):
        """测试服务器健康状态"""
        response = api_client.get('/health')
        
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        # 验证timestamp格式
        assert isinstance(data['timestamp'], str)
        assert len(data['timestamp']) > 0
        
    def test_server_connectivity(self, api_client):
        """测试服务器连通性"""
        response = api_client.get('/')
        
        assert response.status_code == 200
        # 检查是否返回HTML内容
        assert 'text/html' in response.headers.get('content-type', '')
        
    def test_api_root_endpoint(self, api_client):
        """测试API根端点"""
        response = api_client.get('/api/')
        
        # API根端点可能返回404或重定向，这都是正常的
        assert response.status_code in [200, 404, 301, 302]