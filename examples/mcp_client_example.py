#!/usr/bin/env python3
"""
Gmail MCP Client 示例
演示如何使用Python客户端调用Gmail MCP服务器
"""

import requests
import json
from typing import List, Dict, Any, Optional

class GmailMCPClient:
    """Gmail MCP客户端"""
    
    def __init__(self, base_url: str, token: str):
        """
        初始化客户端
        
        Args:
            base_url: MCP服务器基础URL，例如 http://localhost:12000
            token: 从Web界面获取的访问令牌
        """
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def list_messages(
        self, 
        query: str = "", 
        max_results: int = 10,
        page_token: Optional[str] = None,
        label_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        获取邮件列表
        
        Args:
            query: 搜索查询，例如 "from:example@gmail.com"
            max_results: 最大结果数 (1-100)
            page_token: 分页令牌
            label_ids: 标签ID列表，例如 ["INBOX", "UNREAD"]
        
        Returns:
            包含邮件列表的字典
        """
        params = {
            "q": query,
            "max_results": max_results
        }
        
        if page_token:
            params["page_token"] = page_token
        
        if label_ids:
            params["label_ids"] = ",".join(label_ids)
        
        response = requests.get(
            f"{self.base_url}/api/messages",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_message(self, message_id: str) -> Dict[str, Any]:
        """
        获取单个邮件详情
        
        Args:
            message_id: 邮件ID
        
        Returns:
            邮件详情字典
        """
        response = requests.get(
            f"{self.base_url}/api/messages/{message_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def add_labels(self, message_id: str, label_ids: List[str]) -> Dict[str, Any]:
        """
        给邮件添加标签
        
        Args:
            message_id: 邮件ID
            label_ids: 要添加的标签ID列表
        
        Returns:
            操作结果
        """
        data = {
            "message_id": message_id,
            "label_ids": label_ids
        }
        
        response = requests.post(
            f"{self.base_url}/api/messages/{message_id}/labels",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def remove_labels(self, message_id: str, label_ids: List[str]) -> Dict[str, Any]:
        """
        从邮件移除标签
        
        Args:
            message_id: 邮件ID
            label_ids: 要移除的标签ID列表
        
        Returns:
            操作结果
        """
        data = {
            "message_id": message_id,
            "label_ids": label_ids
        }
        
        response = requests.delete(
            f"{self.base_url}/api/messages/{message_id}/labels",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def trash_message(self, message_id: str) -> Dict[str, Any]:
        """
        将邮件移动到垃圾箱
        
        Args:
            message_id: 邮件ID
        
        Returns:
            操作结果
        """
        response = requests.post(
            f"{self.base_url}/api/messages/{message_id}/trash",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_labels(self) -> List[Dict[str, Any]]:
        """
        获取所有标签
        
        Returns:
            标签列表
        """
        response = requests.get(
            f"{self.base_url}/api/labels",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_mcp_tools(self) -> Dict[str, Any]:
        """
        获取MCP工具定义
        
        Returns:
            MCP工具定义
        """
        response = requests.get(f"{self.base_url}/mcp/tools")
        response.raise_for_status()
        return response.json()

def main():
    """示例用法"""
    # 配置客户端
    BASE_URL = "http://localhost:12000"
    TOKEN = "YOUR_ACCESS_TOKEN_HERE"  # 替换为实际的访问令牌
    
    # 创建客户端
    client = GmailMCPClient(BASE_URL, TOKEN)
    
    try:
        print("🔧 获取MCP工具定义...")
        tools = client.get_mcp_tools()
        print(f"可用工具数量: {len(tools['tools'])}")
        for tool in tools['tools']:
            print(f"  - {tool['name']}: {tool['description']}")
        
        print("\n📧 获取最新的5封邮件...")
        messages = client.list_messages(max_results=5)
        print(f"找到 {len(messages['messages'])} 封邮件")
        
        for msg in messages['messages'][:3]:  # 只显示前3封
            print(f"\n邮件ID: {msg['id']}")
            print(f"摘要: {msg['snippet'][:100]}...")
            
            # 获取详细信息
            detail = client.get_message(msg['id'])
            print(f"主题: {detail.get('subject', 'N/A')}")
            print(f"发件人: {detail.get('sender', 'N/A')}")
            print(f"标签: {', '.join(detail.get('label_ids', []))}")
        
        print("\n🏷️ 获取所有标签...")
        labels = client.get_labels()
        print(f"标签数量: {len(labels)}")
        for label in labels[:5]:  # 只显示前5个
            print(f"  - {label.get('name', label.get('id'))}")
        
        # 示例：搜索特定邮件
        print("\n🔍 搜索未读邮件...")
        unread_messages = client.list_messages(
            query="is:unread",
            max_results=3
        )
        print(f"未读邮件数量: {len(unread_messages['messages'])}")
        
        # 注意：以下操作会修改邮件，请谨慎使用
        if False:  # 设置为True以启用修改操作
            if messages['messages']:
                message_id = messages['messages'][0]['id']
                
                print(f"\n🏷️ 给邮件 {message_id} 添加标签...")
                result = client.add_labels(message_id, ["IMPORTANT"])
                print(f"操作结果: {result['success']}")
                
                print(f"\n🗑️ 将邮件 {message_id} 移动到垃圾箱...")
                result = client.trash_message(message_id)
                print(f"操作结果: {result['success']}")
        
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP错误: {e}")
        if e.response.status_code == 401:
            print("请检查访问令牌是否正确或已过期")
    except requests.exceptions.ConnectionError:
        print("❌ 连接错误: 无法连接到MCP服务器")
        print("请确保服务器正在运行在 http://localhost:12000")
    except Exception as e:
        print(f"❌ 未知错误: {e}")

if __name__ == "__main__":
    main()