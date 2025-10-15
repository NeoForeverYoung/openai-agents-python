"""
第四课：会话管理
学习如何实现多轮对话和记忆功能，让 Agent 记住之前的对话内容
"""

import asyncio
import os
from typing import Annotated
from openai import AsyncOpenAI
from agents import (
    Agent, 
    Runner,
    function_tool,
    SQLiteSession,
    set_default_openai_client,
    set_default_openai_api,
    set_tracing_disabled,
)

# 自定义域名配置
CUSTOM_BASE_URL = "https://aihubmix.com/v1"
CUSTOM_API_KEY = os.getenv("AIHUBMIX_API_KEY", "your-api-key-here")
CHEAP_MODEL = "gpt-3.5-turbo"

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

# ============ 工具定义 ============

@function_tool
def get_user_info(user_id: Annotated[str, "用户ID"]) -> str:
    """获取用户信息"""
    print(f"👤 获取用户信息: user_id='{user_id}'")
    
    # 模拟用户数据库
    users = {
        "user_001": "张三，25岁，软件工程师，喜欢编程和阅读",
        "user_002": "李四，30岁，产品经理，喜欢旅行和摄影",
        "user_003": "王五，28岁，设计师，喜欢艺术和音乐",
    }
    
    return users.get(user_id, f"用户 {user_id} 的信息未找到")

@function_tool
def save_user_preference(user_id: Annotated[str, "用户ID"], preference: Annotated[str, "用户偏好"]) -> str:
    """保存用户偏好"""
    print(f"💾 保存用户偏好: user_id='{user_id}', preference='{preference}'")
    return f"已保存用户 {user_id} 的偏好: {preference}"

@function_tool
def get_weather(city: Annotated[str, "城市名称"]) -> str:
    """获取天气信息"""
    print(f"🌤️  查询天气: city='{city}'")
    
    weather_data = {
        "北京": "晴天，温度 15-25°C，空气质量良好",
        "上海": "多云，温度 18-26°C，有轻微雾霾",
        "深圳": "小雨，温度 22-28°C，湿度较高",
        "成都": "阴天，温度 16-23°C，空气质量优",
    }
    
    return weather_data.get(city, f"{city}的天气是晴天，温度 20°C")

# ============ 示例演示 ============

async def example_1_basic_session():
    """示例1: 基础会话管理"""
    print("\n" + "="*60)
    print("📚 示例1: 基础会话管理 - 多轮对话")
    print("="*60)
    
    agent = Agent(
        name="记忆助手",
        instructions="你是一个有记忆的智能助手，会记住之前的对话内容，并基于上下文回答问题。",
        model=CHEAP_MODEL,
    )
    
    # 创建会话
    session = SQLiteSession("user_001", "conversations.db")
    print(f"🗄️  创建会话: {session.session_id}")
    
    # 第一轮对话
    print(f"\n👤 用户: 我的名字是张三")
    result1 = await Runner.run(agent, "我的名字是张三", session=session)
    print(f"🤖 助手: {result1.final_output}")
    
    # 第二轮对话 - Agent 应该记住名字
    print(f"\n👤 用户: 我刚才告诉你我的名字是什么？")
    result2 = await Runner.run(agent, "我刚才告诉你我的名字是什么？", session=session)
    print(f"🤖 助手: {result2.final_output}")
    
    # 第三轮对话 - 继续基于上下文
    print(f"\n👤 用户: 我今年25岁")
    result3 = await Runner.run(agent, "我今年25岁", session=session)
    print(f"🤖 助手: {result3.final_output}")
    
    # 第四轮对话 - 综合信息
    print(f"\n👤 用户: 请介绍一下我")
    result4 = await Runner.run(agent, "请介绍一下我", session=session)
    print(f"🤖 助手: {result4.final_output}")

async def example_2_multiple_sessions():
    """示例2: 多个独立会话"""
    print("\n" + "="*60)
    print("📚 示例2: 多个独立会话 - 不同用户")
    print("="*60)
    
    agent = Agent(
        name="多用户助手",
        instructions="你是一个支持多用户的智能助手，每个用户都有独立的对话历史。",
        model=CHEAP_MODEL,
    )
    
    # 用户1的会话
    session1 = SQLiteSession("user_001", "conversations.db")
    print(f"🗄️  用户1会话: {session1.session_id}")
    
    print(f"\n👤 用户1: 我喜欢编程")
    result1 = await Runner.run(agent, "我喜欢编程", session=session1)
    print(f"🤖 助手: {result1.final_output}")
    
    # 用户2的会话（独立）
    session2 = SQLiteSession("user_002", "conversations.db")
    print(f"\n🗄️  用户2会话: {session2.session_id}")
    
    print(f"\n👤 用户2: 我喜欢旅行")
    result2 = await Runner.run(agent, "我喜欢旅行", session=session2)
    print(f"🤖 助手: {result2.final_output}")
    
    # 回到用户1 - 应该记住用户1的偏好
    print(f"\n👤 用户1: 我的爱好是什么？")
    result3 = await Runner.run(agent, "我的爱好是什么？", session=session1)
    print(f"🤖 助手: {result3.final_output}")
    
    # 用户2的独立记忆
    print(f"\n👤 用户2: 我的爱好是什么？")
    result4 = await Runner.run(agent, "我的爱好是什么？", session=session2)
    print(f"🤖 助手: {result4.final_output}")

async def example_3_session_with_tools():
    """示例3: 会话 + 工具"""
    print("\n" + "="*60)
    print("📚 示例3: 会话 + 工具 - 智能助手")
    print("="*60)
    
    agent = Agent(
        name="智能助手",
        instructions="""你是一个智能助手，可以：
        1. 记住用户的个人信息和偏好
        2. 查询天气信息
        3. 保存用户偏好
        
        请基于对话历史提供个性化的服务。
        """,
        model=CHEAP_MODEL,
        tools=[get_user_info, save_user_preference, get_weather],
    )
    
    session = SQLiteSession("user_003", "conversations.db")
    print(f"🗄️  创建会话: {session.session_id}")
    
    # 对话流程
    conversations = [
        "我的用户ID是user_003",
        "我喜欢科幻电影",
        "帮我查一下北京的天气",
        "记住我喜欢科幻电影这个偏好",
        "我住在北京，今天天气怎么样？",
        "基于我的偏好，推荐一部科幻电影",
    ]
    
    for i, question in enumerate(conversations, 1):
        print(f"\n👤 用户: {question}")
        result = await Runner.run(agent, question, session=session)
        print(f"🤖 助手: {result.final_output}")
        print("-" * 40)

async def example_4_session_management():
    """示例4: 会话管理操作"""
    print("\n" + "="*60)
    print("📚 示例4: 会话管理操作")
    print("="*60)
    
    agent = Agent(
        name="会话管理助手",
        instructions="你是一个会话管理助手，可以帮助用户管理对话历史。",
        model=CHEAP_MODEL,
    )
    
    session = SQLiteSession("demo_user", "conversations.db")
    print(f"🗄️  创建会话: {session.session_id}")
    
    # 添加一些对话历史
    print(f"\n👤 用户: 我叫小明")
    await Runner.run(agent, "我叫小明", session=session)
    
    print(f"\n👤 用户: 我今年20岁")
    await Runner.run(agent, "我今年20岁", session=session)
    
    print(f"\n👤 用户: 我是学生")
    await Runner.run(agent, "我是学生", session=session)
    
    # 查看会话历史
    print(f"\n📋 查看会话历史:")
    items = await session.get_items()
    for i, item in enumerate(items, 1):
        print(f"  {i}. {item}")
    
    # 清除会话
    print(f"\n🗑️  清除会话历史...")
    await session.clear_session()
    
    # 验证清除结果
    print(f"\n👤 用户: 我叫什么名字？")
    result = await Runner.run(agent, "我叫什么名字？", session=session)
    print(f"🤖 助手: {result.final_output}")
    
    # 重新添加信息
    print(f"\n👤 用户: 我叫小红")
    await Runner.run(agent, "我叫小红", session=session)
    
    print(f"\n👤 用户: 我叫什么名字？")
    result = await Runner.run(agent, "我叫什么名字？", session=session)
    print(f"🤖 助手: {result.final_output}")

async def example_5_advanced_session_features():
    """示例5: 高级会话功能"""
    print("\n" + "="*60)
    print("📚 示例5: 高级会话功能")
    print("="*60)
    
    agent = Agent(
        name="高级助手",
        instructions="你是一个高级智能助手，具有复杂的记忆和推理能力。",
        model=CHEAP_MODEL,
    )
    
    session = SQLiteSession("advanced_user", "conversations.db")
    print(f"🗄️  创建高级会话: {session.session_id}")
    
    # 复杂对话场景
    scenarios = [
        "我想学习Python编程",
        "我没有任何编程经验",
        "我应该从哪里开始？",
        "我每天只有1小时学习时间",
        "基于我的情况，给我制定一个学习计划",
        "我昨天问过你什么？",
        "我的学习计划是什么？",
    ]
    
    for i, question in enumerate(scenarios, 1):
        print(f"\n👤 用户: {question}")
        result = await Runner.run(agent, question, session=session)
        print(f"🤖 助手: {result.final_output}")
        print("-" * 40)

async def main():
    """主函数"""
    print("\n" + "🚀"*30)
    print("🎓 第四课：会话管理")
    print("🚀"*30)
    
    setup_custom_client()
    print("✅ 自定义客户端配置完成\n")
    
    # 运行所有示例
    await example_1_basic_session()
    await example_2_multiple_sessions()
    await example_3_session_with_tools()
    await example_4_session_management()
    await example_5_advanced_session_features()
    
    print("\n" + "="*60)
    print("✅ 第四课完成！")
    print("="*60)
    print("\n📖 学习要点:")
    print("1. 使用 SQLiteSession 创建会话")
    print("2. 每个会话都有独立的对话历史")
    print("3. Agent 会自动记住之前的对话内容")
    print("4. 支持会话管理操作（查看、清除历史）")
    print("5. 会话可以与工具结合使用")
    print("6. 支持多用户独立会话")
    print("\n💡 下一步: 学习 Agent 交接和多 Agent 协作")

if __name__ == "__main__":
    if CUSTOM_API_KEY == "your-api-key-here":
        print("⚠️  请先设置 API Key:")
        print("export AIHUBMIX_API_KEY='your-actual-api-key'")
    else:
        asyncio.run(main())
