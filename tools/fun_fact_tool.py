"""
Tool：旅途趣味冷知識
API：https://uselessfacts.jsph.pl/api/v2/facts/random
"""

import requests

TOOL_INFO = {
    "name": "get_fun_fact",
    "api": "https://uselessfacts.jsph.pl/api/v2/facts/random",
    "author": "",
}


def get_fun_fact_data() -> str:
    """呼叫 Useless Facts API，回傳一則隨機趣味冷知識"""
    resp = requests.get(
        "https://uselessfacts.jsph.pl/api/v2/facts/random",
        timeout=10,
    )
    resp.raise_for_status()
    fact = resp.json()["text"]
    return f"🧠 趣味冷知識：{fact}"


# 單獨測試
if __name__ == "__main__":
    print(get_fun_fact_data())
