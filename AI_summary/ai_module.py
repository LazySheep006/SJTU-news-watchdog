import json
import time
import os
from openai import OpenAI

MODELSCOPE_TOKEN = "ms-7fcc3cf4-001e-4d98-ab31-32fdb3028ffc"

client = OpenAI(
    base_url="https://api-inference.modelscope.cn/v1",
    api_key=MODELSCOPE_TOKEN
)

MODEL_NAME = "Qwen/Qwen2.5-72B-Instruct"

INPUT_FILE = "all_notices.json"
OUTPUT_FILE = "all_notices_ai.json"

def build_messages(title, content):
    system_content = """
你是一名上海交通大学本科生的智能学业助手。
请根据用户提供的【标题】和【正文】，执行严格的逻辑判断和总结。

【任务指令】：
1. 身份过滤：
   - 如果通知受众明确且仅限于“研究生”、“硕士生”、“博士生”，不涉及本科生，直接输出唯一标签：<graduate>
   - 否则，进入下一步。

2. 智能总结：
   - 用中文为本科生生成200字以内摘要。
   - 必须包含以下几点（如果有）：时间，地点/方式，学生核心行动(如需要报名/参加的方式)
   - 如果原文出现`[图片 xxx的链接]`这种格式请保留完整链接并提醒是图片放到对应位置（其他链接就放对应位置）
   - 如果原文出现问卷链接，请放在总结文中
   - 遇无正文或权限保护，提示点击链接跳转。
   - 遇附件，提醒附在最后。

3. 输出格式：
   - 禁用markdown
   - 直接输出总结内容或 <graduate>，不要输出废话。
"""
    user_content = f"【标题】：{title}\n【正文】：\n{content}"
    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": user_content}
    ]

def get_ai_summary(title, content):
    if len(content) < 50 and "图片" not in content:
        return content 
    
    messages = build_messages(title, content)

    # 尝试调用 ModelScope
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.3, # 低温度保持严谨
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"Qwen调用失败: {e}")
        return None

def main():
    print(f"AI 模块启动 (Model: {MODEL_NAME})...")
    
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    processed_count = 0
    graduate_count = 0

    for school, items in data.items():
        print(f"\n[处理中] {school} ({len(items)} 条)")
        
        for item in items:
            title = item.get("title", "")
            content = item.get("content", "")
            
            if "summary" in item and item["summary"]:
                continue

            print(f"  [分析] {title[:15]}...", end="", flush=True)
            
            summary = get_ai_summary(title, content)
            
            if summary:
                if "<graduate>" in summary:
                    print(" -> [研究生通知]")
                    item["summary"] = "<graduate>" 
                    graduate_count += 1
                else:
                    print(" -> [完成]")
                    item["summary"] = summary
                    print(summary)
            else:
                print(" -> [失败]")
                item["summary"] = "AI 暂时无法响应"

            processed_count += 1
            
            time.sleep(1) 

    print(f"全部完成！共处理 {processed_count} 条 (研究生通知 {graduate_count} 条)")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"保存至 {OUTPUT_FILE}")

if __name__ == "__main__":
    main()