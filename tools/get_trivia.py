# -*- coding: utf-8 -*-
"""
旅途知識問答 Tool：使用 Open Trivia Database API

功能：
- 從 OpenTDB API 取得隨機知識問答題
- 支援指定題目數量（預設 1 題）
- 支援指定類別與難度篩選
- 回傳問題、選項與正確答案
"""

import html
import random
import sys
import requests

# Windows 終端機 UTF-8 輸出支援
if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Tool 資訊（給人看的，不影響 MCP）
TOOL_INFO = {
    "name": "get_trivia",
    "api": "https://opentdb.com/api.php",
    "author": "D1245806",
}

# OpenTDB API 難度對應
DIFFICULTY_MAP = {
    "easy": "easy",
    "medium": "medium",
    "hard": "hard",
    "簡單": "easy",
    "中等": "medium",
    "困難": "hard",
}


def get_trivia_data(amount: int = 1, difficulty: str = "") -> list[dict]:
    """
    呼叫 OpenTDB API，取得知識問答題目。

    Args:
        amount: 題目數量（1~10，預設 1）
        difficulty: 難度，可選 'easy'、'medium'、'hard'（預設不限）

    Returns:
        題目清單，每題包含 question、options、answer、category、difficulty
    """
    amount = max(1, min(amount, 10))  # 限制 1~10 題

    params = {
        "amount": amount,
        "type": "multiple",  # 四選一選擇題
    }

    # 處理難度參數（支援中英文）
    difficulty_lower = difficulty.lower().strip()
    if difficulty_lower in DIFFICULTY_MAP:
        params["difficulty"] = DIFFICULTY_MAP[difficulty_lower]

    resp = requests.get("https://opentdb.com/api.php", params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if data["response_code"] != 0:
        raise ValueError(f"OpenTDB API 回傳錯誤，response_code={data['response_code']}")

    results = []
    for item in data["results"]:
        # HTML entity decode（API 回傳的文字含 HTML 編碼）
        question = html.unescape(item["question"])
        correct = html.unescape(item["correct_answer"])
        incorrect = [html.unescape(a) for a in item["incorrect_answers"]]

        # 將所有選項混合並隨機排序
        options = incorrect + [correct]
        random.shuffle(options)

        results.append({
            "category": html.unescape(item["category"]),
            "difficulty": item["difficulty"],
            "question": question,
            "options": options,
            "answer": correct,
        })

    return results


def format_trivia(amount: int = 1, difficulty: str = "") -> str:
    """
    取得並格式化知識問答題，回傳易讀的文字。

    Args:
        amount: 題目數量（1~10，預設 1）
        difficulty: 難度篩選，可選 easy / medium / hard / 簡單 / 中等 / 困難

    Returns:
        格式化後的問答題字串，包含選項與正確答案
    """
    try:
        trivia_list = get_trivia_data(amount=amount, difficulty=difficulty)
    except requests.exceptions.Timeout:
        return "[Error] 請求逾時，請稍後再試。"
    except requests.exceptions.ConnectionError:
        return "[Error] 無法連線至 OpenTDB，請確認網路狀態。"
    except ValueError as e:
        return f"[Error] {e}"

    option_labels = ["A", "B", "C", "D"]
    output_lines = [f"[Trivia] 旅途知識問答（共 {len(trivia_list)} 題）\n"]

    for i, trivia in enumerate(trivia_list, start=1):
        difficulty_label = {
            "easy": "[Easy] 簡單",
            "medium": "[Medium] 中等",
            "hard": "[Hard] 困難",
        }.get(trivia["difficulty"], trivia["difficulty"])

        output_lines.append(f"-- 第 {i} 題 ---------------------------")
        output_lines.append(f"類別：{trivia['category']}")
        output_lines.append(f"難度：{difficulty_label}")
        output_lines.append(f"問題：{trivia['question']}\n")

        for label, option in zip(option_labels, trivia["options"]):
            output_lines.append(f"   {label}. {option}")

        output_lines.append(f"\n正確答案：{trivia['answer']}\n")

    return "\n".join(output_lines)


# 單獨測試
if __name__ == "__main__":
    print(format_trivia(amount=3, difficulty="medium"))
