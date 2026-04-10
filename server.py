"""
W8 分組實作：MCP Server
主題：旅遊顧問 MCP Server (純搜尋美食、景點版)
"""

from mcp.server.fastmcp import FastMCP

# 匯入各 Tool 的資料取得函式
from tools.weather_tool import get_weather
from tools.web_search_tool import web_search_data
from tools.travel_search_tool import search_travel_info
from tools.get_trivia import format_trivia


# 初始化單一 FastMCP 實例
mcp = FastMCP("travel-advisor")


# ════════════════════════════════
#  Tools：核心搜尋與輔助工具
# ════════════════════════════════

@mcp.tool()
def fetch_weather(city: str) -> str:
    """取得指定城市的即時天氣資訊。當使用者詢問天氣、溫度、是否該帶傘時使用。"""
    return get_weather(city)

@mcp.tool()
def web_search(query: str) -> str:
    """搜尋景點、美食等旅遊資訊。
    當使用者想查詢特定地點的景點推薦、美食餐廳、旅遊攻略時使用。
    例如：「台北美食推薦」、「京都必去景點」、「花蓮好吃的」。"""
    return web_search_data(query)

@mcp.tool()
def travel_search(query: str, max_results: int = 5) -> str:
    """進階旅遊與美食搜尋，可指定回傳數量。"""
    return search_travel_info(query, max_results)

@mcp.tool()
def travel_trivia(amount: int = 1, difficulty: str = "") -> str:
    """取得旅途知識問答題，增加旅途趣味。
    可指定數量 (amount，1~10) 與難度 (difficulty：easy, medium, hard)。"""
    return format_trivia(amount, difficulty)



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

@mcp.resource("info://weather-guide")
def get_weather_guide() -> str:
    """行前天氣與穿搭指標指南"""
    return (
        "天氣與穿搭建議指標：\n"
        "- 10度以下：極度寒冷，建議羽絨衣、圍巾、毛帽、手套全副武裝。\n"
        "- 10~15度：寒冷，建議厚外套、毛衣、發熱衣。\n"
        "- 15~20度：初秋微涼，建議薄外套、長袖上衣、洋蔥式穿搭。\n"
        "- 20~25度：舒適溫暖，建議短袖或薄長袖，早晚可帶薄外套。\n"
        "- 25度以上：炎熱，建議短袖、防曬衣物、墨鏡並多補充水分。"
    )

@mcp.resource("info://trivia-rules")
def get_trivia_rules() -> str:
    """旅途知識問答玩法說明"""
    return (
        "旅途知識問答 (Travel Trivia) 規則說明：\n"
        "- 透過 travel_trivia 工具可以呼叫題庫來消磨搭車時間。\n"
        "- 參數 amount：限制為 1~10 題。\n"
        "- 參數 difficulty：可選 easy, medium, hard。\n"
        "- 建議讓系統列出選項讓你猜，猜對後再給詳細解答，增加互動感！"
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
        f"3. {city} 的天氣狀況以及穿搭建議\n"
        f"請你盡量使用 web_search 與 fetch_weather 等工具來查詢豐富的行程資訊，然後用生動活潑的語氣回覆我！"
    )

@mcp.prompt()
def weather_check(city: str) -> str:
    """產生查詢當地天氣並給予穿搭建議的提示詞"""
    return (
        f"我即將前往 {city} 旅行。請幫我呼叫 fetch_weather 查詢 {city} 的即時天氣。\n"
        f"另外，請你模擬一位貼心的天氣預報員，根據氣溫給我具體的穿搭與攜帶物品建議！"
    )

@mcp.prompt()
def play_trivia(amount: int = 3, difficulty: str = "medium") -> str:
    """產生開啟旅途問答遊戲的提示詞"""
    return (
        f"我們在長途搭車有點無聊，來玩點知識問答吧！\n"
        f"請幫我用 travel_trivia 工具生成 {amount} 題難度為 {difficulty} 的題目。\n"
        f"請不要直接告訴我答案，把題目跟 4 個選項列出來讓我猜，等我回答後再跟我說對不對！"
    )


if __name__ == "__main__":
    print("MCP Server (旅遊顧問整合版) 啟動中... http://localhost:8000")
    mcp.run(transport="sse")
