"""
Tool：景點與美食搜尋
API：duckduckgo-search
"""

from duckduckgo_search import DDGS

TOOL_INFO = {
    "name": "search_travel_info",
    "api": "duckduckgo-search",
    "author": "",
}


def search_travel_info(query: str, max_results: int = 5) -> str:
    """
    使用 DuckDuckGo 搜尋景點或美食資訊。
    
    Args:
        query (str): 搜尋關鍵字，例如 "台北 景點" 或 "台南 美食"。
        max_results (int): 最多回傳幾筆資料，預設為 5 筆。
    
    Returns:
        str: 搜尋結果的彙整字串。
    """
    try:
        with DDGS() as ddgs:
            # 取得搜尋結果
            results = list(ddgs.text(query, max_results=max_results))
            
        if not results:
            return f"找不到關於「{query}」的相關資訊。"
            
        response = f"🔍 關於「{query}」的搜尋結果（取前 {len(results)} 筆）：\n"
        for i, res in enumerate(results, 1):
            title = res.get('title', '無標題')
            body = res.get('body', '無摘要')
            href = res.get('href', '')
            response += f"\n{i}. {title}\n   摘要：{body}\n   參考連結：{href}\n"
            
        return response
    except Exception as e:
        return f"搜尋過程中發生錯誤：{str(e)}"

# 單獨測試
if __name__ == "__main__":
    print("=== 測試景點搜尋 ===")
    print(search_travel_info("台北 信義區 景點", max_results=3))
    print("\n=== 測試美食搜尋 ===")
    print(search_travel_info("台南 國華街 美食", max_results=3))
