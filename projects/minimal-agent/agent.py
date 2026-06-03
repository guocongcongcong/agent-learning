"""
Minimal Agent — 从零理解 Agent 的每一个环节

这是一个不到 300 行的 Agent 实现，让你看到：
1. Agent Loop（思考→行动→观察 循环）
2. 工具注册与调用
3. 步数限制（防止无限循环）
4. 简单的记忆系统

运行方式：
  export ANTHROPIC_API_KEY=your_key   # 或 OPENAI_API_KEY
  python agent.py "帮我查一下北京天气"

设计原则：零依赖框架，只用标准库 + openai SDK。每行代码都加了注释。
"""

import json, os, sys
from openai import OpenAI

# ============================================================
# 第一部分：工具定义
# ============================================================
# 每个工具是一个函数 + 一段描述（给 LLM 看的）
# LLM 通过描述来理解工具的用途，绝不会调用没描述过的工具

def tool_get_date():
    """获取当前日期和时间"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S %A")

def tool_calculate(expression: str):
    """安全的数学计算器，只支持 + - * / () 和数字"""
    allowed = set("0123456789+-*/(). ")
    if not all(c in allowed for c in expression):
        return f"Error: 表达式包含不允许的字符。只支持数字和 + - * / ()"
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return f"{expression} = {result}"
    except Exception as e:
        return f"计算错误: {e}"

def tool_read_file(filepath: str):
    """读取文件内容（限制前500行）"""
    try:
        with open(os.path.expanduser(filepath), "r") as f:
            lines = f.readlines()[:500]
            return "".join(lines)
    except FileNotFoundError:
        return f"Error: 文件不存在: {filepath}"
    except Exception as e:
        return f"Error: {e}"

def tool_search_web(query: str):
    """
    模拟网页搜索（实际工程中会接 Google/Bing API）。
    这里返回模拟结果，让你看到工具调用的完整流程。
    """
    # 模拟搜索
    fake_db = {
        "北京天气": "北京今天晴，18-28°C，北风3-4级，空气质量良",
        "python": "Python 3.13 是最新版本，发布于2024年10月",
        "agent": "AI Agent 是能自主使用工具完成多步任务的 AI 系统",
    }
    for key, answer in fake_db.items():
        if key in query.lower():
            return answer
    return f"搜索 '{query}' 未找到相关结果（模拟数据有限，请尝试搜索'北京天气'）"

# ---- 工具注册表 ----
# Agent 能用的所有工具都注册在这里
# 每个工具包含：函数、LLM 可读的描述、参数schema

TOOLS = [
    {
        "name": "get_date",
        "description": "获取当前日期和时间。不需要参数。",
        "function": tool_get_date,
        "parameters": {"type": "object", "properties": {}, "required": []}
    },
    {
        "name": "calculate",
        "description": "执行数学计算。参数 expression 是一个数学表达式，如 '2+3*4'",
        "function": tool_calculate,
        "parameters": {
            "type": "object",
            "properties": {"expression": {"type": "string", "description": "数学表达式，只支持 + - * / ()"}},
            "required": ["expression"]
        }
    },
    {
        "name": "read_file",
        "description": "读取文件内容。参数 filepath 是文件路径。",
        "function": tool_read_file,
        "parameters": {
            "type": "object",
            "properties": {"filepath": {"type": "string", "description": "文件路径"}},
            "required": ["filepath"]
        }
    },
    {
        "name": "search_web",
        "description": "搜索网页信息。参数 query 是搜索关键词。",
        "function": tool_search_web,
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "搜索关键词"}},
            "required": ["query"]
        }
    },
]


# ============================================================
# 第二部分：Agent Loop（Agent 的"心脏"）
# ============================================================

class Agent:
    """
    极简 Agent 实现。
    
    核心流程就是 Agent Loop：
    while 任务没完成 and 没到步数上限:
        1. 把对话历史发给 LLM
        2. LLM 决定：直接回复用户，还是调用工具？
        3. 如果调用工具 → 执行工具 → 把结果加回对话 → 继续循环
        4. 如果直接回复 → 任务完成，退出
    """

    def __init__(self, max_steps=10):
        self.max_steps = max_steps        # 防止无限循环
        self.memory = {}                   # 跨轮次记忆（本次对话内）
        self.conversation = []             # 对话历史

    def run(self, task: str) -> str:
        """主入口：接收任务，运行 Agent Loop，返回结果"""

        # 初始化对话：系统提示 + 用户任务
        self.conversation = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": task}
        ]

        print(f"\n{'='*60}")
        print(f"🤖 Agent 启动")
        print(f"📋 任务: {task}")
        print(f"{'='*60}\n")

        for step in range(1, self.max_steps + 1):
            print(f"--- Step {step}/{self.max_steps} ---")

            # ---------- THOUGHT（思考）----------
            # 把对话历史发送给 LLM，LLM 决定下一步
            response = self._call_llm()

            # ---------- 判断：继续还是结束？----------
            if response.get("finish") == "stop":
                # LLM 决定结束了，返回最终回复
                final_answer = response["text"]
                print(f"✅ 完成: {final_answer[:200]}...")
                return final_answer

            # ---------- ACTION（行动）----------
            # LLM 要求调用工具
            tool_name = response["tool"]
            tool_args = json.loads(response.get("tool_args", "{}"))

            print(f"🔧 调用工具: {tool_name}({tool_args})")

            # ---------- OBSERVATION（观察结果）----------
            tool_result = self._execute_tool(tool_name, tool_args)
            print(f"📊 工具返回: {str(tool_result)[:200]}")

            # 把工具调用和结果加入对话历史，供下一轮 LLM 参考
            self.conversation.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": f"call_{step}",
                    "type": "function",
                    "function": {"name": tool_name, "arguments": json.dumps(tool_args, ensure_ascii=False)}
                }]
            })
            self.conversation.append({
                "role": "tool",
                "tool_call_id": f"call_{step}",
                "content": str(tool_result)
            })

            # 保存到记忆
            self.memory[tool_name] = tool_result

        # 达到步数上限
        return f"⚠️ 达到最大步数 {self.max_steps}，Agent 停止。已完成的记忆: {list(self.memory.keys())}"

    def _call_llm(self):
        """调用 LLM，让它决定下一步做什么"""

        # 构建给 LLM 的工具描述（OpenAI function calling 格式）
        tool_schemas = [
            {
                "type": "function",
                "function": {
                    "name": t["name"],
                    "description": t["description"],
                    "parameters": t["parameters"]
                }
            }
            for t in TOOLS
        ]

        client = _get_client()
        model_name = os.getenv("AGENT_MODEL", "deepseek-chat")
        resp = client.chat.completions.create(
            model=model_name,
            messages=self.conversation,
            tools=tool_schemas,
            tool_choice="auto",      # LLM 自己决定调不调工具
            temperature=0.1,
        )

        msg = resp.choices[0].message

        # 情况1：LLM 决定不调工具，直接回复
        if msg.tool_calls is None:
            return {"finish": "stop", "text": msg.content or "完成"}

        # 情况2：LLM 要调工具
        tool_call = msg.tool_calls[0]
        return {
            "finish": "tool",
            "tool": tool_call.function.name,
            "tool_args": tool_call.function.arguments
        }

    def _execute_tool(self, name: str, args: dict):
        """执行工具并处理异常"""
        for tool in TOOLS:
            if tool["name"] == name:
                try:
                    if args.get("expression"):
                        return tool["function"](args["expression"])
                    elif args.get("filepath"):
                        return tool["function"](args["filepath"])
                    elif args.get("query"):
                        return tool["function"](args["query"])
                    else:
                        return tool["function"]()
                except Exception as e:
                    return f"工具执行失败: {e}"
        return f"Error: 未找到工具 '{name}'"


# ============================================================
# 第三部分：系统提示词（Agent 的"员工手册"）
# ============================================================

SYSTEM_PROMPT = """你是一个有用的 AI 助手。你可以调用工具来完成任务。

