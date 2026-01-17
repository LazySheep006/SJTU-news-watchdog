import os
import sys
import json
import time
import spider
import db_ai
import mailer 

DATA_DIR = "data"
TODAY_JSON = os.path.join(DATA_DIR, "today.json")
NEW_UPDATES_JSON = os.path.join(DATA_DIR, "new_updates.json")

def run_workflow():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    raw_data = spider.run_all_spiders()
    total_count = sum(len(v) for v in raw_data.values())
    with open(TODAY_JSON, "w", encoding="utf-8") as f:
        json.dump(raw_data, f, ensure_ascii=False, indent=2)

    db_ai.main()
    
    if not os.path.exists(NEW_UPDATES_JSON):
        print("[跳过] 未找到增量更新文件，今天可能没有新通知。")
    else:
        with open(NEW_UPDATES_JSON, 'r', encoding='utf-8') as f:
            updates = json.load(f)
            
        if not updates or len(updates) == 0:
            print("[跳过] 增量列表为空，无需发送邮件。")
        else:
            print(f"发现 {len(updates)} 条新通知，开始分发邮件...")
            mailer.send_all_subscribed_emails()
if __name__ == "__main__":
    run_workflow()