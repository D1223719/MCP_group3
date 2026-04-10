"""
W8 分組實作：MCP Server
主題：旅遊顧問 MCP Server (純搜尋美食、景點版)
"""

from mcp.server.fastmcp import FastMCP
from tools.weather_tool import get_weather

# 匯入各 Tool 的資料取得函式
from tools.web_search_tool import web_search_data

mcp = FastMCP("旅遊顧問-server")
mcp = FastMCP("travel-advisor")


# ════════════════════════════════
#  Tools：核心搜尋工具
# ════════════════════════════════

# 把你的函式包裝成 MCP Tool
@mcp.tool()
def fetch_weather(city: str) -> str:
    # 直接呼叫剛剛寫好的邏輯
    return get_weather(city)


@mcp.tool()
def web_search(query: str) -> str:
    """搜尋景點、美食等旅遊資訊。
    當使用者想查詢特定地點的景點推薦、美食餐廳、旅遊攻略時使用。
    例如：「台北美食推薦」、「京都必去景點」、「花蓮好吃的」。"""
    return web_search_data(query)


# ════════════════════════════════
#  Resource：提供靜態參考資料
#  URI 格式：info://名稱
# ════════════════════════════════

@mcp.resource("info://travel-tips")
def get_travel_tips() -> str:
    """旅行必帶物品與注意事項清單"""
    return (
        "找尋美食與景點的小提示：\n"
        "- 輸入具體的地區與食物種類（如：台南 牛肉湯 推薦）能找到更精確的結果！\n"
        "- 搜尋景點時可以加上『必去』或『私房景點』等關鍵字哦！"
    )


# ════════════════════════════════
#  Prompt：整合多個 Tool 的提示詞模板
#  使用者透過 /use <名稱> [參數] 呼叫
# ════════════════════════════════

@mcp.prompt()
def search_local(city: str) -> str:
    """產生當地美食與景點探索的提示詞"""
    return (
        f"我想到 {city} 去走走。請幫我搜尋並整理出：\n"
        f"1. {city} 3個必吃的在地美食推薦\n"
        f"2. {city} 2個熱門的旅遊景點\n"
        f"請你一定要使用 web_search 工具來查詢最新的推薦名單，然後用生動活潑的語氣回覆我！"
    )


if __name__ == "__main__":
    print("MCP Server (純搜尋版) 啟動中... http://localhost:8000")
    mcp.run(transport="sse")
