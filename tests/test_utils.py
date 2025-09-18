"""
测试工具函数

提供测试所需的辅助功能
"""

import os
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def get_jwt_token_from_server(google_access_token: str, user_email: str = "test@example.com", base_url: str = "http://localhost:12000") -> str:
    """
    从服务器获取JWT token
    
    Args:
        google_access_token: Google访问令牌
        user_email: 用户邮箱
        base_url: 服务器基础URL
        
    Returns:
        JWT token字符串
    """
    import requests
    
    try:
        response = requests.post(
            f"{base_url}/test/generate-token",
            json={
                "google_token": google_access_token,
                "user_email": user_email
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data["api_token"]
        else:
            raise Exception(f"获取JWT token失败: {response.status_code} - {response.text}")
            
    except Exception as e:
        raise Exception(f"获取JWT token异常: {e}")

def create_test_jwt_token(google_access_token: str, user_email: str = "test@example.com") -> str:
    """
    创建测试用的JWT token（通过服务器端点）
    
    Args:
        google_access_token: Google访问令牌
        user_email: 用户邮箱
        
    Returns:
        JWT token字符串
    """
    return get_jwt_token_from_server(google_access_token, user_email)

def register_test_token_in_manager(jwt_token: str, google_access_token: str, user_email: str = "test@example.com"):
    """
    在token manager中注册测试token（已弃用）
    
    现在使用服务器端点生成token，不需要手动注册
    """
    pass