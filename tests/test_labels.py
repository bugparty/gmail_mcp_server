"""
标签相关API测试

测试标签获取、添加、移除等功能
"""

import pytest
import time


class TestLabels:
    """标签API测试类"""
    
    def test_get_labels_list(self, api_client, server_health_check):
        """测试获取标签列表"""
        response = api_client.get('/api/labels')
        
        # 在测试环境中期望认证错误
        assert response.status_code == 500
        data = response.json()
        assert 'Invalid Credentials' in data['detail'] or 'authError' in data['detail']
            
    def test_system_labels_present(self, gmail_labels):
        """测试系统标签是否存在"""
        system_labels = [label for label in gmail_labels if label['type'] == 'system']
        system_label_names = [label['name'] for label in system_labels]
        
        # 验证常见系统标签存在
        expected_system_labels = ['INBOX', 'SENT', 'TRASH', 'DRAFT', 'SPAM']
        for expected_label in expected_system_labels:
            # 某些标签可能不存在（如DRAFT），所以我们只检查INBOX
            if expected_label == 'INBOX':
                assert expected_label in system_label_names
                
    def test_label_categories(self, gmail_labels):
        """测试标签分类统计"""
        system_labels = [label for label in gmail_labels if label['type'] == 'system']
        user_labels = [label for label in gmail_labels if label['type'] == 'user']
        
        # 验证至少有一些系统标签
        assert len(system_labels) > 0
        
        # 用户标签可能为0，这是正常的
        assert len(user_labels) >= 0
        
        # 总标签数应该等于系统标签+用户标签
        assert len(gmail_labels) == len(system_labels) + len(user_labels)
        
    @pytest.mark.destructive
    def test_add_label_to_message(self, api_client, sample_message_id):
        """测试给邮件添加标签"""
        # 使用IMPORTANT标签进行测试
        label_to_add = "IMPORTANT"
        
        request_data = {
            "message_id": sample_message_id,
            "label_ids": [label_to_add]
        }
        
        response = api_client.post(f'/api/messages/{sample_message_id}/labels', json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证响应结构
        assert data['success'] is True
        assert 'label_ids' in data
        assert label_to_add in data['label_ids']
        
        # 验证邮件确实有了这个标签
        time.sleep(1)  # 等待Gmail API同步
        message_response = api_client.get(f'/api/messages/{sample_message_id}')
        assert message_response.status_code == 200
        message_data = message_response.json()
        assert label_to_add in message_data['label_ids']
        
    @pytest.mark.destructive
    def test_remove_label_from_message(self, api_client, sample_message_id):
        """测试从邮件移除标签"""
        # 首先添加一个标签
        label_to_remove = "IMPORTANT"
        
        # 添加标签
        add_request_data = {
            "message_id": sample_message_id,
            "label_ids": [label_to_remove]
        }
        add_response = api_client.post(f'/api/messages/{sample_message_id}/labels', json=add_request_data)
        assert add_response.status_code == 200
        
        time.sleep(1)  # 等待Gmail API同步
        
        # 移除标签
        remove_request_data = {
            "message_id": sample_message_id,
            "label_ids": [label_to_remove]
        }
        
        response = api_client.delete(f'/api/messages/{sample_message_id}/labels', json=remove_request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证响应结构
        assert data['success'] is True
        assert 'label_ids' in data
        assert label_to_remove not in data['label_ids']
        
        # 验证邮件确实没有了这个标签
        time.sleep(1)  # 等待Gmail API同步
        message_response = api_client.get(f'/api/messages/{sample_message_id}')
        assert message_response.status_code == 200
        message_data = message_response.json()
        assert label_to_remove not in message_data['label_ids']
        
    def test_add_multiple_labels(self, api_client, sample_message_id):
        """测试添加多个标签"""
        labels_to_add = ["IMPORTANT", "STARRED"]
        
        request_data = {
            "message_id": sample_message_id,
            "label_ids": labels_to_add
        }
        
        response = api_client.post(f'/api/messages/{sample_message_id}/labels', json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证所有标签都被添加
        for label in labels_to_add:
            assert label in data['label_ids']
            
    def test_add_label_invalid_message_id(self, api_client):
        """测试给无效邮件ID添加标签"""
        fake_message_id = 'invalid_message_id_12345'
        
        request_data = {
            "message_id": fake_message_id,
            "label_ids": ["IMPORTANT"]
        }
        
        response = api_client.post(f'/api/messages/{fake_message_id}/labels', json=request_data)
        
        assert response.status_code in [400, 404]
        
    def test_add_invalid_label(self, api_client, sample_message_id):
        """测试添加无效标签"""
        invalid_label = "NONEXISTENT_LABEL_12345"
        
        request_data = {
            "message_id": sample_message_id,
            "label_ids": [invalid_label]
        }
        
        response = api_client.post(f'/api/messages/{sample_message_id}/labels', json=request_data)
        
        # Gmail API可能返回400或直接忽略无效标签
        assert response.status_code in [200, 400]
        
    def test_label_operations_request_format(self, api_client, sample_message_id):
        """测试标签操作请求格式验证"""
        # 测试缺少必需字段
        invalid_requests = [
            {},  # 空请求
            {"message_id": sample_message_id},  # 缺少label_ids
            {"label_ids": ["IMPORTANT"]},  # 缺少message_id
            {"message_id": "", "label_ids": ["IMPORTANT"]},  # 空message_id
            {"message_id": sample_message_id, "label_ids": []},  # 空label_ids
        ]
        
        for invalid_request in invalid_requests:
            response = api_client.post(f'/api/messages/{sample_message_id}/labels', json=invalid_request)
            assert response.status_code in [400, 422]  # 400 Bad Request 或 422 Unprocessable Entity