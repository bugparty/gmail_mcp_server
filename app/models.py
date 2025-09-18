from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime

class UserToken(BaseModel):
    user_id: str
    email: str
    access_token: str
    refresh_token: str
    token_expires_at: datetime
    created_at: datetime

class EmailMessage(BaseModel):
    id: str
    thread_id: str
    label_ids: List[str]
    snippet: str
    payload: Dict[str, Any]
    size_estimate: int
    history_id: str
    internal_date: str

class EmailListResponse(BaseModel):
    messages: List[EmailMessage]
    next_page_token: Optional[str] = None
    result_size_estimate: int

class EmailDetail(BaseModel):
    id: str
    thread_id: str
    label_ids: List[str]
    snippet: str
    history_id: str
    internal_date: str
    payload: Dict[str, Any]
    size_estimate: int
    subject: Optional[str] = None
    sender: Optional[str] = None
    recipient: Optional[str] = None
    body_text: Optional[str] = None
    body_html: Optional[str] = None

class LabelRequest(BaseModel):
    message_id: str
    label_ids: List[str]

class LabelResponse(BaseModel):
    message_id: str
    label_ids: List[str]
    success: bool
    message: str

class TrashRequest(BaseModel):
    message_id: str

class TrashResponse(BaseModel):
    message_id: str
    success: bool
    message: str

class APITokenResponse(BaseModel):
    api_url: str
    token: str
    expires_at: datetime
    user_email: str

class MCPToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]

class MCPResponse(BaseModel):
    tools: List[MCPToolDefinition]