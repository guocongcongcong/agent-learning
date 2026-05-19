---
title: 工具与MCP
created: 2026-05-19
updated: 2026-05-19
type: concept
order: 3
tags: [tool, mcp, intermediate]
confidence: high
contested: false
contradictions: []
---

# 工具与 MCP

## 工具 = Agent 的手

Agent 本身只会"想"和"说"。它要"做"任何事——读文件、搜网页、执行命令——都必须通过工具。

### 好工具长什么样

```
工具名: search_files
描述:   在文件系统中搜索文件内容或文件名
参数:
  - pattern (必填): 搜索模式（正则或 glob）
  - path (可选):   搜索路径，默认当前目录
  - limit (可选):  最大返回数，默认 50
```

**好工具的四个标准：**

1. **名字清晰** — `search_files`，不是 `sf`
2. **描述准确** — Agent 读完就知道这工具干什么
3. **参数有默认值** — 减少 Agent 的决策负担
4. **错误友好** — 出错了返回人类可读的信息，不是 "Error code 500"

#### 标准 1：名字清晰

```typescript
// ✅ 好：名字自解释，Agent 一眼就知道用途
{
  name: "read_file",
  description: "读取指定路径的文件内容"
}

// ❌ 坏：缩写模糊，Agent 要猜
{
  name: "rf",
  description: "read file"
}
```

#### 标准 2：描述准确

```typescript
// ✅ 好：描述具体，说明了何时用、返回什么
{
  name: "search_code",
  description: "在代码库中搜索匹配正则表达式的代码行。" +
    "支持 glob 过滤文件类型。返回匹配行的文件路径、行号和内容。" +
    "适用于找到某个函数的所有调用点、某个类的所有引用。"
}

// ❌ 坏：描述太空泛，Agent 没法判断适不适合用
{
  name: "search_code",
  description: "搜索代码"
}
```

#### 标准 3：参数有默认值

```typescript
// ✅ 好：可选参数有合理默认值，Agent 不用纠结
{
  name: "list_issues",
  parameters: {
    repo: { type: "string", required: true },
    state: { type: "string", default: "open" },     // 默认查 open
    limit: { type: "number", default: 20 },          // 默认 20 条
    sort: { type: "string", default: "updated" }     // 默认按更新时间
  }
}

// ❌ 坏：所有参数必填，Agent 每次都要写满
{
  name: "list_issues",
  parameters: {
    repo: { type: "string", required: true },
    state: { type: "string", required: true },       // 必填……
    limit: { type: "number", required: true },       // 必填……
    sort: { type: "string", required: true }         // 必填……
  }
}
```

#### 标准 4：错误友好

```typescript
// ✅ 好：返回可读的错误，Agent 能据此自我纠正
try {
  const result = await fetchData(url);
  return { success: true, data: result };
} catch (err) {
  return {
    success: false,
    error: `无法访问 ${url}：连接超时。请检查网络或稍后重试。`,
    suggestion: "可以尝试用 search_web 替代，或者换一个 URL"
  };
}

// ❌ 坏：返回原始错误码，Agent 不知道发生了什么
try {
  const result = await fetchData(url);
  return { success: true, data: result };
} catch (err) {
  return { success: false, error: `Error: ${err.code}` };
  // Agent 收到 "Error: ECONNRESET"，完全不知道该怎么办
}
```

---

## 工具设计的原则

> "工具设计就是 Agent 的 UX" —— Anthropic

Agent 是你的用户。你设计的工具好不好用，决定了 Agent 能不能完成任务。

| 好 | 坏 |
|----|-----|
| 一个工具做一件事 | 一个工具包揽天下 |
| 参数类型明确（string/number/bool） | 参数都是 any |
| 返回结构化 JSON | 返回纯文本，Agent 要自己解析 |
| 有超时和重试 | 挂了就挂了 |

---

## MCP：工具的"USB 标准"

**MCP = Model Context Protocol**

没有 MCP 之前，每个 AI 平台都有自己的工具格式。Claude 一种格式，OpenAI 一种格式，各不兼容。

MCP 做了一件事：**统一工具接口**。

```
以前：
  Claude  ←→  Claude 专属工具格式
  OpenAI  ←→  OpenAI 专属工具格式

现在（有 MCP）：
  任何 LLM  ←→  MCP 标准接口  ←→  任何工具
```

就像 USB-C 统一了充电口——你不需要为每个设备配不同的充电线了。

