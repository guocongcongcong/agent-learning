---
title: 理解 Agent
created: 2026-05-19
updated: 2026-05-19
type: concept
order: 4
tags: [agent, concept, beginner]
confidence: high
contested: false
contradictions: []
---

# 理解 Agent

## 一句话

**Agent = 能自主使用工具、做决策、完成多步任务的 AI。**

它不是"你问一句它答一句"的聊天机器人。它有目标、有计划、会用工具、会从错误中恢复。

---

## Agent Loop：Agent 的"呼吸"

每个 Agent 都在跑同一个循环：

```
Thought（思考）
  → Action（行动，调用工具）
    → Observation（观察结果）
      → Thought（重新思考）
        → Action（再次行动）
          → ...直到任务完成
```

### 举个例子

你让 Agent "帮我查一下北京今天的天气，如果下雨就提醒我带伞"：

```
Thought:  用户想知道北京天气，我需要调用天气工具
Action:   tool_call(weather, city="北京")
Observation: {"weather": "小雨", "temp": 18}

Thought:  下雨了，用户需要带伞。任务完成。
Action:   回复"今天北京小雨，18°C，记得带伞☔"
```

这就是一个完整的 Agent Loop——总共两次 Thought→Action→Observation。

### 更复杂的例子：写一篇关于 AI Agent 的博客并发布

```
用户: "帮我写一篇关于 AI Agent 的博客，然后发布到我的博客网站"

Loop 1:
  Thought:  需要先了解用户对博客的具体要求——主题、长度、风格
  Action:   回复询问用户偏好（字数、风格、目标读者）
  Observation: 用户回复"1500 字左右，面向初学者，轻松风格"

Loop 2:
  Thought:  主题是 AI Agent，最好先搜一下最新的行业动态作为素材
  Action:   tool_call(web_search, query="AI Agent trends 2026")
  Observation: 返回 5 篇相关文章摘要

Loop 3:
  Thought:  素材够了，开始写初稿
  Action:   tool_call(write_file, filename="ai-agent-blog.md", content="...")
  Observation: 文件已写入

Loop 4:
  Thought:  写完了，得检查一下字数是否符合要求
  Action:   tool_call(count_words, filename="ai-agent-blog.md")
  Observation: 1420 字

Loop 5:
  Thought:  字数接近 1500，可以发布。调用博客发布工具
  Action:   tool_call(publish_blog, file="ai-agent-blog.md")
  Observation: {"status": "published", "url": "https://myblog.com/ai-agent-intro"}

Loop 6:
  Thought:  发布成功，告诉用户结果
  Action:   回复"博客已发布！链接：https://myblog.com/ai-agent-intro"
```

这个任务走了 6 次 Loop。每一次循环 Agent 都在"思考→行动→观察结果→重新思考"。复杂任务本质上就是更多次高质量的 Loop 迭代。

---

## Agent 的核心组件

| 组件 | 是什么 | 类比 | 为什么重要 |
|------|--------|------|------------|
| **LLM（大脑）** | 做推理和决策的模型 | 大脑皮层 | 决定了 Agent 的智商上限——模型越强，决策质量越高 |
| **Tools（手）** | Agent 能调用的外部功能 | 手和脚 | 没有工具的 Agent 只是一个聊天机器人，什么也做不了 |
| **Memory（记忆）** | 跨对话记住的东西 | 便利贴 | 让 Agent 能记住你的偏好和背景，不用每次都重新解释 |
| **System Prompt（规则）** | 定义 Agent 身份和行为 | 员工手册 | 设定了 Agent 的性格、边界和能力范围，是最底层的约束 |
| **Context Window（视野）** | 一次能"看到"的全部内容 | 视野范围 | 决定了 Agent 能记住多少上下文——装不下的信息等于不存在 |

---

## Agent vs Chatbot vs Workflow

很多人把这三个混为一谈，但它们有本质区别：

| 维度 | Chatbot | Workflow | Agent |
|------|---------|----------|-------|
| **决策方式** | 一问一答，无自主决策 | 按预设流程图执行 | 自主判断下一步做什么 |
| **工具使用** | 通常无工具 | 固定节点调用固定工具 | 动态选择工具和参数 |
| **错误处理** | 不会。答错就错了 | 预设的 fallback 路径 | 能发现问题并自己重试 |
| **路径** | 单轮对话 | 固定的 if-else 分支 | 动态、非线性的 Loop |
| **举例** | ChatGPT 基础模式 | CI/CD Pipeline、Zapier | Hermes、Claude Code、Devin |

一句话区分：**Chatbot 是"你说什么它回什么"，Workflow 是"不管谁来了都走一样的路"，Agent 是"看情况自己决定怎么走"。**

