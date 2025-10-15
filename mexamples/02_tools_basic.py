"""
第二课：工具集成基础
学习如何给 Agent 添加工具函数，让 Agent 能够执行实际操作
"""

import asyncio
import os
from typing import Annotated
from openai import AsyncOpenAI
from agents import (
    Agent, 
    Runner,
    function_tool,
    set_default_openai_client,
    set_default_openai_api,
    set_tracing_disabled,
)

# 自定义域名配置
CUSTOM_BASE_URL = "https://aihubmix.com/v1"
CUSTOM_API_KEY = os.getenv("AIHUBMIX_API_KEY", "your-api-key-here")

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

# 这个function_tool装饰器，是用来定义工具的，定义的工具需要有参数和返回值
# 参数和返回值需要有类型提示，类型提示需要用 Annotated 类型提示
# Annotated 类型提示是用来给类型添加元数据的，元数据是用来描述类型的，比如描述类型是用来做什么的
# 比如这个 get_weather 工具，参数 city 是用来查询天气的城市名称，返回值是用来返回天气信息
# 参数和返回值的类型提示是用来帮助 Agent 理解参数和返回值的，Agent 会根据参数和返回值的类型提示来选择合适的工具
@function_tool
def get_weather(city: Annotated[str, "要查询天气的城市名称"]) -> str:
    """获取指定城市的天气信息"""
    print(f"🌤️  调用工具: get_weather(city='{city}')")
    
    # 这里可以集成真实的天气 API，现在我们返回模拟数据
    weather_data = {
        "北京": "晴天，温度 15-25°C，空气质量良好",
        "上海": "多云，温度 18-26°C，有轻微雾霾",
        "深圳": "小雨，温度 22-28°C，湿度较高",
        "成都": "阴天，温度 16-23°C，空气质量优",
    }
    
    return weather_data.get(city, f"{city}的天气是晴天，温度 20°C")

@function_tool
def calculate(
    operation: Annotated[str, "运算类型：add(加), sub(减), mul(乘), div(除)"],
    a: Annotated[float, "第一个数字"],
    b: Annotated[float, "第二个数字"]
) -> str:
    """执行数学计算"""
    print(f"🔢 调用工具: calculate(operation='{operation}', a={a}, b={b})")
    
    operations = {
        "add": a + b,
        "sub": a - b,
        "mul": a * b,
        "div": a / b if b != 0 else "错误：除数不能为零"
    }
    
    result = operations.get(operation, "不支持的运算")
    return f"计算结果: {a} {operation} {b} = {result}"

@function_tool
def get_current_time() -> str:
    """获取当前时间"""
    print(f"⏰ 调用工具: get_current_time()")
    
    from datetime import datetime
    now = datetime.now()
    return f"当前时间: {now.strftime('%Y年%m月%d日 %H:%M:%S')}"

# ============ 示例演示 ============

async def example_1_single_tool():
    """示例1: 使用单个工具"""
    print("\n" + "="*50)
    print("📚 示例1: 单个工具 - 天气查询")
    print("="*50)
    
    agent = Agent(
        name="天气助手",
        instructions="你是一个天气查询助手，可以帮助用户查询城市天气。",
        tools=[get_weather],  # 只添加天气工具
    )
    
    questions = [
        "北京今天天气怎么样？",
        #"我想知道上海的天气",
    ]
    
    for question in questions:
        print(f"\n👤 用户: {question}")
        result = await Runner.run(agent, question)
        print(f"🤖 助手: {result.final_output}")

async def example_2_multiple_tools():
    """示例2: 使用多个工具"""
    print("\n" + "="*50)
    print("📚 示例2: 多个工具 - 智能助手")
    print("="*50)

    """ 
    agent = Agent(
        name="智能助手",
        instructions="你是一个多功能智能助手，可以查询天气、进行计算和告诉用户当前时间。",
        tools=[get_weather, calculate, get_current_time],  # 添加多个工具
    )
    """
    agent = Agent(
    name="智能助手",
    instructions="""你是一个多功能智能助手，可以：
    1. 查询天气信息
    2. 进行数学计算  
    3. 告诉用户当前时间
    
    如果用户的问题与这些功能无关，请礼貌地告知用户你只能处理上述类型的任务。
    """,
    tools=[get_weather, calculate, get_current_time],
)
    
    questions = [
        #"现在几点了？",
        #"帮我算一下 25 乘以 8 等于多少",
        #"深圳今天天气如何？",
        #"100 除以 5 是多少？",
        "苹果和梨哪个更甜",
    ]
    
    for question in questions:
        print(f"\n👤 用户: {question}")
        result = await Runner.run(agent, question)
        print(f"🤖 助手: {result.final_output}")

async def example_3_complex_query():
    """示例3: 复杂查询 - Agent 自动选择和组合工具"""
    print("\n" + "="*50)
    print("📚 示例3: 复杂查询 - 工具组合")
    print("="*50)
    
    agent = Agent(
        name="超级助手",
        instructions="""你是一个超级智能助手，可以：
        1. 查询天气信息
        2. 进行数学计算
        3. 告诉用户时间
        
        根据用户需求自动选择合适的工具，如果需要多个步骤，可以调用多个工具。
        """,
        tools=[get_weather, calculate, get_current_time],
    )
    
    # 复杂问题：需要组合使用多个工具
    questions = [
        "先告诉我现在几点，然后查一下北京的天气",
        "帮我算一下 15 加 27，然后再乘以 2",
    ]
    
    for question in questions:
        print(f"\n👤 用户: {question}")
        result = await Runner.run(agent, question)
        print(f"🤖 助手: {result.final_output}")

# 主函数,async 异步函数是异步函数，需要用 asyncio.run() 运行
async def main():
    """主函数"""
    print("\n" + "🚀"*25)
    print("🎓 第二课：工具集成基础")
    print("🚀"*25)
    
    # 设置自定义客户端
    setup_custom_client()
    print("✅ 自定义客户端配置完成\n")
    
    # 运行所有示例
    #await example_1_single_tool()
    await example_2_multiple_tools()
    #await example_3_complex_query()

    
    
    """
    print("\n" + "="*50)
    print("✅ 第二课完成！")
    print("="*50)
    print("\n📖 学习要点:")
    print("1. 使用 @function_tool 装饰器定义工具")
    print("2. 使用 Annotated 类型提示帮助 Agent 理解参数")
    print("3. Agent 会自动选择合适的工具来完成任务")
    print("4. 可以为 Agent 添加多个工具，它会智能地组合使用")
    print("\n💡 下一步: 学习结构化输出和类型安全")
    """

if __name__ == "__main__":
    if CUSTOM_API_KEY == "your-api-key-here":
        print("⚠️  请先设置 API Key:")
        print("export AIHUBMIX_API_KEY='your-actual-api-key'")
    else:
        asyncio.run(main())