### MCP 的传输方式

MCP 支持两种传输方式，适应不同场景：

```
stdio（标准输入输出）
   ┌──────────┐    stdin/stdout     ┌──────────┐
   │  Client  │ ◄──────────────────► │  Server  │
   │ (Hermes) │    (本地进程)        │  (子进程) │
   └──────────┘                      └──────────┘

HTTP（Server-Sent Events + POST）
   ┌──────────┐    HTTP/SSE          ┌──────────┐
   │  Client  │ ◄──────────────────► │  Server  │
   │ (Hermes) │    (远程连接)         │ (独立服务) │
   └──────────┘                      └──────────┘
```

| | stdio | HTTP |
|---|-------|------|
| **通信方式** | 标准输入输出流 | HTTP + SSE（Server-Sent Events） |
| **服务器位置** | 本地，作为 Client 的子进程启动 | 远程，独立运行的服务 |
| **延迟** | 极低（进程内通信） | 取决于网络 |
| **适用场景** | 本地工具：文件系统、Git、数据库 | 共享服务、远程 API、多用户工具 |
| **安全性** | 高（不暴露网络端口） | 需要认证和 TLS |
| **配置复杂度** | 低（一行 command + args） | 高（需要部署服务、配 URL） |

**怎么选？**

```
本地工具 → stdio
  例：filesystem、git、sqlite、postgres（本地实例）

远程/共享工具 → HTTP
  例：公司内部的知识库搜索、多团队共享的 GitHub Server、
      需要独立扩缩容的高负载工具
```

---

## MCP 的两个角色

```
MCP Server（服务端）
  = 提供工具的一方
  = "我有这些能力，你来用"
  例：GitHub Server 提供 list_issues、create_pr 等工具

MCP Client（客户端）
  = 使用工具的一方
  = "我要调用你的工具"
  例：Hermes Agent 连接 GitHub Server，调用其工具
```

---

## Hermes 怎么用 MCP

你在 `~/.hermes/config.yaml` 里加几行：

```yaml
mcp_servers:
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_xxx"
```

重启后，Hermes 自动就能用 `mcp_github_list_issues` 这样的工具了——Agent 不需要知道工具怎么实现的，它只知道"有个工具能做这个事"。

---

## 实战：拆解一个 MCP Server

打开 `projects/weread-cli/` ——这是一个典型的"一个 Skill + 一个 CLI/MCP"结构：
- CLI 封装了微信读书的操作（搜书、导出笔记）
- Skill 告诉 Agent 什么时候用它、怎么用它

---

## 工具的类型

按功能分类，Agent 常用的工具可以归为四类：

### 1. 文件工具

操作文件系统：读、写、搜索、编辑。

| 工具 | 来源 | 做什么 |
|------|------|--------|
| `Read` | Claude Code 内置 | 读取文件内容，支持文本和图片 |
| `Glob` | Claude Code 内置 | 按 glob 模式匹配文件路径 |
| `Edit` | Claude Code 内置 | 精确字符串替换编辑文件 |
| `Write` | Claude Code 内置 | 创建或覆盖写入文件 |

```yaml
# Hermes 中的文件工具——通常是平台内置的，不需要额外配置
# 但可以通过 MCP Filesystem Server 获得更安全的文件访问
mcp_servers:
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/allowed/dir"]
```

### 2. 网络工具

访问互联网：抓取网页、搜索信息、调用外部 API。

| 工具 | 来源 | 做什么 |
|------|------|--------|
| `WebFetch` | Claude Code 内置 | 抓取 URL 内容并转换为 markdown |
| `WebSearch` | Claude Code 内置 | 搜索网页并返回结果 |
| `brave_search` | Brave Search MCP | 更强大的网页搜索，支持本地化结果 |

### 3. Shell 工具

执行系统命令：运行脚本、安装依赖、git 操作。

| 工具 | 来源 | 做什么 |
|------|------|--------|
| `Bash` | Claude Code 内置 | 执行任意 shell 命令 |
| `Task` | Claude Code 内置 | 在后台运行长时间任务 |

```yaml
# Hermes 中，Shell 能力通常是平台内置的
# 但可以通过 MCP 获得更精细的命令执行控制
mcp_servers:
  command:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-command"]
    # 允许在沙箱中执行白名单命令
```

### 4. API 工具

对接第三方服务：GitHub、数据库、项目管理。

