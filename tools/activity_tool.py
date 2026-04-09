"""
Tool：推薦活動
API：https://bored-api.appbrewery.com/random
"""

import requests

TOOL_INFO = {
    "name": "get_activity",
    "api": "https://bored-api.appbrewery.com/random",
    "author": "",
}


def get_activity_data() -> str:
    """呼叫 Bored API，回傳一項隨機推薦活動"""
    resp = requests.get("https://bored-api.appbrewery.com/random", timeout=10)
    resp.raise_for_status()
    data = resp.json()

    activity = data.get("activity", "未知活動")
    act_type = data.get("type", "未知")
    participants = data.get("participants", "?")

    return (
        f"🎯 推薦活動：{activity}\n"
        f"  📂 類型：{act_type}\n"
        f"  👥 適合人數：{participants}"
    )


# 單獨測試
if __name__ == "__main__":
    print(get_activity_data())
