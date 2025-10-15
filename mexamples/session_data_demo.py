"""
会话数据存储演示
展示 SQLiteSession 实际存储的数据结构
"""

import asyncio
import os
import json
from openai import AsyncOpenAI
from agents import (
    Agent, 
    Runner,
    SQLiteSession,
    set_default_openai_client,
    set_default_openai_api,
    set_tracing_disabled,
)

# 自定义域名配置
CUSTOM_BASE_URL = "https://aihubmix.com/v1"
CUSTOM_API_KEY = os.getenv("AIHUBMIX_API_KEY", "your-api-key-here")
# 模型配置 - 使用最便宜的模型进行测试
#CHEAP_MODEL = "gpt-3.5-turbo"  # 最便宜的 OpenAI 模型
#CHEAP_MODEL = "gpt-4.1"  # 最便宜的 OpenAI 模型
#CHEAP_MODEL = "gpt-4.1-mini"  # 最便宜的 OpenAI 模型
CHEAP_MODEL = "gpt-4.1-nano"  # 最便宜的 OpenAI 模型

def setup_custom_client():
    """设置自定义客户端"""
    client = AsyncOpenAI(
        base_url=CUSTOM_BASE_URL,
        api_key=CUSTOM_API_KEY,
        timeout=30.0,
        max_retries=3,
    )
    set_default_openai_client(client=client, use_for_tracing=False)
    set_default_openai_api("chat_completions")
    set_tracing_disabled(disabled=True)
    return client

async def demo_session_data_structure():
    """演示会话数据结构"""
    print("\n" + "="*60)
    print("🔍 会话数据结构演示")
    print("="*60)
    
    agent = Agent(
        name="数据演示助手",
        instructions="你是一个演示助手，会详细记录对话内容。",
        model=CHEAP_MODEL,
    )
    
    # 创建会话
    session = SQLiteSession("demo_user", "demo_conversations.db")
    print(f"🗄️  创建会话: {session.session_id}")
    print(f"📁 数据库文件: demo_conversations.db")
    
    # 第一轮对话
    print(f"\n👤 用户: 我的名字是张三")
    result1 = await Runner.run(agent, "我的名字是张三", session=session)
    print(f"🤖 助手: {result1.final_output}")
    
    # 查看存储的数据
    print(f"\n📋 查看存储的数据:")
    items = await session.get_items()
    for i, item in enumerate(items, 1):
        print(f"  {i}. {json.dumps(item, ensure_ascii=False, indent=2)}")
    
    # 第二轮对话
    print(f"\n👤 用户: 我今年25岁")
    result2 = await Runner.run(agent, "我今年25岁", session=session)
    print(f"🤖 助手: {result2.final_output}")
    
    # 再次查看存储的数据
    print(f"\n📋 更新后的存储数据:")
    items = await session.get_items()
    for i, item in enumerate(items, 1):
        print(f"  {i}. {json.dumps(item, ensure_ascii=False, indent=2)}")
    
    # 第三轮对话
    print(f"\n👤 用户: 我刚才告诉你什么信息？")
    result3 = await Runner.run(agent, "我刚才告诉你什么信息？", session=session)
    print(f"🤖 助手: {result3.final_output}")
    
    # 最终数据
    print(f"\n📋 最终存储的数据:")
    items = await session.get_items()
    for i, item in enumerate(items, 1):
        print(f"  {i}. {json.dumps(item, ensure_ascii=False, indent=2)}")

async def demo_session_management():
    """演示会话管理操作"""
    print("\n" + "="*60)
    print("🛠️  会话管理操作演示")
    print("="*60)
    
    agent = Agent(
        name="管理助手",
        instructions="你是一个管理助手。",
        model=CHEAP_MODEL,
    )
    
    session = SQLiteSession("management_demo", "management.db")
    print(f"🗄️  创建会话: {session.session_id}")
    
    # 添加一些对话
    conversations = [
        "我叫李四",
        "我住在上海",
        "我喜欢编程",
    ]
    
    for conv in conversations:
        print(f"\n👤 用户: {conv}")
        await Runner.run(agent, conv, session=session)
    
    # 查看所有数据
    print(f"\n📋 当前会话数据:")
    items = await session.get_items()
    print(f"总共有 {len(items)} 条记录")
    for i, item in enumerate(items, 1):
        print(f"  {i}. 角色: {item.get('role', 'unknown')}")
        print(f"     内容: {item.get('content', 'unknown')}")
        print(f"     时间: {item.get('timestamp', 'unknown')}")
        print()
    
    # 删除最后一条记录
    print(f"🗑️  删除最后一条记录...")
    last_item = await session.pop_item()
    print(f"删除的记录: {last_item}")
    
    # 查看删除后的数据
    print(f"\n📋 删除后的数据:")
    items = await session.get_items()
    print(f"总共有 {len(items)} 条记录")
    for i, item in enumerate(items, 1):
        print(f"  {i}. 角色: {item.get('role', 'unknown')}")
        print(f"     内容: {item.get('content', 'unknown')}")
    
    # 清除所有数据
    print(f"\n🗑️  清除所有数据...")
    await session.clear_session()
    
    # 验证清除结果
    print(f"\n📋 清除后的数据:")
    items = await session.get_items()
    print(f"总共有 {len(items)} 条记录")

async def demo_database_inspection():
    """演示数据库检查"""
    print("\n" + "="*60)
    print("🗄️  数据库文件检查")
    print("="*60)
    
    import sqlite3
    
    # 检查数据库文件
    db_files = ["demo_conversations.db", "management.db"]
    
    for db_file in db_files:
        if os.path.exists(db_file):
            print(f"\n📁 数据库文件: {db_file}")
            print(f"📊 文件大小: {os.path.getsize(db_file)} bytes")
            
            # 连接数据库查看表结构
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # 查看表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"📋 表列表: {[table[0] for table in tables]}")
            
            # 查看数据
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"📊 表 {table_name} 有 {count} 条记录")
                
                if count > 0:
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                    rows = cursor.fetchall()
                    print(f"📝 示例数据: {rows[:2]}")
            
            conn.close()
        else:
            print(f"❌ 数据库文件 {db_file} 不存在")

async def main():
    """主函数"""
    print("\n" + "🚀"*30)
    print("🔍 会话数据存储演示")
    print("🚀"*30)
    
    setup_custom_client()
    print("✅ 自定义客户端配置完成\n")
    
    # 运行演示
    await demo_session_data_structure()
    await demo_session_management()
    await demo_database_inspection()
    
    print("\n" + "="*60)
    print("✅ 演示完成！")
    print("="*60)
    print("\n📖 关键理解:")
    print("1. 会话数据是透明的，不是黑盒")
    print("2. 数据存储在 SQLite 数据库中")
    print("3. 每条对话都有明确的数据结构")
    print("4. 你可以查看、修改、删除数据")
    print("5. 数据格式是标准化的 JSON")
    print("\n💡 总结:")
    print("- 会话管理是透明的数据存储")
    print("- 你可以完全控制数据的存储和检索")
    print("- 不是黑盒，而是标准化的数据结构")

if __name__ == "__main__":
    if CUSTOM_API_KEY == "your-api-key-here":
        print("⚠️  请先设置 API Key:")
        print("export AIHUBMIX_API_KEY='your-actual-api-key'")
    else:
        asyncio.run(main())
