import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def run():
    print("Connecting to FastMCP...")
    try:
        async with sse_client("http://127.0.0.1:8000/sse") as (r, w):
            async with ClientSession(r, w) as session:
                await session.initialize()
                print("Initialized! Calling web_search...")
                res = await session.call_tool("web_search", {"query": "東京景點"})
                print("Result:\n", res.content[0].text)
    except Exception as e:
        print("Error:", e)
        
asyncio.run(run())
