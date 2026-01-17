import json
import time
import os
from database import init_db, is_url_exists, save_notice
from ai import get_ai_summary 

INPUT_FILE = "data/today.json"        
CACHE_FILE = "data/today_ai_summary.json"  
FINAL_OUTPUT_FILE = "data/today_ai_summary.json"
NEW_UPDATES_FILE = "data/new_updates.json"      

def load_summary_cache():
    print("[系统] 正在加载本地缓存...")
    if not os.path.exists(CACHE_FILE):
        return {}
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        cache = {}
        for school, items in data.items():
            for item in items:
                url = item.get("url")
                summary = item.get("summary")
                if url and summary and "AI 暂时无法响应" not in summary:
                    cache[url] = summary
        return cache
    except Exception as e:
        print(f"[警告] 加载缓存失败: {e}")
        return {}

def main():
    init_db()
    summary_cache = load_summary_cache()
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    new_ai_count = 0
    skip_count = 0
    updated_data = {} 
    new_items_list = []

    for school, items in data.items():
        print(f"\n[正在处理] {school} ({len(items)} 条)")
        updated_items = []
        
        for item in items:
            title = item.get("title", "")
            url = item.get("url", "")
            content = item.get("content", "")
            
            if is_url_exists(url):
                if url in summary_cache:
                    item["summary"] = summary_cache[url]
                skip_count += 1
                updated_items.append(item)
                continue
            if url in summary_cache:
                print(f"  [缓存命中] {title[:10]}... -> 同步到云端")
                cached_summary = summary_cache[url]
                item["summary"] = cached_summary
                
                save_notice(item, cached_summary)
                
                new_items_list.append(item)
                updated_items.append(item)
                continue 

            print(f"  [新发现] 正在 AI 总结: {title[:10]}...")
            
            summary = get_ai_summary(title, content)
            if summary:
                item["summary"] = summary
                
                save_notice(item, summary)
                new_ai_count += 1
                
                new_items_list.append(item)
                
                time.sleep(5) 
            else:
                print("    -> [失败] 暂时跳过入库")
            
            updated_items.append(item)        
        
        updated_data[school] = updated_items

    print(f"云端已有跳过: {skip_count} 条")
    print(f"新增并入库:   {new_ai_count} 条")
    print(f"待发送邮件数: {len(new_items_list)} 条")

    with open(FINAL_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=2)
    print(f"全量备份已保存至 {FINAL_OUTPUT_FILE}")

    if new_items_list:
        with open(NEW_UPDATES_FILE, "w", encoding="utf-8") as f:
            json.dump(new_items_list, f, ensure_ascii=False, indent=2)
        print(f"增量更新已保存至 {NEW_UPDATES_FILE} (准备发送邮件)")
    else:
        print("今日无新增内容，不生成增量文件。")
        if os.path.exists(NEW_UPDATES_FILE):
            os.remove(NEW_UPDATES_FILE)

if __name__ == "__main__":
    main()