| 工具 | 来源 | 做什么 |
|------|------|--------|
| `mcp_github_list_issues` | GitHub MCP | 列出 Issue |
| `mcp_github_create_pr` | GitHub MCP | 创建 Pull Request |
| `mcp_postgres_query` | Postgres MCP | 执行 SQL 查询 |

这四类工具的共同点：**Agent 不关心你内部怎么实现**，它只关心"我能用你做什么"和"我需要传什么参数"。

---

## 工具的权限控制

### 为什么 Agent 需要权限控制？

Agent 有能力执行"危险"操作——删文件、执行 shell 命令、访问网络。没有权限控制，Agent 可能因为：
- **幻觉**：错误地判断了什么该做
- **Prompt 注入**：用户输入中嵌入了恶意指令
- **意外**：Agent 误操作导致数据丢失

> 原则：**给 Agent 最小的必要权限，而不是全部权限。**

### Hermes 的权限控制

Hermes 在 `config.yaml` 中控制权限，按 MCP Server 粒度授权：

```yaml
# 全局开关：是否允许 MCP
mcp_enabled: true

mcp_servers:
  # 只读的 GitHub——Agent 可以看 Issue，但不能创建/修改
  github:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-github"]
    env:
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_readonly_xxx"  # 只读 token
    tools:
      allow: ["list_issues", "get_issue", "search_repositories"]  # 白名单
      # deny: ["create_pr", "delete_repo"]  # 也可以黑名单

  # 文件系统——限制访问路径
  filesystem:
    command: "npx"
    args: ["-y", "@modelcontextprotocol/server-filesystem", "/home/user/safe-dir"]
    # Server 启动时就限制了只能访问 safe-dir，Agent 跑不出去
```

**Hermes 的权限模型：**
- 在 MCP Server 层面控制（用只读 token、限制文件路径）
- 通过 `allow` / `deny` 列表精细控制工具
- 环境变量隔离（敏感信息不进代码仓库）

### Claude Code 的权限模式

Claude Code 有三级权限模式：

| 模式 | 行为 | 适合 |
|------|------|------|
| **Default** | 每次调用工具都弹确认框 | 日常开发，最安全 |
| **Accept Edits** | 编辑文件自动通过，其他操作仍需确认 | 信任 Agent 做代码修改 |
| **Bypass** | 所有操作自动通过，不询问 | 仅在完全信任的自动化脚本中使用 |

```bash
# 启动时指定权限模式
claude --permission-mode default
claude --permission-mode accept-edits
claude --permission-mode bypass
```

**两者的差异：**
- Hermes 靠 **配置驱动**——配置文件写好后，权限策略就定了
- Claude Code 靠 **交互式弹窗**——运行时让用户决定每一步是否允许
- 前者适合自动化流程，后者适合交互式开发

---

## 动手练习

### 目标

打开 Hermes 的配置文件，理解 MCP 配置结构，添加一个新的 MCP Server。

### Step 1：找到并打开配置文件

```bash
# 配置文件路径
cat ~/.hermes/config.yaml
```

如果你用的是 Claude Code，查看它的 MCP 配置：

```bash
# Claude Code 的 MCP 配置文件
cat ~/.claude/mcp.json   # 用户级
cat .claude/mcp.json     # 项目级（覆盖用户级）
```

### Step 2：理解每个字段

以 GitHub Server 为例，逐字段理解：

```yaml
mcp_servers:           # ← 所有 MCP Server 的列表
  github:              # ← Server 的名字（你自己起，唯一就行）
    command: "npx"     # ← 启动命令：用什么程序来跑这个 Server
    args:              # ← 命令参数：传给 npx 的
      - "-y"           #   -y: 自动确认安装（不再问 "Install? y/n"）
      - "@modelcontextprotocol/server-github"  # ← NPM 包名
    env:               # ← 环境变量：Server 进程需要的
      GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_xxx"  # ← GitHub Token
```

**关键字段总结：**

| 字段 | 含义 | 必填 |
|------|------|------|
| `command` | 启动 Server 的可执行文件（npx、node、python 等） | 是 |
| `args` | 传给 command 的参数列表 | 否 |
| `env` | 环境变量（Token、API Key 等敏感信息放这里） | 否 |
| `tools.allow` | 白名单：只允许 Agent 用这些工具 | 否 |
| `tools.deny` | 黑名单：禁止 Agent 用这些工具 | 否 |

