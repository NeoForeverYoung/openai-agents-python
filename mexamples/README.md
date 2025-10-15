# OpenAI Agents SDK 学习示例

这是一个循序渐进的学习路径，帮助你掌握 OpenAI Agents SDK 的核心功能。

## 📚 学习路径

### ✅ 第一课：Hello World
**文件**: `hello_world.py`

**学习目标**:
- 配置自定义 API 域名
- 创建第一个 Agent
- 理解 Agent 和 Runner 的基本用法
- 掌握异步编程基础

**运行**:
```bash
export AIHUBMIX_API_KEY='your-api-key'
python mexamples/hello_world.py
```

---

### 🔧 第二课：工具集成
**文件**: `02_tools_basic.py`

**学习目标**:
- 使用 @function_tool 装饰器定义工具
- 给 Agent 添加功能
- 理解 Agent 如何自动选择工具
- 实现工具的组合使用

**核心概念**:
- 工具函数定义
- 参数类型提示（Annotated）
- 单个工具 vs 多个工具
- 工具的智能组合

**运行**:
```bash
python mexamples/02_tools_basic.py
```

---

### 📊 第三课：结构化输出
**文件**: `03_structured_output.py`

**学习目标**:
- 使用 Pydantic 定义数据结构
- 让 Agent 返回 JSON 格式的数据
- 实现类型安全的输出
- 结合工具和结构化输出

**核心概念**:
- BaseModel 定义
- output_type 参数
- final_output_as() 方法
- 复杂嵌套结构

**运行**:
```bash
python mexamples/03_structured_output.py
```

---

### 💾 第四课：会话管理（即将更新）
**文件**: `04_session_memory.py`

**学习目标**:
- 实现对话记忆
- 多轮对话管理
- 使用 SQLite Session
- 上下文保持

---

### 🔀 第五课：Agent 交接（即将更新）
**文件**: `05_handoffs.py`

**学习目标**:
- 多 Agent 协作
- 智能路由
- 任务转交
- 专业化 Agent

---

## 🚀 快速开始

### 1. 设置环境
```bash
# 安装依赖
pip install openai-agents

# 设置 API Key
export AIHUBMIX_API_KEY='your-api-key-here'
```

### 2. 运行示例
```bash
# 从第一课开始
python mexamples/hello_world.py

# 运行第二课
python mexamples/02_tools_basic.py

# 运行第三课
python mexamples/03_structured_output.py
```

### 3. 修改和实验
- 每个示例都有详细的注释
- 尝试修改代码，观察结果
- 创建自己的工具和结构

## 📖 学习建议

### 学习方法
1. **按顺序学习**: 从第一课开始，循序渐进
2. **动手实践**: 运行每个示例，观察输出
3. **修改代码**: 尝试修改参数和逻辑
4. **创造项目**: 结合学到的知识创建自己的项目

### 时间安排
- 每课学习时间: 30-60 分钟
- 实践时间: 30-60 分钟
- 总计: 1-2 小时/课

### 学习检查清单

#### 第一课 ✅
- [ ] 成功运行 hello_world.py
- [ ] 理解自定义域名配置
- [ ] 掌握基本的 Agent 创建

#### 第二课 🔧
- [ ] 创建自己的工具函数
- [ ] 理解工具的参数类型提示
- [ ] 实现多个工具的组合

####第三课 📊
- [ ] 定义自己的数据结构
- [ ] 理解结构化输出的优势
- [ ] 结合工具和结构化输出

## 🆘 常见问题

### Q: API Key 如何设置？
```bash
# 方法1: 环境变量
export AIHUBMIX_API_KEY='your-key'

# 方法2: 代码中直接设置
CUSTOM_API_KEY = "your-key"
```

### Q: 如何修改域名？
```python
CUSTOM_BASE_URL = "https://your-domain.com/v1"
```

### Q: 遇到错误怎么办？
1. 检查 API Key 是否正确
2. 检查域名是否可访问
3. 查看错误信息的详细描述
4. 参考代码注释

## 📚 相关资源

- [OpenAI Agents SDK 文档](https://openai.github.io/openai-agents-python/)
- [学习路径指南](../mdocs/learning_path.md)
- [官方示例](../examples/)

## 💡 下一步

完成这些示例后，你可以：
1. 学习更高级的功能（会话管理、Agent 交接）
2. 查看官方的复杂示例（research_bot, financial_agent）
3. 开始构建自己的 Agent 应用

---

**祝学习愉快！** 🎉

如有问题，欢迎参考文档或查看官方示例。

