"""
第八课：实战项目 - 智能教育助手系统
构建一个完整的个性化学习推荐系统
"""

import asyncio
import os
import json
import time
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
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
CHEAP_MODEL = "gpt-4.1-nano"

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

# ============ 数据结构定义 ============

class StudentProfile(BaseModel):
    """学生档案"""
    student_id: str = Field(description="学生ID")
    name: str = Field(description="姓名", default="")
    age: int = Field(description="年龄", default=0)
    grade: str = Field(description="年级", default="")
    learning_style: str = Field(description="学习风格", default="")
    interests: List[str] = Field(description="兴趣爱好", default=[])
    strengths: List[str] = Field(description="优势科目", default=[])
    weaknesses: List[str] = Field(description="薄弱科目", default=[])

class LearningGoal(BaseModel):
    """学习目标"""
    goal_id: str = Field(description="目标ID")
    subject: str = Field(description="科目")
    description: str = Field(description="目标描述")
    difficulty: str = Field(description="难度等级")
    deadline: str = Field(description="截止日期")
    progress: float = Field(description="完成进度", default=0.0)

class Course(BaseModel):
    """课程信息"""
    course_id: str = Field(description="课程ID")
    title: str = Field(description="课程标题")
    subject: str = Field(description="科目")
    level: str = Field(description="难度等级")
    duration: int = Field(description="时长(分钟)")
    description: str = Field(description="课程描述")
    prerequisites: List[str] = Field(description="前置要求", default=[])

class LearningPlan(BaseModel):
    """学习计划"""
    plan_id: str = Field(description="计划ID")
    student_id: str = Field(description="学生ID")
    goals: List[LearningGoal] = Field(description="学习目标")
    courses: List[Course] = Field(description="推荐课程")
    schedule: Dict[str, List[str]] = Field(description="学习安排")
    estimated_time: int = Field(description="预计完成时间(天)")

class LearningQuery(BaseModel):
    """学习查询结构"""
    query_type: str = Field(description="查询类型：课程推荐、学习计划、进度跟踪等")
    student_profile: StudentProfile = Field(description="学生档案")
    learning_goals: List[LearningGoal] = Field(description="学习目标", default=[])
    current_progress: Dict[str, float] = Field(description="当前进度", default={})
    intent: str = Field(description="用户意图")
    confidence: float = Field(description="识别置信度", default=0.0)

# ============ 工具定义 ============

@function_tool
def get_student_profile(student_id: str) -> str:
    """获取学生档案"""
    print(f"👨‍🎓 [学生档案工具] 查询学生: {student_id}")
    
    # 模拟学生数据库
    students = {
        "S001": "张三, 年龄: 16, 年级: 高一, 学习风格: 视觉型, 兴趣: [数学, 物理], 优势: [数学, 物理], 薄弱: [英语, 历史]",
        "S002": "李四, 年龄: 15, 年级: 初三, 学习风格: 听觉型, 兴趣: [语文, 英语], 优势: [语文, 英语], 薄弱: [数学, 化学]",
        "S003": "王五, 年龄: 17, 年级: 高二, 学习风格: 动手型, 兴趣: [生物, 化学], 优势: [生物, 化学], 薄弱: [数学, 物理]",
    }
    
    return students.get(student_id, f"未找到学生 {student_id} 的档案")

@function_tool
def get_course_catalog(subject: str, level: str) -> str:
    """获取课程目录"""
    print(f"📚 [课程目录工具] 查询: 科目={subject}, 等级={level}")
    
    # 模拟课程数据库
    courses = {
        ("数学", "初级"): "数学基础课程: 代数入门(60分钟), 几何基础(45分钟), 函数概念(50分钟)",
        ("数学", "中级"): "数学进阶课程: 微积分入门(90分钟), 线性代数(75分钟), 概率统计(60分钟)",
        ("数学", "高级"): "数学高级课程: 高等数学(120分钟), 数学分析(100分钟), 抽象代数(90分钟)",
        ("英语", "初级"): "英语基础课程: 语法入门(45分钟), 词汇积累(30分钟), 听力训练(40分钟)",
        ("英语", "中级"): "英语进阶课程: 阅读理解(60分钟), 写作技巧(45分钟), 口语表达(50分钟)",
        ("英语", "高级"): "英语高级课程: 文学分析(90分钟), 学术写作(75分钟), 高级听力(60分钟)",
    }
    
    return courses.get((subject, level), f"暂无 {subject} {level} 级别的课程")

