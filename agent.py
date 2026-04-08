"""
W8 分組實作：MCP Client + Gemini Agent

這個檔案用 AI 產生。請把以下設計指令貼給你的 AI 工具（Copilot / Antigravity），
讓它幫你產生完整的程式碼：

────────────────────────────────────────────
設計指令（複製貼給 AI）：

幫我寫一個 Python Agent，需求如下：

1. 用 MCP SSE Client 連接到 http://localhost:8000/sse
   （server.py 已在另一個終端機獨立執行）
2. 連接後，自動取得 Server 提供的所有工具清單（list_tools）
3. 把工具清單轉換成 Gemini API 的 function declaration 格式
4. 使用 Gemini 2.0 Flash（免費版），進行多輪對話
5. 當 Gemini 回傳 function_call 時：
   - 透過 MCP call_tool 呼叫對應的 Tool
   - 把結果送回 Gemini 繼續對話
6. 當 Gemini 回傳文字時，直接顯示給使用者
7. 需要的套件：google-genai、mcp、python-dotenv
8. API Key 從 .env 的 GEMINI_API_KEY 讀取
9. 用 asyncio 執行（因為 MCP Client 是非同步的）
10. 加上 debug 輸出，顯示 Agent 呼叫了哪個工具和結果

MCP SSE Client 的連接方式：
from mcp.client.sse import sse_client
async with sse_client("http://localhost:8000/sse") as (read, write):
    ...
────────────────────────────────────────────

啟動方式：
  終端機 1：python server.py   （先啟動 Server）
  終端機 2：python agent.py    （再啟動 Agent）
"""

# TODO：把上面的設計指令貼給 AI，用產生的程式碼取代這段
print("請用 AI 產生這個檔案的程式碼。設計指令在檔案上方的註解中。")