### Step 3：添加你的第一个自定义 MCP Server

以 **Time MCP Server**（一个返回当前时间的简单 Server）为例：

```yaml
mcp_servers:
  # ... 你已有的配置 ...

  time:                                    # Server 名
    command: "npx"
    args:
      - "-y"
      - "@anthropic/mcp-server-time"       # 官方示例 time server
```

或者用 Python 版：

```yaml
mcp_servers:
  time:
    command: "python"
    args: ["-m", "mcp_server_time"]
```

重启 Hermes 后，Agent 就多了一个 `get_current_time` 工具，可以查询不同时区的当前时间。

### Step 4：验证

重启后对 Agent 说：

> "现在几点了？东京时间呢？"

如果 Agent 能正确回答，说明 MCP Server 配置成功。

---

## 常见 MCP Server 推荐

以下是 5 个最有用的 MCP Server，涵盖了大多数开发场景：

### 1. GitHub — `@modelcontextprotocol/server-github`

管理 GitHub 上的一切：仓库、Issue、PR、分支。

```
能做什么：
  - 搜索仓库、查看文件内容
  - 列出/创建/更新 Issue 和 Pull Request
  - 查看 CI 状态、Review 评论
  - 创建分支、合并代码

典型的 Agent 工作流：
  读 Issue → 创建分支 → 写代码 → 提交 PR → 等待 CI → 合并
```

```yaml
github:
  command: "npx"
  args: ["-y", "@modelcontextprotocol/server-github"]
  env:
    GITHUB_PERSONAL_ACCESS_TOKEN: "ghp_xxx"
```

### 2. Filesystem — `@modelcontextprotocol/server-filesystem`

安全的文件系统访问，限制在指定目录内。

```
能做什么：
  - 读取、创建、编辑、删除文件和目录
  - 搜索文件内容
  - 获取文件元信息

为什么比直接 shell 好：
  限定访问路径，Agent 跑不出你指定的目录
```

```yaml
filesystem:
  command: "npx"
  args: ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/project"]
```

### 3. Postgres — `@anthropic/mcp-server-postgres`

直接查询数据库，Agent 可以帮你写 SQL、分析数据。

```
能做什么：
  - 列出表结构（schema）
  - 执行 SELECT 查询（只读模式推荐）
  - 执行 DDL/DML（可配置开关）

典型用法：
  "帮我查一下上个月注册用户的地理分布"
  Agent 会读 schema → 写 SQL → 执行查询 → 返回分析结果
```

```yaml
postgres:
  command: "npx"
  args: ["-y", "@anthropic/mcp-server-postgres", "postgresql://localhost/mydb"]
```

### 4. Puppeteer — `@modelcontextprotocol/server-puppeteer`

浏览器自动化：截图、抓取动态页面、端到端测试。

```
能做什么：
  - 导航到任意 URL
  - 点击、输入、滚动
  - 截图、获取页面 HTML
  - 执行 JavaScript

典型用法：
  "打开首页，看看有没有报错"
  Agent 会打开浏览器 → 导航到页面 → 截图 → 检查 console
```

```yaml
puppeteer:
  command: "npx"
  args: ["-y", "@modelcontextprotocol/server-puppeteer"]
```

### 5. Brave Search — `@anthropic/mcp-server-brave-search`

让 Agent 能搜索互联网，获取最新信息。

```
能做什么：
  - Web 搜索（支持本地化结果）
  - 新闻搜索

和内置 WebSearch 的差异：
  Brave Search 的 API 更稳定，结果质量可控
```

```yaml
brave:
  command: "npx"
  args: ["-y", "@anthropic/mcp-server-brave-search"]
  env:
    BRAVE_API_KEY: "your-api-key"
```

### 快速选型指南

| 你想要 Agent 能... | 用这个 |
|--------------------|--------|
| 操作 GitHub（Issue/PR/代码） | GitHub Server |
| 读写项目文件 | Filesystem Server |
| 查询/分析数据库 | Postgres Server |
| 测试网页、截图 | Puppeteer Server |
| 搜索互联网 | Brave Search Server |

这 5 个组合起来，Agent 就具备了"读代码 → 理解需求 → 查资料 → 写代码 → 测试 → 提 PR"的完整能力链。

---

## 相关

- [[写Skill]] — 上一层：Skill 是工具的"用户手册"
- [[上下文工程]] — 下一层：工具的输入输出都在 Context 里
