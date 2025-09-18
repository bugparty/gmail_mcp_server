import base64
import email
from typing import List, Optional, Dict, Any
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app.models import EmailMessage, EmailDetail, EmailListResponse

class GmailClient:
    def __init__(self, credentials: Credentials):
        self.service = build('gmail', 'v1', credentials=credentials)
    
    def list_messages(
        self, 
        query: str = "", 
        max_results: int = 10, 
        page_token: Optional[str] = None,
        label_ids: Optional[List[str]] = None
    ) -> EmailListResponse:
        """获取邮件列表"""
        try:
            request_params = {
                'userId': 'me',
                'maxResults': max_results,
                'q': query
            }
            
            if page_token:
                request_params['pageToken'] = page_token
            
            if label_ids:
                request_params['labelIds'] = label_ids
            
            result = self.service.users().messages().list(**request_params).execute()
            
            messages = []
            if 'messages' in result:
                for msg in result['messages']:
                    # 获取每个消息的基本信息
                    message_detail = self.service.users().messages().get(
                        userId='me', 
                        id=msg['id'],
                        format='metadata',
                        metadataHeaders=['Subject', 'From', 'Date']
                    ).execute()
                    
                    messages.append(EmailMessage(
                        id=message_detail['id'],
                        thread_id=message_detail['threadId'],
                        label_ids=message_detail.get('labelIds', []),
                        snippet=message_detail.get('snippet', ''),
                        payload=message_detail.get('payload', {}),
                        size_estimate=message_detail.get('sizeEstimate', 0),
                        history_id=message_detail.get('historyId', ''),
                        internal_date=message_detail.get('internalDate', '')
                    ))
            
            return EmailListResponse(
                messages=messages,
                next_page_token=result.get('nextPageToken'),
                result_size_estimate=result.get('resultSizeEstimate', 0)
            )
            
        except HttpError as error:
            raise Exception(f"Gmail API error: {error}")
    
    def get_message(self, message_id: str) -> EmailDetail:
        """获取单个邮件详情"""
        try:
            message = self.service.users().messages().get(
                userId='me', 
                id=message_id,
                format='full'
            ).execute()
            
            # 解析邮件内容
            payload = message.get('payload', {})
            headers = payload.get('headers', [])
            
            # 提取头部信息
            subject = None
            sender = None
            recipient = None
            
            for header in headers:
                name = header.get('name', '').lower()
                value = header.get('value', '')
                
                if name == 'subject':
                    subject = value
                elif name == 'from':
                    sender = value
                elif name == 'to':
                    recipient = value
            
            # 提取邮件正文
            body_text, body_html = self._extract_message_body(payload)
            
            return EmailDetail(
                id=message['id'],
                thread_id=message['threadId'],
                label_ids=message.get('labelIds', []),
                snippet=message.get('snippet', ''),
                history_id=message.get('historyId', ''),
                internal_date=message.get('internalDate', ''),
                payload=payload,
                size_estimate=message.get('sizeEstimate', 0),
                subject=subject,
                sender=sender,
                recipient=recipient,
                body_text=body_text,
                body_html=body_html
            )
            
        except HttpError as error:
            raise Exception(f"Gmail API error: {error}")
    
    def _extract_message_body(self, payload: Dict[str, Any]) -> tuple[Optional[str], Optional[str]]:
        """提取邮件正文"""
        body_text = None
        body_html = None
        
        def extract_parts(parts):
            nonlocal body_text, body_html
            
            for part in parts:
                mime_type = part.get('mimeType', '')
                
                if mime_type == 'text/plain':
                    data = part.get('body', {}).get('data')
                    if data:
                        body_text = base64.urlsafe_b64decode(data).decode('utf-8')
                
                elif mime_type == 'text/html':
                    data = part.get('body', {}).get('data')
                    if data:
                        body_html = base64.urlsafe_b64decode(data).decode('utf-8')
                
                elif 'parts' in part:
                    extract_parts(part['parts'])
        
        # 如果是简单的文本邮件
        if payload.get('mimeType') == 'text/plain':
            data = payload.get('body', {}).get('data')
            if data:
                body_text = base64.urlsafe_b64decode(data).decode('utf-8')
        
        elif payload.get('mimeType') == 'text/html':
            data = payload.get('body', {}).get('data')
            if data:
                body_html = base64.urlsafe_b64decode(data).decode('utf-8')
        
        # 如果是多部分邮件
        elif 'parts' in payload:
            extract_parts(payload['parts'])
        
        return body_text, body_html
    
    def add_labels(self, message_id: str, label_ids: List[str]) -> Dict[str, Any]:
        """给邮件添加标签"""
        try:
            result = self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'addLabelIds': label_ids}
            ).execute()
            
            return {
                'message_id': message_id,
                'label_ids': result.get('labelIds', []),
                'success': True,
                'message': 'Labels added successfully'
            }
            
        except HttpError as error:
            return {
                'message_id': message_id,
                'label_ids': [],
                'success': False,
                'message': f'Gmail API error: {error}'
            }
    
    def remove_labels(self, message_id: str, label_ids: List[str]) -> Dict[str, Any]:
        """从邮件移除标签"""
        try:
            result = self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': label_ids}
            ).execute()
            
            return {
                'message_id': message_id,
                'label_ids': result.get('labelIds', []),
                'success': True,
                'message': 'Labels removed successfully'
            }
            
        except HttpError as error:
            return {
                'message_id': message_id,
                'label_ids': [],
                'success': False,
                'message': f'Gmail API error: {error}'
            }
    
    def trash_message(self, message_id: str) -> Dict[str, Any]:
        """将邮件移动到垃圾箱"""
        try:
            result = self.service.users().messages().trash(
                userId='me',
                id=message_id
            ).execute()
            
            return {
                'message_id': message_id,
                'success': True,
                'message': 'Message moved to trash successfully'
            }
            
        except HttpError as error:
            return {
                'message_id': message_id,
                'success': False,
                'message': f'Gmail API error: {error}'
            }
    
    def get_labels(self) -> List[Dict[str, Any]]:
        """获取所有标签"""
        try:
            result = self.service.users().labels().list(userId='me').execute()
            return result.get('labels', [])
            
        except HttpError as error:
            raise Exception(f"Gmail API error: {error}")