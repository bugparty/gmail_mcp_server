"""
MCP协议相关测试

测试MCP工具定义和协议兼容性
"""

import pytest


class TestMCP:
    """MCP协议测试类"""
    
    def test_mcp_tools_endpoint(self, api_client, server_health_check):
        """测试MCP工具定义端点"""
        response = api_client.get('/mcp/tools')
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证响应结构
        assert 'tools' in data
        assert isinstance(data['tools'], list)
        assert len(data['tools']) > 0
        
    def test_mcp_tools_structure(self, api_client, server_health_check):
        """测试MCP工具定义结构"""
        response = api_client.get('/mcp/tools')
        data = response.json()
        
        tools = data['tools']
        
        # 验证每个工具的结构
        for tool in tools:
            assert 'name' in tool
            assert 'description' in tool
            assert 'input_schema' in tool
            
            # 验证基本字段类型
            assert isinstance(tool['name'], str)
            assert isinstance(tool['description'], str)
            assert isinstance(tool['input_schema'], dict)
            
            # 验证名称不为空
            assert len(tool['name']) > 0
            assert len(tool['description']) > 0
            
    def test_expected_mcp_tools(self, api_client, server_health_check):
        """测试预期的MCP工具是否存在"""
        response = api_client.get('/mcp/tools')
        data = response.json()
        
        tool_names = [tool['name'] for tool in data['tools']]
        
        # 验证预期的工具存在
        expected_tools = [
            'list_gmail_messages',
            'get_gmail_message',
            'add_gmail_labels',
            'remove_gmail_labels',
            'trash_gmail_message',
            'get_gmail_labels'
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names, f"缺少预期的MCP工具: {expected_tool}"
            
    def test_mcp_tool_schemas(self, api_client, server_health_check):
        """测试MCP工具的输入模式"""
        response = api_client.get('/mcp/tools')
        data = response.json()
        
        for tool in data['tools']:
            schema = tool['input_schema']
            
            # 验证schema基本结构
            assert 'type' in schema
            assert schema['type'] == 'object'
            
            # 大多数工具应该有properties
            if 'properties' in schema:
                assert isinstance(schema['properties'], dict)
                
            # 如果有required字段，应该是列表
            if 'required' in schema:
                assert isinstance(schema['required'], list)
                
    def test_list_messages_tool_schema(self, api_client, server_health_check):
        """测试list_gmail_messages工具的模式"""
        response = api_client.get('/mcp/tools')
        data = response.json()
        
        list_tool = None
        for tool in data['tools']:
            if tool['name'] == 'list_gmail_messages':
                list_tool = tool
                break
                
        assert list_tool is not None, "未找到list_gmail_messages工具"
        
        schema = list_tool['input_schema']
        properties = schema.get('properties', {})
        
        # 验证预期的参数
        expected_params = ['max_results', 'query', 'page_token']
        for param in expected_params:
            if param in properties:
                param_schema = properties[param]
                assert 'type' in param_schema
                
    def test_get_message_tool_schema(self, api_client, server_health_check):
        """测试get_gmail_message工具的模式"""
        response = api_client.get('/mcp/tools')
        data = response.json()
        
        get_tool = None
        for tool in data['tools']:
            if tool['name'] == 'get_gmail_message':
                get_tool = tool
                break
                
        assert get_tool is not None, "未找到get_gmail_message工具"
        
        schema = get_tool['input_schema']
        properties = schema.get('properties', {})
        
        # 应该有message_id参数
        assert 'message_id' in properties
        assert properties['message_id']['type'] == 'string'
        
        # message_id应该是必需的
        required = schema.get('required', [])
        assert 'message_id' in required
        
    def test_label_tools_schema(self, api_client, server_health_check):
        """测试标签操作工具的模式"""
        response = api_client.get('/mcp/tools')
        data = response.json()
        
        label_tools = ['add_gmail_labels', 'remove_gmail_labels']
        
        for tool_name in label_tools:
            tool = None
            for t in data['tools']:
                if t['name'] == tool_name:
                    tool = t
                    break
                    
            assert tool is not None, f"未找到{tool_name}工具"
            
            schema = tool['input_schema']
            properties = schema.get('properties', {})
            
            # 应该有message_id和label_ids参数
            assert 'message_id' in properties
            assert 'label_ids' in properties
            
            # 验证参数类型
            assert properties['message_id']['type'] == 'string'
            assert properties['label_ids']['type'] == 'array'
            
            # 验证必需参数
            required = schema.get('required', [])
            assert 'message_id' in required
            assert 'label_ids' in required
            
    def test_trash_tool_schema(self, api_client, server_health_check):
        """测试垃圾箱工具的模式"""
        response = api_client.get('/mcp/tools')
        data = response.json()
        
        trash_tool = None
        for tool in data['tools']:
            if tool['name'] == 'trash_gmail_message':
                trash_tool = tool
                break
                
        assert trash_tool is not None, "未找到trash_gmail_message工具"
        
        schema = trash_tool['input_schema']
        properties = schema.get('properties', {})
        
        # 应该有message_id参数
        assert 'message_id' in properties
        assert properties['message_id']['type'] == 'string'
        
        # message_id应该是必需的
        required = schema.get('required', [])
        assert 'message_id' in required
        
    def test_mcp_tool_descriptions(self, api_client, server_health_check):
        """测试MCP工具描述的质量"""
        response = api_client.get('/mcp/tools')
        data = response.json()
        
        for tool in data['tools']:
            description = tool['description']
            
            # 描述应该有合理的长度
            assert len(description) >= 10, f"工具{tool['name']}的描述太短"
            assert len(description) <= 200, f"工具{tool['name']}的描述太长"
            
            # 描述应该包含工具名称的关键词
            tool_name_parts = tool['name'].split('_')
            for part in tool_name_parts:
                if part not in ['gmail', 'get', 'add', 'remove']:  # 跳过通用词
                    # 描述中应该包含相关的关键词
                    assert any(keyword in description.lower() for keyword in [part, part[:-1], part + 's'])
                    
    def test_mcp_response_format(self, api_client, server_health_check):
        """测试MCP响应格式的一致性"""
        response = api_client.get('/mcp/tools')
        
        # 验证Content-Type
        content_type = response.headers.get('content-type', '')
        assert 'application/json' in content_type
        
        # 验证响应可以被正确解析为JSON
        data = response.json()
        assert isinstance(data, dict)
        
        # 验证顶级结构
        assert 'tools' in data
        assert len(data.keys()) >= 1  # 至少有tools字段