规则：
1. 每一步只调用一个工具。
2. 拿到工具结果后，判断是否需要继续调用其他工具。
3. 当你有了足够信息来回答用户，就直接给出最终答案，不再调用工具。
4. 如果工具失败了，告诉用户失败原因，不要死循环重试。
5. 用中文回复。
"""


# ============================================================
# 第四部分：工具函数
# ============================================================

def _get_client():
    """获取 LLM 客户端，支持 OpenAI 和 DeepSeek"""
    # 优先用 DeepSeek（便宜），其次 OpenAI
    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")

    if not api_key:
        print("Error: 请设置 DEEPSEEK_API_KEY 或 OPENAI_API_KEY 环境变量")
        print("  export DEEPSEEK_API_KEY=sk-xxx")
        sys.exit(1)

    return OpenAI(api_key=api_key, base_url=base_url)


# ============================================================
# 第五部分：入口
# ============================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python agent.py \"你的任务\"")
        print("示例: python agent.py \"帮我查一下北京天气\"")
        print("示例: python agent.py \"今天是周几？计算 123*456 等于多少\"")
        sys.exit(1)

    task = sys.argv[1]
    agent = Agent(max_steps=10)
    result = agent.run(task)
    print(f"\n{'='*60}")
    print(f"📝 最终结果:\n{result}")
    print(f"{'='*60}")