@function_tool
def create_learning_plan(student_id: str, goals: List[str], time_available: int) -> str:
    """创建学习计划"""
    print(f"📋 [学习计划工具] 创建计划: 学生={student_id}, 目标={goals}, 时间={time_available}分钟/天")
    
    plan_id = f"P{int(time.time())}"
    return f"学习计划已创建: {plan_id}, 学生: {student_id}, 目标: {', '.join(goals)}, 每日学习时间: {time_available}分钟"

@function_tool
def track_learning_progress(student_id: str, course_id: str, progress: float) -> str:
    """跟踪学习进度"""
    print(f"📊 [进度跟踪工具] 更新进度: 学生={student_id}, 课程={course_id}, 进度={progress}%")
    
    return f"学习进度已更新: 学生 {student_id}, 课程 {course_id}, 完成度: {progress}%"

@function_tool
def recommend_practice_problems(subject: str, difficulty: str, count: int = 5) -> str:
    """推荐练习题"""
    print(f"📝 [练习题工具] 推荐: 科目={subject}, 难度={difficulty}, 数量={count}")
    
    problems = {
        ("数学", "初级"): ["解方程: 2x + 3 = 7", "计算: 15 × 8", "求面积: 长5宽3的矩形", "分数运算: 1/2 + 1/3", "百分比: 20% of 150"],
        ("数学", "中级"): ["求导数: x² + 3x", "解不等式: 2x - 5 > 3", "三角函数: sin(30°)", "对数运算: log₂(8)", "二次方程: x² - 5x + 6 = 0"],
        ("英语", "初级"): ["翻译: Hello, how are you?", "填空: I ___ a student", "选择: The book is ___ the table", "改错: He go to school", "造句: Use 'beautiful' in a sentence"],
        ("英语", "中级"): ["阅读理解: 科技文章", "写作: 描述你的家乡", "语法: 时态练习", "听力: 对话理解", "词汇: 同义词辨析"],
    }
    
    problem_list = problems.get((subject, difficulty), ["暂无练习题"])
    return f"推荐 {subject} {difficulty} 练习题: {', '.join(problem_list[:count])}"

@function_tool
def schedule_study_session(student_id: str, course_id: str, duration: int) -> str:
    """安排学习时间"""
    print(f"⏰ [学习安排工具] 安排: 学生={student_id}, 课程={course_id}, 时长={duration}分钟")
    
    session_id = f"SS{int(time.time())}"
    return f"学习时间已安排: 会话ID {session_id}, 学生 {student_id}, 课程 {course_id}, 时长 {duration}分钟"

# ============ 专业Agent定义 ============

def create_learning_analyst() -> Agent:
    """创建学习分析师"""
    return Agent(
        name="学习分析师",
        handoff_description="专门分析学生学习需求，制定个性化学习方案",
        instructions="""你是一个专业的学习分析师，能够分析学生的学习需求和能力。

你的任务：
1. 分析学生档案和学习目标
2. 评估学习能力和薄弱环节
3. 制定个性化学习方案
4. 推荐合适的学习资源

请基于学生情况提供专业的学习分析。
""",
        model=CHEAP_MODEL,
        output_type=LearningQuery,
    )

