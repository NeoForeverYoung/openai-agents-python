"""
智能会话管理演示
展示如何存储关键数据而不是完整对话历史
"""

import asyncio
import os
import json
from typing import Dict, List, Any
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

# ============ 智能会话管理类 ============

class SmartSession:
    """智能会话管理 - 只存储关键数据"""
    
    def __init__(self, session_id: str, db_file: str = "smart_sessions.db"):
        self.session_id = session_id
        self.db_file = db_file
        self.user_profile = {}  # 用户画像
        self.conversation_summary = []  # 对话摘要
        self.key_facts = {}  # 关键事实
        self.preferences = {}  # 用户偏好
        self.context = {}  # 上下文信息
        
    def add_user_info(self, key: str, value: Any):
        """添加用户信息"""
        self.user_profile[key] = value
        print(f"📝 存储用户信息: {key} = {value}")
    
    def add_preference(self, category: str, preference: str):
        """添加用户偏好"""
        if category not in self.preferences:
            self.preferences[category] = []
        self.preferences[category].append(preference)
        print(f"💡 存储偏好: {category} = {preference}")
    
    def add_fact(self, fact: str, value: Any):
        """添加关键事实"""
        self.key_facts[fact] = value
        print(f"🔍 存储事实: {fact} = {value}")
    
    def get_context_summary(self) -> str:
        """获取上下文摘要"""
        summary = []
        
        if self.user_profile:
            summary.append(f"用户信息: {self.user_profile}")
        
        if self.preferences:
            summary.append(f"用户偏好: {self.preferences}")
        
        if self.key_facts:
            summary.append(f"关键事实: {self.key_facts}")
        
        return " | ".join(summary)
    
    def save_to_file(self):
        """保存到文件"""
        data = {
            "session_id": self.session_id,
            "user_profile": self.user_profile,
            "preferences": self.preferences,
            "key_facts": self.key_facts,
            "context": self.context
        }
        
        with open(f"{self.session_id}_smart_session.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 保存智能会话数据到: {self.session_id}_smart_session.json")
    
    def load_from_file(self):
        """从文件加载"""
        try:
            with open(f"{self.session_id}_smart_session.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.user_profile = data.get("user_profile", {})
                self.preferences = data.get("preferences", {})
                self.key_facts = data.get("key_facts", {})
                self.context = data.get("context", {})
            print(f"📂 加载智能会话数据: {self.session_id}_smart_session.json")
        except FileNotFoundError:
            print(f"📂 创建新的智能会话: {self.session_id}")

# ============ 工具定义 ============

@function_tool
def extract_user_info(info: str) -> str:
    """提取用户信息"""
    print(f"🔍 提取用户信息: {info}")
    return f"已提取用户信息: {info}"

@function_tool
def save_user_preference(category: str, preference: str) -> str:
    """保存用户偏好"""
    print(f"💾 保存用户偏好: {category} = {preference}")
    return f"已保存偏好: {category} = {preference}"

@function_tool
def get_weather(city: str) -> str:
    """获取天气信息"""
    print(f"🌤️  查询天气: {city}")
    weather_data = {
        "北京": "晴天，温度 15-25°C",
        "上海": "多云，温度 18-26°C",
        "深圳": "小雨，温度 22-28°C",
    }
    return weather_data.get(city, f"{city}的天气是晴天，温度 20°C")

# ============ 智能会话管理示例 ============

async def demo_smart_session():
    """演示智能会话管理"""
    print("\n" + "="*60)
    print("🧠 智能会话管理演示")
    print("="*60)
    
    # 创建智能会话
    smart_session = SmartSession("smart_user_001")
    smart_session.load_from_file()
    
    # 创建智能 Agent
    agent = Agent(
        name="智能助手",
        instructions="""你是一个智能助手，能够：
        1. 提取和存储用户的关键信息
        2. 识别用户的偏好和习惯
        3. 基于存储的信息提供个性化服务
        
        请主动提取用户信息并存储到智能会话中。
        """,
        model=CHEAP_MODEL,
        tools=[extract_user_info, save_user_preference, get_weather],
    )
    
    # 模拟对话流程
    conversations = [
        "我的名字是张三，今年25岁，住在北京",
        "我喜欢科幻电影和编程",
        "我每天工作8小时，喜欢在晚上学习",
        "帮我查一下北京的天气",
        "基于我的信息，推荐一部科幻电影",
    ]
    
    for i, question in enumerate(conversations, 1):
        print(f"\n👤 用户: {question}")
        
        # 智能提取信息
        if "名字" in question and "岁" in question:
            smart_session.add_user_info("name", "张三")
            smart_session.add_user_info("age", 25)
            smart_session.add_user_info("location", "北京")
        
        if "喜欢" in question:
            if "科幻电影" in question:
                smart_session.add_preference("电影", "科幻")
            if "编程" in question:
                smart_session.add_preference("爱好", "编程")
        
        if "工作" in question:
            smart_session.add_fact("工作时间", "8小时")
            smart_session.add_fact("学习时间", "晚上")
        
        # 运行 Agent
        result = await Runner.run(agent, question)
        print(f"🤖 助手: {result.final_output}")
        
        # 显示当前存储的关键数据
        print(f"📊 当前存储的关键数据:")
        print(f"   用户信息: {smart_session.user_profile}")
        print(f"   用户偏好: {smart_session.preferences}")
        print(f"   关键事实: {smart_session.key_facts}")
        print("-" * 40)
    
    # 保存智能会话
    smart_session.save_to_file()
    
    # 显示最终数据
    print(f"\n📋 最终存储的关键数据:")
    print(f"   用户信息: {smart_session.user_profile}")
    print(f"   用户偏好: {smart_session.preferences}")
    print(f"   关键事实: {smart_session.key_facts}")
    print(f"   上下文摘要: {smart_session.get_context_summary()}")

async def demo_data_comparison():
    """演示数据存储对比"""
    print("\n" + "="*60)
    print("📊 数据存储对比")
    print("="*60)
    
    # 传统方式存储的数据量
    traditional_data = [
        {"role": "user", "content": "我的名字是张三，今年25岁，住在北京"},
        {"role": "assistant", "content": "你好张三！很高兴认识你..."},
        {"role": "user", "content": "我喜欢科幻电影和编程"},
        {"role": "assistant", "content": "很好！科幻电影和编程都是很有趣的..."},
        {"role": "user", "content": "我每天工作8小时，喜欢在晚上学习"},
        {"role": "assistant", "content": "听起来你很有规划！..."},
    ]
    
    # 智能方式存储的数据量
    smart_data = {
        "user_profile": {
            "name": "张三",
            "age": 25,
            "location": "北京"
        },
        "preferences": {
            "电影": ["科幻"],
            "爱好": ["编程"]
        },
        "key_facts": {
            "工作时间": "8小时",
            "学习时间": "晚上"
        }
    }
    
    print(f"📊 传统方式存储的数据量:")
    print(f"   记录数: {len(traditional_data)}")
    print(f"   数据大小: {len(json.dumps(traditional_data, ensure_ascii=False))} 字符")
    print(f"   内容: 完整的对话历史")
    
    print(f"\n📊 智能方式存储的数据量:")
    print(f"   记录数: {len(smart_data)}")
    print(f"   数据大小: {len(json.dumps(smart_data, ensure_ascii=False))} 字符")
    print(f"   内容: 提取的关键信息")
    
    # 计算节省的空间
    traditional_size = len(json.dumps(traditional_data, ensure_ascii=False))
    smart_size = len(json.dumps(smart_data, ensure_ascii=False))
    savings = ((traditional_size - smart_size) / traditional_size) * 100
    
    print(f"\n💡 空间节省: {savings:.1f}%")
    print(f"   传统方式: {traditional_size} 字符")
    print(f"   智能方式: {smart_size} 字符")
    print(f"   节省空间: {traditional_size - smart_size} 字符")

async def demo_context_usage():
    """演示上下文使用"""
    print("\n" + "="*60)
    print("🔄 上下文使用演示")
    print("="*60)
    
    # 创建智能会话
    smart_session = SmartSession("context_demo")
    
    # 模拟存储一些信息
    smart_session.add_user_info("name", "李四")
    smart_session.add_user_info("age", 30)
    smart_session.add_preference("电影", "动作片")
    smart_session.add_preference("音乐", "摇滚")
    smart_session.add_fact("职业", "软件工程师")
    
    # 显示上下文摘要
    context_summary = smart_session.get_context_summary()
    print(f"📋 上下文摘要: {context_summary}")
    
    # 模拟基于上下文的对话
    agent = Agent(
        name="上下文助手",
        instructions=f"基于以下上下文信息回答用户问题：{context_summary}",
        model=CHEAP_MODEL,
    )
    
    questions = [
        "我的名字是什么？",
        "我喜欢什么类型的电影？",
        "我的职业是什么？",
        "基于我的偏好，推荐一部电影",
    ]
    
    for question in questions:
        print(f"\n👤 用户: {question}")
        result = await Runner.run(agent, question)
        print(f"🤖 助手: {result.final_output}")

async def main():
    """主函数"""
    print("\n" + "🚀"*30)
    print("🧠 智能会话管理演示")
    print("🚀"*30)
    
    setup_custom_client()
    print("✅ 自定义客户端配置完成\n")
    
    # 运行演示
    await demo_smart_session()
    await demo_data_comparison()
    await demo_context_usage()
    
    print("\n" + "="*60)
    print("✅ 演示完成！")
    print("="*60)
    print("\n📖 智能会话管理的优势:")
    print("1. 只存储关键信息，节省空间")
    print("2. 结构化数据，便于查询和更新")
    print("3. 支持用户画像和偏好分析")
    print("4. 上下文摘要，提高效率")
    print("5. 可扩展的数据结构")
    print("\n💡 总结:")
    print("- 传统方式：存储完整对话历史")
    print("- 智能方式：提取和存储关键信息")
    print("- 空间节省：通常可节省 60-80% 的存储空间")
    print("- 效率提升：更快的查询和加载速度")

if __name__ == "__main__":
    if CUSTOM_API_KEY == "your-api-key-here":
        print("⚠️  请先设置 API Key:")
        print("export AIHUBMIX_API_KEY='your-actual-api-key'")
    else:
        asyncio.run(main())
