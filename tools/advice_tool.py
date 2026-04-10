"""
Tool：旅行前的人生建議
API：https://api.adviceslip.com/advice
"""

import requests

TOOL_INFO = {
    "name": "get_advice",
    "api": "https://api.adviceslip.com/advice",
    "author": "",
}


def get_advice_data() -> str:
    """呼叫 Advice Slip API，回傳一則隨機人生建議"""
    resp = requests.get("https://api.adviceslip.com/advice", timeout=10)
    resp.raise_for_status()
    advice = resp.json()["slip"]["advice"]
    return f"💡 人生建議：{advice}"


# 單獨測試
if __name__ == "__main__":
    print(get_advice_data())
