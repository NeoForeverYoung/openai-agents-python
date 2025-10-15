import asyncio
import os
from openai import AsyncOpenAI
from agents import (
    Agent, 
    Runner,
    set_default_openai_client,
    set_default_openai_api,
    set_tracing_disabled,
)

# 自定义域名配置
CUSTOM_BASE_URL = "https://aihubmix.com/v1"  # 你的自定义域名
CUSTOM_API_KEY = os.getenv("AIHUBMIX_API_KEY", "your-api-key-here")  # 从环境变量读取或直接设置

def setup_custom_client():
    """设置自定义客户端"""
    print(f"🔧 配置自定义域名: {CUSTOM_BASE_URL}")
    
    # 创建自定义客户端
    client = AsyncOpenAI(
        base_url=CUSTOM_BASE_URL,
        api_key=CUSTOM_API_KEY,
        timeout=30.0,
        max_retries=3,
    )
    
    # 设置为默认客户端
    set_default_openai_client(client=client, use_for_tracing=False)
    set_default_openai_api("chat_completions")  # 使用 Chat Completions API
    set_tracing_disabled(disabled=True)  # 禁用追踪
    
    print("✅ 自定义客户端配置完成")
    return client

async def main():
    # 设置自定义客户端
    client = setup_custom_client()
    
    agent = Agent(
        name="Assistant",
        instructions="You only respond in haikus.",
    )

    result = await Runner.run(agent, "Tell me about recursion in programming.")
    print(result.final_output)
    # Function calls itself,
    # Looping in smaller pieces,
    # Endless by design.


if __name__ == "__main__":
    # 检查 API Key 配置
    if CUSTOM_API_KEY == "your-api-key-here":
        print("⚠️  请设置 API Key:")
        print("方法1 - 环境变量:")
        print("export AIHUBMIX_API_KEY='your-actual-api-key'")
        print("\n方法2 - 直接修改代码:")
        print("将 CUSTOM_API_KEY 改为你的实际 API Key")
        print("\n方法3 - 创建 .env 文件:")
        print("echo 'AIHUBMIX_API_KEY=your-actual-api-key' > .env")
    else:
        asyncio.run(main())
