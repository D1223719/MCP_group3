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
import asyncio
import os
import sys
import traceback
from dotenv import load_dotenv

# 強制將輸入/輸出流設定為 utf-8 (較安全且相容性高的寫法)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding='utf-8')
from mcp import ClientSession
from mcp.client.sse import sse_client
from google import genai
from google.genai import types

# 讀取 .env 中的環境變數
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

async def main():
    if not GEMINI_API_KEY:
        print("[錯誤] 找不到 GEMINI_API_KEY，請確認 .env 檔案是否已經設定。")
        return

    # 1. 初始化 Gemini 客戶端
    ai_client = genai.Client(api_key=GEMINI_API_KEY)
    
    print("正在連接到 MCP Server (http://localhost:8000/sse)...")
    
    try:
        # 2. 使用 SSE 連接到 MCP Server
        async with sse_client("http://localhost:8000/sse") as (read, write):
            async with ClientSession(read, write) as session:
                # 必須先初始化 MCP session
                await session.initialize()
                
                # 3. 取得 Server 提供的所有工具
                tools_response = await session.list_tools()
                mcp_tools = tools_response.tools
                
                print(f"[成功] 共取得 {len(mcp_tools)} 個工具。")
                
                # 4. 將 MCP 格式的 Tools 轉換成 Gemini API 的 function declarations 格式
                gemini_tools = []
                for t in mcp_tools:
                    gemini_tools.append(
                        types.Tool(
                            function_declarations=[
                                types.FunctionDeclaration(
                                    name=t.name,
                                    description=t.description,
                                    parameters=t.inputSchema
                                )
                            ]
                        )
                    )

                # 5. 開啟與 Gemini 的對話 (使用 Gemini 2.5 Flash 避開舊版 2.0 的免費額度卡關)
                chat = ai_client.chats.create(
                    model="gemini-2.5-flash",
                    config=types.GenerateContentConfig(
                        tools=gemini_tools,
                        temperature=0.7,
                    )
                )

                print("\n=======================================================")
                print("聊天開始 (輸入 'exit' 或 'quit' 離開)")
                print("你可以試著問：請告訴我今天台北的天氣，該帶傘嗎？")
                print("=======================================================\n")
                
                while True:
                    user_input = input("你：")
                    if user_input.lower() in ['exit', 'quit']:
                        print("掰掰！")
                        break
                        
                    if not user_input.strip():
                        continue

                    try:
                        # 傳送使用者訊息
                        response = chat.send_message(user_input)
                        
                        # 6. 當 Gemini 回傳 function_call 時 (代表它想要呼叫外部工具)
                        while response.function_calls:
                            for fn_call in response.function_calls:
                                tool_name = fn_call.name
                                tool_args = fn_call.args
                                
                                print(f"\n[DEBUG] Gemini 決定呼叫工具：{tool_name}")
                                print(f"[DEBUG] 傳入參數：{tool_args}")
                                
                                # 透過 MCP call_tool 呼叫對應的 Tool
                                tool_result = await session.call_tool(tool_name, tool_args)
                                
                                # 取得工具回傳內容
                                result_text = tool_result.content[0].text if tool_result.content else "無回傳內容"
                                print(f"[DEBUG] 工具回傳結果長度：{len(result_text)} 字\n")
                                
                                # 將結果送回給 Gemini 繼續對話
                                response = chat.send_message(
                                    types.Part.from_function_response(
                                        name=tool_name,
                                        response={"result": result_text}
                                    )
                                )
                        
                        # 7. 當 Gemini 回傳文字時，直接顯示給使用者
                        if response.text:
                            print(f"Gemini：{response.text}\n")
                            
                    except Exception as e:
                        print(f"\n[錯誤] 發生例外：{e}")
                        traceback.print_exc()
                        print("\n")
                        
    except Exception as server_err:
        print(f"連接 Server 失敗，請確認你的 server.py 是否已經在另一個終端機啟動！\n錯誤訊息：{server_err}")


if __name__ == "__main__":
    asyncio.run(main())
