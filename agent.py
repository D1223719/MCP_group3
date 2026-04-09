"""
W8 分組實作：MCP Client + Gemini Agent

啟動方式：
  終端機 1：python server.py   （先啟動 Server）
  終端機 2：python agent.py    （再啟動 Agent）

功能：
  - 一般對話：直接輸入文字與 AI 對話
  - /prompts：列出所有可用的 Prompt
  - /use <名稱> <參數>：使用指定 Prompt（例如 /use plan_trip Taipei）
  - /quit：結束對話
"""

import os
import asyncio
import json

from dotenv import load_dotenv
from google import genai
from google.genai import types
from mcp import ClientSession
from mcp.client.sse import sse_client

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    # 強制覆蓋系統可能舊有的 GOOGLE_API_KEY，避免 SDK 抓錯
    os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY

MODEL_NAME = "gemini-2.0-flash"
MCP_SERVER_URL = "http://localhost:8000/sse"


def mcp_tools_to_gemini_declarations(mcp_tools):
    """將 MCP tool 清單轉換成 Gemini function declaration 格式"""
    declarations = []
    for tool in mcp_tools:
        properties = {}
        required = []

        if tool.inputSchema and "properties" in tool.inputSchema:
            for prop_name, prop_info in tool.inputSchema["properties"].items():
                prop_type = prop_info.get("type", "string").upper()
                # Gemini 只支援部分型別
                type_mapping = {
                    "STRING": "STRING",
                    "INTEGER": "INTEGER",
                    "NUMBER": "NUMBER",
                    "BOOLEAN": "BOOLEAN",
                }
                properties[prop_name] = types.Schema(
                    type=type_mapping.get(prop_type, "STRING"),
                    description=prop_info.get("description", ""),
                )

            if "required" in tool.inputSchema:
                required = tool.inputSchema["required"]

        # 建立 function declaration
        func_decl = types.FunctionDeclaration(
            name=tool.name,
            description=tool.description or "",
            parameters=types.Schema(
                type="OBJECT",
                properties=properties,
                required=required,
            ) if properties else None,
        )
        declarations.append(func_decl)

    return declarations