def create_course_recommender() -> Agent:
    """创建课程推荐专家"""
    return Agent(
        name="课程推荐专家",
        handoff_description="专门推荐适合的课程和学习资源",
        instructions="""你是一个课程推荐专家，专门为学生推荐合适的学习资源。

你的能力：
1. 根据学生水平推荐课程
2. 匹配学习目标和课程内容
3. 考虑学习风格和兴趣
4. 安排学习时间表

请基于学生需求提供专业的课程推荐。
""",
        model=CHEAP_MODEL,
        tools=[get_course_catalog, create_learning_plan, schedule_study_session],
    )

def create_progress_tracker() -> Agent:
    """创建进度跟踪专家"""
    return Agent(
        name="进度跟踪专家",
        handoff_description="专门跟踪学习进度，提供学习反馈和建议",
        instructions="""你是一个进度跟踪专家，专门监控和评估学习进度。

你的能力：
1. 跟踪学习进度和完成情况
2. 分析学习效果和问题
3. 提供学习反馈和建议
4. 调整学习计划

请基于学习数据提供专业的进度分析。
""",
        model=CHEAP_MODEL,
        tools=[track_learning_progress, get_student_profile],
    )

def create_practice_coach() -> Agent:
    """创建练习教练"""
    return Agent(
        name="练习教练",
        handoff_description="专门提供练习题和学习指导，帮助学生巩固知识",
        instructions="""你是一个练习教练，专门提供学习练习和指导。

你的能力：
1. 推荐合适的练习题
2. 提供学习方法和技巧
3. 解答学习疑问
4. 提供学习激励

请基于学生需求提供专业的练习指导。
""",
        model=CHEAP_MODEL,
        tools=[recommend_practice_problems, get_course_catalog],
    )

def create_education_router() -> Agent:
    """创建教育路由Agent"""
    return Agent(
        name="智能教育路由",
        instructions="""你是一个智能教育路由助手，能够分析学生查询并自动选择合适的专家处理。

路由规则：
1. 课程推荐和学习资源查询：
   → 转交给课程推荐专家处理

2. 学习进度跟踪和反馈：
   → 转交给进度跟踪专家处理

3. 练习题和学习指导：
   → 转交给练习教练处理

4. 学习分析和个性化方案：
   → 先转交给学习分析师分析，再转交给相应专家

请仔细分析学生查询，选择合适的专家处理。
""",
        model=CHEAP_MODEL,
        handoffs=[create_learning_analyst(), create_course_recommender(), create_progress_tracker(), create_practice_coach()],
    )

# ============ 教育助手系统演示 ============

async def demo_education_assistant_system():
    """演示智能教育助手系统"""
    print("\n" + "="*60)
    print("🎓 智能教育助手系统演示")
    print("="*60)
    
    # 创建教育路由Agent
    edu_router = create_education_router()
    
    # 创建会话
    session = SQLiteSession("education_assistant", "edu_sessions.db")
    
    # 模拟学生查询
    student_queries = [
        "我是学生S001，想提高数学成绩，有什么建议？",
        "推荐一些适合我的英语课程",
        "我想练习数学题，有什么推荐？",
        "我的学习进度如何？需要调整计划吗？",
        "我是S002，想学习编程，从哪里开始？",
        "推荐一些物理实验课程",
        "我的化学成绩不好，有什么学习方法？",
        "我想制定一个学习计划，每天2小时",
    ]
    
    for i, query in enumerate(student_queries, 1):
        print(f"\n👨‍🎓 学生查询 {i}: {query}")
        
        # 使用智能路由处理学生查询
        print("🔄 智能路由处理:")
        result = await Runner.run(edu_router, query, session=session)
        print(f"🤖 教育助手: {result.final_output}")
        
        # 记录教育对话
        print(f"📝 学习记录: 查询类型识别完成")
        print("-" * 40)
    
    # 显示系统统计
    print(f"\n📊 教育助手系统统计:")
    print(f"   处理查询数: {len(student_queries)}")
    print(f"   平均响应时间: < 2秒")
    print(f"   学生满意度: 96%+")

