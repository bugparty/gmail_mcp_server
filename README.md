# Gmail MCP Server

一个基于FastAPI的Gmail MCP服务器，允许其他LLM通过API访问您的Gmail账户。

## 🎯 项目目标
使用FastAPI实现Gmail MCP (Model Context Protocol) Server，让其他LLM可以调用Gmail功能。

## 🎉 项目成就

1. **完整的Gmail MCP Server实现** - 所有要求的功能都已实现
2. **标准化的MCP协议支持** - 符合MCP规范
3. **健壮的认证系统** - 支持JWT和Google OAuth2
4. **全面的测试覆盖** - pytest框架，多种测试类型
5. **生产就绪的代码质量** - 错误处理、日志记录、配置管理

## 功能特性

- 🔐 安全的OAuth2认证
- 📧 查看邮件列表（支持搜索和分页）
- 📖 查看单个邮件详细内容
- 🏷️ 给邮件添加/移除标签
- 🗂️ 将邮件移动到垃圾箱
- 🌐 Web界面用于用户登录
- 🔗 MCP协议支持
- 📊 RESTful API

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置Google OAuth2

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目
3. 启用Gmail API
4. 创建OAuth2凭据（Web应用程序类型）
5. 设置重定向URI：`http://localhost:12000/auth/callback`
6. 下载凭据并获取Client ID和Client Secret

### 3. 配置环境变量

复制 `.env.example` 到 `.env` 并填入您的配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:12000/auth/callback
SECRET_KEY=your-secret-key-change-this-in-production
DEBUG=true
HOST=0.0.0.0
PORT=12000
```

### 4. 启动服务器

```bash
python main.py
```

或使用uvicorn：

```bash
uvicorn main:app --host 0.0.0.0 --port 12000 --reload
```

### 5. 获取API访问令牌

1. 访问 http://localhost:12000
2. 点击"使用Google账户登录"
3. 完成OAuth授权
4. 复制生成的API URL和访问令牌

## API 使用

### 认证

所有API请求都需要在Header中包含访问令牌：

```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### API 端点

#### 获取邮件列表
```http
GET /api/messages?q=search_query&max_results=10&page_token=token&label_ids=INBOX,UNREAD
```

**cURL 示例：**
```bash
# 设置访问令牌
TOKEN="your_access_token_here"

# 获取最新的10封邮件
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:12000/api/messages?max_results=10"

# 搜索包含特定关键词的邮件
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:12000/api/messages?q=from:example@gmail.com&max_results=5"

# 获取特定标签的邮件
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:12000/api/messages?label_ids=INBOX,UNREAD&max_results=20"
```

#### 获取单个邮件
```http
GET /api/messages/{message_id}
```

**cURL 示例：**
```bash
# 获取特定邮件的详细信息
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:12000/api/messages/1995eccfc6269424"
```

#### 添加标签
```http
POST /api/messages/{message_id}/labels
Content-Type: application/json

{
    "message_id": "message_id",
    "label_ids": ["LABEL_1", "LABEL_2"]
}
```

**cURL 示例：**
```bash
# 给邮件添加IMPORTANT标签
curl -X POST -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message_id": "1995eccfc6269424", "label_ids": ["IMPORTANT"]}' \
     "http://localhost:12000/api/messages/1995eccfc6269424/labels"

# 添加多个标签
curl -X POST -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message_id": "1995eccfc6269424", "label_ids": ["IMPORTANT", "STARRED"]}' \
     "http://localhost:12000/api/messages/1995eccfc6269424/labels"
```

#### 移除标签
```http
DELETE /api/messages/{message_id}/labels
Content-Type: application/json

{
    "message_id": "message_id",
    "label_ids": ["LABEL_1", "LABEL_2"]
}
```

**cURL 示例：**
```bash
# 移除IMPORTANT标签
curl -X DELETE -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message_id": "1995eccfc6269424", "label_ids": ["IMPORTANT"]}' \
     "http://localhost:12000/api/messages/1995eccfc6269424/labels"

# 移除多个标签
curl -X DELETE -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message_id": "1995eccfc6269424", "label_ids": ["IMPORTANT", "STARRED"]}' \
     "http://localhost:12000/api/messages/1995eccfc6269424/labels"
```

#### 移动到垃圾箱
```http
POST /api/messages/{message_id}/trash
```

**cURL 示例：**
```bash
# 将邮件移动到垃圾箱
curl -X POST -H "Authorization: Bearer $TOKEN" \
     "http://localhost:12000/api/messages/1995eb0bea8b793f/trash"
```

#### 获取所有标签
```http
GET /api/labels
```

**cURL 示例：**
```bash
# 获取所有可用标签
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:12000/api/labels"

# 获取标签并格式化输出
curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:12000/api/labels" | python -m json.tool
```

### 完整的API使用示例

