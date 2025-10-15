"""
第三课：结构化输出
学习如何让 Agent 返回结构化的数据（JSON 格式）
"""

import asyncio
import os
from typing import Annotated, List
from pydantic import BaseModel, Field
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

# 模型配置 - 使用最便宜的模型进行测试
#CHEAP_MODEL = "gpt-3.5-turbo"  # 最便宜的 OpenAI 模型
#CHEAP_MODEL = "gpt-4.1"  # 最便宜的 OpenAI 模型
#CHEAP_MODEL = "gpt-4.1-mini"  # 最便宜的 OpenAI 模型
CHEAP_MODEL = "gpt-4.1-nano"  # 最便宜的 OpenAI 模型

# ============ 定义输出结构 ============

class WeatherInfo(BaseModel):
    """天气信息结构"""
    city: str = Field(description="城市名称")
    temperature: str = Field(description="温度范围")
    condition: str = Field(description="天气状况")
    air_quality: str = Field(description="空气质量")

class CalculationResult(BaseModel):
    """计算结果结构"""
    expression: str = Field(description="计算表达式")
    result: float = Field(description="计算结果")
    explanation: str = Field(description="计算说明")

class TaskAnalysis(BaseModel):
    """任务分析结构"""
    task_type: str = Field(description="任务类型：查询、计算、信息获取等")
    difficulty: str = Field(description="难度等级：简单、中等、困难")
    steps: List[str] = Field(description="完成任务的步骤")
    estimated_time: str = Field(description="预计完成时间")

class MovieRecommendation(BaseModel):
    """电影推荐结构"""
    title: str = Field(description="电影名称")
    genre: str = Field(description="电影类型")
    rating: float = Field(description="评分 (0-10)")
    reason: str = Field(description="推荐理由")

class MovieList(BaseModel):
    """电影列表"""
    recommendations: List[MovieRecommendation] = Field(description="推荐的电影列表")

# ============ 工具定义 ============

@function_tool
def search_movies(genre: Annotated[str, "电影类型"]) -> str:
    """搜索指定类型的电影"""
    # 这是mock数据，实际搜索需要调用API，这里只是模拟一下
    print(f"🎬 搜索电影: genre='{genre}'")
    movies = {
        "科幻": ["星际穿越", "盗梦空间", "黑客帝国"],
        "动作": ["碟中谍", "速度与激情", "复仇者联盟"],
        "爱情": ["泰坦尼克号", "罗马假日", "怦然心动"],
    }
    return f"找到以下{genre}电影: {', '.join(movies.get(genre, ['暂无相关电影']))}"

# ============ 示例演示 ============

async def example_1_simple_structure():
    """示例1: 简单结构化输出"""
    print("\n" + "="*50)
    print("📚 示例1: 简单结构化输出 - 天气信息")
    print("="*50)
    
    agent = Agent(
        name="天气分析师",
        instructions="分析天气信息并以结构化格式返回",
        model=CHEAP_MODEL,  # 使用最便宜的模型
        output_type=WeatherInfo,  # 指定输出类型
    )
    
    query = "北京今天晴天，温度15-25度，空气质量良好"
    print(f"\n📝 输入: {query}")
    
    result = await Runner.run(agent, query)
    weather = result.final_output_as(WeatherInfo)
    
    print(f"\n📊 结构化输出:")
    print(f"  城市: {weather.city}")
    print(f"  温度: {weather.temperature}")
    print(f"  天气: {weather.condition}")
    print(f"  空气: {weather.air_quality}")

async def example_2_calculation_structure():
    """示例2: 计算结果结构化"""
    print("\n" + "="*50)
    print("📚 示例2: 计算结果结构化")
    print("="*50)
    
    agent = Agent(
        name="计算助手",
        instructions="执行数学计算并以结构化格式返回结果",
        model=CHEAP_MODEL,  # 使用最便宜的模型
        output_type=CalculationResult,
    )
    
    query = "计算 123 加 456 的结果"
    print(f"\n📝 输入: {query}")
    
    result = await Runner.run(agent, query)
    calc = result.final_output_as(CalculationResult)
    
    print(f"\n📊 结构化输出:")
    print(f"  表达式: {calc.expression}")
    print(f"  结果: {calc.result}")
    print(f"  说明: {calc.explanation}")

async def example_3_task_analysis():
    """示例3: 任务分析"""
    print("\n" + "="*50)
    print("📚 示例3: 任务分析 - 复杂结构")
    print("="*50)
    
    agent = Agent(
        name="任务规划师",
        instructions="分析用户的任务需求，制定详细的执行计划",
        model=CHEAP_MODEL,  # 使用最便宜的模型
        output_type=TaskAnalysis,
    )
    
    query = "我想学习 Python 编程"
    print(f"\n📝 输入: {query}")
    
    result = await Runner.run(agent, query)
    analysis = result.final_output_as(TaskAnalysis)
    
    print(f"\n📊 任务分析:")
    print(f"  类型: {analysis.task_type}")
    print(f"  难度: {analysis.difficulty}")
    print(f"  步骤:")
    for i, step in enumerate(analysis.steps, 1):
        print(f"    {i}. {step}")
    print(f"  预计时间: {analysis.estimated_time}")

async def example_4_with_tools():
    """示例4: 结合工具的结构化输出"""
    print("\n" + "="*50)
    print("📚 示例4: 工具 + 结构化输出")
    print("="*50)
    
    agent = Agent(
        name="电影推荐助手",
        instructions="根据用户喜好推荐电影，使用搜索工具查找电影，并以结构化格式返回推荐列表",
        model=CHEAP_MODEL,  # 使用最便宜的模型
        tools=[search_movies],
        output_type=MovieList,
    )
    
    query = "我很喜欢看科幻电影，推荐1部科幻电影给我"
    print(f"\n📝 输入: {query}")
    
    result = await Runner.run(agent, query)
    movie_list = result.final_output_as(MovieList)
    
    print(f"\n📊 电影推荐:")
    for i, movie in enumerate(movie_list.recommendations, 1):
        print(f"\n  {i}. {movie.title}")
        print(f"     类型: {movie.genre}")
        print(f"     评分: {movie.rating}/10")
        print(f"     推荐理由: {movie.reason}")

async def main():
    """主函数"""
    print("\n" + "🚀"*25)
    print("🎓 第三课：结构化输出")
    print("🚀"*25)
    
    # 设置自定义客户端
    setup_custom_client()
    print("✅ 自定义客户端配置完成\n")
    
    # 运行所有示例
    #await example_1_simple_structure()
    #await example_2_calculation_structure()
    #await example_3_task_analysis()
    await example_4_with_tools()
    
    """
    print("\n" + "="*50)
    print("✅ 第三课完成！")
    print("="*50)
    print("\n📖 学习要点:")
    print("1. 使用 Pydantic BaseModel 定义输出结构")
    print("2. 通过 output_type 参数指定 Agent 的输出类型")
    print("3. 使用 result.final_output_as() 获取类型安全的输出")
    print("4. 可以定义复杂的嵌套结构（如列表、对象）")
    print("5. 结构化输出可以和工具结合使用")
    print("\n💡 下一步: 学习会话管理和多轮对话")

    """

if __name__ == "__main__":
    if CUSTOM_API_KEY == "your-api-key-here":
        print("⚠️  请先设置 API Key:")
        print("export AIHUBMIX_API_KEY='your-actual-api-key'")
    else:
        asyncio.run(main())

