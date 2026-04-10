"""
Tool：查詢目的地天氣
API：https://wttr.in/{city}?format=j1
"""

import requests

TOOL_INFO = {
    "name": "get_weather",
    "api": "https://wttr.in/{city}?format=j1",
    "author": "",
}


def get_weather_data(city: str) -> str:
    """呼叫 wttr.in API，回傳指定城市的即時天氣資訊"""
    url = f"https://wttr.in/{city}?format=j1"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    current = data["current_condition"][0]
    temp_c = current["temp_C"]
    feels_like = current["FeelsLikeC"]
    humidity = current["humidity"]
    desc = current["weatherDesc"][0]["value"]
    wind_speed = current["windspeedKmph"]
    uv_index = current["uvIndex"]

    return (
        f"🌍 {city} 即時天氣：\n"
        f"  🌡️ 溫度：{temp_c}°C（體感 {feels_like}°C）\n"
        f"  ☁️ 天氣狀況：{desc}\n"
        f"  💧 濕度：{humidity}%\n"
        f"  🌬️ 風速：{wind_speed} km/h\n"
        f"  ☀️ 紫外線指數：{uv_index}"
    )


# 單獨測試
if __name__ == "__main__":
    print(get_weather_data("Taipei"))
import requests

def get_weather(city: str) -> str:
    """
    取得指定城市的即時天氣資訊，包含溫度、體感溫度和天氣狀況。
    當使用者詢問目的地天氣、是否該帶雨傘或適合穿什麼衣服時使用。
    """
    url = f"https://wttr.in/{city}?format=j1"
    
    # 發送請求獲取 JSON 資料
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    
    # 提取當前天氣狀況
    current = data["current_condition"][0]
    temp_c = current['temp_C']
    feels_like = current['FeelsLikeC']
    desc = current['weatherDesc'][0]['value']
    
    return (
        f"{city} 的天氣狀況：\n"
        f"- 目前溫度：{temp_c}°C\n"
        f"- 體感溫度：{feels_like}°C\n"
        f"- 天氣描述：{desc}"
    )
