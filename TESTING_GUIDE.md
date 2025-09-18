# Gmail MCP Server 测试指南

本文档详细说明了如何测试Gmail MCP Server的各项功能。我们提供了完整的测试工具链，包括快速验证工具和全面的测试框架，满足不同场景的测试需求。

## 🧪 测试工具概览

我们提供了三种不同的测试工具，适用于不同的测试需求：

| 测试工具 | 用途 | 执行时间 | 特点 |
|---------|------|----------|------|
| `quick_test.py` | 快速验证 | ~5秒 | 简单快速，适合日常检查 |
| `test_gmail_api.py` | 完整测试 | ~30秒 | 详细报告，全功能覆盖 |
| `test_api.sh` | Bash测试 | ~20秒 | 命令行友好，无需Python |

### 🚀 正式测试框架

| 文件 | 类型 | 用途 | 复杂度 |
|------|------|------|--------|
| `run_tests.py` | pytest运行器 | 正式测试框架入口 | 高 |
| `quick_test.py` | 简单API测试 | 快速功能验证 | 低 |
| `test_api.sh` | Shell脚本 | 命令行API测试 | 中 |

### 🧪 测试模块 (tests/ 目录)

| 文件 | 测试内容 | 重要性 |
|------|----------|--------|
| `test_health.py` | 服务器健康检查 | ⭐⭐⭐ |
| `test_messages.py` | 邮件功能测试 | ⭐⭐⭐ |
| `test_labels.py` | 标签管理测试 | ⭐⭐⭐ |
| `test_mcp.py` | MCP协议测试 | ⭐⭐⭐ |
| `test_trash.py` | 垃圾箱功能测试 | ⭐⭐ |
| `test_integration.py` | 集成测试 | ⭐⭐ |
| `conftest.py` | pytest配置和fixtures | ⭐⭐⭐ |
| `test_utils.py` | 测试工具函数 | ⭐⭐ |

## 🛠️ 测试工具详解

## 1. 快速测试 (推荐)

### 使用场景
- 服务器启动后的快速验证
- 部署后的健康检查
- 日常开发中的功能确认

### 使用方法
```bash
# 使用环境变量中的令牌
python quick_test.py

# 直接提供访问令牌
python quick_test.py eyJhbGciOiJIUzI1NiIs...
```

### 测试内容
1. ✅ 服务器健康检查
2. ✅ 获取邮件列表
3. ✅ 获取邮件详情
4. ✅ 获取标签列表
5. ✅ MCP工具定义

### 示例输出
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

## 2. 完整测试

### 使用场景
- 新功能开发后的全面测试
- 生产环境部署前的验证
- 问题排查和调试

### 使用方法
```bash
python test_gmail_api.py
```

### 测试内容
1. ✅ 服务器健康检查
2. ✅ 获取邮件列表（带详细信息）
3. ✅ 获取单个邮件详情
4. ✅ 添加标签功能
5. ✅ 移除标签功能
6. ✅ 获取标签列表（分类统计）
7. ✅ MCP工具定义（详细列表）
8. ✅ 移动邮件到垃圾箱（安全测试）

### 特色功能
- 📊 详细的测试统计报告
- 🔍 智能错误检测和诊断
- 🗂️ 安全的垃圾箱测试（只测试促销邮件）
- ✅ 操作验证（确认标签添加/移除成功）

### 示例输出
```
🧪 Gmail MCP Server API 完整测试
==================================================
服务器地址: http://localhost:12000
访问令牌: eyJhbGciOiJIUzI1NiIs...

✅ 通过 服务器健康检查
✅ 通过 获取邮件列表 - 成功获取 5 封邮件，总数估计: 201
✅ 通过 获取单个邮件详情
✅ 通过 添加标签 - 成功添加标签，当前标签: ['UNREAD', 'IMPORTANT', 'CATEGORY_UPDATES', 'INBOX']
✅ 通过 移除标签 - 成功移除标签，当前标签: ['UNREAD', 'CATEGORY_UPDATES', 'INBOX']
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

## 3. Bash测试脚本

### 使用场景
- 不想安装Python依赖的环境
- CI/CD管道中的自动化测试
- 系统管理员的快速检查

### 使用方法
```bash
# 使用环境变量中的令牌
./test_api.sh

# 直接提供访问令牌
./test_api.sh eyJhbGciOiJIUzI1NiIs...
```

### 测试内容
- 所有REST API端点
- cURL命令示例
- JSON响应格式验证

## 环境配置

### 访问令牌设置

有三种方式提供访问令牌：

1. **环境变量** (推荐)
```bash
export TEST_ACCESS_TOKEN="your_token_here"
```

2. **.env文件**
```bash
echo "TEST_ACCESS_TOKEN=your_token_here" >> .env
```

3. **命令行参数**
```bash
python quick_test.py your_token_here
```

### 服务器地址配置

默认服务器地址是 `http://localhost:12000`，可以通过环境变量修改：

