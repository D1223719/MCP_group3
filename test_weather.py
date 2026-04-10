from tools.weather_tool import get_weather
import sys
import io

# 強制將 stdout 設為 utf-8 避免 Windows 編碼問題
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def test():
    print("正在測試天氣工具，抓取 Taipei 的天氣...")
    try:
        result = get_weather("Taipei")
        print("\n[測試成功] 獲取到的結果如下：\n")
        print(result)
    except Exception as e:
        print(f"\n[測試失敗] {e}")

if __name__ == "__main__":
    test()
