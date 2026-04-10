import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()

print("你的 API 金鑰支援的可用模型清單：")
for m in client.models.list():
    print(m.name)
    
