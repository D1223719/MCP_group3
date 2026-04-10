# MCP Server + AI agent 分組實作

> 課程：AI Agent 開發 — MCP（Model Context Protocol）
> 主題：旅遊顧問 MCP Server (純搜尋美食、景點版)

---

## Server 功能總覽

> 這是整合天氣提醒、旅遊知識問答與景點美食搜尋的旅遊顧問 Server。提供下列 Tool：

| Tool 名稱                 | 功能說明            | 負責組員 |
| ------------------------- | ------------------- | -------- |
| `tools/weather_tool.py`       | 查詢指定城市即時天氣 |  辛晴        |
| `tools/travel_search_tool.py`    | 搜尋景點、美食等資訊 | 蔡秉倫  |
|`tools/get_trivia.py`   | 取得旅途知識問答題   |  楊永蘭 |

---
## 組員與分工

| 姓名 | 負責功能            | 檔案          | 使用的 API |
| ---- | ------------------- | ------------- | ---------- |
| 辛晴  | 查詢指定城市即時天氣 | `tools/weather_tool.py`       | wttr.in API       |
| 蔡秉倫 |  搜尋景點、美食等資訊 | `tools/travel_search_tool.py` | DuckDuckGo API    |
| 楊永蘭 |  取得旅途知識問答題   | `tools/get_trivia.py`         | OpenTDB API       |
| 黃國傑 | Resource + Prompt   | `server.py` | Gemini API |
| 黃國傑 | Agent（用 AI 產生） | `agent.py`  | Gemini API |

---

## 專案架構

```
├── server.py              # MCP Server 主程式
├── agent.py               # MCP Client + Gemini Agent（用 AI 產生）
├── tools/
│   ├── __init__.py
│   ├── weather_tool.py    # 查詢天氣的 Tool
│   ├── web_search_tool.py # 景點/美食搜尋 Tool
│   ├── travel_search_tool.py # 進階美食/景點搜尋 Tool
│   └── get_trivia.py      # 旅途知識問答 Tool
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 使用方式

```bash
# 1. 建立虛擬環境
python3 -m venv .venv
source .venv/bin/activate

# 2. 安裝依賴
pip install -r requirements.txt

# 3. 設定 API Key
cp .env.example .env
# 編輯 .env，填入你的 GEMINI_API_KEY

# 4. 用 MCP Inspector 測試 Server
mcp dev server.py

# 5. 用 Agent 對話
python agent.py
```

---

## 測試結果

### MCP Inspector 截圖

> 貼上 Inspector 的截圖（Tools / Resources / Prompts 三個分頁都要有）
> <img width="1914" height="963" alt="image" src="https://github.com/user-attachments/assets/a7d4bbb3-166b-4be8-8078-24237e3938ec" />
> <img width="1905" height="964" alt="image" src="https://github.com/user-attachments/assets/d931481b-c6f0-4b76-ab1e-dd90ac7e6447" />
<img width="1498" height="595" alt="image" src="https://github.com/user-attachments/assets/82c14fae-fb28-4032-bc08-9ca3469d0b63" />
<img width="708" height="532" alt="image" src="https://github.com/user-attachments/assets/cbc62e04-55ba-4151-a252-7a06fffb0829" />
<img width="708" height="532" alt="image" src="https://github.com/user-attachments/assets/c0bb9d21-34b1-42da-9a0f-adf4e06fc05e" />


### Agent 對話截圖

> 貼上 Agent 對話的截圖（顯示 Gemini 呼叫 Tool 的過程，以及使用 /use 呼叫 Prompt 的結果）
<img width="468" height="737" alt="image" src="https://github.com/user-attachments/assets/e22b30fd-2d4e-4a6a-a249-089f85c0efc0" />
<img width="747" height="522" alt="image" src="https://github.com/user-attachments/assets/23932b73-29cb-418b-bc85-46768c2254b6" />

---

## 各 Tool 說明

### `fetch_weather`（負責：辛晴）

- **功能**：取得指定城市的即時天氣資訊，包含溫度、體感溫度和天氣狀況。當使用者詢問天氣、溫度、是否該帶傘時使用。
- **使用 API**：https://wttr.in/{city}?format=j1
- **參數**：`city` (字串型態) - 目標城市名稱，如 "Taipei"。
- **回傳範例**：
```text
🌍 Taipei 即時天氣：
  🌡️ 溫度：25°C（體感 26°C）
  ☁️ 天氣狀況：Partly cloudy
```

---

### `web_search`（負責：蔡秉倫）

- **功能**：使用 DuckDuckGo 搜尋景點、美食等旅遊資訊，回傳前 5 筆結果。當查詢特定地區景點或推薦美食時使用。
- **使用 API**：duckduckgo-search 套件
- **參數**：`query` (字串型態) - 搜尋關鍵字，例如 "台北美食推薦"。
- **回傳範例**：
```text
🔍 搜尋「台北美食推薦」的結果：

1. **台北美食總整理**
2. **2026必吃在地小吃**


---
```
### `travel_trivia`（負責：楊永蘭）

- **功能**：取得隨機的旅途知識問答題（四選一），增加旅途趣味，提供長途搭車時娛樂。
- **使用 API**：Open Trivia Database (https://opentdb.com/api.php)
- **參數**：
  - `amount` (整數) - 題目數量，限制 1~10 題。
  - `difficulty` (字串) - 題目難易度，支援 easy, medium, hard。
- **回傳範例**：
```text
[Trivia] 旅途知識問答（共 3 題）

-- 第 1 題 ---------------------------
類別：Geography
難度：[Easy] 簡單
問題：What is the capital of Japan?

   A. Beijing
   B. Seoul
   C. Bangkok
   D. Tokyo

正確答案：Tokyo
```

---

## 心得

### 遇到最難的問題

> 在實作中遇到最難的問題是連線 Gemini API 時經常遇到 "429 RESOURCE_EXHAUSTED" 的配額問題，需要準備額度充分的 API Key。另外，在 Windows 環境下使用 Python 終端機進行中文對話時，當輸入中文字串傳遞到底層網路模組 `httpx` 會因為預設編碼並未轉碼而拋出 `UnicodeEncodeError (surrogates not allowed)`。後來經過摸索，發現只要在主程式 (`agent.py`) 最前端加入 `sys.stdin.reconfigure(encoding='utf-8')`，就可以確保終端機捕捉中文輸入時採用正確編碼，順利解決報錯。

### MCP 跟上週的 Tool Calling 有什麼不同？

> MCP 的好處在於將 Tool 的開發實作與 Agent 模型「完全解耦」。以前上週寫的 Tool Calling 必須將函式直接寫在 Agent 所在的同一個專案或模組裡；現在透過 MCP，我們可以把功能獨立發布成一個伺服器。不僅所有語言皆能互通，甚至未來這套開發好的 Server 換成別家的大型語言模型（比如 Claude）也都能無縫接軌使用，無需修改任何一行旅遊搜尋或天氣查詢的原始碼。這讓工具的維護、發布與擴充性變得非常強大。

