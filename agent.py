# -*- coding: utf-8 -*-
"""
W8 分組實作：MCP Client + Gemini Agent

啟動方式：
  終端機 1：python server.py   （先啟動 Server）
  終端機 2：python agent.py    （再啟動 Agent）
"""

import asyncio
import sys
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types
from mcp import ClientSession
from mcp.client.sse import sse_client

# Windows 終端機 UTF-8 支援
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 載入 .env 中的 GEMINI_API_KEY
load_dotenv()

MCP_SERVER_URL = "http://localhost:8000/sse"

# 與配額耗盡時自動轉換的備用模型序列（由湻到強）
GEMINI_MODELS = [
    "gemini-2.0-flash-lite",   # 輕量、免費配額最宬
    "gemini-2.5-flash",        # 較強、獨立配額桶
    "gemini-2.0-flash",        # 備用 3
    "gemini-2.5-pro",          # 最強（通常需付費）
]


# ── 工具清單轉換：MCP → Gemini function declaration ──────────────────────────

def mcp_tool_to_gemini(tool) -> dict:
    """將單一 MCP Tool 物件轉為 Gemini FunctionDeclaration dict。"""
    # 取得 inputSchema，若沒有則給空 object schema
    schema = getattr(tool, "inputSchema", None) or {"type": "object", "properties": {}}

    return {
        "name": tool.name,
        "description": tool.description or "",
        "parameters": schema,
    }


def build_gemini_tools(mcp_tools) -> list[types.Tool]:
    """將所有 MCP Tools 包裝成 Gemini Tool 物件。"""
    declarations = [mcp_tool_to_gemini(t) for t in mcp_tools]
    return [
        types.Tool(
            function_declarations=[
                types.FunctionDeclaration(**d) for d in declarations
            ]
        )
    ]


# ── 主要 Agent 流程 ──────────────────────────────────────────────────────────

async def run_agent():
    """連接 MCP Server，啟動 Gemini 多輪對話 Agent。"""

    print(f"[Agent] 正在連接 MCP Server：{MCP_SERVER_URL} ...")

    async with sse_client(MCP_SERVER_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("[Agent] MCP Server 連接成功！\n")

            # 1. 取得所有工具清單
            tools_result = await session.list_tools()
            mcp_tools = tools_result.tools
            print(f"[Agent] 取得工具清單（共 {len(mcp_tools)} 個）：")
            for t in mcp_tools:
                print(f"  - {t.name}：{t.description or '（無描述）'}")
            print()

            # 2. 轉換成 Gemini function declaration 格式
            gemini_tools = build_gemini_tools(mcp_tools)

            # 3. 初始化 Gemini Client
            client = genai.Client()

            # 對話歷史
            history: list[types.Content] = []

            print("=" * 50)
            print("  旅途知識問答 Agent（輸入 'exit' 結束）")
            print("=" * 50)

            while True:
                # 取得使用者輸入
                try:
                    user_input = input("\n你：").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\n[Agent] 結束對話。")
                    break

                if user_input.lower() in ("exit", "quit", "bye", "q"):
                    print("[Agent] 掰掰！")
                    break

                if not user_input:
                    continue

                # 加入使用者訊息到歷史
                history.append(
                    types.Content(
                        role="user",
                        parts=[types.Part(text=user_input)],
                    )
                )

                # 4. 多輪呼叫：Gemini → function_call → MCP → 回 Gemini
                while True:
                    # 呼叫 Gemini，遇到 429 自動轉換備用模型
                    response = None
                    for model_idx, current_model in enumerate(GEMINI_MODELS):
                        try:
                            print(f"[Debug] 使用模型：{current_model}")
                            response = client.models.generate_content(
                                model=current_model,
                                contents=history,
                                config=types.GenerateContentConfig(tools=gemini_tools),
                            )
                            break  # 成功就跳出
                        except Exception as e:
                            err_str = str(e)
                            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                                if model_idx + 1 < len(GEMINI_MODELS):
                                    next_model = GEMINI_MODELS[model_idx + 1]
                                    print(f"[警告] {current_model} 配額耗盡，轉換為 {next_model}")
                                else:
                                    print(f"[警告] 所有備用模型配額均耗盡，等待 30 秒再試一次...")
                                    time.sleep(30)
                                    try:
                                        response = client.models.generate_content(
                                            model=GEMINI_MODELS[0],
                                            contents=history,
                                            config=types.GenerateContentConfig(tools=gemini_tools),
                                        )
                                    except Exception:
                                        pass
                            else:
                                print(f"\n[錯誤] Gemini API 發生錯誤：{e}")
                                raise
                    if response is None:
                        print("[錯誤] 所有模型配額耗盡，請明日再試或更換 API Key。")
                        history.pop()  # 移除剛加入的 user 訊息，避免歷史污染
                        break

                    candidate = response.candidates[0]
                    content   = candidate.content  # Content 物件

                    # 把模型回應加入歷史
                    history.append(content)

                    # 判斷是否有 function_call
                    function_calls = [
                        p for p in content.parts if p.function_call is not None
                    ]

                    if not function_calls:
                        # 純文字回應，顯示給使用者後跳出內層迴圈
                        text_parts = [
                            p.text for p in content.parts
                            if hasattr(p, "text") and p.text
                        ]
                        ai_reply = "".join(text_parts).strip()
                        if ai_reply:
                            print(f"\nAI：{ai_reply}")
                        break

                    # 5. 處理所有 function_call
                    tool_response_parts = []
                    for part in function_calls:
                        fc   = part.function_call
                        name = fc.name
                        args = dict(fc.args) if fc.args else {}

                        print(f"\n[Debug] 呼叫工具：{name}，參數：{args}")

                        # 透過 MCP 呼叫 Tool
                        mcp_result = await session.call_tool(name, args)

                        # 取出純文字結果
                        result_text = ""
                        for c in mcp_result.content:
                            if hasattr(c, "text"):
                                result_text += c.text
                        if not result_text:
                            result_text = str(mcp_result.content)

                        print(f"[Debug] 工具結果：{result_text[:200]}{'...' if len(result_text) > 200 else ''}")

                        tool_response_parts.append(
                            types.Part(
                                function_response=types.FunctionResponse(
                                    name=name,
                                    response={"result": result_text},
                                )
                            )
                        )

                    # 把 Tool 結果回傳給 Gemini
                    history.append(
                        types.Content(role="tool", parts=tool_response_parts)
                    )
                    # 繼續內層迴圈讓 Gemini 產生最終文字回應


def main():
    asyncio.run(run_agent())


if __name__ == "__main__":
    main()
