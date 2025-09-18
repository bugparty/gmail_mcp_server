"""
垃圾箱操作测试

测试邮件移动到垃圾箱的功能
"""

import pytest
import time


class TestTrash:
    """垃圾箱操作测试类"""
    
    @pytest.mark.destructive
    def test_trash_message(self, api_client, sample_messages):
        """测试移动邮件到垃圾箱"""
        # 寻找一个不在垃圾箱的邮件进行测试
        test_message_id = None
        for message in sample_messages:
            if 'TRASH' not in message.get('label_ids', []):
                test_message_id = message['id']
                break
                
        if not test_message_id:
            pytest.skip("没有找到可以移动到垃圾箱的邮件")
            
        # 记录原始标签
        original_response = api_client.get(f'/api/messages/{test_message_id}')
        assert original_response.status_code == 200
        original_labels = set(original_response.json()['label_ids'])
        
        # 移动到垃圾箱
        response = api_client.post(f'/api/messages/{test_message_id}/trash')
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证响应结构
        assert data['success'] is True
        assert 'message_id' in data
        assert data['message_id'] == test_message_id
        
        # 等待Gmail API同步
        time.sleep(2)
        
        # 验证邮件确实在垃圾箱中
        updated_response = api_client.get(f'/api/messages/{test_message_id}')
        assert updated_response.status_code == 200
        updated_data = updated_response.json()
        
        # 验证TRASH标签被添加
        assert 'TRASH' in updated_data['label_ids']
        
        # 验证INBOX标签被移除（如果原来有的话）
        if 'INBOX' in original_labels:
            assert 'INBOX' not in updated_data['label_ids']
            
    def test_trash_already_trashed_message(self, api_client, sample_messages):
        """测试移动已在垃圾箱的邮件"""
        # 寻找一个已在垃圾箱的邮件
        trashed_message_id = None
        for message in sample_messages:
            if 'TRASH' in message.get('label_ids', []):
                trashed_message_id = message['id']
                break
                
        if not trashed_message_id:
            # 如果没有垃圾箱邮件，先创建一个
            test_message_id = sample_messages[0]['id']
            trash_response = api_client.post(f'/api/messages/{test_message_id}/trash')
            if trash_response.status_code == 200:
                time.sleep(2)
                trashed_message_id = test_message_id
            else:
                pytest.skip("无法创建垃圾箱邮件进行测试")
                
        # 尝试再次移动到垃圾箱
        response = api_client.post(f'/api/messages/{trashed_message_id}/trash')
        
        # 应该成功或返回适当的状态
        assert response.status_code in [200, 400]
        
        if response.status_code == 200:
            data = response.json()
            assert data['success'] is True
            
    def test_trash_nonexistent_message(self, api_client):
        """测试移动不存在的邮件到垃圾箱"""
        fake_message_id = 'nonexistent_message_id_12345'
        response = api_client.post(f'/api/messages/{fake_message_id}/trash')
        
        assert response.status_code == 404
        
    def test_trash_invalid_message_id(self, api_client):
        """测试使用无效邮件ID移动到垃圾箱"""
        invalid_ids = ['', '   ', 'invalid-id-format']
        
        for invalid_id in invalid_ids:
            response = api_client.post(f'/api/messages/{invalid_id}/trash')
            assert response.status_code in [400, 404]
            
    @pytest.mark.slow
    def test_trash_multiple_messages_sequentially(self, api_client, sample_messages):
        """测试连续移动多个邮件到垃圾箱"""
        # 选择最多3个不在垃圾箱的邮件
        test_messages = []
        for message in sample_messages[:3]:
            if 'TRASH' not in message.get('label_ids', []):
                test_messages.append(message['id'])
                
        if len(test_messages) < 2:
            pytest.skip("没有足够的邮件进行批量垃圾箱测试")
            
        successful_operations = 0
        
        for message_id in test_messages:
            response = api_client.post(f'/api/messages/{message_id}/trash')
            if response.status_code == 200:
                successful_operations += 1
                time.sleep(1)  # 避免API限制
                
        # 至少应该有一个操作成功
        assert successful_operations > 0
        
    def test_trash_operation_idempotency(self, api_client, sample_messages):
        """测试垃圾箱操作的幂等性"""
        # 选择一个邮件进行测试
        test_message_id = sample_messages[0]['id']
        
        # 第一次移动到垃圾箱
        first_response = api_client.post(f'/api/messages/{test_message_id}/trash')
        
        if first_response.status_code != 200:
            pytest.skip("无法执行第一次垃圾箱操作")
            
        time.sleep(2)
        
        # 第二次移动到垃圾箱（应该是幂等的）
        second_response = api_client.post(f'/api/messages/{test_message_id}/trash')
        
        # 两次操作都应该成功或第二次返回适当的状态
        assert second_response.status_code in [200, 400]
        
        # 验证邮件仍在垃圾箱中
        verify_response = api_client.get(f'/api/messages/{test_message_id}')
        if verify_response.status_code == 200:
            verify_data = verify_response.json()
            assert 'TRASH' in verify_data['label_ids']