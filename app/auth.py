import json
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from config.settings import settings

class TokenManager:
    def __init__(self):
        self.tokens: Dict[str, Dict[str, Any]] = {}
    
    def generate_api_token(self, user_email: str, google_credentials: Credentials) -> str:
        """生成API访问token"""
        token_data = {
            "user_email": user_email,
            "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            "iat": datetime.utcnow(),
            "type": "api_access"
        }
        
        api_token = jwt.encode(token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        # 存储用户的Google凭据
        self.tokens[api_token] = {
            "user_email": user_email,
            "google_credentials": {
                "token": google_credentials.token,
                "refresh_token": google_credentials.refresh_token,
                "token_uri": google_credentials.token_uri,
                "client_id": google_credentials.client_id,
                "client_secret": google_credentials.client_secret,
                "scopes": google_credentials.scopes
            },
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        
        return api_token
    
    def verify_api_token(self, token: str) -> Optional[Dict[str, Any]]:
        """验证API token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_email: str = payload.get("user_email")
            if user_email is None:
                return None
            
            # 检查token是否在存储中
            if token not in self.tokens:
                return None
            
            token_data = self.tokens[token]
            
            # 检查是否过期
            if datetime.utcnow() > token_data["expires_at"]:
                del self.tokens[token]
                return None
            
            return token_data
            
        except JWTError:
            return None
    
    def get_google_credentials(self, token: str) -> Optional[Credentials]:
        """获取Google凭据"""
        token_data = self.verify_api_token(token)
        if not token_data:
            return None
        
        cred_data = token_data["google_credentials"]
        credentials = Credentials(
            token=cred_data["token"],
            refresh_token=cred_data["refresh_token"],
            token_uri=cred_data["token_uri"],
            client_id=cred_data["client_id"],
            client_secret=cred_data["client_secret"],
            scopes=cred_data["scopes"]
        )
        
        # 如果token过期，尝试刷新
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
            # 更新存储的token
            self.tokens[token]["google_credentials"]["token"] = credentials.token
        
        return credentials

class GoogleOAuthManager:
    def __init__(self):
        self.flow = None
    
    def create_authorization_url(self) -> tuple[str, str]:
        """创建OAuth授权URL"""
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            raise ValueError("Google OAuth credentials not configured")
        
        client_config = {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI]
            }
        }
        
        self.flow = Flow.from_client_config(
            client_config,
            scopes=settings.GMAIL_SCOPES,
            redirect_uri=settings.GOOGLE_REDIRECT_URI
        )
        
        authorization_url, state = self.flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        return authorization_url, state
    
    def exchange_code_for_credentials(self, authorization_code: str, state: str) -> Credentials:
        """交换授权码获取凭据"""
        if not self.flow:
            raise ValueError("OAuth flow not initialized")
        
        self.flow.fetch_token(code=authorization_code)
        return self.flow.credentials
    
    def get_user_info(self, credentials: Credentials) -> Dict[str, Any]:
        """获取用户信息"""
        service = build('gmail', 'v1', credentials=credentials)
        profile = service.users().getProfile(userId='me').execute()
        return {
            "email": profile.get('emailAddress'),
            "messages_total": profile.get('messagesTotal', 0),
            "threads_total": profile.get('threadsTotal', 0)
        }

# 全局实例
token_manager = TokenManager()
oauth_manager = GoogleOAuthManager()