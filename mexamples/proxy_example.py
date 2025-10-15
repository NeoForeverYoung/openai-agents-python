#!/usr/bin/env python3
"""
代理服务配置示例
支持使用代理服务运行 OpenAI Agents SDK
"""

import asyncio
import os
from openai import AsyncOpenAI
from agents import (
    Agent,
    Runner,
    function_tool,
    set_default_openai_client,
    set_default_openai_api,
    set_tracing_disabled,
)

# 代理服务配置
PROXY_BASE_URL = os.getenv("PROXY_BASE_URL", "https://your-proxy-domain.com/v1")
PROXY_API_KEY = os.getenv("PROXY_API_KEY", "your-proxy-api-key")
MODEL_NAME = os.getenv("PROXY_MODEL_NAME", "gpt-3.5-turbo")

def setup_proxy_client():
    """设置代理客户端"""
    print(f"🔧 配置代理服务: {PROXY_BASE_URL}")
    
    # 创建自定义客户端
    client = AsyncOpenAI(
        base_url=PROXY_BASE_URL,
        api_key=PROXY_API_KEY,
        timeout=30.0,
        max_retries=3,
    )
    
    # 设置为默认客户端
    set_default_openai_client(client=client, use_for_tracing=False)
    set_default_openai_api("chat_completions")  # 大多数代理使用 Chat Completions API
    set_tracing_disabled(disabled=True)  # 禁用追踪
    
    print("✅ 代理客户端配置完成")
    return client

@function_tool
def get_weather(city: str) -> str:
    """获取天气信息"""
    print(f"🌤️ 查询 {city} 的天气")
    return f"{city}的天气是晴天，温度25°C，湿度60%"

@function_tool
def get_time() -> str:
    """获取当前时间"""
    import datetime
    now = datetime.datetime.now()
    return f"当前时间是: {now.strftime('%Y-%m-%d %H:%M:%S')}"

async def main():
    """主函数"""
    print("🚀 启动代理服务示例")
    
    # 设置代理客户端
    client = setup_proxy_client()
    
    # 创建 Agent
    agent = Agent(
        name="代理助手",
        instructions="你是一个通过代理服务运行的智能助手，可以帮助用户查询天气和时间。",
        model=MODEL_NAME,
        tools=[get_weather, get_time],
    )
    
    print(f"🤖 创建 Agent: {agent.name}")
    print(f"📝 使用模型: {MODEL_NAME}")
    
    # 测试对话
    test_questions = [
        "你好，请介绍一下你自己",
        "北京今天天气怎么样？",
        "现在几点了？",
        "上海和北京的天气有什么不同？"
    ]
    
    for question in test_questions:
        print(f"\n👤 用户: {question}")
        try:
            result = await Runner.run(agent, question)
            print(f"🤖 助手: {result.final_output}")
        except Exception as e:
            print(f"❌ 错误: {e}")
    
    print("\n✅ 示例运行完成")

if __name__ == "__main__":
    # 检查环境变量
    if PROXY_BASE_URL == "https://your-proxy-domain.com/v1":
        print("⚠️  请设置环境变量:")
        print("export PROXY_BASE_URL='https://your-proxy-domain.com/v1'")
        print("export PROXY_API_KEY='your-proxy-api-key'")
        print("export PROXY_MODEL_NAME='gpt-3.5-turbo'")
        print("\n或者直接修改代码中的配置")
    else:
        asyncio.run(main())
