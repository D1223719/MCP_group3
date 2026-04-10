import asyncio
import os
import sys
import traceback
import json
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding='utf-8')

from mcp import ClientSession
from mcp.client.sse import sse_client
from google import genai
from google.genai import types

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

async def main():
    if not GEMINI_API_KEY:
        print("❌ [錯誤] 找不到 GEMINI_API_KEY，請確認 .env 檔案是否已經設定。")
        return

    # 初始化 Gemini 客戶端
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    print("🔌 正在連接到 MCP Server (http://localhost:8000/sse)...")
    
    try:
        async with sse_client("http://localhost:8000/sse") as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                tools_response = await session.list_tools()
                mcp_tools = tools_response.tools
                
                print(f"✅ 連接成功！取得 {len(mcp_tools)} 個工具：")
                for t in mcp_tools:
                    print(f"   🔧 {t.name}：{t.description}")
                
                prompts_response = await session.list_prompts()
                prompts = prompts_response.prompts
                print(f"📋 取得 {len(prompts)} 個 Prompt。")
                
                gemini_tools = [{"function_declarations": [
                    {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.inputSchema
                    } for t in mcp_tools
                ]}]
                config_tools = gemini_tools if mcp_tools else None

                # 使用預設模型建立 Chat
                current_model = "gemini-2.0-flash"
                chat = client.chats.create(
                    model=current_model,
                    config=types.GenerateContentConfig(
                        tools=config_tools,
                        temperature=0.7,
                    )
                )

                print("\n🌍 旅遊顧問 Agent 已就緒！")
                print("💬 指令：/prompts（列出 Prompt）、/use <名稱> <參數>（使用 Prompt）、/quit（結束）")
                print("-" * 50)
                
                while True:
                    try:
                        user_input = input("\n🧑 你：").strip()
                    except (EOFError, KeyboardInterrupt):
                        break

                    if not user_input:
                        continue
                        
                    if user_input.lower() in ['/quit', 'exit', 'quit']:
                        print("👋 再見！祝旅途愉快！")
                        break

                    if user_input.lower() == "/prompts":
                        print("\n📋 可用的 Prompt：")
                        for p in prompts:
                            print(f"   📝 {p.name}：{p.description}")
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
                            print(f"📝 使用 Prompt「{prompt_name}」，已將系統詞設定為前情提要。")
                        except Exception as e:
                            print(f"❌ 無法使用 Prompt：{e}")
                            continue

                    try:
                        # 傳送使用者訊息，加入簡易的重試機制
                        max_retries = 3
                        response = None
                        
                        for attempt in range(max_retries):
                            try:
                                response = chat.send_message(user_input)
                                break  # 成功取得後跳出重試迴圈
                            except Exception as e:
                                error_str = str(e)
                                if "503" in error_str or "UNAVAILABLE" in error_str or "429" in error_str:
                                    if attempt < max_retries - 1:
                                        print(f"\n⏳ 模型目前較忙碌 (嘗試 {attempt + 1}/{max_retries})，等待 3 秒後重試...")
                                        await asyncio.sleep(3)
                                        continue
                                    else:
                                        raise Exception(f"嘗試了 {max_retries} 次仍無法連線，伺服器可能滿載中。")
                                else:
                                    # 其他錯誤直接拋出
                                    raise e

                        if not response:
                            continue
                            
                        # 當 Gemini 回傳 function_call 時
                        while response.function_calls:
                            for fn_call in response.function_calls:
                                tool_name = fn_call.name
                                tool_args = fn_call.args
                                
                                print(f"\n   🔧 呼叫工具：{tool_name}({json.dumps(tool_args, ensure_ascii=False)})")
                                
                                # 透過 MCP call_tool 呼叫 Tool
                                try:
                                    tool_result = await session.call_tool(tool_name, tool_args)
                                    result_text = tool_result.content[0].text if tool_result.content else "無回傳內容"
                                    print(f"   ✅ 結果取得，長度：{len(result_text)} 字")
                                except Exception as e:
                                    result_text = f"工具呼叫失敗：{str(e)}"
                                    print(f"   ❌ {result_text}")
                                
                                # 將結果回傳給 Gemini
                                response = chat.send_message(
                                    types.Part.from_function_response(
                                        name=tool_name,
                                        response={"result": result_text}
                                    )
                                )
                        
                        # 當 Gemini 產生最終文字回應時
                        if response.text:
                            print(f"\n🤖 Agent：{response.text}")
                            
                    except Exception as e:
                        print(f"\n❌ 呼叫 Gemini API 時發生問題：{e}")
                        print("👉 （自動防護：已攔截錯誤，你可以重新輸入文字繼續對話）")
                        
    except Exception as server_err:
        print(f"❌ 連接 Server 失敗，請確認你的 server.py 是否已經在另一個終端機啟動！\n錯誤訊息：{server_err}")

if __name__ == "__main__":
    asyncio.run(main())
