---
title: Agent Loop 学习总结
source: 《马书》第3章 — Agent Loop：从用户输入到模型响应的完整生命周期
created: 2026-05-19
type: learning-note
---

# Agent Loop 学习总结

## 一句话概括

Agent Loop 不是简单的 REPL（Read-Eval-Print Loop），而是一个**自修改状态机（self-modifying state machine）**——每一轮迭代都可能改变自身的运行条件（压缩缩减消息、模型降级切换后端、Hook 注入新约束）。

## queryLoop() 的核心设计

《马书》第3章分析了 CC 的 `queryLoop()` 函数（1730 行），它是整个 Claude Code 的"心跳"。每次迭代分为 8 个阶段：

1. **上下文预处理**：五级管线（工具结果裁剪 → snip → microcompact → context collapse → autocompact），从轻到重逐级释放 token 空间
2. **Blocking limit 检查**：token 数超过硬限制则直接终止，防止 API 调用必然失败
3. **API 调用**：带 fallback 的模型调用，流式处理响应，扣留可恢复错误
4. **中断检查**：用户在流式响应期间中断则立即返回
5. **恢复与终止判定**（模型无 tool_use 时）：处理 prompt-too-long / max_output_tokens / stop hooks / token budget 四种恢复路径
6. **工具执行**：并行执行所有 tool_use，收集结果
7. **附件注入**：消费后台预取的 memory、skill discovery、队列命令
8. **继续判定**：检查 maxTurns，构造完整新 State 进入下一轮

## 最让我震撼的设计

### 1. 显式状态重建而非增量修改

每个 `continue` 站点都构造完整的新 `State` 对象——没有 `state.turnCount++`，只有 `state = { ..., turnCount: turnCount + 1, ... }`。这样"忘记重置字段"的 bug 类被物理消灭了。

### 2. 扣留-释放（Withhold-Release）模式

可恢复错误不立即暴露给上层消费者。它们被扣留在内部，只有所有恢复手段耗尽后才被"释放"。这防止了 SDK 消费者在看到错误时过早终止会话——恢复成功就不需要让外部知道曾经出错。

### 3. 从轻到重的分层恢复

无论是压缩（snip → microcompact → collapse → autocompact）还是错误恢复（escalate → multi-turn → reactive compact），策略总是从信息损失最小的方法开始。这不是性能优化，而是信息保留策略。

### 4. 死循环保护的单次尝试守卫

`hasAttemptedReactiveCompact`、`maxOutputTokensRecoveryCount ≤ 3`——每个恢复策略都有布尔标记或计数器防止无限循环。源码注释中反复出现 "death spiral" 一词，这些守卫来自真实生产事故的教训。

### 5. 后台并行化的滑动窗口

Memory 预取在循环入口启动，工具摘要在工具执行后异步启动——它们都在模型流式响应的 5-30 秒"免费"窗口期内完成计算。延迟被隐藏得几乎不可见。

## 与我正在做的 Hermes 的对比

| 维度 | Claude Code (queryLoop) | Hermes (当前) |
|------|------------------------|---------------|
| 循环模型 | 自修改状态机（7 个 Continue + 10 个 Terminal） | 标准 ReAct 循环 |
| 上下文压缩 | 五级管线（snip→micro→collapse→auto） | 自动压缩（依赖平台） |
| 错误恢复 | escalate → multi-turn recovery ×3 → reactive compact | 工具失败 → Agent 收到错误 → 自行调整 |
| 状态管理 | 显式 State 对象，完整重建 | 隐式状态（对话历史承载） |
| 并行预取 | 流式窗口期内后台完成 memory/skill 预取 | Skill 按需激活（懒加载） |
| 观测 | logEvent 遥测系统 | Task list + 对话日志 |

## 一个可以直接用的启示

在写 Skill 时，加上类似"单次尝试守卫"的设计——如果一个 Skill 包含重试逻辑，必须声明 maxRetries 和退避策略，防止 Skill 内部的循环成为 Agent 整体循环中的"死亡螺旋放大器"。
