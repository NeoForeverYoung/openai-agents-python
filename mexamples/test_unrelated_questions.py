"""
测试 Agent 如何处理与工具无关的问题
"""

import asyncio
import os
from typing import Annotated
from openai import AsyncOpenAI
from agents import (
    Agent, 
    Runner,
    function_tool,
    InputGuardrail,
    GuardrailFunctionOutput,
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

# 工具定义
@function_tool
def get_weather(city: Annotated[str, "要查询天气的城市名称"]) -> str:
    """获取指定城市的天气信息"""
    print(f"🌤️  调用工具: get_weather(city='{city}')")
    return f"{city}的天气是晴天，温度 20°C"

@function_tool
def calculate(
    operation: Annotated[str, "运算类型：add(加), sub(减), mul(乘), div(除)"],
    a: Annotated[float, "第一个数字"],
    b: Annotated[float, "第二个数字"]
) -> str:
    """执行数学计算"""
    print(f"🔢 调用工具: calculate(operation='{operation}', a={a}, b={b})")
    return f"计算结果: {a} {operation} {b} = {a + b}"

@function_tool
def get_current_time() -> str:
    """获取当前时间"""
    print(f"⏰ 调用工具: get_current_time()")
    from datetime import datetime
    now = datetime.now()
    return f"当前时间: {now.strftime('%Y年%m月%d日 %H:%M:%S')}"

# ============ Guardrails 定义 ============

async def question_type_guardrail(ctx, agent, input_data):
    """检查问题类型是否与可用工具相关"""
    print(f"🛡️  护栏检查: 分析问题类型")
    
    # 定义相关关键词
    weather_keywords = ["天气", "温度", "下雨", "晴天", "阴天", "多云", "雾霾", "湿度"]
    calc_keywords = ["计算", "加", "减", "乘", "除", "等于", "算", "数学", "数字"]
    time_keywords = ["时间", "几点", "现在", "当前", "日期", "钟表"]
    
    question = input_data.lower()
    
    # 检查是否包含相关关键词
    has_weather = any(keyword in question for keyword in weather_keywords)
    has_calc = any(keyword in question for keyword in calc_keywords)
    has_time = any(keyword in question for keyword in time_keywords)
    
    is_related = has_weather or has_calc or has_time
    
    print(f"   天气相关: {has_weather}, 计算相关: {has_calc}, 时间相关: {has_time}")
    print(f"   是否相关: {is_related}")
    
    return GuardrailFunctionOutput(
        output_info={
            "is_related": is_related,
            "has_weather": has_weather,
            "has_calc": has_calc,
            "has_time": has_time
        },
        tripwire_triggered=not is_related,  # 如果不相关，触发护栏
    )

async def content_safety_guardrail(ctx, agent, input_data):
    """内容安全护栏 - 检查是否包含不当内容"""
    print(f"🛡️  安全护栏: 检查内容安全性")
    
    # 定义敏感词（示例）
    sensitive_words = ["暴力", "色情", "政治", "仇恨"]
    question = input_data.lower()
    
    has_sensitive = any(word in question for word in sensitive_words)
    
    print(f"   包含敏感词: {has_sensitive}")
    
    return GuardrailFunctionOutput(
        output_info={"has_sensitive_content": has_sensitive},
        tripwire_triggered=has_sensitive,  # 如果包含敏感内容，触发护栏
    )

async def length_guardrail(ctx, agent, input_data):
    """长度护栏 - 检查问题长度是否合理"""
    print(f"🛡️  长度护栏: 检查问题长度")
    
    question_length = len(input_data)
    is_too_short = question_length < 3
    is_too_long = question_length > 500
    
    print(f"   问题长度: {question_length}")
    print(f"   太短: {is_too_short}, 太长: {is_too_long}")
    
    return GuardrailFunctionOutput(
        output_info={
            "length": question_length,
            "is_too_short": is_too_short,
            "is_too_long": is_too_long
        },
        tripwire_triggered=is_too_short or is_too_long,
    )

async def test_agent_behavior():
    """测试 Agent 对不同类型问题的处理"""
    
    # 测试1: 默认行为
    print("\n" + "="*60)
    print("🧪 测试1: 默认行为 - Agent 会如何处理无关问题？")
    print("="*60)
    
    agent_default = Agent(
        name="默认助手",
        instructions="你是一个多功能智能助手，可以查询天气、进行计算和告诉用户当前时间。",
        tools=[get_weather, calculate, get_current_time],
    )
    
    test_questions = [
        "北京今天天气怎么样？",  # 相关 - 应该调用工具
        "苹果和梨哪个更甜？",    # 无关 - 会如何回答？
        "帮我算一下 5+3",       # 相关 - 应该调用工具
        "什么是人工智能？",      # 无关 - 会如何回答？
    ]
    
    for question in test_questions:
        print(f"\n👤 用户: {question}")
        result = await Runner.run(agent_default, question)
        print(f"🤖 助手: {result.final_output}")
        print("-" * 40)
    
    # 测试2: 限制性行为
    print("\n" + "="*60)
    print("🧪 测试2: 限制性行为 - 明确告知只能处理特定问题")
    print("="*60)
    
    agent_restricted = Agent(
        name="限制性助手",
        instructions="""你是一个多功能智能助手，只能处理以下类型的任务：
        1. 查询天气信息
        2. 进行数学计算
        3. 告诉用户当前时间
        
        如果用户的问题与这些功能无关，请礼貌地告知用户你只能处理上述类型的任务，并建议用户重新提问。
        """,
        tools=[get_weather, calculate, get_current_time],
    )
    
    for question in test_questions:
        print(f"\n👤 用户: {question}")
        result = await Runner.run(agent_restricted, question)
        print(f"🤖 助手: {result.final_output}")
        print("-" * 40)

async def test_guardrails_behavior():
    """测试3: 使用 Guardrails 控制行为"""
    print("\n" + "="*60)
    print("🧪 测试3: Guardrails 护栏 - 智能过滤问题")
    print("="*60)
    
    # 测试3a: 问题类型护栏
    print("\n📋 测试3a: 问题类型护栏")
    print("-" * 40)
    
    agent_with_type_guardrail = Agent(
        name="类型护栏助手",
        instructions="你是一个多功能智能助手，可以查询天气、进行计算和告诉用户当前时间。",
        tools=[get_weather, calculate, get_current_time],
        input_guardrails=[
            InputGuardrail(guardrail_function=question_type_guardrail),
        ],
    )
    
    type_test_questions = [
        "北京今天天气怎么样？",  # 相关 - 应该通过
        "苹果和梨哪个更甜？",    # 无关 - 应该被拦截
        "帮我算一下 5+3",       # 相关 - 应该通过
        "什么是人工智能？",      # 无关 - 应该被拦截
    ]
    
    for question in type_test_questions:
        print(f"\n👤 用户: {question}")
        try:
            result = await Runner.run(agent_with_type_guardrail, question)
            print(f"🤖 助手: {result.final_output}")
        except Exception as e:
            print(f"🚫 护栏拦截: {type(e).__name__}: {e}")
        print("-" * 40)
    
    # 测试3b: 内容安全护栏
    print("\n📋 测试3b: 内容安全护栏")
    print("-" * 40)
    
    agent_with_safety_guardrail = Agent(
        name="安全护栏助手",
        instructions="你是一个多功能智能助手。",
        tools=[get_weather, calculate, get_current_time],
        input_guardrails=[
            InputGuardrail(guardrail_function=content_safety_guardrail),
        ],
    )
    
    safety_test_questions = [
        "北京今天天气怎么样？",  # 正常 - 应该通过
        "这是一个政治问题",      # 敏感 - 应该被拦截
        "帮我算一下 5+3",       # 正常 - 应该通过
    ]
    
    for question in safety_test_questions:
        print(f"\n👤 用户: {question}")
        try:
            result = await Runner.run(agent_with_safety_guardrail, question)
            print(f"🤖 助手: {result.final_output}")
        except Exception as e:
            print(f"🚫 护栏拦截: {type(e).__name__}: {e}")
        print("-" * 40)
    
    # 测试3c: 长度护栏
    print("\n📋 测试3c: 长度护栏")
    print("-" * 40)
    
    agent_with_length_guardrail = Agent(
        name="长度护栏助手",
        instructions="你是一个多功能智能助手。",
        tools=[get_weather, calculate, get_current_time],
        input_guardrails=[
            InputGuardrail(guardrail_function=length_guardrail),
        ],
    )
    
    length_test_questions = [
        "北京今天天气怎么样？",  # 正常长度 - 应该通过
        "好",                    # 太短 - 应该被拦截
        "北京今天天气怎么样？" * 100,  # 太长 - 应该被拦截
    ]
    
    for question in length_test_questions:
        print(f"\n👤 用户: {question[:50]}{'...' if len(question) > 50 else ''}")
        try:
            result = await Runner.run(agent_with_length_guardrail, question)
            print(f"🤖 助手: {result.final_output}")
        except Exception as e:
            print(f"🚫 护栏拦截: {type(e).__name__}: {e}")
        print("-" * 40)
    
    # 测试3d: 多重护栏组合
    print("\n📋 测试3d: 多重护栏组合")
    print("-" * 40)
    
    agent_with_multiple_guardrails = Agent(
        name="多重护栏助手",
        instructions="你是一个多功能智能助手，可以查询天气、进行计算和告诉用户当前时间。",
        tools=[get_weather, calculate, get_current_time],
        input_guardrails=[
            InputGuardrail(guardrail_function=question_type_guardrail),
            InputGuardrail(guardrail_function=content_safety_guardrail),
            InputGuardrail(guardrail_function=length_guardrail),
        ],
    )
    
    multiple_test_questions = [
        "北京今天天气怎么样？",  # 正常 - 应该通过
        "苹果和梨哪个更甜？",    # 无关 - 被类型护栏拦截
        "这是一个政治问题",      # 敏感 - 被安全护栏拦截
        "好",                    # 太短 - 被长度护栏拦截
        "帮我算一下 5+3",       # 正常 - 应该通过
    ]
    
    for question in multiple_test_questions:
        print(f"\n👤 用户: {question}")
        try:
            result = await Runner.run(agent_with_multiple_guardrails, question)
            print(f"🤖 助手: {result.final_output}")
        except Exception as e:
            print(f"🚫 护栏拦截: {type(e).__name__}: {e}")
        print("-" * 40)

async def main():
    """主函数"""
    print("\n" + "🚀"*30)
    print("🧪 Agent 行为测试：无关问题的处理")
    print("🚀"*30)
    
    setup_custom_client()
    print("✅ 自定义客户端配置完成\n")
    
    # 运行所有测试
    await test_agent_behavior()
    await test_guardrails_behavior()
    
    print("\n" + "="*60)
    print("📊 测试总结:")
    print("="*60)
    print("1. 默认情况下，Agent 会基于训练数据回答所有问题")
    print("2. 即使没有相关工具，Agent 也不会拒绝回答")
    print("3. 通过修改 instructions 可以控制 Agent 的行为")
    print("4. 工具主要用于执行具体操作，不是限制回答范围")
    print("5. Guardrails 提供了强大的输入过滤和控制能力")
    print("6. 可以组合多个护栏来实现复杂的过滤逻辑")
    print("\n🛡️  Guardrails 优势:")
    print("- 问题类型过滤：只允许相关类型的问题")
    print("- 内容安全过滤：拦截敏感或不当内容")
    print("- 长度控制：防止过短或过长的问题")
    print("- 多重保护：可以组合多个护栏")
    print("- 异常处理：被拦截的问题会抛出异常")

if __name__ == "__main__":
    if CUSTOM_API_KEY == "your-api-key-here":
        print("⚠️  请先设置 API Key:")
        print("export AIHUBMIX_API_KEY='your-actual-api-key'")
    else:
        asyncio.run(main())
