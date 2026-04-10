import asyncio
import os
import sys
import traceback
from dotenv import load_dotenv

# 強制將輸入/輸出流設定為 utf-8 (較安全且相容性高的寫法)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding='utf-8')
from mcp import ClientSession
from mcp.client.sse import sse_client
from google import genai
from google.genai import types

# 讀取 .env 中的環境變數
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

async def main():
    if not GEMINI_API_KEY:
        print("[錯誤] 找不到 GEMINI_API_KEY，請確認 .env 檔案是否已經設定。")
        return

    # 1. 初始化 Gemini 客戶端
    ai_client = genai.Client(api_key=GEMINI_API_KEY)
    
    print("正在連接到 MCP Server (http://localhost:8000/sse)...")
    
    try:
        # 2. 使用 SSE 連接到 MCP Server
        async with sse_client("http://localhost:8000/sse") as (read, write):
            async with ClientSession(read, write) as session:
                # 必須先初始化 MCP session
                await session.initialize()
                
                # 3. 取得 Server 提供的所有工具
                tools_response = await session.list_tools()
                mcp_tools = tools_response.tools
                
                print(f"[成功] 共取得 {len(mcp_tools)} 個工具。")
                
                # 4. 將 MCP 格式的 Tools 轉換成 Gemini API 的 function declarations 格式
                gemini_tools = []
                for t in mcp_tools:
                    gemini_tools.append(
                        types.Tool(
                            function_declarations=[
                                types.FunctionDeclaration(
                                    name=t.name,
                                    description=t.description,
                                    parameters=t.inputSchema
                                )
                            ]
                        )
                    )

                # 5. 開啟與 Gemini 的對話 (使用 Gemini 2.5 Flash 避開舊版 2.0 的免費額度卡關)
                chat = ai_client.chats.create(
                    model="gemini-2.5-flash",
                    config=types.GenerateContentConfig(
                        tools=gemini_tools,
                        temperature=0.7,
                    )
                )

                print("\n=======================================================")
                print("聊天開始 (輸入 'exit' 或 'quit' 離開)")
                print("你可以試著問：請告訴我今天台北的天氣，該帶傘嗎？")
                print("=======================================================\n")
                
                while True:
                    user_input = input("你：")
                    if user_input.lower() in ['exit', 'quit']:
                        print("掰掰！")
                        break
                        
                    if not user_input.strip():
                        continue

                    try:
                        # 傳送使用者訊息
                        response = chat.send_message(user_input)
                        
                        # 6. 當 Gemini 回傳 function_call 時 (代表它想要呼叫外部工具)
                        while response.function_calls:
                            for fn_call in response.function_calls:
                                tool_name = fn_call.name
                                tool_args = fn_call.args
                                
                                print(f"\n[DEBUG] Gemini 決定呼叫工具：{tool_name}")
                                print(f"[DEBUG] 傳入參數：{tool_args}")
                                
                                # 透過 MCP call_tool 呼叫對應的 Tool
                                tool_result = await session.call_tool(tool_name, tool_args)
                                
                                # 取得工具回傳內容
                                result_text = tool_result.content[0].text if tool_result.content else "無回傳內容"
                                print(f"[DEBUG] 工具回傳結果長度：{len(result_text)} 字\n")
                                
                                # 將結果送回給 Gemini 繼續對話
                                response = chat.send_message(
                                    types.Part.from_function_response(
                                        name=tool_name,
                                        response={"result": result_text}
                                    )
                                )
                        
                        # 7. 當 Gemini 回傳文字時，直接顯示給使用者
                        if response.text:
                            print(f"Gemini：{response.text}\n")
                            
                    except Exception as e:
                        print(f"\n[錯誤] 發生例外：{e}")
                        traceback.print_exc()
                        print("\n")
                        
    except Exception as server_err:
        print(f"連接 Server 失敗，請確認你的 server.py 是否已經在另一個終端機啟動！\n錯誤訊息：{server_err}")


if __name__ == "__main__":
    asyncio.run(main())
