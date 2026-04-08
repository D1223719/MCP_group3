# MCP Server + AI agent 分組實作

> 課程：AI Agent 開發 — MCP（Model Context Protocol）
> 主題：（填入你們選的主題）

---

## Server 功能總覽

> 說明這個 MCP Server 提供哪些 Tool

| Tool 名稱                 | 功能說明     | 負責組員 |
| ------------------------- | ------------ | -------- |
| （範例：`get_weather`） | 查詢即時天氣 |          |
|                           |              |          |
|                           |              |          |

---

## 組員與分工

| 姓名 | 負責功能            | 檔案          | 使用的 API |
| ---- | ------------------- | ------------- | ---------- |
|      |                     | `tools/`    |            |
|      |                     | `tools/`    |            |
|      |                     | `tools/`    |            |
|      | Resource + Prompt   | `server.py` | —         |
|      | Agent（用 AI 產生） | `agent.py`  | Gemini API |

---

## 專案架構

```
├── server.py              # MCP Server 主程式
├── agent.py               # MCP Client + Gemini Agent（用 AI 產生）
├── tools/
│   ├── __init__.py
│   ├── example_tool.py    # 範例（可刪除）
│   ├── xxx_tool.py        # 組員 A 的 Tool
│   ├── xxx_tool.py        # 組員 B 的 Tool
│   └── xxx_tool.py        # 組員 C 的 Tool
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

### Agent 對話截圖

> 貼上 Agent 對話的截圖（顯示 Gemini 呼叫 Tool 的過程，以及使用 /use 呼叫 Prompt 的結果）

---

## 各 Tool 說明

### `tool_name`（負責：姓名）

- **功能**：
- **使用 API**：
- **參數**：
- **回傳範例**：

```python
@mcp.tool()
def tool_name(param: str) -> str:
    """Tool 的 docstring（這就是 AI 看到的描述）"""
    ...
```

### `tool_name`（負責：姓名）

- **功能**：
- **使用 API**：
- **參數**：
- **回傳範例**：

### `tool_name`（負責：姓名）

- **功能**：
- **使用 API**：
- **參數**：
- **回傳範例**：

---

## 心得

### 遇到最難的問題

> 寫下這次實作遇到最困難的事，以及怎麼解決的

### MCP 跟上週的 Tool Calling 有什麼不同？

> 用自己的話說說，做完後你覺得 MCP 的好處是什麼