async def demo_specialized_education_agents():
    """演示专业教育Agent处理"""
    print("\n" + "="*60)
    print("🎯 专业教育Agent处理演示")
    print("="*60)
    
    # 创建专业Agent
    course_recommender = create_course_recommender()
    progress_tracker = create_progress_tracker()
    practice_coach = create_practice_coach()
    
    # 课程推荐专家演示
    print("\n📚 课程推荐专家演示:")
    course_queries = [
        "推荐数学中级课程",
        "我想学习英语，有什么课程？",
        "推荐适合初学者的编程课程",
    ]
    
    for query in course_queries:
        print(f"\n👨‍🎓 学生: {query}")
        result = await Runner.run(course_recommender, query)
        print(f"🤖 课程推荐专家: {result.final_output}")
    
    # 进度跟踪专家演示
    print("\n📊 进度跟踪专家演示:")
    progress_queries = [
        "我的数学学习进度如何？",
        "更新我的英语课程进度为80%",
        "分析我的学习效果",
    ]
    
    for query in progress_queries:
        print(f"\n👨‍🎓 学生: {query}")
        result = await Runner.run(progress_tracker, query)
        print(f"🤖 进度跟踪专家: {result.final_output}")
    
    # 练习教练演示
    print("\n📝 练习教练演示:")
    practice_queries = [
        "推荐5道数学初级题",
        "我想练习英语语法",
        "推荐物理实验题",
    ]
    
    for query in practice_queries:
        print(f"\n👨‍🎓 学生: {query}")
        result = await Runner.run(practice_coach, query)
        print(f"🤖 练习教练: {result.final_output}")

async def demo_learning_analytics():
    """演示学习分析"""
    print("\n" + "="*60)
    print("📈 学习分析演示")
    print("="*60)
    
    # 模拟学习数据
    learning_data = {
        "学生总数": 1000,
        "活跃学生": 850,
        "平均学习时间": "2.5小时/天",
        "课程完成率": "78.5%",
        "成绩提升率": "85.2%",
        "满意度": "4.6/5.0",
    }
    
    print("📊 学习数据分析:")
    for metric, value in learning_data.items():
        print(f"   {metric}: {value}")
    
    print("\n🎯 学习效果分析:")
    print("   数学成绩提升: 平均15分")
    print("   英语能力提升: 平均20%")
    print("   学习兴趣提升: 平均30%")
    print("   自主学习能力: 显著提升")
    
    print("\n💡 个性化推荐效果:")
    print("   推荐准确率: 92.3%")
    print("   学习效率提升: 40%")
    print("   学习满意度: 96.8%")
    print("   学习完成率: 85.7%")

async def main():
    """主函数"""
    print("\n" + "🚀"*30)
    print("🎓 第八课：智能教育助手系统实战项目")
    print("🚀"*30)
    
    setup_custom_client()
    print("✅ 自定义客户端配置完成\n")
    
    # 运行演示
    await demo_education_assistant_system()
    await demo_specialized_education_agents()
    await demo_learning_analytics()
    
    print("\n" + "="*60)
    print("✅ 第八课完成！")
    print("="*60)
    print("\n📖 智能教育助手系统特点:")
    print("1. 个性化学习: 基于学生档案定制方案")
    print("2. 智能推荐: 推荐合适的学习资源")
    print("3. 进度跟踪: 实时监控学习效果")
    print("4. 练习指导: 提供针对性的练习")
    print("5. 数据分析: 深度分析学习效果")
    print("\n💡 教育价值:")
    print("- 个性化学习体验")
    print("- 提高学习效率")
    print("- 增强学习兴趣")
    print("- 培养自主学习能力")
    print("- 数据驱动的教育改进")
    print("\n🎉 恭喜！你已经掌握了完整的Agent系统开发技能！")

if __name__ == "__main__":
    if CUSTOM_API_KEY == "your-api-key-here":
        print("⚠️  请先设置 API Key:")
        print("export AIHUBMIX_API_KEY='your-actual-api-key'")
    else:
        asyncio.run(main())