```bash
export TEST_SERVER_URL="http://your-server:port"
```

## 4. 正式测试框架

### run_tests.py - pytest运行器

**功能特点**:
- 🔧 环境检查和依赖验证
- 📊 多种测试模式选择
- 📈 覆盖率报告生成
- 📄 HTML测试报告
- ⚡ 并行测试执行
- 🔍 灵活的测试过滤

## 🔍 故障排除

### 常见问题

#### 1. 连接失败
```
❌ 网络错误: Connection refused
```

**解决方案：**
- 确保服务器正在运行：`python start_server.py`
- 检查端口是否正确（默认12000）
- 验证防火墙设置

#### 2. 认证失败
```
❌ 401 Unauthorized
```

**解决方案：**
- 检查访问令牌是否有效
- 确认令牌未过期
- 重新进行OAuth认证

#### 3. 权限不足
```
❌ 403 Forbidden
```

**解决方案：**
- 确认Gmail API权限范围
- 检查Google Cloud Console配置
- 验证OAuth同意屏幕设置

#### 4. 邮件不存在
```
❌ 404 Not Found
```

**解决方案：**
- 确认邮箱中有邮件
- 检查邮件ID是否正确
- 验证邮件未被删除

### 调试技巧

1. **启用详细日志**
```bash
export DEBUG=true
python start_server.py
```

2. **检查服务器日志**
服务器会输出详细的请求日志，包括：
- HTTP请求方法和路径
- 响应状态码
- 错误信息

3. **使用curl手动测试**
```bash
curl -H "Authorization: Bearer your_token" \
     http://localhost:12000/health
```

## 📊 性能基准

### 测试性能参考

| 操作 | 平均响应时间 | 备注 |
|------|-------------|------|
| 健康检查 | <100ms | 本地检查 |
| 获取邮件列表 | 200-500ms | 取决于邮件数量 |
| 获取单个邮件 | 150-300ms | 取决于邮件大小 |
| 添加/移除标签 | 300-600ms | Gmail API操作 |
| 获取标签列表 | 100-200ms | 缓存优化 |
| 垃圾箱操作 | 400-800ms | Gmail API操作 |

### 优化建议

1. **使用分页**：获取大量邮件时使用`max_results`参数
2. **缓存标签**：标签列表变化不频繁，可以缓存
3. **批量操作**：一次性处理多个邮件标签
4. **异步处理**：对于耗时操作考虑异步处理

## 🛠️ 正式测试框架详解

### run_tests.py - pytest运行器

**功能特点**:
- 🔧 环境检查和依赖验证
- 📊 多种测试模式选择
- 📈 覆盖率报告生成
- 📄 HTML测试报告
- ⚡ 并行测试执行
- 🔍 灵活的测试过滤

**使用方法**:
```bash
# 快速测试（推荐日常开发使用）
python run_tests.py --quick

# 完整测试套件
python run_tests.py

# 冒烟测试（最基本验证）
python run_tests.py --smoke

# 集成测试
python run_tests.py --integration

# 生成覆盖率报告
python run_tests.py --coverage

# 生成HTML报告
python run_tests.py --html

# 并行运行（4个进程）
python run_tests.py --parallel 4

# 运行特定测试文件
python run_tests.py --file tests/test_health.py

# 过滤特定测试
python run_tests.py --filter "test_health"

# 详细输出
python run_tests.py --verbose
```

**测试模式说明**:
- `--quick`: 运行核心功能测试，跳过慢速测试
- `--smoke`: 最基本的功能验证，确保服务可用
- `--integration`: 端到端集成测试
- `--slow`: 包含耗时较长的测试
- `--destructive`: 包含可能修改Gmail数据的测试（谨慎使用）

### 2. quick_test.py - 快速验证工具

**功能特点**:
- ⚡ 快速执行（通常<10秒）
- 🎯 专注核心功能验证
- 📱 最小依赖要求
- 🔍 简洁的输出格式

**使用方法**:
```bash
# 使用环境变量中的token
python quick_test.py

# 指定access token
python quick_test.py your_jwt_token_here

# 指定服务器地址
python quick_test.py your_token http://localhost:8000
```

**测试内容**:
1. ✅ 服务器健康检查
2. ✅ JWT token验证
3. ✅ MCP工具列表获取
4. ✅ 基本API端点测试

### 3. test_api.sh - Shell脚本测试

**功能特点**:
- 🐚 纯Shell脚本，无Python依赖
- 🔧 使用curl进行HTTP测试
- 📋 逐步验证各个端点
- 🎨 彩色输出显示

**使用方法**:
```bash
# 基本测试
./test_api.sh

# 指定服务器地址
./test_api.sh http://localhost:8000

# 指定JWT token
JWT_TOKEN="your_token" ./test_api.sh
```

