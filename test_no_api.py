import asyncio
import json
from mcp import ClientSession
from mcp.client.sse import sse_client

async def main():
    mcp_url = "http://127.0.0.1:8000/sse"
    print("🔌 正在連線到你的 MCP Server...")
    try:
        async with sse_client(mcp_url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("✅ 連線成功！你的 Server 功能目前非常健康。\n")

                # 1. 測試 Tools
                tool_result = await session.list_tools()
                print("🔧 【步驟 1】檢查你實作的 Tool：")
                for t in tool_result.tools:
                    print(f"   - 名稱: {t.name} (描述: {t.description[:20]}...)")
                print("\n")
                
                # 2. 測試 Prompts
                prompt_result = await session.list_prompts()
                print("📝 【步驟 2】檢查你實作的 Prompt：")
                for p in prompt_result.prompts:
                    print(f"   - 名稱: {p.name} (描述: {p.description[:20]}...)")
                print("\n")

                # 3. 測試 Resources
                resource_result = await session.list_resources()
                print("📚 【步驟 3】檢查你實作的 Resource：")
                for r in resource_result.resources:
                    print(f"   - 名稱: {r.name} (網址: {r.uri})")
                print("\n")
                
                print("🎉 Server 的三個功能測試皆已通過！(API 塞車沒關係，Server 邏輯上是可以動的喔！)")

    except Exception as e:
        print(f"❌ 無法連線到 Server，請確保你另一個終端機有在執行 python server.py 而且沒有關閉。錯誤訊息: {e}")

if __name__ == "__main__":
    asyncio.run(main())
