import asyncio
import json
from mcp import ClientSession
from mcp.client.sse import sse_client

async def main():
    mcp_url = "http://127.0.0.1:8000/sse"
    print("🔌 正在連線到 MCP Server...")
    try:
        async with sse_client(mcp_url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("\n🌍 【本地離線版】旅遊顧問 Agent 已就緒！(無需外部 API)")
                print("💬 支援指令：")
                print("   /prompts                  （列出所有 Prompt）")
                print("   /tools                    （列出所有 Tool）")
                print("   /use <Prompt名> <參數>      （使用提示詞）")
                print("   /call <Tool名> <參數>       （直接呼叫工具下載內容）")
                print("   /quit                     （結束對話）")
                print("-" * 50)

                while True:
                    user_input = input("\n🧑 你：").strip()
                    if not user_input:
                        continue

                    if user_input.lower() == "/quit":
                        print("👋 再見！祝旅途愉快！")
                        break

                    # 1. 查詢所有的 Prompts
                    if user_input.lower() == "/prompts":
                        prompt_result = await session.list_prompts()
                        print("\n📋 可用的 Prompt：")
                        for p in prompt_result.prompts:
                            print(f"   📝 {p.name}：{p.description}")
                        continue
                    
                    # 2. 查詢所有的 Tools
                    if user_input.lower() == "/tools":
                        tool_result = await session.list_tools()
                        print("\n🔧 可用的 Tool：")
                        for t in tool_result.tools:
                            print(f"   - {t.name}：{t.description[:30]}...")
                        continue

                    # 3. 本地執行 Prompt 渲染
                    if user_input.startswith("/use "):
                        parts = user_input.split(maxsplit=2)
                        if len(parts) < 3:
                            print("⚠️ 用法：/use <prompt名稱> <參數> （例如：/use search_local 東京）")
                            continue
                        
                        prompt_name = parts[1]
                        prompt_arg = parts[2]
                        try:
                            prompt_result = await session.get_prompt(
                                prompt_name,
                                arguments={"city": prompt_arg},
                            )
                            content = prompt_result.messages[0].content.text
                            print(f"\n🤖 【系統詞預覽 - {prompt_name}】：\n{content}")
                        except Exception as e:
                            print(f"❌ 無法使用 Prompt：{e}")
                        continue
                    
                    # 4. 本地直接呼叫 Tool，免透過 AI
                    if user_input.startswith("/call "):
                        parts = user_input.split(maxsplit=2)
                        if len(parts) < 3:
                            print("⚠️ 用法：/call <Tool名稱> <查詢字串> （例如：/call web_search 東京美食）")
                            continue
                        
                        tool_name = parts[1]
                        tool_query = parts[2]
                        
                        print(f"\n⏳ 正在本地直接呼叫 {tool_name}，下載並索取「{tool_query}」的資料...")
                        try:
                            # 所有的 tool 預設使用 {"query": ...} 作為參數 (這邊依據 web_search 的實作)
                            result = await session.call_tool(tool_name, {"query": tool_query})
                            # 解析回傳文字並印出
                            tool_result_text = result.content[0].text
                            print(f"\n✅ 工具回傳結果：\n{tool_result_text}")
                        except Exception as e:
                            print(f"❌ 工具呼叫失敗：{e}")
                        continue

                    print("⚠️ 這是離線版，無法使用 AI 閒聊！請用 `/use` 或 `/call` 指令呼叫工具。")

    except Exception as e:
        print(f"❌ 無法連線到 Server，請確保你另一個終端機有在執行 python server.py。錯誤訊息: {e}")

if __name__ == "__main__":
    asyncio.run(main())