## 📁 测试模块详解

### 核心测试模块

#### test_health.py - 健康检查测试
```python
# 测试内容
- 服务器连通性
- 健康检查端点
- API根端点响应
- 基本错误处理
```

#### test_messages.py - 邮件功能测试
```python
# 测试内容
- 邮件列表获取
- 单个邮件详情
- 搜索功能
- 分页功能
- 错误处理
```

#### test_labels.py - 标签管理测试
```python
# 测试内容
- 标签列表获取
- 添加标签到邮件
- 从邮件移除标签
- 标签验证
- 批量操作
```

#### test_mcp.py - MCP协议测试
```python
# 测试内容
- MCP工具发现
- 工具调用接口
- 参数验证
- 响应格式验证
- 错误处理
```

### 支持文件

#### conftest.py - pytest配置
```python
# 提供功能
- 测试fixtures
- 环境配置
- 认证token生成
- 测试数据准备
- 清理函数
```

#### test_utils.py - 测试工具
```python
# 工具函数
- JWT token生成
- HTTP请求封装
- 响应验证
- 测试数据生成
- 断言辅助函数
```

## 🎯 测试策略

### 1. 开发阶段测试
```bash
# 日常开发 - 快速反馈
python quick_test.py

# 功能开发 - 相关模块测试
python run_tests.py --file tests/test_messages.py

# 提交前 - 快速测试
python run_tests.py --quick
```

### 2. 集成测试
```bash
# 完整功能验证
python run_tests.py --integration

# 端到端测试
python run_tests.py
```

### 3. 部署验证
```bash
# 生产环境快速检查
python quick_test.py

# 冒烟测试
python run_tests.py --smoke
```

### 4. CI/CD 流水线
```bash
# 并行执行，生成报告
python run_tests.py --parallel 4 --coverage --html
```

## 📊 测试覆盖范围

### 功能覆盖
- ✅ **邮件管理**: 列表、详情、搜索、分页
- ✅ **标签管理**: 获取、添加、删除、批量操作
- ✅ **垃圾箱操作**: 移动到垃圾箱、恢复
- ✅ **MCP协议**: 工具发现、调用、参数验证
- ✅ **认证系统**: JWT验证、Google OAuth2
- ✅ **错误处理**: 各种异常情况

### 测试类型
- 🔍 **单元测试**: 独立功能模块
- 🔗 **集成测试**: 模块间交互
- 🌐 **API测试**: HTTP接口验证
- 🏥 **健康检查**: 服务可用性
- 🚨 **错误测试**: 异常处理验证

## 🚨 注意事项

### 测试环境要求
1. **服务器运行**: 确保Gmail MCP Server在localhost:12000运行
2. **依赖安装**: `pip install -r requirements.txt`
3. **环境变量**: 配置必要的环境变量或.env文件

### 测试数据安全
- 🔒 测试使用模拟数据，不会影响真实Gmail账户
- 🛡️ TestCredentials类防止真实API调用
- ⚠️ 避免在生产环境运行破坏性测试

### 性能考虑
- ⚡ quick_test.py: ~5-10秒
- 🏃 --quick模式: ~30秒
- 🚶 完整测试: ~2-5分钟
- 🐌 --slow模式: ~10分钟+

## 🔧 故障排除

### 常见问题

#### 1. 服务器连接失败
```bash
# 检查服务器是否运行
curl http://localhost:12000/health

# 启动服务器
python main.py
```

#### 2. 认证失败
```bash
# 检查环境变量
echo $TEST_ACCESS_TOKEN

# 重新生成token
python -c "from tests.test_utils import generate_test_token; print(generate_test_token())"
```

#### 3. 依赖缺失
```bash
# 安装测试依赖
pip install -r requirements.txt

# 检查pytest安装
python -m pytest --version
```

#### 4. 测试失败分析
```bash
# 详细输出模式
python run_tests.py --verbose

# 运行单个失败的测试
python run_tests.py --file tests/test_health.py --verbose
```

## 📈 测试报告

### 覆盖率报告
```bash
# 生成覆盖率报告
python run_tests.py --coverage

# 查看报告
open htmlcov/index.html
```

### HTML测试报告
```bash
# 生成HTML报告
python run_tests.py --html

# 查看报告
open report.html
```

## 🎉 最佳实践

1. **开发时**: 使用`quick_test.py`获得快速反馈
2. **功能测试**: 使用`run_tests.py --quick`验证核心功能
3. **提交前**: 运行完整测试套件确保质量
4. **部署后**: 使用冒烟测试验证部署成功
5. **CI/CD**: 使用并行测试和报告生成提高效率

---

**测试是代码质量的保障，选择合适的测试工具能够提高开发效率和代码可靠性！** 🚀