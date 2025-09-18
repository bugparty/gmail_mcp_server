# Gmail MCP Server 设置指南

## 🚀 快速开始

### 第一步：获取Google OAuth2凭据

1. **访问Google Cloud Console**
   - 打开 [Google Cloud Console](https://console.cloud.google.com/)
   - 登录您的Google账户

2. **创建或选择项目**
   - 点击项目选择器
   - 创建新项目或选择现有项目

3. **启用Gmail API**
   - 在左侧菜单中选择"API和服务" > "库"
   - 搜索"Gmail API"
   - 点击"启用"

4. **创建OAuth2凭据**
   - 在左侧菜单中选择"API和服务" > "凭据"
   - 点击"创建凭据" > "OAuth客户端ID"
   - 选择应用类型："Web应用程序"
   - 设置名称：例如"Gmail MCP Server"
   - 添加授权重定向URI：`http://localhost:12000/auth/callback`
   - 点击"创建"

5. **下载凭据**
   - 复制客户端ID和客户端密钥
   - 保存这些信息，稍后需要用到

### 第二步：配置环境

1. **克隆或下载项目**
   ```bash
   # 如果您有项目文件
   cd gmail-mcp-server
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境变量**
   ```bash
   cp .env.example .env
   ```
   
   编辑 `.env` 文件：
   ```env
   GOOGLE_CLIENT_ID=您的客户端ID
   GOOGLE_CLIENT_SECRET=您的客户端密钥
   GOOGLE_REDIRECT_URI=http://localhost:12000/auth/callback
   SECRET_KEY=生成一个安全的密钥
   DEBUG=true
   HOST=0.0.0.0
   PORT=12000
   ```

### 第三步：启动服务器

```bash
python start_server.py
```

或者：

```bash
python main.py
```

### 第四步：获取API访问令牌

1. **访问Web界面**
   - 打开浏览器访问：http://localhost:12000

2. **登录授权**
   - 点击"使用Google账户登录"
   - 完成Google OAuth授权流程
   - 授权应用访问您的Gmail

3. **获取令牌**
   - 登录成功后，页面会显示：
     - API基础URL：`http://localhost:12000/api`
     - 访问令牌：`eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...`
   - 复制这些信息

## 🔧 在其他工具中使用

### Claude Desktop

在Claude Desktop的配置文件中添加：

```json
{
  "mcpServers": {
    "gmail": {
      "command": "node",
      "args": ["-e", "
        const https = require('https');
        const http = require('http');
        
        const token = 'YOUR_ACCESS_TOKEN';
        const baseUrl = 'http://localhost:12000';
        
        // MCP服务器实现
        // 这里需要实现完整的MCP协议
      "]
    }
  }
}
```

### 直接API调用

使用curl测试：

```bash
# 获取邮件列表
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:12000/api/messages?max_results=5"

# 获取单个邮件
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:12000/api/messages/MESSAGE_ID"

# 添加标签
curl -X POST \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message_id":"MESSAGE_ID","label_ids":["IMPORTANT"]}' \
     "http://localhost:12000/api/messages/MESSAGE_ID/labels"
```

### Python客户端示例

```python
import requests

class GmailMCPClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}
    
    def list_messages(self, query="", max_results=10):
        response = requests.get(
            f"{self.base_url}/api/messages",
            headers=self.headers,
            params={"q": query, "max_results": max_results}
        )
        return response.json()
    
    def get_message(self, message_id):
        response = requests.get(
            f"{self.base_url}/api/messages/{message_id}",
            headers=self.headers
        )
        return response.json()

# 使用示例
client = GmailMCPClient("http://localhost:12000", "YOUR_TOKEN")
messages = client.list_messages("from:example@gmail.com")
```

## 🛠️ 高级配置

### 自定义端口

修改 `.env` 文件中的 `PORT` 变量：

```env
PORT=8080
```

同时更新Google OAuth重定向URI为：`http://localhost:8080/auth/callback`

### 生产环境部署

1. **设置安全的密钥**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **禁用调试模式**
   ```env
   DEBUG=false
   ```

3. **使用HTTPS**
   - 配置反向代理（如Nginx）
   - 更新重定向URI为HTTPS地址

4. **环境变量安全**
   - 不要将 `.env` 文件提交到版本控制
   - 使用系统环境变量或密钥管理服务

### Docker部署

创建 `Dockerfile`：

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 12000

CMD ["python", "main.py"]
```

构建和运行：

```bash
docker build -t gmail-mcp-server .
docker run -p 12000:12000 --env-file .env gmail-mcp-server
```

## 🔍 故障排除

### 常见问题

1. **OAuth错误：redirect_uri_mismatch**
   - 检查Google Cloud Console中的重定向URI设置
   - 确保URI完全匹配，包括协议和端口

2. **Token过期**
   - 令牌有效期为7天
   - 重新访问Web界面获取新令牌

3. **Gmail API配额限制**
   - 默认配额通常足够个人使用
   - 如需更高配额，在Google Cloud Console中申请

4. **端口被占用**
   - 修改 `.env` 文件中的端口号
   - 或停止占用端口的其他服务

### 日志调试

启用详细日志：

```bash
export DEBUG=true
python main.py
```

### 测试连接

```bash
# 健康检查
curl http://localhost:12000/health

# 测试MCP工具定义
curl http://localhost:12000/mcp/tools
```

## 📚 API参考

详细的API文档可以在服务器运行时访问：
- Swagger UI: http://localhost:12000/docs
- OpenAPI JSON: http://localhost:12000/openapi.json

## 🔒 安全建议

1. **保护访问令牌**
   - 不要在公共场所分享令牌
   - 定期更新令牌

2. **网络安全**
   - 在生产环境中使用HTTPS
   - 考虑使用防火墙限制访问

3. **权限管理**
   - 只授权必要的Gmail权限
   - 定期检查Google账户的应用权限

4. **监控使用**
   - 监控API调用频率
   - 注意异常访问模式