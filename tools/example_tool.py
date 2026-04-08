"""
範例 Tool：取得隨機貓咪冷知識

這是一個範例，展示如何建立 Tool 檔案。
請參考這個格式建立你自己的 Tool。
"""

import requests

# Tool 資訊（給人看的，不影響 MCP）
TOOL_INFO = {
    "name": "get_cat_fact",
    "api": "https://catfact.ninja/fact",
    "author": "範例",
}


def get_cat_fact_data() -> str:
    """呼叫 Cat Facts API，回傳一則貓咪冷知識"""
    resp = requests.get("https://catfact.ninja/fact", timeout=10)
    resp.raise_for_status()
    return resp.json()["fact"]


# 單獨測試
if __name__ == "__main__":
    print(get_cat_fact_data())