async def main():
    """主程式：連接 MCP Server，啟動 Gemini Agent 對話"""
    client = genai.Client(api_key=GEMINI_API_KEY)

    print("🔌 正在連接 MCP Server...")

    async with sse_client(MCP_SERVER_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 取得所有工具
            tools_result = await session.list_tools()
            mcp_tools = tools_result.tools
            print(f"✅ 已連接！取得 {len(mcp_tools)} 個工具：")
            for t in mcp_tools:
                print(f"   🔧 {t.name}：{t.description}")

            # 取得所有 Prompts
            prompts_result = await session.list_prompts()
            available_prompts = prompts_result.prompts
            print(f"📋 可用 Prompt：{len(available_prompts)} 個")
            for p in available_prompts:
                print(f"   📝 {p.name}：{p.description}")

            # 轉換 MCP tools → Gemini function declarations
            declarations = mcp_tools_to_gemini_declarations(mcp_tools)
            gemini_tools = types.Tool(function_declarations=declarations)

            # 對話歷史
            chat_history = []

            print("\n🌍 旅遊顧問 Agent 已就緒！")
            print("💬 指令：/prompts（列出 Prompt）、/use <名稱> <參數>（使用 Prompt）、/quit（結束）")
            print("-" * 50)

            while True:
                user_input = input("\n🧑 你：").strip()
                if not user_input:
                    continue

                # 指令處理
                if user_input.lower() == "/quit":
                    print("👋 再見！祝旅途愉快！")
                    break

                if user_input.lower() == "/prompts":
                    print("\n📋 可用的 Prompt：")
                    for p in available_prompts:
                        args = ", ".join(
                            [a.name for a in p.arguments] if p.arguments else []
                        )
                        print(f"   📝 {p.name}({args})：{p.description}")
                    continue

                if user_input.startswith("/use "):
                    parts = user_input.split(maxsplit=2)
                    if len(parts) < 3:
                        print("⚠️ 用法：/use <prompt名稱> <參數>")
                        continue

                    prompt_name = parts[1]
                    prompt_arg = parts[2]

                    try:
                        prompt_result = await session.get_prompt(
                            prompt_name,
                            arguments={"city": prompt_arg},
                        )
                        user_input = prompt_result.messages[0].content.text
                        print(f"📝 使用 Prompt「{prompt_name}」，內容：\n{user_input}")
                    except Exception as e:
                        print(f"❌ 無法使用 Prompt：{e}")
                        continue

                # 加入對話歷史
                chat_history.append(
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=user_input)],
                    )
                )

                # 呼叫 Gemini 的多輪重試迴圈（處理 Function calling）
                fallback_models = ["gemini-2.0-flash", "gemini-2.0-flash-lite", "gemini-2.5-flash", "gemini-flash-latest"]
                
                while True:
                    # 每次與 Gemini 對話時，預設從首選模型開始嘗試
                    model_index = 0
                    response = None
                    
                    # 處理 Rate Limit 的內部重試迴圈
                    while True:
                        current_model = fallback_models[model_index]
                        try:
                            response = client.models.generate_content(
                                model=current_model,
                                contents=chat_history,
                                config=types.GenerateContentConfig(
                                    tools=[gemini_tools],
                                ),
                            )
                            break  # 成功取得 response，跳出內部限流重試迴圈
                        except Exception as e:
                            error_msg = str(e)
                            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg or "retryDelay" in error_msg:
                                if model_index < len(fallback_models) - 1:
                                    model_index += 1
                                    print(f"\n⏳ 模型 {current_model} 達到上限，自動切換至 {fallback_models[model_index]} 重新嘗試...")
                                    continue
                                else:
                                    print("\n⏳ 所有備用模型皆達到上限。自動等待 30 秒後重新嘗試首選模型...")
                                    import time
                                    time.sleep(30)
                                    model_index = 0  # 重置回首選模型繼續重試
                                    continue
                            else:
                                print(f"\n❌ 呼叫 Gemini API ({current_model}) 時發生錯誤：\n{e}")
                                print("👉 請確認您的 API Key 是否正確。")
                                break
                    
                    if response is None:
                        break  # 發生非限流的嚴重錯誤，跳出外部重試迴圈，結束這回合對話

                    # 取得回應
                    candidate = response.candidates[0]
                    parts = candidate.content.parts

                    # 加入 assistant 回應到歷史
                    chat_history.append(candidate.content)

                    # 檢查是否有 function call
                    function_calls = [p for p in parts if p.function_call]

                    if not function_calls:
                        # 純文字回應
                        text_parts = [p.text for p in parts if p.text]
                        if text_parts:
                            print(f"\n🤖 Agent：{''.join(text_parts)}")
                        break

                    # 處理 function calls
                    function_responses = []
                    for fc_part in function_calls:
                        fc = fc_part.function_call
                        tool_name = fc.name
                        tool_args = dict(fc.args) if fc.args else {}

                        print(f"\n   🔧 呼叫工具：{tool_name}({json.dumps(tool_args, ensure_ascii=False)})")

                        try:
                            result = await session.call_tool(tool_name, tool_args)
                            tool_result = result.content[0].text
                            print(f"   ✅ 結果：{tool_result[:100]}...")
                        except Exception as e:
                            tool_result = f"工具呼叫失敗：{str(e)}"
                            print(f"   ❌ {tool_result}")

                        function_responses.append(
                            types.Part.from_function_response(
                                name=tool_name,
                                response={"result": tool_result},
                            )
                        )

                    # 把工具結果送回 Gemini
                    chat_history.append(
                        types.Content(
                            role="user",
                            parts=function_responses,
                        )
                    )


if __name__ == "__main__":
    asyncio.run(main())
