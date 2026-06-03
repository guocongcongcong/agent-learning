# Minimal Agent

从零理解 Agent 的极简实现。不到 300 行 Python，展示 Agent 的每个核心环节。

## 运行

```bash
export DEEPSEEK_API_KEY=sk-xxx    # 或 OPENAI_API_KEY
python agent.py "帮我查一下北京天气"
python agent.py "今天是周几？算一下 123*456"
python agent.py "读一下 agent.py 文件前50行，告诉我文件大小"
```

## 核心概念

### Agent Loop（核心循环）
```
while 任务没完成 and 没到步数上限:
    Thought  →  把对话历史发给 LLM，让它思考
    Action   →  LLM 决定调用哪个工具
    Observation → 执行工具，把结果加回对话
    → 回到 Thought，继续循环
```

### 三个关键设计
1. **步数上限（max_steps）**：防止 Agent 无限循环。生产环境中 Hermes 默认 100 步，Claude Code 也是有限步数。
2. **工具注册表（TOOLS）**：Agent 能用的所有工具。每个工具 = 函数 + 描述 + 参数 schema。LLM 通过描述来理解工具用途。
3. **系统提示词（SYSTEM_PROMPT）**：定义了 Agent 的身份和行为边界——什么时候该调工具、什么时候该结束。

### 与 Hermes 的对应关系
| 本项目的组件 | Hermes 的对应 |
|-------------|-------------|
| Agent Loop | Hermes 的 ReAct Loop（Thought → Tool Call → Observation）|
| TOOLS 列表 | Hermes 的 20+ 工具（Bash、Read、Write、WebSearch 等）|
| SYSTEM_PROMPT | Hermes 系统提示词（角色定义 + 规则 + 工具描述）|
| max_steps | Hermes 的 maxTurns |
| memory | Hermes 的 Memory 系统（跨 session 持久化）|
| tool.execute() | Hermes 的权限检查 + 工具执行 + 结果观测 |

## 拓展练习

理解这个 Agent 后，试试：
1. 加一个新工具（比如 `tool_send_email`）
2. 把 max_steps 改成 3，观察 Agent 在复杂任务中断的表现
3. 把对话历史保存到文件，实现跨会话"记忆"
4. 加上权限检查——某些危险工具需要用户确认
