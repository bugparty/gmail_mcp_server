# Gmail MCP Server 测试指南

本文档详细说明了如何测试Gmail MCP Server的各项功能。

## 测试工具概览

我们提供了三种不同的测试工具，适用于不同的测试需求：

| 测试工具 | 用途 | 执行时间 | 特点 |
|---------|------|----------|------|
| `quick_test.py` | 快速验证 | ~5秒 | 简单快速，适合日常检查 |
| `test_gmail_api.py` | 完整测试 | ~30秒 | 详细报告，全功能覆盖 |
| `test_api.sh` | Bash测试 | ~20秒 | 命令行友好，无需Python |

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

## 故障排除

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

## 性能基准

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

## 测试最佳实践

### 开发阶段
1. 每次代码修改后运行快速测试
2. 新功能开发完成后运行完整测试
3. 提交代码前确保所有测试通过

### 部署阶段
1. 部署前在测试环境运行完整测试
2. 部署后立即运行快速测试验证
3. 定期运行完整测试确保服务稳定

### 生产环境
1. 设置定时健康检查
2. 监控API响应时间
3. 记录和分析测试失败情况

## 扩展测试

### 添加自定义测试

如果需要测试特定功能，可以扩展现有测试脚本：

```python
def test_custom_feature(self):
    """测试自定义功能"""
    print("🔧 测试 X: 自定义功能")
    
    # 你的测试代码
    success, data = self.make_request('GET', '/api/custom')
    
    if success:
        self.log_test("自定义功能", True, "功能正常")
    else:
        self.log_test("自定义功能", False, f"测试失败: {data}")
```

### 集成到CI/CD

在GitHub Actions中使用：

```yaml
- name: Test Gmail MCP Server
  run: |
    python start_server.py &
    sleep 5
    python quick_test.py ${{ secrets.TEST_ACCESS_TOKEN }}
```

## 总结

选择合适的测试工具：

- 🚀 **日常开发**：使用 `quick_test.py`
- 🧪 **功能验证**：使用 `test_gmail_api.py`
- 🔧 **系统集成**：使用 `test_api.sh`

记住：测试是确保Gmail MCP Server稳定运行的关键！