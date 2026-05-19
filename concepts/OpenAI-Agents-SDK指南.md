---
title: OpenAI Agents SDK 指南
created: 2026-05-19
updated: 2026-05-19
type: concept
order: 2
tags: [agent, openai, sdk, guide, official]
sources: [https://platform.openai.com/docs/guides/agents]
confidence: high
contested: false
contradictions: []
---

# OpenAI Agents SDK 指南

---

## 概述

OpenAI Agents SDK 使开发者能够「以轻量、易用的方式构建 agentic AI 应用，仅使用极少的抽象层」。它是 OpenAI 早期实验项目 Swarm 的生产级演进版本。SDK 提供三个核心原语（primitive）：

- **Agents（Agent）** — 配置了指令（instructions）和工具（tools）的 LLM
- **Agents as tools / Handoffs（Agent 即工具 / 移交）** — Agent 之间委托工作的机制
- **Guardrails（护栏）** — 输入输出的验证层

SDK 还包含内置的追踪（tracing）功能，用于可视化、调试和评估 Agent 工作流。

---

## 设计原则

1. 最少但强大的原语集合 — 学习曲线低，但功能足够支撑真实场景使用。
2. 开箱即用的强默认配置，同时保留完全自定义的能力。

---

## 核心功能总览

| 功能 | 说明 |
|---|---|
| **Agent loop（Agent 循环）** | 内置运行时，处理工具调用、将结果送回 LLM 并持续到任务完成 |
| **Python-first（Python 优先）** | 使用原生语言特性进行编排，不引入额外抽象 |
| **Handoffs（移交）** | 允许 Agent 将任务委托给其他 Agent 处理专门工作 |
| **Sandbox agents（沙箱 Agent）** | 在隔离工作空间中运行专家 Agent，支持清单定义的文件和可恢复会话 |
| **Guardrails（护栏）** | 并行输入验证和安全检查，快速失败机制 |
| **Function tools（函数工具）** | 将任意 Python 函数转换为工具，自动生成 schema 和 Pydantic 验证 |
| **MCP tool calling（MCP 工具调用）** | 内置 Model Context Protocol（模型上下文协议）服务端工具集成 |
| **Sessions（会话）** | 持久记忆层，在 Agent 循环轮次间维护上下文 |
| **Human-in-the-loop（人机协同）** | 内置的人工介入机制 |
| **Tracing（追踪）** | 内置可观测性，支持 OpenAI 的评估、微调和蒸馏工具 |
| **Realtime Agents（实时 Agent）** | 语音 Agent 支持，基于 `gpt-realtime-2`，具备打断检测、上下文管理和护栏 |

---

## Agents SDK vs. Responses API 的选择

SDK 默认对 OpenAI 模型使用 Responses API，但在此之上封装了更高级的运行时。

**直接使用 Responses API 的场景：**
- 希望自己掌握循环、工具分发和状态处理
- 工作流是短生命周期的，主要返回模型响应

**使用 Agents SDK 的场景：**
- 需要运行时管理轮次、工具执行、护栏、移交或会话
- Agent 需要产出 artifacts（产物）或跨多个协调步骤运行
- 需要通过沙箱 Agent 获得真实工作空间或可恢复执行

两种方式并非互斥 — 许多应用会结合使用。

---

## 安装

```bash
pip install openai-agents
```

需要设置 `OPENAI_API_KEY` 环境变量：

```bash
export OPENAI_API_KEY=sk-...
```

语音支持：
```bash
pip install 'openai-agents[voice]'
```

Redis 会话存储：
```bash
pip install 'openai-agents[redis]'
```

JavaScript/TypeScript：
```bash
npm install @openai/agents zod
```

---

## Hello World 示例

```python
from agents import Agent, Runner

agent = Agent(name="Assistant", instructions="You are a helpful assistant")

result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
print(result.final_output)

# Code within the code,
# Functions calling themselves,
# Infinite loop's dance.
```

---

## 核心概念详解

### Agent（Agent）

Agent 是配备了指令、工具、护栏和移交配置的 LLM。创建一个 Agent 只需要名称和 instructions：

```python
from agents import Agent

agent = Agent(
    name="Math Tutor",
    instructions="You provide help with math problems. Explain your reasoning.",
    tools=[...],   # 可选：函数工具、托管工具、Agent-as-tool
    guardrails=[...],  # 可选：输入/输出护栏
    handoffs=[...],    # 可选：移交目标 Agent
)
```

### Tools（工具）

SDK 支持三类工具：

1. **Function tools（函数工具）**：将任意 Python 函数装饰为工具，自动从类型注解生成 schema。
   ```python
   from agents import function_tool

   @function_tool
   def get_weather(city: str) -> str:
       """Get the current weather for a city."""
       return f"The weather in {city} is sunny."
   ```

2. **Hosted tools（托管工具）**：OpenAI 平台原生支持的工具，如 WebSearch、FileSearch、Code Interpreter。

3. **Agents as tools（Agent 即工具）**：将一个 Agent 封装为另一个 Agent 可调用的工具，实现模块化组合。

### Handoffs（移交）

Handoff 是 Agent 将对话控制权移交给另一个 Agent 的机制，适用于多 Agent 协作场景：

```python
from agents import Agent, handoff

billing_agent = Agent(name="Billing Agent", instructions="Handle billing inquiries.")
support_agent = Agent(name="Support Agent", instructions="Handle general support.")

triage_agent = Agent(
    name="Triage Agent",
    instructions="Route users to the right department.",
    handoffs=[handoff(billing_agent), handoff(support_agent)],
)
```

### Guardrails（护栏）

护栏对 Agent 的输入和输出进行验证：

- **Input guardrails（输入护栏）**：在 Agent 处理前检查用户输入
- **Output guardrails（输出护栏）**：在返回给用户前检查 Agent 输出

护栏可以抛出异常阻止处理流程，或仅触发警告。它们支持并行执行以保持低延迟。

```python
from agents import input_guardrail, GuardrailFunctionOutput

@input_guardrail
def check_topic(ctx, agent, input_text):
    blocked_topics = ["violence", "hate speech"]
    for topic in blocked_topics:
        if topic in input_text.lower():
            return GuardrailFunctionOutput(
                output_info={"blocked_topic": topic},
                tripwire_triggered=True
            )
    return GuardrailFunctionOutput(tripwire_triggered=False)
```

### Sessions（会话）/ Memory（记忆）

Sessions 提供了跨 Agent 运行轮次的持久记忆层，解决了 LLM 无状态的问题。支持的存储后端：

- **SQLite**（默认）：适用于本地开发
- **Redis**：适用于生产环境的高性能会话存储
- **SQLAlchemy**：适用于关系数据库集成
- **MongoDB / Dapr**：扩展后端支持
- **EncryptedSession**：加密会话存储，适合敏感数据

```python
from agents import Agent, Runner, SQLiteSession

session = SQLiteSession("user_123")
result = Runner.run_sync(agent, "My name is Alice.", session=session)
# 后续调用可以访问之前的对话上下文
result2 = Runner.run_sync(agent, "What's my name?", session=session)
```

### Agent 编排（Orchestration）

SDK 支持两种主流的多 Agent 编排模式：

1. **Handoffs（移交模式）**：Agent 将控制权直接交给另一 Agent。适合路由式场景（如客服分流）。
2. **Manager orchestration（管理器编排）**：一个中心 Agent 作为管理器，通过 Agent-as-tool 调用其他 Agent。适合需要中心化协调的复杂工作流。

选择取决于：任务是否需要中心化决策，还是更适合逐步委派。

### Tracing（追踪）

内置追踪系统自动记录所有 Agent 运行细节，包括：

- LLM 调用（model、token 消耗、延迟）
- 工具调用（参数、返回值）
- 护栏检查
- 移交事件

追踪数据可通过 OpenAI 平台 dashboard 可视化查看，也可导出用于评估和蒸馏。

### Sandbox Agents（沙箱 Agent）

沙箱 Agent 在隔离的容器化环境中运行，拥有独立文件系统。适用场景：

- 代码生成与执行
- 文档审查与编辑
- 需要工作空间持久化的长时间任务

```python
from agents import SandboxAgent

agent = SandboxAgent(
    name="Code Reviewer",
    instructions="Review the code in the workspace and suggest improvements.",
    manifest="path/to/manifest.yaml",  # 定义文件和权限
)
```

沙箱后端支持 Modal、E2B、Cloudflare、Daytona、Vercel 等。

### Realtime Agents（实时 / 语音 Agent）

基于 `gpt-realtime-2` 模型，支持低延迟语音交互：

- 打断检测（interruption detection）
- 上下文管理
- 语音活动和说话者识别
- 护栏集成

```python
from agents import RealtimeAgent, RealtimeRunner

agent = RealtimeAgent(name="Voice Assistant", instructions="You are a helpful voice assistant.")
runner = RealtimeRunner()
await runner.run(agent)
```

### MCP（Model Context Protocol）集成

SDK 内置 MCP 客户端，可直接连接任何 MCP 服务端，将其工具暴露给 Agent：

```python
from agents.mcp import MCPServerStdio

async with MCPServerStdio(name="Filesystem Server", params={"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path"]}) as server:
    agent = Agent(name="Assistant", mcp_servers=[server])
    result = await Runner.run(agent, "List files in the directory")
```

---

## 最佳实践

1. **保持 Agent 职责单一**：每个 Agent 专注于一个领域，通过 handoff 组合
2. **充分利用 tracing**：开发阶段开启追踪，快速定位问题
3. **合理使用护栏**：输入护栏做安全检查，输出护栏做格式验证
4. **选择合适的记忆策略**：简单场景用 SQLite session，生产环境用 Redis
5. **先构建再优化**：从最简单的单 Agent 开始，需要时再引入多 Agent 编排

---

## 快速入门路径

1. **构建第一个文本 Agent** → 参考 Hello World 示例
2. **选择跨轮次的记忆策略** → 使用 Sessions 模块
3. **任务依赖真实文件或隔离环境** → 使用 Sandbox agents
4. **决定 handoff vs 管理器编排** → 参考 Agent orchestration 文档
5. **构建语音 Agent** → 使用 Realtime agents quickstart

---

## 相关资源

- GitHub 仓库（Python）：[openai/openai-agents-python](https://github.com/openai/openai-agents-python)
- GitHub 仓库（JS/TS）：[openai/openai-agents-js](https://github.com/openai/openai-agents-js)
- 官方文档：[openai.github.io/openai-agents-python](https://openai.github.io/openai-agents-python/)
- npm 包：[`@openai/agents`](https://www.npmjs.com/package/@openai/agents)
