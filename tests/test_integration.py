"""
集成测试

测试完整的工作流程和端到端功能
"""

import pytest
import time


class TestIntegration:
    """集成测试类"""
    
    @pytest.mark.slow
    def test_complete_email_workflow(self, api_client, server_health_check):
        """测试完整的邮件处理工作流程"""
        # 1. 获取邮件列表
        messages_response = api_client.get('/api/messages?max_results=3')
        assert messages_response.status_code == 200
        messages_data = messages_response.json()
        assert len(messages_data['messages']) > 0
        
        test_message_id = messages_data['messages'][0]['id']
        
        # 2. 获取单个邮件详情
        message_response = api_client.get(f'/api/messages/{test_message_id}')
        assert message_response.status_code == 200
        message_data = message_response.json()
        assert message_data['id'] == test_message_id
        
        original_labels = set(message_data['label_ids'])
        
        # 3. 添加标签
        add_label_data = {
            "message_id": test_message_id,
            "label_ids": ["IMPORTANT"]
        }
        add_response = api_client.post(f'/api/messages/{test_message_id}/labels', json=add_label_data)
        assert add_response.status_code == 200
        assert add_response.json()['success'] is True
        
        time.sleep(1)  # 等待同步
        
        # 4. 验证标签已添加
        updated_message_response = api_client.get(f'/api/messages/{test_message_id}')
        assert updated_message_response.status_code == 200
        updated_message_data = updated_message_response.json()
        assert 'IMPORTANT' in updated_message_data['label_ids']
        
        # 5. 移除标签
        remove_label_data = {
            "message_id": test_message_id,
            "label_ids": ["IMPORTANT"]
        }
        remove_response = api_client.delete(f'/api/messages/{test_message_id}/labels', json=remove_label_data)
        assert remove_response.status_code == 200
        assert remove_response.json()['success'] is True
        
        time.sleep(1)  # 等待同步
        
        # 6. 验证标签已移除
        final_message_response = api_client.get(f'/api/messages/{test_message_id}')
        assert final_message_response.status_code == 200
        final_message_data = final_message_response.json()
        assert 'IMPORTANT' not in final_message_data['label_ids']
        
    @pytest.mark.slow
    @pytest.mark.destructive
    def test_trash_and_label_workflow(self, api_client, sample_messages):
        """测试垃圾箱和标签的组合工作流程"""
        # 选择一个不在垃圾箱的邮件
        test_message_id = None
        for message in sample_messages:
            if 'TRASH' not in message.get('label_ids', []):
                test_message_id = message['id']
                break
                
        if not test_message_id:
            pytest.skip("没有找到可用于测试的邮件")
            
        # 1. 添加标签
        add_label_data = {
            "message_id": test_message_id,
            "label_ids": ["STARRED"]
        }
        add_response = api_client.post(f'/api/messages/{test_message_id}/labels', json=add_label_data)
        assert add_response.status_code == 200
        
        time.sleep(1)
        
        # 2. 验证标签已添加
        message_response = api_client.get(f'/api/messages/{test_message_id}')
        assert message_response.status_code == 200
        assert 'STARRED' in message_response.json()['label_ids']
        
        # 3. 移动到垃圾箱
        trash_response = api_client.post(f'/api/messages/{test_message_id}/trash')
        assert trash_response.status_code == 200
        assert trash_response.json()['success'] is True
        
        time.sleep(2)
        
        # 4. 验证邮件在垃圾箱中且保留了STARRED标签
        trashed_message_response = api_client.get(f'/api/messages/{test_message_id}')
        assert trashed_message_response.status_code == 200
        trashed_message_data = trashed_message_response.json()
        assert 'TRASH' in trashed_message_data['label_ids']
        assert 'STARRED' in trashed_message_data['label_ids']  # 标签应该保留
        
    def test_mcp_and_api_consistency(self, api_client, server_health_check):
        """测试MCP工具定义与实际API的一致性"""
        # 获取MCP工具定义
        mcp_response = api_client.get('/mcp/tools')
        assert mcp_response.status_code == 200
        mcp_data = mcp_response.json()
        
        tool_names = [tool['name'] for tool in mcp_data['tools']]
        
        # 验证每个MCP工具对应的API端点都存在
        api_tests = [
            ('list_gmail_messages', '/api/messages'),
            ('get_gmail_labels', '/api/labels'),
        ]
        
        for tool_name, api_endpoint in api_tests:
            assert tool_name in tool_names, f"MCP工具{tool_name}不存在"
            
            # 测试对应的API端点
            api_response = api_client.get(api_endpoint)
            assert api_response.status_code == 200, f"API端点{api_endpoint}不可用"
            
    def test_error_handling_consistency(self, api_client):
        """测试错误处理的一致性"""
        # 测试各种无效请求的错误处理
        error_tests = [
            ('/api/messages/invalid_id', 404),
            ('/api/messages/', 404),  # 缺少邮件ID
            ('/api/nonexistent', 404),
        ]
        
        for endpoint, expected_status in error_tests:
            response = api_client.get(endpoint)
            assert response.status_code == expected_status, f"端点{endpoint}返回了意外的状态码"
            
    @pytest.mark.slow
    def test_performance_baseline(self, api_client, server_health_check):
        """测试性能基线"""
        import time
        
        # 测试健康检查响应时间
        start_time = time.time()
        health_response = api_client.get('/health')
        health_time = time.time() - start_time
        
        assert health_response.status_code == 200
        assert health_time < 1.0, f"健康检查响应时间过长: {health_time:.2f}秒"
        
        # 测试邮件列表响应时间
        start_time = time.time()
        messages_response = api_client.get('/api/messages?max_results=5')
        messages_time = time.time() - start_time
        
        assert messages_response.status_code == 200
        assert messages_time < 5.0, f"邮件列表响应时间过长: {messages_time:.2f}秒"
        
        # 测试标签列表响应时间
        start_time = time.time()
        labels_response = api_client.get('/api/labels')
        labels_time = time.time() - start_time
        
        assert labels_response.status_code == 200
        assert labels_time < 3.0, f"标签列表响应时间过长: {labels_time:.2f}秒"
        
    def test_concurrent_requests(self, api_client, server_health_check):
        """测试并发请求处理"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            try:
                response = api_client.get('/health')
                results.put(('success', response.status_code))
            except Exception as e:
                results.put(('error', str(e)))
                
        # 创建5个并发请求
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
            
        # 等待所有线程完成
        for thread in threads:
            thread.join(timeout=10)
            
        # 检查结果
        success_count = 0
        while not results.empty():
            result_type, result_value = results.get()
            if result_type == 'success' and result_value == 200:
                success_count += 1
                
        # 至少应该有大部分请求成功
        assert success_count >= 3, f"并发请求成功率过低: {success_count}/5"
        
    def test_data_consistency(self, api_client, sample_message_id):
        """测试数据一致性"""
        # 多次获取同一邮件，验证数据一致性
        responses = []
        for _ in range(3):
            response = api_client.get(f'/api/messages/{sample_message_id}')
            assert response.status_code == 200
            responses.append(response.json())
            time.sleep(0.5)
            
        # 验证所有响应的核心数据一致
        first_response = responses[0]
        for response in responses[1:]:
            assert response['id'] == first_response['id']
            assert response['thread_id'] == first_response['thread_id']
            # 标签可能会变化，但基本结构应该一致
            assert 'label_ids' in response
            assert 'payload' in response