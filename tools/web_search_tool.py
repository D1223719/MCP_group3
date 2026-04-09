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
            return f"🔍 搜尋「{query}」沒有找到相關結果。"

        output = f"🔍 搜尋「{query}」的結果：\n\n"
        for i, r in enumerate(results, 1):
            title = r.get("title", "無標題")
            body = r.get("body", "無摘要")
            href = r.get("href", "")
            output += f"{i}. **{title}**\n   {body}\n   🔗 {href}\n\n"

        return output.strip()
    except Exception as e:
        return f"搜尋時發生錯誤：{str(e)}"


# 單獨測試
if __name__ == "__main__":
    print(web_search_data("台北景點推薦"))
