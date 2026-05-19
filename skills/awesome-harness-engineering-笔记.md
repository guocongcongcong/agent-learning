---
title: awesome-harness-engineering 笔记
status: 已分析
source_project: awesome-harness-engineering
complexity: medium
tags:
  - harness-engineering
  - awesome-list
  - agent-design
  - context-management
  - tool-design
  - skills-mcp
  - reference-implementations
created: 2026-05-19
updated: 2026-05-19
---

## 项目概况

awesome-harness-engineering 是由 ai-boost 维护的精选资源列表（CC0 协议），定义了"驾驭工程"这一新兴学科的知识版图。核心理念：**驾驭系统（context delivery, tool interfaces, planning artifacts, verification loops, memory systems, sandboxes）——而非模型本身——决定了 AI Agent 在真实任务中的成败。**

列表按问题域而非厂商组织，每个条目都附带 1-2 句观点鲜明的推荐理由，质量极高。

## 收录内容总览

| 板块 | 条目数 | 内容 |
|------|--------|------|
| Foundations | 26 | 定义学科的基础文章（OpenAI, Anthropic, Martin Fowler, LangChain, Google, Microsoft） |
| Agent Loop | 14 | ReAct 模式、循环架构、Codex 内部分析 |
| Planning & Task Decomposition | 12 | Plan.md、任务分解、多 Agent 模式 |
| Context Delivery & Compaction | 21 | 压缩算法、缓存策略、RAG 上下文模式 |
| Tool Design | 14 | 有效工具设计、JSON Schema、MCP 协议 |
| Skills & MCP | 24 | MCP 协议、A2A、Composio、Microsoft Skills |
| Permissions & Authorization | 12 | 权限提示、OWASP、OAuth 集成 |
| Memory & State | 19 | MemGPT、mem0、Zep、知识对象 |
| Task Runners & Orchestration | 25 | LangGraph、OpenAI Agents SDK、AutoGen、CrewAI |
| Verification & CI | 10 | promptfoo、AgentBench、eval-driven development |
| Observability & Tracing | 15 | OpenLLMetry、Phoenix、Langfuse、W&B Weave |
| Debugging & DX | 12 | AgentOps、claude-devtools、AgentStepper |
| Human-in-the-Loop | 11 | AWS HITL 模式、Dify、LangGraph interrupts |
| Reference Implementations | 53 | 教程、元驾驭系统、Demo 驾驭系统 |
| Security & Sandbox | 26 | E2B、Daytona、NeMo Guardrails |
| Evals & Verification | 15 | DeepEval、SWE-bench、Inspect AI |
| Templates | 4 | AGENTS.md、PLAN.md、IMPLEMENT.md、HARNESS_CHECKLIST.md |
| Production Operations | 15 | 扩展、成本优化、FinOps、Stripe Minions |

## 五个最有价值的条目

### 1. Harness Engineering（OpenAI 原版论文）
**URL**: https://openai.com/index/harness-engineering/
**为什么值得看**：命名了整个学科的原版论文，定义了"驾驭工程"的核心命题——围绕 AI Agent 的脚手架（而非模型本身）决定任务成败，是所有后续讨论的起点。

### 2. Building Effective Agents（Anthropic）
**URL**: https://www.anthropic.com/research/building-effective-agents
**为什么值得看**：最权威的 Agent 设计实践指南，明确了 workflow vs agent 的选择标准、augmented LLM 的组成原语（工具、记忆、规划），以及何时自建 vs 买框架——被列表中几乎每个后续条目引用。

### 3. everything-claude-code（140,000+ stars）
**URL**: https://github.com/affaan-m/everything-claude-code
**为什么值得看**：列表中最亮的星，是目前最全面的开源 Agent 驾驭性能优化系统，包含生产级 skills、instincts、记忆优化、安全扫描、hooks、规则和 MCP 配置，跨 Claude Code/Codex/Cursor/OpenCode/Gemini 五个平台。

### 4. OpenCode（131,000+ stars）
**URL**: https://github.com/anomalyco/opencode
**为什么值得看**：最完整的终端优先编码驾驭系统开源参考，支持 75+ LLM 厂商、原生 LSP 配置、多会话并行 Agent、MCP 扩展、Client/Server 架构——是目前已发布的最清晰的编码 Agent 驾驭系统架构模型。

### 5. Harness Engineering（Martin Fowler）
**URL**: https://martinfowler.com/articles/exploring-gen-ai/harness-engineering.html
**为什么值得看**：Martin Fowler 将驾驭工程定义为三个互锁系统（context engineering, architectural constraints, entropy management），提出"humans on the loop"框架——驾驭工程师设计并维护 Agent 环境而非逐个检查输出——是该学科最清晰的概念地图。

## 我的阅读计划

- [ ] Foundations 全读（26 篇基础文章）
- [ ] Agent Loop & Context Delivery 精读（理解核心循环和上下文管理）
- [ ] Tool Design & Skills/MCP 精读（理解工具和技能系统设计）
- [ ] 研读 2-3 个 Reference Implementation（OpenHands, Aider, OpenCode）
- [ ] 使用 Templates/ 下的模板（AGENTS.md, PLAN.md, HARNESS_CHECKLIST.md）

## 关键收获

1. **驾驭 > 模型**：整个列表的组织原则——问题域（Agent Loop, Context, Tools, Memory）优先于厂商（OpenAI, Anthropic, Google），反映了"驾驭工程是独立学科"的信念。
2. **每个条目都是"为什么"而非"是什么"**：列表的价值在于每条推荐都有 1-2 句观点鲜明的判断，等于一个专家在帮你做 curation。
3. **模板是落地抓手**：AGENTS.md、PLAN.md、IMPLEMENT.md、HARNESS_CHECKLIST.md 四个模板可以直接用于任何 Agent 项目的驾驭设计。
4. **前沿追踪**：包含 2026 年 5 月的最新内容（GitHub Copilot harness 分析），说明列表在持续更新。
