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
