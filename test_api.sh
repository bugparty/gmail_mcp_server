#!/bin/bash

# Gmail MCP Server API 测试脚本
# 使用方法: ./test_api.sh YOUR_ACCESS_TOKEN

# 检查是否提供了访问令牌
if [ -z "$1" ]; then
    echo "❌ 错误: 请提供访问令牌"
    echo "使用方法: ./test_api.sh YOUR_ACCESS_TOKEN"
    echo ""
    echo "获取访问令牌的步骤:"
    echo "1. 访问 http://localhost:12000"
    echo "2. 点击'使用Google账户登录'"
    echo "3. 完成OAuth授权"
    echo "4. 复制生成的访问令牌"
    exit 1
fi

# 设置访问令牌和服务器地址
TOKEN="$1"
BASE_URL="http://localhost:12000"

echo "🧪 Gmail MCP Server API 测试"
echo "================================"
echo "服务器地址: $BASE_URL"
echo "令牌: ${TOKEN:0:20}..."
echo ""

# 测试服务器健康状态
echo "🔍 1. 检查服务器健康状态..."
curl -s "$BASE_URL/health" | python -m json.tool
echo ""

# 获取邮件列表
echo "📧 2. 获取邮件列表 (最新5封)..."
MESSAGES_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
     "$BASE_URL/api/messages?max_results=5")

echo "$MESSAGES_RESPONSE" | python -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(f'✅ 成功获取 {len(data[\"messages\"])} 封邮件')
    print(f'📊 总邮件数估计: {data[\"result_size_estimate\"]}')
    print('📋 邮件列表:')
    for i, msg in enumerate(data['messages'][:3], 1):
        subject = next((h['value'] for h in msg['payload']['headers'] if h['name'] == 'Subject'), 'No Subject')
        from_addr = next((h['value'] for h in msg['payload']['headers'] if h['name'] == 'From'), 'Unknown')
        print(f'  {i}. ID: {msg[\"id\"]}')
        print(f'     主题: {subject[:50]}...')
        print(f'     发件人: {from_addr[:50]}...')
        print(f'     标签: {msg[\"label_ids\"]}')
        print()
except Exception as e:
    print(f'❌ 错误: {e}')
    print('原始响应:', sys.stdin.read())
"
echo ""

# 获取第一封邮件的详细信息
echo "📄 3. 获取单个邮件详情..."
FIRST_MESSAGE_ID=$(echo "$MESSAGES_RESPONSE" | python -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(data['messages'][0]['id'])
except:
    print('')
")

if [ -n "$FIRST_MESSAGE_ID" ]; then
    echo "正在获取邮件 ID: $FIRST_MESSAGE_ID"
    curl -s -H "Authorization: Bearer $TOKEN" \
         "$BASE_URL/api/messages/$FIRST_MESSAGE_ID" | python -c "
import json, sys
try:
    data = json.load(sys.stdin)
    subject = next((h['value'] for h in data['payload']['headers'] if h['name'] == 'Subject'), 'No Subject')
    from_addr = next((h['value'] for h in data['payload']['headers'] if h['name'] == 'From'), 'Unknown')
    date = next((h['value'] for h in data['payload']['headers'] if h['name'] == 'Date'), 'Unknown')
    print(f'✅ 邮件详情获取成功')
    print(f'📧 主题: {subject}')
    print(f'👤 发件人: {from_addr}')
    print(f'📅 日期: {date}')
    print(f'🏷️ 标签: {data[\"label_ids\"]}')
    print(f'📏 大小估计: {data[\"size_estimate\"]} 字节')
except Exception as e:
    print(f'❌ 错误: {e}')
"
    echo ""
    
    # 测试添加标签
    echo "🏷️ 4. 测试添加标签 (IMPORTANT)..."
    curl -s -X POST -H "Authorization: Bearer $TOKEN" \
         -H "Content-Type: application/json" \
         -d "{\"message_id\": \"$FIRST_MESSAGE_ID\", \"label_ids\": [\"IMPORTANT\"]}" \
         "$BASE_URL/api/messages/$FIRST_MESSAGE_ID/labels" | python -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if data['success']:
        print(f'✅ 标签添加成功')
        print(f'🏷️ 当前标签: {data[\"label_ids\"]}')
    else:
        print(f'❌ 标签添加失败: {data[\"message\"]}')
except Exception as e:
    print(f'❌ 错误: {e}')
"
    echo ""
    
    # 测试移除标签
    echo "🗑️ 5. 测试移除标签 (IMPORTANT)..."
    curl -s -X DELETE -H "Authorization: Bearer $TOKEN" \
         -H "Content-Type: application/json" \
         -d "{\"message_id\": \"$FIRST_MESSAGE_ID\", \"label_ids\": [\"IMPORTANT\"]}" \
         "$BASE_URL/api/messages/$FIRST_MESSAGE_ID/labels" | python -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if data['success']:
        print(f'✅ 标签移除成功')
        print(f'🏷️ 当前标签: {data[\"label_ids\"]}')
    else:
        print(f'❌ 标签移除失败: {data[\"message\"]}')
except Exception as e:
    print(f'❌ 错误: {e}')
"
    echo ""
else
    echo "❌ 无法获取邮件ID，跳过标签测试"
    echo ""
fi

# 获取标签列表
echo "📋 6. 获取标签列表..."
curl -s -H "Authorization: Bearer $TOKEN" \
     "$BASE_URL/api/labels" | python -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(f'✅ 成功获取 {len(data)} 个标签')
    print('📋 系统标签:')
    system_labels = [label for label in data if label['type'] == 'system'][:5]
    for label in system_labels:
        print(f'  - {label[\"name\"]} ({label[\"id\"]})')
    
    user_labels = [label for label in data if label['type'] == 'user']
    if user_labels:
        print('👤 用户标签:')
        for label in user_labels[:5]:
            print(f'  - {label[\"name\"]} ({label[\"id\"]})')
    else:
        print('👤 用户标签: 无')
except Exception as e:
    print(f'❌ 错误: {e}')
"
echo ""

# 获取MCP工具定义
echo "🔧 7. 获取MCP工具定义..."
curl -s "$BASE_URL/mcp/tools" | python -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(f'✅ 成功获取 {len(data[\"tools\"])} 个MCP工具')
    print('🛠️ 可用工具:')
    for tool in data['tools']:
        print(f'  - {tool[\"name\"]}: {tool[\"description\"]}')
except Exception as e:
    print(f'❌ 错误: {e}')
"
echo ""

echo "🎉 API测试完成！"
echo ""
echo "📝 使用说明:"
echo "- 所有核心功能都已测试"
echo "- 如需测试垃圾箱功能，请手动运行:"
echo "  curl -X POST -H \"Authorization: Bearer $TOKEN\" \\"
echo "       \"$BASE_URL/api/messages/MESSAGE_ID/trash\""
echo ""
echo "🔗 更多信息请查看 README.md"