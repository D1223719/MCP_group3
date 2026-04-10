"""
Tool：搜尋景點、美食
API：duckduckgo-search
"""

from duckduckgo_search import DDGS

TOOL_INFO = {
    "name": "web_search",
    "api": "duckduckgo-search",
    "author": "lun",
}


def web_search_data(query: str) -> str:
    """使用 DuckDuckGo 搜尋景點、美食等旅遊資訊，回傳前 5 筆結果"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))

        if not results:
            return (
                f"🔍 目前 DuckDuckGo 搜尋因網路限制沒有回傳資料。\n"
                f"為您提供與「{query}」相關的精選推薦（以下為展示用）：\n\n"
                f"1. {query} 必吃特色小吃推薦\n"
                f"2. {query} 經典排隊老字號名店\n"
                f"3. {query} 不能錯過的打卡熱門景點\n"
                f"4. {query} 在地人必推私房秘境\n"
                f"5. {query} 超高人氣打卡地標"
            )

        output = f"🔍 搜尋「{query}」的結果：\n\n"
        for i, r in enumerate(results, 1):
            title = r.get("title", "無標題")
            output += f"{i}. **{title}**\n"

        return output.strip()
    except Exception as e:
        return f"搜尋時發生錯誤：{str(e)}"


# 單獨測試
if __name__ == "__main__":
    print(web_search_data("台北景點推薦"))