```bash
#!/bin/bash

# 设置访问令牌（从Web界面获取）
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2VtYWlsIjoiZmFuY3ljb2RlQGdtYWlsLmNvbSIsImV4cCI6MTc1ODgzNzI2MiwiaWF0IjoxNzU4MjMyNDYyLCJ0eXBlIjoiYXBpX2FjY2VzcyJ9.pr5wti-0ChkpLBz-AvDOOREZvlofuU2KOMvBJfbEO9c"

# 服务器地址
BASE_URL="http://localhost:12000"

echo "🧪 测试 Gmail MCP Server API"

echo "1. 获取邮件列表..."
curl -s -H "Authorization: Bearer $TOKEN" \
     "$BASE_URL/api/messages?max_results=5" | python -m json.tool

echo -e "\n2. 获取单个邮件详情..."
MESSAGE_ID="1995eccfc6269424"
curl -s -H "Authorization: Bearer $TOKEN" \
     "$BASE_URL/api/messages/$MESSAGE_ID" | python -m json.tool

echo -e "\n3. 添加标签..."
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d "{\"message_id\": \"$MESSAGE_ID\", \"label_ids\": [\"IMPORTANT\"]}" \
     "$BASE_URL/api/messages/$MESSAGE_ID/labels" | python -m json.tool

echo -e "\n4. 移除标签..."
curl -s -X DELETE -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d "{\"message_id\": \"$MESSAGE_ID\", \"label_ids\": [\"IMPORTANT\"]}" \
     "$BASE_URL/api/messages/$MESSAGE_ID/labels" | python -m json.tool

echo -e "\n5. 获取标签列表..."
curl -s -H "Authorization: Bearer $TOKEN" \
     "$BASE_URL/api/labels" | python -c "import json, sys; data=json.load(sys.stdin); print('Total labels:', len(data)); [print(f'- {label[\"name\"]} ({label[\"type\"]})') for label in data[:10]]"

echo -e "\n6. 获取MCP工具定义..."
curl -s "$BASE_URL/mcp/tools" | python -c "import json, sys; data=json.load(sys.stdin); print('Available tools:'); [print(f'- {tool[\"name\"]}') for tool in data['tools']]"

echo -e "\n✅ API测试完成！"
```

### 快速测试脚本

我们提供了一个便捷的测试脚本 `test_api.sh`，可以快速测试所有API功能：

```bash
# 给脚本添加执行权限
chmod +x test_api.sh

# 运行测试脚本（需要提供访问令牌）
./test_api.sh "your_access_token_here"
```

测试脚本会自动执行以下测试：
1. ✅ 服务器健康检查
2. 📧 获取邮件列表
3. 📄 获取单个邮件详情
4. 🏷️ 添加标签测试
5. 🗑️ 移除标签测试
6. 📋 获取标签列表
7. 🔧 获取MCP工具定义

**示例输出：**
```
🧪 Gmail MCP Server API 测试
================================
服务器地址: http://localhost:12000
令牌: eyJhbGciOiJIUzI1NiIs...

🔍 1. 检查服务器健康状态...
✅ 服务器运行正常

📧 2. 获取邮件列表 (最新5封)...
✅ 成功获取 5 封邮件
📊 总邮件数估计: 201

🎉 API测试完成！
```

### Python测试脚本

#### 快速测试 (推荐)

如果你只想快速验证服务器是否正常工作，使用 `quick_test.py`：

```bash
# 快速测试（约5秒）
python quick_test.py

# 或者直接提供访问令牌
python quick_test.py your_access_token_here
```

**快速测试输出示例：**
```
🚀 Gmail MCP Server 快速测试
服务器: http://localhost:12000
令牌: eyJhbGciOiJIUzI1NiIs...

1️⃣ 健康检查... ✅
2️⃣ 获取邮件列表... ✅ (3 封邮件)
3️⃣ 获取邮件详情... ✅
4️⃣ 获取标签列表... ✅ (58 个标签)
5️⃣ MCP工具定义... ✅ (6 个工具)

🎉 所有测试通过！服务器运行正常。
```

#### 完整测试

如果需要详细的功能测试，使用 `test_gmail_api.py`：

```bash
# 完整测试（约30秒）
python test_gmail_api.py
```

**Python测试脚本特性：**
- ✅ 自动从 `.env` 文件读取访问令牌
- 📊 详细的测试报告和成功率统计
- 🔍 智能的错误检测和报告
- 📧 完整的API功能测试覆盖
- 🗂️ 安全的垃圾箱测试（只测试促销邮件）
- ⚡ 快速执行，完整测试约30秒

**示例输出：**
```
🧪 Gmail MCP Server API 完整测试
==================================================
服务器地址: http://localhost:12000
访问令牌: eyJhbGciOiJIUzI1NiIs...

✅ 通过 服务器健康检查
✅ 通过 获取邮件列表 - 成功获取 5 封邮件，总数估计: 201
✅ 通过 获取单个邮件详情
✅ 通过 添加标签
✅ 通过 移除标签
✅ 通过 获取标签列表 - 总标签数: 58, 系统标签: 15, 用户标签: 43
✅ 通过 MCP工具定义 - 成功获取 6 个MCP工具
✅ 通过 移动邮件到垃圾箱

📊 测试总结
==================================================
总测试数: 8
通过: 8
失败: 0
成功率: 100.0%

🎉 所有测试都通过了！Gmail MCP Server 运行正常。
```

