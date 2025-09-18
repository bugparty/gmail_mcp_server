from fastapi import FastAPI, Request, HTTPException, Depends, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime
import uvicorn

from config.settings import settings
from app.auth import oauth_manager, token_manager
from app.gmail_client import GmailClient
from app.models import (
    EmailListResponse, EmailDetail, LabelRequest, LabelResponse, 
    TrashRequest, TrashResponse, APITokenResponse, MCPResponse, MCPToolDefinition
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Gmail MCP Server - 让其他LLM可以访问您的Gmail"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 设置模板和静态文件
templates = Jinja2Templates(directory="templates")
security = HTTPBearer()

# 依赖函数：验证API token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    token_data = token_manager.verify_api_token(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return token_data

# 依赖函数：获取Gmail客户端
async def get_gmail_client(credentials: HTTPAuthorizationCredentials = Depends(security)) -> GmailClient:
    token = credentials.credentials
    google_credentials = token_manager.get_google_credentials(token)
    if not google_credentials:
        raise HTTPException(status_code=401, detail="Unable to get Google credentials")
    return GmailClient(google_credentials)

# Web界面路由
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """首页"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/auth/login")
async def login():
    """开始OAuth登录流程"""
    try:
        authorization_url, state = oauth_manager.create_authorization_url()
        return RedirectResponse(url=authorization_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth configuration error: {str(e)}")

@app.get("/auth/callback")
async def auth_callback(request: Request, code: str = None, state: str = None, error: str = None):
    """OAuth回调处理"""
    if error:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error_message": f"OAuth error: {error}"
        })
    
    if not code:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error_message": "Authorization code not received"
        })
    
    try:
        # 交换授权码获取凭据
        credentials = oauth_manager.exchange_code_for_credentials(code, state)
        
        # 获取用户信息
        user_info = oauth_manager.get_user_info(credentials)
        user_email = user_info.get("email")
        
        if not user_email:
            raise Exception("Unable to get user email")
        
        # 生成API token
        api_token = token_manager.generate_api_token(user_email, credentials)
        
        # 构建API URL
        api_url = f"http://{settings.HOST}:{settings.PORT}/api"
        expires_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        
        return templates.TemplateResponse("success.html", {
            "request": request,
            "user_email": user_email,
            "api_url": api_url,
            "token": api_token,
            "expires_at": expires_at
        })
        
    except Exception as e:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "error_message": str(e)
        })

# API路由
@app.get("/api/messages", response_model=EmailListResponse)
async def list_messages(
    gmail_client: GmailClient = Depends(get_gmail_client),
    q: str = Query("", description="搜索查询"),
    max_results: int = Query(10, ge=1, le=100, description="最大结果数"),
    page_token: Optional[str] = Query(None, description="分页token"),
    label_ids: Optional[str] = Query(None, description="标签ID，多个用逗号分隔")
):
    """获取邮件列表"""
    try:
        label_list = label_ids.split(",") if label_ids else None
        return gmail_client.list_messages(
            query=q,
            max_results=max_results,
            page_token=page_token,
            label_ids=label_list
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/messages/{message_id}", response_model=EmailDetail)
async def get_message(
    message_id: str,
    gmail_client: GmailClient = Depends(get_gmail_client)
):
    """获取单个邮件详情"""
    try:
        return gmail_client.get_message(message_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/messages/{message_id}/labels", response_model=LabelResponse)
async def add_labels(
    message_id: str,
    request: LabelRequest,
    gmail_client: GmailClient = Depends(get_gmail_client)
):
    """给邮件添加标签"""
    try:
        result = gmail_client.add_labels(message_id, request.label_ids)
        return LabelResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/messages/{message_id}/labels", response_model=LabelResponse)
async def remove_labels(
    message_id: str,
    request: LabelRequest,
    gmail_client: GmailClient = Depends(get_gmail_client)
):
    """从邮件移除标签"""
    try:
        result = gmail_client.remove_labels(message_id, request.label_ids)
        return LabelResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/messages/{message_id}/trash", response_model=TrashResponse)
async def trash_message(
    message_id: str,
    gmail_client: GmailClient = Depends(get_gmail_client)
):
    """将邮件移动到垃圾箱"""
    try:
        result = gmail_client.trash_message(message_id)
        return TrashResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/labels")
async def get_labels(gmail_client: GmailClient = Depends(get_gmail_client)):
    """获取所有标签"""
    try:
        return gmail_client.get_labels()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# MCP协议支持
@app.get("/mcp/tools", response_model=MCPResponse)
async def get_mcp_tools():
    """获取MCP工具定义"""
    tools = [
        MCPToolDefinition(
            name="list_gmail_messages",
            description="获取Gmail邮件列表，支持搜索和分页",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索查询"},
                    "max_results": {"type": "integer", "description": "最大结果数", "default": 10},
                    "page_token": {"type": "string", "description": "分页token"},
                    "label_ids": {"type": "string", "description": "标签ID，多个用逗号分隔"}
                }
            }
        ),
        MCPToolDefinition(
            name="get_gmail_message",
            description="获取单个Gmail邮件的详细内容",
            input_schema={
                "type": "object",
                "properties": {
                    "message_id": {"type": "string", "description": "邮件ID"}
                },
                "required": ["message_id"]
            }
        ),
        MCPToolDefinition(
            name="add_gmail_labels",
            description="给Gmail邮件添加标签",
            input_schema={
                "type": "object",
                "properties": {
                    "message_id": {"type": "string", "description": "邮件ID"},
                    "label_ids": {"type": "array", "items": {"type": "string"}, "description": "要添加的标签ID列表"}
                },
                "required": ["message_id", "label_ids"]
            }
        ),
        MCPToolDefinition(
            name="remove_gmail_labels",
            description="从Gmail邮件移除标签",
            input_schema={
                "type": "object",
                "properties": {
                    "message_id": {"type": "string", "description": "邮件ID"},
                    "label_ids": {"type": "array", "items": {"type": "string"}, "description": "要移除的标签ID列表"}
                },
                "required": ["message_id", "label_ids"]
            }
        ),
        MCPToolDefinition(
            name="trash_gmail_message",
            description="将Gmail邮件移动到垃圾箱",
            input_schema={
                "type": "object",
                "properties": {
                    "message_id": {"type": "string", "description": "邮件ID"}
                },
                "required": ["message_id"]
            }
        ),
        MCPToolDefinition(
            name="get_gmail_labels",
            description="获取所有Gmail标签",
            input_schema={
                "type": "object",
                "properties": {}
            }
        )
    ]
    
    return MCPResponse(tools=tools)

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )