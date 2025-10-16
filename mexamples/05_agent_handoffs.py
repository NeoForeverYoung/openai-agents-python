"""
第五课：Agent 交接
学习如何实现多 Agent 协作，让不同的 Agent 处理不同类型的任务
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

# ============ 工具定义 ============

@function_tool
def get_weather(city: Annotated[str, "城市名称"]) -> str:
    """获取天气信息"""
    # 实际调用天气API，这里只是模拟一下
    print(f"🌤️  [天气工具] 查询: {city}")
    weather_data = {
        "北京": "晴天，温度 15-25°C，空气质量良好",
        "上海": "多云，温度 18-26°C，有轻微雾霾",
        "深圳": "小雨，温度 22-28°C，湿度较高",
    }
    return weather_data.get(city, f"{city}的天气是晴天，温度 20°C")

@function_tool
def calculate(expression: Annotated[str, "数学表达式"]) -> str:
    """执行数学计算"""
    print(f"🔢 [计算工具] 计算: {expression}")
    try:
        # 简单的计算器（实际应用中需要更安全的实现）
        result = eval(expression)
        return f"计算结果: {expression} = {result}"
    except:
        return f"无法计算表达式: {expression}"

@function_tool
def search_books(keyword: Annotated[str, "搜索关键词"]) -> str:
    """搜索书籍"""
    print(f"📚 [图书工具] 搜索: {keyword}")
    books = {
        "python": "《Python编程：从入门到实践》、《流畅的Python》",
        "ai": "《人工智能：一种现代的方法》、《深度学习》",
        "算法": "《算法导论》、《数据结构与算法分析》",
    }
    return books.get(keyword.lower(), f"找到关于'{keyword}'的书籍")

@function_tool
def get_time() -> str:
    """获取当前时间"""
    print(f"⏰ [时间工具] 获取当前时间")
    from datetime import datetime
    now = datetime.now()
    return f"当前时间: {now.strftime('%Y年%m月%d日 %H:%M:%S')}"

# ============ 示例演示 ============

async def example_1_basic_handoff():
    """示例1: 基础 Agent 交接"""
    print("\n" + "="*60)
    print("📚 示例1: 基础 Agent 交接 - 任务路由")
    print("="*60)
    
    # 创建专业化的 Agent
    weather_agent = Agent(
        name="天气专家",
        handoff_description="专门处理天气查询的专家",
        instructions="你是一个天气专家，专门回答天气相关的问题。",
        model=CHEAP_MODEL,
        tools=[get_weather],
    )
    
    math_agent = Agent(
        name="数学专家",
        handoff_description="专门处理数学计算的专家",
        instructions="你是一个数学专家，专门处理数学计算和问题。",
        model=CHEAP_MODEL,
        tools=[calculate],
    )
    
    # 创建路由 Agent
    router_agent = Agent(
        name="智能路由助手",
        instructions="""你是一个智能路由助手，根据用户的问题类型，将任务转交给合适的专家：
        - 天气相关问题 → 转交给天气专家
        - 数学计算问题 → 转交给数学专家
        - 其他问题 → 直接回答
        """,
        model=CHEAP_MODEL,
        handoffs=[weather_agent, math_agent],
    )
    
    # 测试不同类型的任务
    test_questions = [
        "北京今天天气怎么样？",  # 应该转交给天气专家
        "帮我算一下 25 + 37",    # 应该转交给数学专家
        "你好，请介绍一下你自己",  # 直接回答
        "上海明天会下雨吗？",     # 应该转交给天气专家
        "100 除以 5 等于多少？",  # 应该转交给数学专家
    ]
    
    for question in test_questions:
        print(f"\n👤 用户: {question}")
        result = await Runner.run(router_agent, question)
        print(f"🤖 助手: {result.final_output}")
        print("-" * 40)

async def example_2_complex_handoff():
    """示例2: 复杂 Agent 交接"""
    print("\n" + "="*60)
    print("📚 示例2: 复杂 Agent 交接 - 多专家协作")
    print("="*60)
    
    # 创建多个专业 Agent
    weather_agent = Agent(
        name="天气专家",
        handoff_description="天气查询和预报专家",
        instructions="你是天气专家，提供准确的天气信息和建议。",
        model=CHEAP_MODEL,
        tools=[get_weather],
    )
    
    math_agent = Agent(
        name="数学专家",
        handoff_description="数学计算和问题解决专家",
        instructions="你是数学专家，擅长各种数学计算和问题解决。",
        model=CHEAP_MODEL,
        tools=[calculate],
    )
    
    book_agent = Agent(
        name="图书专家",
        handoff_description="图书推荐和搜索专家",
        instructions="你是图书专家，可以推荐和搜索各种书籍。",
        model=CHEAP_MODEL,
        tools=[search_books],
    )
    
    time_agent = Agent(
        name="时间专家",
        handoff_description="时间和日期查询专家",
        instructions="你是时间专家，提供准确的时间信息。",
        model=CHEAP_MODEL,
        tools=[get_time],
    )
    
    # 创建智能路由 Agent
    smart_router = Agent(
        name="智能路由助手",
        instructions="""你是一个智能路由助手，根据用户问题将任务转交给最合适的专家：
        
        专家列表：
        - 天气专家：处理天气查询、预报、建议
        - 数学专家：处理数学计算、公式、问题
        - 图书专家：处理图书推荐、搜索、评价
        - 时间专家：处理时间查询、日期计算
        
        请仔细分析用户问题，选择最合适的专家。
        """,
        model=CHEAP_MODEL,
        handoffs=[weather_agent, math_agent, book_agent, time_agent],
    )
    
    # 复杂测试场景
    complex_questions = [
        "我想学习Python，推荐几本书",  # 图书专家
        "现在几点了？",                # 时间专家
        "北京和上海的天气有什么不同？",  # 天气专家
        "帮我算一下 (25 + 37) * 2",    # 数学专家
        "推荐一些关于人工智能的书",     # 图书专家
        "明天是星期几？",              # 时间专家
        "深圳今天会下雨吗？",          # 天气专家
        "计算 100 的平方根",           # 数学专家
    ]
    
    for question in complex_questions:
        print(f"\n👤 用户: {question}")
        result = await Runner.run(smart_router, question)
        print(f"🤖 助手: {result.final_output}")
        print("-" * 40)

async def example_3_handoff_with_session():
    """示例3: 交接 + 会话管理"""
    print("\n" + "="*60)
    print("📚 示例3: 交接 + 会话管理 - 记忆协作")
    print("="*60)
    
    # 创建带记忆的专业 Agent
    weather_agent = Agent(
        name="天气专家",
        handoff_description="天气查询专家，会记住用户的天气偏好",
        instructions="你是天气专家，会记住用户之前查询过的城市和偏好。",
        model=CHEAP_MODEL,
        tools=[get_weather],
    )
    
    math_agent = Agent(
        name="数学专家",
        handoff_description="数学计算专家，会记住用户的计算历史",
        instructions="你是数学专家，会记住用户之前做过的计算。",
        model=CHEAP_MODEL,
        tools=[calculate],
    )
    
    # 创建带记忆的路由 Agent
    memory_router = Agent(
        name="记忆路由助手",
        instructions="""你是一个有记忆的智能路由助手，会记住用户的偏好和历史，并将任务转交给合适的专家。
        
        专家：
        - 天气专家：处理天气相关查询
        - 数学专家：处理数学计算
        
        请记住用户的信息，提供个性化服务。
        """,
        model=CHEAP_MODEL,
        handoffs=[weather_agent, math_agent],
    )
    
    # 创建会话
    session = SQLiteSession("handoff_user", "conversations.db")
    print(f"🗄️  创建会话: {session.session_id}")
    
    # 多轮对话测试
    conversations = [
        "我叫小明，住在北京",
        "北京今天天气怎么样？",  # 转交给天气专家
        "帮我算一下 25 + 37",    # 转交给数学专家
        "我刚才问过你什么？",     # 基于记忆回答
        "我住在哪个城市？",       # 基于记忆回答
        "上海天气如何？",         # 转交给天气专家
        "我做过什么计算？",       # 基于记忆回答
    ]
    
    for question in conversations:
        print(f"\n👤 用户: {question}")
        result = await Runner.run(memory_router, question, session=session)
        print(f"🤖 助手: {result.final_output}")
        print("-" * 40)

async def example_4_conditional_handoff():
    """示例4: 条件性交接"""
    print("\n" + "="*60)
    print("📚 示例4: 条件性交接 - 智能决策")
    print("="*60)
    
    # 创建不同级别的专家
    junior_math_agent = Agent(
        name="初级数学助手",
        handoff_description="处理简单数学计算（加减乘除）",
        instructions="你是初级数学助手，专门处理简单的数学计算。",
        model=CHEAP_MODEL,
        tools=[calculate],
    )
    
    senior_math_agent = Agent(
        name="高级数学专家",
        handoff_description="处理复杂数学问题（微积分、代数等）",
        instructions="你是高级数学专家，专门处理复杂的数学问题。",
        model=CHEAP_MODEL,
        tools=[calculate],
    )
    
    # 创建智能决策 Agent
    # handoffs的过程，其实也是AI大模型自动分析任务，然后选择合适的专家的过程
    decision_agent = Agent(
        name="智能决策助手",
        instructions="""你是一个智能决策助手，根据问题的复杂度选择合适的专家：
        
        - 简单计算（加减乘除、基本运算）→ 初级数学助手
        - 复杂问题（微积分、代数、几何等）→ 高级数学专家
        
        请仔细分析问题的复杂度，选择合适的专家。
        """,
        model=CHEAP_MODEL,
        handoffs=[junior_math_agent, senior_math_agent],
    )
    
    # 不同复杂度的问题
    math_questions = [
        "25 + 37 等于多少？",           # 简单 → 初级
        "100 除以 5 等于多少？",        # 简单 → 初级
        "计算 x^2 + 2x + 1 = 0 的解",   # 复杂 → 高级
        "求函数 f(x) = x^2 的导数",     # 复杂 → 高级
        "15 * 8 等于多少？",            # 简单 → 初级
        "计算 ∫(x^2)dx 从 0 到 1",     # 复杂 → 高级
    ]
    
    for question in math_questions:
        print(f"\n👤 用户: {question}")
        result = await Runner.run(decision_agent, question)
        print(f"🤖 助手: {result.final_output}")
        print("-" * 40)

async def example_5_handoff_chain():
    """示例5: 交接链 - 多级协作"""
    print("\n" + "="*60)
    print("📚 示例5: 交接链 - 多级协作")
    print("="*60)
    
    # 第三级专家
    weather_forecast_agent = Agent(
        name="天气预报专家",
        handoff_description="提供详细的天气预报和建议",
        instructions="你是天气预报专家，提供详细的天气预报和生活建议。",
        model=CHEAP_MODEL,
        tools=[get_weather],
    )
    
    # 第二级专家
    weather_router = Agent(
        name="天气路由助手",
        handoff_description="天气问题的路由助手",
        instructions="你是天气路由助手，将天气问题转交给天气预报专家。",
        model=CHEAP_MODEL,
        handoffs=[weather_forecast_agent],
    )
    
    # 第一级总路由
    main_router = Agent(
        name="主路由助手",
        instructions="""你是主路由助手，根据问题类型进行初步分类：
        - 天气问题 → 转交给天气路由助手
        - 其他问题 → 直接回答
        """,
        model=CHEAP_MODEL,
        handoffs=[weather_router],
    )
    
    # 测试交接链
    chain_questions = [
        "北京今天天气怎么样？",  # 主路由 → 天气路由 → 天气预报专家
        "你好，请介绍一下你自己",  # 主路由直接回答
        "上海明天会下雨吗？",     # 主路由 → 天气路由 → 天气预报专家
    ]
    
    for question in chain_questions:
        print(f"\n👤 用户: {question}")
        result = await Runner.run(main_router, question)
        print(f"🤖 助手: {result.final_output}")
        print("-" * 40)

async def main():
    """主函数"""
    print("\n" + "🚀"*30)
    print("🎓 第五课：Agent 交接")
    print("🚀"*30)
    
    setup_custom_client()
    print("✅ 自定义客户端配置完成\n")
    
    # 运行所有示例
    await example_1_basic_handoff()
    await example_2_complex_handoff()
    await example_3_handoff_with_session()
    await example_4_conditional_handoff()
    await example_5_handoff_chain()
    
    print("\n" + "="*60)
    print("✅ 第五课完成！")
    print("="*60)
    print("\n📖 学习要点:")
    print("1. 使用 handoffs 参数定义可交接的 Agent")
    print("2. 使用 handoff_description 描述 Agent 的专长")
    print("3. Agent 会自动选择合适的交接目标")
    print("4. 支持多级交接和复杂协作")
    print("5. 交接可以与会话管理结合")
    print("6. 实现专业化和模块化的 Agent 系统")
    print("\n🎉 恭喜！你已经完成了 OpenAI Agents SDK 的核心学习！")

if __name__ == "__main__":
    if CUSTOM_API_KEY == "your-api-key-here":
        print("⚠️  请先设置 API Key:")
        print("export AIHUBMIX_API_KEY='your-actual-api-key'")
    else:
        asyncio.run(main())