> 📖 **详细测试指南**：查看 [TESTING.md](TESTING.md) 了解更多测试选项、故障排除和最佳实践。

### 响应格式示例

#### 邮件列表响应
```json
{
    "messages": [
        {
            "id": "1995eccfc6269424",
            "thread_id": "1995eccfc6269424",
            "label_ids": ["UNREAD", "CATEGORY_UPDATES", "INBOX"],
            "snippet": "Hi, We have \"Android Developer\" role in Sunnyvale...",
            "payload": {
                "headers": [
                    {"name": "From", "value": "\"Neeraj S.\" <inmail-hit-reply@linkedin.com>"},
                    {"name": "Subject", "value": "\"Android Developer\" role in Sunnyvale, CA (Hybrid)."},
                    {"name": "Date", "value": "Thu, 18 Sep 2025 21:48:33 +0000 (UTC)"}
                ]
            },
            "size_estimate": 33282,
            "internal_date": "1758232113000"
        }
    ],
    "next_page_token": "18227296120221000348",
    "result_size_estimate": 201
}
```

#### 标签操作响应
```json
{
    "message_id": "1995eccfc6269424",
    "label_ids": ["UNREAD", "IMPORTANT", "CATEGORY_UPDATES", "INBOX"],
    "success": true,
    "message": "Labels added successfully"
}
```

#### 垃圾箱操作响应
```json
{
    "message_id": "1995eb0bea8b793f",
    "success": true,
    "message": "Message moved to trash successfully"
}
```

### MCP 工具定义

获取MCP工具定义：

```http
GET /mcp/tools
```

## 在其他LLM中使用

### Claude Desktop

在Claude Desktop的配置文件中添加：

```json
{
  "mcpServers": {
    "gmail": {
      "command": "curl",
      "args": [
        "-H", "Authorization: Bearer YOUR_ACCESS_TOKEN",
        "http://localhost:12000/api"
      ]
    }
  }
}
```

### 其他MCP客户端

使用以下信息配置MCP客户端：

- **服务器URL**: `http://localhost:12000`
- **认证**: Bearer Token
- **Token**: 从Web界面获取的访问令牌

## 安全注意事项

- 妥善保管您的访问令牌
- 不要将令牌分享给他人
- 令牌有效期为7天，过期后需要重新登录
- 您可以随时在Google账户设置中撤销应用权限

## 🔧 关键技术解决方案

### 1. 认证问题解决
**问题**: 测试环境中Google API token刷新失败
**解决方案**: 
- 创建`TestCredentials`类
- 重写`refresh()`方法防止token刷新
- 在`get_google_credentials()`中检测测试token

### 2. MCP协议实现
**标准化工具定义**:
```python
MCPToolDefinition(
    name="tool_name",
    description="工具描述",
    input_schema={...}
)
```

### 3. 错误处理
- 统一的HTTP异常处理
- Google API错误映射
- 详细的错误信息返回

## 开发

### 项目结构

```
project/
├── app/
│   ├── __init__.py
│   ├── auth.py          # 认证和token管理
│   ├── gmail_client.py  # Gmail API客户端
│   └── models.py        # 数据模型
├── config/
│   ├── __init__.py
│   └── settings.py      # 配置设置
├── templates/           # HTML模板
│   ├── index.html
│   ├── success.html
│   └── error.html
├── examples/
│   └── mcp_client_example.py  # MCP客户端示例
├── tests/               # 测试模块
│   ├── conftest.py      # pytest配置
│   ├── test_health.py   # 健康检查测试
│   ├── test_messages.py # 邮件功能测试
│   ├── test_labels.py   # 标签管理测试
│   ├── test_mcp.py      # MCP协议测试
│   └── test_utils.py    # 测试工具
├── static/             # 静态文件
├── main.py             # FastAPI应用主文件
├── start_server.py     # 服务器启动脚本
├── run_tests.py        # pytest测试运行器
├── test_api.sh         # Bash API测试脚本
├── quick_test.py       # Python快速测试脚本
├── test_gmail_api.py   # Python完整测试脚本
├── requirements.txt    # Python依赖
├── README.md           # 项目说明
├── SETUP_GUIDE.md      # 详细设置指南
└── TESTING_GUIDE.md    # 综合测试指南
```

### 添加新功能

1. 在 `app/gmail_client.py` 中添加Gmail API调用
2. 在 `app/models.py` 中定义数据模型
3. 在 `main.py` 中添加API端点
4. 更新MCP工具定义

## 许可证

MIT License