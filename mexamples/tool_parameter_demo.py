"""
工具参数提取演示
展示 Agent 如何自动从用户问题中提取参数并调用工具
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
def get_weather(city: Annotated[str, "要查询天气的城市名称"]) -> str:
    """获取指定城市的天气信息"""
    print(f"🌤️  [工具调用] get_weather(city='{city}')")
    print(f"    📍 参数来源: Agent 从用户问题中自动提取")
    print(f"    🔍 提取过程: 用户说'{city}' → Agent 识别为城市名 → 传递给工具")
    
    weather_data = {
        "北京": "晴天，温度 15-25°C，空气质量良好",
        "上海": "多云，温度 18-26°C，有轻微雾霾",
        "深圳": "小雨，温度 22-28°C，湿度较高",
        "成都": "阴天，温度 16-23°C，空气质量优",
    }
    
    result = weather_data.get(city, f"{city}的天气是晴天，温度 20°C")
    print(f"    📤 返回结果: {result}")
    return result

@function_tool
def calculate(
    operation: Annotated[str, "运算类型：add(加), sub(减), mul(乘), div(除)"],
    a: Annotated[float, "第一个数字"],
    b: Annotated[float, "第二个数字"]
) -> str:
    """执行数学计算"""
    print(f"🔢 [工具调用] calculate(operation='{operation}', a={a}, b={b})")
    print(f"    📍 参数来源: Agent 从用户问题中自动提取")
    print(f"    🔍 提取过程: 用户说'{a} {operation} {b}' → Agent 识别为数学表达式 → 分解参数")
    
    operations = {
        "add": a + b,
        "sub": a - b,
        "mul": a * b,
        "div": a / b if b != 0 else "错误：除数不能为零"
    }
    
    result = operations.get(operation, "不支持的运算")
    print(f"    📤 返回结果: {result}")
    return f"计算结果: {a} {operation} {b} = {result}"

@function_tool
def search_books(
    title: Annotated[str, "书籍标题"],
    author: Annotated[str, "作者姓名"]
) -> str:
    """搜索指定作者的书"""
    print(f"📚 [工具调用] search_books(title='{title}', author='{author}')")
    print(f"    📍 参数来源: Agent 从用户问题中自动提取")
    print(f"    🔍 提取过程: 用户提到书名和作者 → Agent 智能识别并分离参数")
    
    # 模拟搜索结果
    result = f"找到书籍《{title}》，作者：{author}，评分：8.5/10"
    print(f"    📤 返回结果: {result}")
    return result

# ============ 演示示例 ============

async def demo_weather_parameter_extraction():
    """演示天气查询的参数提取"""
    print("\n" + "="*60)
    print("🌤️  演示1: 天气查询参数提取")
    print("="*60)
    
    agent = Agent(
        name="天气助手",
        instructions="你是一个天气查询助手，可以帮助用户查询城市天气。",
        model=CHEAP_MODEL,
        tools=[get_weather],
    )
    
    # 不同的提问方式，Agent 都能正确提取参数
    test_questions = [
        "北京今天天气怎么样？",
        "我想知道上海的天气",
        "深圳的天气如何？",
        "帮我查一下成都的天气情况",
    ]
    
    for question in test_questions:
        print(f"\n👤 用户: {question}")
        print("🤖 Agent 分析过程:")
        result = await Runner.run(agent, question)
        print(f"📝 最终回复: {result.final_output}")
        print("-" * 50)

async def demo_calculation_parameter_extraction():
    """演示计算器的参数提取"""
    print("\n" + "="*60)
    print("🔢 演示2: 计算器参数提取")
    print("="*60)
    
    agent = Agent(
        name="计算助手",
        instructions="你是一个数学计算助手，可以执行基本的数学运算。",
        model=CHEAP_MODEL,
        tools=[calculate],
    )
    
    # 不同的数学表达方式
    test_questions = [
        "帮我算一下 25 加 8",
        "100 减去 30 等于多少？",
        "15 乘以 6 的结果",
        "50 除以 5 是多少？",
    ]
    
    for question in test_questions:
        print(f"\n👤 用户: {question}")
        print("🤖 Agent 分析过程:")
        result = await Runner.run(agent, question)
        print(f"📝 最终回复: {result.final_output}")
        print("-" * 50)

async def demo_complex_parameter_extraction():
    """演示复杂参数提取"""
    print("\n" + "="*60)
    print("📚 演示3: 复杂参数提取")
    print("="*60)
    
    agent = Agent(
        name="图书助手",
        instructions="你是一个图书搜索助手，可以根据书名和作者搜索书籍。",
        model=CHEAP_MODEL,
        tools=[search_books],
    )
    
    # 复杂的自然语言表达
    test_questions = [
        "我想找余华写的《活着》这本书",
        "帮我搜索一下《三体》，作者是刘慈欣",
        "村上春树的《挪威的森林》怎么样？",
    ]
    
    for question in test_questions:
        print(f"\n👤 用户: {question}")
        print("🤖 Agent 分析过程:")
        result = await Runner.run(agent, question)
        print(f"📝 最终回复: {result.final_output}")
        print("-" * 50)

async def demo_parameter_extraction_mechanism():
    """演示参数提取机制"""
    print("\n" + "="*60)
    print("🔍 参数提取机制详解")
    print("="*60)
    
    print("""
📋 Agent 参数提取的工作原理：

1. 🧠 问题理解
   - Agent 使用 LLM 理解用户问题的语义
   - 识别问题类型和所需工具

2. 🔍 参数识别
   - 从自然语言中提取关键信息
   - 匹配工具函数的参数要求
   - 进行类型转换（字符串→数字等）

3. 🛠️ 工具调用
   - 自动构造函数调用
   - 传递正确的参数
   - 处理异常情况

4. 📤 结果处理
   - 获取工具执行结果
   - 生成用户友好的回复
   - 整合到对话流程中

💡 关键点：
- 参数提取是自动的，不需要手动解析
- Agent 能理解各种自然语言表达方式
- 支持类型转换和参数验证
- 错误处理机制完善
    """)

async def main():
    """主函数"""
    print("\n" + "🚀"*30)
    print("🔍 工具参数提取演示")
    print("🚀"*30)
    
    setup_custom_client()
    print("✅ 自定义客户端配置完成\n")
    
    # 运行所有演示
    await demo_weather_parameter_extraction()
    await demo_calculation_parameter_extraction()
    await demo_complex_parameter_extraction()
    await demo_parameter_extraction_mechanism()
    
    print("\n" + "="*60)
    print("✅ 演示完成！")
    print("="*60)
    print("\n📖 总结:")
    print("1. Agent 会自动从用户问题中提取参数")
    print("2. 支持各种自然语言表达方式")
    print("3. 自动进行类型转换和验证")
    print("4. 无需手动解析用户输入")
    print("5. 这是 LLM 的强大能力之一")

if __name__ == "__main__":
    if CUSTOM_API_KEY == "your-api-key-here":
        print("⚠️  请先设置 API Key:")
        print("export AIHUBMIX_API_KEY='your-actual-api-key'")
    else:
        asyncio.run(main())
