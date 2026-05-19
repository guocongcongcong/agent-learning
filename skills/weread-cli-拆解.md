---
title: weread-cli 拆解
status: 已分析
source_project: weread-cli
complexity: medium
tags:
  - agent-cli-skill-pattern
  - cli-design
  - skill-system
  - tool-design
  - weread
  - typeScript
created: 2026-05-19
updated: 2026-05-19
---

## 项目概况

weread-cli 是一个 TypeScript CLI 工具，封装微信读书的官方 Agent API，并配套一个 Anthropic Agent Skill 定义。版本 0.1.2，MIT 协议，作者 shiquda。**仅一个运行时依赖（commander）**，其余全部使用 Node.js 内置模块。

核心理念："一个 Skill + 一个 CLI"设计模式 —— CLI 是确定性、可审计的 Shell 接口，Skill 是 Agent 面向的指令层。两者分开发布但协同工作。

## 架构全景

```
CLI 调用 (weread <command>)
  → cli.ts (commander 解析参数)
    → options.ts (标准化标志值)
    → client.ts (WereadClient.call() 构建 HTTP 请求)
      → fetch() → 微信读书 Agent Gateway
    → format.ts (格式化响应用到 stdout)
```

## 分层拆解

### 1. 入口层：cli.ts（729 行）

- **程序定义**：commander 解析命令树，`--json` / `--compact` 为全局标志
- **withClient 装饰器**：高阶函数，每次命令调用创建新的 WereadClient 实例并注入为第一个参数
- **runCall 中央调度**：所有 API 命令统一通过 runCall() 执行，自动处理 JSON/人类可读双模式输出
- **api call 逃生舱**：原始 API 调用保留完整 CLI 基础设施（认证、skill_version 注入、JSON 解析、错误标准化）
- **分页策略**：三种模型——游标分页（notebooks）、synckey 分页（reviews）、命令级分页（--limit/--all/--max-idx）
- **错误处理**：WereadError → 结构化 JSON 失败输出；普通 Error → invalid_input 包装

### 2. 客户端层：client.ts（310 行）

- **配置优先级链**：构造函数参数 > 环境变量 > ~/.weread-cli/config.json > 默认值
- **每次配置记录来源**：constructor/env/config/default/null，doctor 命令可审计
- **请求构建**：自动注入 skill_version，剥离 undefined 参数
- **响应处理四层验证**：JSON 解析 → HTTP 状态码 → upgrade_info（硬停止，exitCode 3）→ errcode
- **重试逻辑**：最多 3 次，线性退避 150ms × attempt，499/网络错误/AbortError 可重试

### 3. 配置层：config.ts（52 行）

- **存储位置**：`~/.weread-cli/config.json`（可覆盖）
- **安全设计**：文件权限 0o600（仅 owner 可读写），密钥掩码显示（前 4 后 4）
- **操作**：readConfig / writeConfig / updateConfig（原子读-合并-写）

### 4. 格式化层：format.ts（602 行）

- **双输出模式**：--json（结构化 JSON）vs 默认（人类可读）
- **jsonView 标准化**：按 API 端点提取 items[] + totalCount + empty_reason（确定性空结果语义）
- **截断提示**：人类可读输出超限时提示"使用 --json, --limit, 或 --all"
- **notes export 并行编排**：单命令内 Promise.all 调用 4 个 API（book info + chapters + bookmarks + reviews），交叉引用 chapterUids 构建 Markdown 输出

### 5. 选项解析层：options.ts（107 行）

- **类型强制**：coerceScalar 自动检测 true/false/null/数字/JSON
- **范围别名**：book → 10, all → 0
- **compactParams**：剥离 undefined 值后发送
- **parseParams**：--param key=value 解析为 GatewayParams

### 6. Skill 层：skills/weread/SKILL.md

- **触发条件**：用户提及微信读书相关概念
- **启动流程**：先执行 weread doctor 检查连通性
- **命令选择**：从命令映射表选择，默认加 --json
- **错误路由**：missing_auth → 加载 first-use.md；upgrade_required → 停止
- **渐进式信息披露**：SKILL.md 是简洁命令映射，领域知识在 references/ 中按需加载

## "一个 Skill + 一个 CLI"设计模式总结

### 六个原则

1. **CLI 是确定性层**：处理认证、请求构造、skill_version 注入、JSON 解析、升级检查、错误标准化。Agent 绝不应该手动构造 curl 请求。
2. **Skill 是指令层**：教 Agent 使用哪些命令、如何解读结果、如何处理错误、何时加载参考文档。
3. **渐进式信息披露**：SKILL.md 是简洁的命令映射表，详细领域知识在 references/ 中按需加载，保持 Agent 启动上下文精简。
4. **可组合的产品名词**：命令按产品概念组织（book, shelf, notes, reviews, readdata, discover），而非暴露原始 API 路径。
5. **--json 无处不在**：每个命令都支持 --json 输出，JSON 格式稳定可解析，诊断信息走 stderr。
6. **原始 API 逃生舱**：api call 覆盖未包装的边界情况，但仍享受 CLI 全套基础设施。

### 关键设计决策

| 决策 | 理由 |
|------|------|
| 单一运行时依赖（commander） | 最小化攻击面、安装体积和维护负担 |
| 双输出模式（--json vs 人类可读） | 一条代码路径同时服务 Agent 自动化和终端用户 |
| skill_version 服务端注入 | 消除调用方出错可能，保持协议稳定 |
| 构造函数注入 + 级联优先级 | 可测试、可通过环境变量覆盖、可审计（每个值追踪来源） |
| upgrade_info 作为硬停止（exit code 3） | 防止 Agent 在协议过时时继续操作 |
| 线性退避重试（3 次） | 容忍 transient gateway timeout，无需复杂重试框架 |
| 测试用本地 mock HTTP server | CI 零外部依赖，测试封闭且快速 |
| weread doctor 不发网络请求 | 离线或配置错误时仍可诊断认证问题 |
| 分页游标作为一级 CLI 标志 | Agent 直接传递原生游标值（sort, synckey, searchIdx） |
| JSON 输出中的稳定 empty_reason 字符串 | 给 Agent 确定性语义信号，而非让 Agent 从空数组猜测 |
| buildNotesExport 并行请求 4 个 API | 优化最昂贵操作（完整笔记导出） |
| 发布包同时包含 dist/ 和 skills/ | CLI 和配套 Skill 作为一个包分发 |

### 适用场景

这个模式特别适合：
- **有官方 API 的服务**：将 API 包装为 CLI，再为 CLI 编写 Skill
- **需要 Agent 可审计操作**：CLI 命令比原始 HTTP 调用更可追踪、可重放
- **需要跨 Agent 平台复用**：CLI 是通用接口，Skill 是平台特定适配层
- **需要人类也可用**：同一套命令既服务 Agent 也服务终端用户

## 与当前项目的关联

weread-cli 的 "Skill + CLI" 模式可以直接应用于 agent-learning-vault 的 skill 开发：
- **Skill** = Agent 指令文件（已有 skills/ 目录结构）
- **CLI** = 可以是一个学习笔记管理 CLI，封装知识库的 CRUD 操作
- **分工**：CLI 做确定性操作（文件读写、Git 提交），Skill 做意图理解和命令路由