---

## Agent 的类型

### ReAct Agent

最常见的 Agent 类型。ReAct = Reasoning + Acting，即"边想边做"。每走一步都先思考（Thought），再行动（Action），观察结果（Observation）后进入下一轮。大部分对话式 Agent（包括 Hermes 和 Claude Code）都是 ReAct 模式。**优点是简单直观，缺点是有时容易在局部打转、缺少全局规划。**

### Plan-and-Execute Agent

"先计划，再执行"。Agent 接到任务后先生成一个完整的执行计划（Plan），然后按计划逐条执行，执行过程中可以根据结果调整计划。**优点是全局观强、步骤清晰，缺点是计划生成本身有成本，对简单任务来说有点"杀鸡用牛刀"。**

### Multi-Agent

多个 Agent 同时工作，每个 Agent 各司其职。比如一个 Agent 负责写代码，另一个负责 review 代码，第三个负责写测试。**优点是分工明确、可以并行工作、互相校验，缺点是协调成本高、容易"吵架"或重复劳动。** Hermes 通过 Skill 调度多个模型就是一种 Multi-Agent 的前身。

---

## 你已经在用的 Agent

你不用"学 Agent"——你天天在用它们：

| 你用的 | 是什么类型 | 说明 |
|--------|-----------|------|
| **Hermes** | ReAct Agent（调度型） | 你的个人 AI 管家。它不直接回答复杂问题，而是把任务分发给子 Agent 或 Skill 去执行，自己负责"调度和整合"。 |
| **Claude Code** | ReAct Agent（执行型） | 直接在你的终端里工作——读文件、写代码、执行命令、跑测试。它的 Loop 是 Thought → Tool Call → Observation。你每次看它"思考...调用工具...看到结果..."就是一个 Loop。 |
| **ChatGPT** | ReAct Agent + 插件 | 基础模式是 Chatbot，但开启联网搜索或 Code Interpreter 后就是 Agent 模式——它能自主决定"要不要搜""怎么写代码"。 |

---

## 动手练习

> 目标：观察一次真实的 Agent Loop。5 分钟。

**步骤：**

1. 打开和 Hermes 的对话窗口
2. 对 Hermes 输入：

   ```
   帮我查一下今天的日期，然后告诉我离周五还有几天
   ```

3. 回来看 Hermes 走的每一步：
   - 它调用了什么工具？（可能是获取日期的工具）
   - 它走了几次 Loop？（Hemes 输出中的每一次"思考→工具调用→结果"就是一次 Loop）
   - 它有没有遇到意外情况？（比如工具调用失败后自动重试）

**思考题：**

- 这个任务 Agent 走了几次 Loop？你预测的和你观察到的有什么不同？
- 如果 Agent 没有日期工具，你觉得它会怎么做？
- Hermes 的 Loop 和本文写的 Thought → Action → Observation 能对上吗？哪里不一样？

---

## 你必须理解的三件事

### 1. Agent 不是万能的

Agent 只能做它能调用的工具允许它做的事。一个没有"发送邮件"工具的 Agent 永远发不了邮件。

### 2. Context 是 Agent 的命

Agent 看不到的东西等于不存在。你的 System Prompt、对话历史、工具输出，全在一个叫 Context Window 的"视野框"里。框满了，旧信息就被挤出去。

### 3. Agent 会犯错 —— 设计时要考虑恢复

好的 Agent 设计不是"从来不犯错"，而是"犯错后能自己发现并纠正"。

---

## 必读文章

1. **Anthropic: Building Effective Agents**
   https://www.anthropic.com/engineering/building-effective-agents
   → Agent 开发的"圣经"，Anthropic 官方出品

2. **OpenAI: A Practical Guide to Building Agents**
   https://platform.openai.com/docs/guides/agents
   → 生产级实践指南

3. **Lilian Weng: LLM Powered Autonomous Agents**
   https://lilianweng.github.io/posts/2023-06-23-agent/
   → 经典博客，Agent 架构全景

---

## 关键术语速查

| 术语 | 含义 |
|------|------|
| Agent Loop | Thought → Action → Observation 循环 |
| Tool Call | Agent 调用外部工具 |
| Context Window | Agent 一次能处理的最大文本量 |
| Prompt | 发给模型的指令 |
| System Prompt | 每次对话自动注入的底层规则 |

---

## 相关

- [[学习路线总览]] — 回到路线图
- [[写Skill]] — 下一步：动手写第一个 Skill
- [[Agent 思考与实践]] — 深入 Agent 设计的实战经验
- [[Skill 开发指南]] — 如何为 Hermes 写 Skill
