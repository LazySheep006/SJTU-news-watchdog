import json
import time
import os
import SPIDER.cs_sais_spider as cs
import SPIDER.ic_spider as ic
import SPIDER.jwc_spider as jwc
import SPIDER.see_spider as see


json_filename = "data/today.json"


def run_all_spiders():
    all_data_categorized = {
        "计算机学院": [],
        "自动化与感知学院": [],
        "集成电路学院": [],
        "电气工程学院": [],
        "教务处": [],
        "其他": [] 
    }
    cs_sais_items = cs.fetch_cs_sais_data()
    for item in cs_sais_items:
        source = item.get('source', '其他')
        if source in all_data_categorized:
            all_data_categorized[source].append(item)
        else:
            all_data_categorized["其他"].append(item)

    ic_items = ic.fetch_ic_data()
    all_data_categorized["集成电路学院"].extend(ic_items)
    
    see_items = see.fetch_see_data()
    all_data_categorized["电气工程学院"].extend(see_items)

    jwc_items = jwc.fetch_jwc_data()
    all_data_categorized["教务处"].extend(jwc_items)

    return all_data_categorized

if __name__ == "__main__":
    final_data = run_all_spiders()

    total_count = sum(len(v) for v in final_data.values())
    print(f"总计 {total_count} 条通知")
    for k, v in final_data.items():
        if len(v) > 0:
            print(f"   - {k}: {len(v)} 条")

    with open(json_filename, "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)