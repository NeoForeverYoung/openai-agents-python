---
search:
  exclude: true
---
# 指南

本指南将深入介绍如何使用 OpenAI Agents SDK 的实时功能来构建语音交互的 AI 智能体。

!!! warning "测试版功能"
实时智能体处于测试阶段。随着实现的改进，可能会发生不兼容变更。

## 概述

实时智能体支持对话式流程，可实时处理音频与文本输入，并以实时音频作出响应。它们与 OpenAI 的 Realtime API 保持持久连接，实现低延迟的自然语音对话，并能优雅地处理中断。

## 架构

### 核心组件

实时系统由以下关键组件构成：

-   **RealtimeAgent**: 一个智能体，通过 instructions、工具和任务转移进行配置。
-   **RealtimeRunner**: 管理配置。可调用 `runner.run()` 获取会话。
-   **RealtimeSession**: 一次交互会话。通常在每次用户开始对话时创建一个，并在对话结束前保持存活。
-   **RealtimeModel**: 底层模型接口（通常是 OpenAI 的 WebSocket 实现）

### 会话流程

典型的实时会话流程如下：

1. **创建 RealtimeAgent**，配置 instructions、工具和任务转移。
2. **设置 RealtimeRunner**，传入智能体与配置选项。
3. **启动会话**，使用 `await runner.run()` 获取 `RealtimeSession`。
4. **发送音频或文本消息** 到会话，使用 `send_audio()` 或 `send_message()`。
5. **监听事件**，通过遍历会话获取事件——包括音频输出、转录文本、工具调用、任务转移和错误。
6. **处理中断**，当用户打断智能体说话时，会自动停止当前音频生成。

会话维护对话历史，并管理与实时模型的持久连接。

## 智能体配置

RealtimeAgent 的工作方式与常规 Agent 类似，但有一些关键差异。完整 API 详情见 [`RealtimeAgent`][agents.realtime.agent.RealtimeAgent] API 参考。

相较常规智能体的主要差异：

-   模型选择在会话级别配置，而非智能体级别。
-   不支持 structured output（不支持 `outputType`）。
-   语音可按智能体进行配置，但在第一个智能体发声后不可再更改。
-   其他功能如工具、任务转移和 instructions 的工作方式相同。

## 会话配置

### 模型设置

会话配置允许控制底层实时模型的行为。你可以配置模型名称（如 `gpt-realtime`）、语音选择（alloy、echo、fable、onyx、nova、shimmer），以及支持的模态（文本和/或音频）。音频格式可分别为输入和输出设置，默认是 PCM16。

### 音频配置

音频设置控制会话如何处理语音输入与输出。你可以使用如 Whisper 等模型进行输入音频转录、设置语言偏好，并提供转录提示以提升特定领域术语的识别准确率。轮次检测（turn detection）设置用于控制智能体何时开始与停止响应，可配置语音活动检测阈值、静音时长，以及检测语音周围的填充时长。

## 工具与函数

### 添加工具

与常规智能体相同，实时智能体支持在对话中执行的工具调用（function tools）：

```python
from agents import function_tool

@function_tool
def get_weather(city: str) -> str:
    """Get current weather for a city."""
    # Your weather API logic here
    return f"The weather in {city} is sunny, 72°F"

@function_tool
def book_appointment(date: str, time: str, service: str) -> str:
    """Book an appointment."""
    # Your booking logic here
    return f"Appointment booked for {service} on {date} at {time}"

agent = RealtimeAgent(
    name="Assistant",
    instructions="You can help with weather and appointments.",
    tools=[get_weather, book_appointment],
)
```

## 任务转移

### 创建任务转移

任务转移允许在专门化的智能体之间转移对话。

```python
from agents.realtime import realtime_handoff

# Specialized agents
billing_agent = RealtimeAgent(
    name="Billing Support",
    instructions="You specialize in billing and payment issues.",
)

technical_agent = RealtimeAgent(
    name="Technical Support",
    instructions="You handle technical troubleshooting.",
)

# Main agent with handoffs
main_agent = RealtimeAgent(
    name="Customer Service",
    instructions="You are the main customer service agent. Hand off to specialists when needed.",
    handoffs=[
        realtime_handoff(billing_agent, tool_description="Transfer to billing support"),
        realtime_handoff(technical_agent, tool_description="Transfer to technical support"),
    ]
)
```

## 事件处理

会话会以流的形式发送事件，你可以通过遍历会话对象来监听。事件包括音频输出片段、转录结果、工具执行的开始与结束、智能体任务转移以及错误。关键事件包括：

-   **audio**: 来自智能体响应的原始音频数据
-   **audio_end**: 智能体完成发声
-   **audio_interrupted**: 用户打断了智能体
-   **tool_start/tool_end**: 工具执行生命周期
-   **handoff**: 发生了智能体任务转移
-   **error**: 处理过程中发生错误

完整事件详情参见 [`RealtimeSessionEvent`][agents.realtime.events.RealtimeSessionEvent]。

## 安全防护措施

实时智能体仅支持输出类安全防护措施。这些防护会去抖并定期运行（不是每个词都运行），以避免实时生成期间的性能问题。默认去抖长度为 100 个字符，可配置。

安全防护措施可以直接附加到 `RealtimeAgent`，或通过会话的 `run_config` 提供。两处提供的防护会共同生效。

```python
from agents.guardrail import GuardrailFunctionOutput, OutputGuardrail

def sensitive_data_check(context, agent, output):
    return GuardrailFunctionOutput(
        tripwire_triggered="password" in output,
        output_info=None,
    )

agent = RealtimeAgent(
    name="Assistant",
    instructions="...",
    output_guardrails=[OutputGuardrail(guardrail_function=sensitive_data_check)],
)
```

当安全防护措施被触发时，会生成 `guardrail_tripped` 事件，并可中断智能体当前的响应。去抖行为有助于在安全性与实时性能之间取得平衡。与文本智能体不同，实时智能体在防护被触发时不会抛出异常（Exception）。

## 音频处理

使用 [`session.send_audio(audio_bytes)`][agents.realtime.session.RealtimeSession.send_audio] 发送音频到会话，或使用 [`session.send_message()`][agents.realtime.session.RealtimeSession.send_message] 发送文本。

对于音频输出，监听 `audio` 事件并通过你偏好的音频库播放音频数据。务必监听 `audio_interrupted` 事件，以便在用户打断智能体时立即停止播放并清空任何排队的音频。

## 直接访问模型

你可以访问底层模型以添加自定义监听器或执行高级操作：

```python
# Add a custom listener to the model
session.model.add_listener(my_custom_listener)
```

这将为你提供对 [`RealtimeModel`][agents.realtime.model.RealtimeModel] 接口的直接访问，适用于需要对连接进行更低层级控制的高级用例。

## 示例

要查看完整可运行的示例，请访问 [examples/realtime 目录](https://github.com/openai/openai-agents-python/tree/main/examples/realtime)，其中包含带 UI 与不带 UI 的演示。