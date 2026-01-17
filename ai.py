import json
import time
import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

GITHUB_TOKEN = os.environ["SJTU_new"]

ENDPOINT = "https://models.github.ai/inference"

MODEL_NAME = "openai/gpt-4.1-mini"

# MODEL_NAME = "deepseek/DeepSeek-V3-0324" #这个有速率限制 很慢，但是效果好

client = ChatCompletionsClient(
    endpoint=ENDPOINT,
    credential=AzureKeyCredential(GITHUB_TOKEN),
)

INPUT_FILE = "data/today.json"
OUTPUT_FILE = "data/today_ai_summary.json"

def build_messages(title, content):
    system_text = """
你是一名上海交通大学本科生的智能学业助手。
请根据用户提供的【标题】和【正文】，执行严格的逻辑判断和总结。

【任务指令】：
1. 身份过滤：
   - 如果通知受众明确且仅限于“研究生”、“硕士生”、“博士生”，不涉及本科生，直接输出唯一标签：<graduate>
   - 只有面向本科生，才进入下一步。

2. 智能总结：
   - 用中文为本科生生成150字以内摘要。
   - 必须包含以下几点,如果没有请忽略：
     1. 截止时间 (要用markdown格式的粗体)
     2. 地点/方式 (要用markdown格式的粗体)
     3. 对面需要做什么(如报名/参加)
     4. 如果有重要的联系邮箱，请放出来 (要用markdown格式的粗体)
   - 如果原文出现 [图片: http...]这样的格式的。请保留完整链接并写出提示是图片。
   - 遇无正文或权限保护，提示点击标题跳转。
   - 遇附件，在最后写”附件下载链接将附在最后，请查收“。

3. 输出格式：
   - 直接输出总结内容或 <graduate>，不要输出“好的”等废话。
   - 禁止使用其他的markdown语法。适当分段(保留'\n')。
   - 使用纯文本列表，不要使用Emoji

4. 输出语气：
    - 你是一个和蔼的助人为乐的学业助手，语言简洁明了，富有亲和力。同时不失重点
"""
    user_text = f"【标题】：{title}\n【正文】：\n{content}"

    return [
        SystemMessage(content=system_text),
        UserMessage(content=user_text),
    ]

def get_ai_summary(title, content):
    if len(content) < 50 and "图片" not in content:
        return content 
    
    try:
        messages_objects = build_messages(title, content)

        response = client.complete(
            messages=messages_objects,
            temperature=0.3, 
            top_p=1.0,
            max_tokens=1000,
            model=MODEL_NAME
        )
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"GitHub调用失败: {e}")
        return None

def main():
    print(f"[System] AI 模块启动 (Model: {MODEL_NAME})...")
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

            print(f"[分析] {title[:15]}...", end="", flush=True)
            
            summary = get_ai_summary(title, content)
            
            if summary:
                if "<graduate>" in summary:
                    print("->[研究生通知]")
                    item["summary"] = "<graduate>" 
                    graduate_count += 1
                    print(summary)
                else:
                    print(" -> [完成]")
                    item["summary"] = summary
                    print(summary)
            else:
                print("->[失败]")
                item["summary"] = "AI 暂时无法响应"

            processed_count += 1
            time.sleep(4) 

    print(f"全部完成！共处理 {processed_count} 条 (研究生通知 {graduate_count} 条)")
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"保存至 {OUTPUT_FILE}")

if __name__ == "__main__":
    main()