import requests
from bs4 import BeautifulSoup
import time
import json

FILE_EXTENSIONS = [".pdf", ".doc", ".docx", ".ppt",".pptx",".xls",".xlsx",".zip",".rar",".7z",".tar",".gz",".bz2",".txt",".md"]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

urls = {"https://see.sjtu.edu.cn/xsgz_tzgg/","https://see.sjtu.edu.cn/bks_tzgg.html"}

def parse_see_list(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    items_data = []
    news_items = soup.select("div.nu6 li") 
    # print(f"  - 解析到 {len(news_items)} 条通知")
    for li in news_items:
        a_tag = li.select_one("a")
        url = a_tag.get("href", "")
        txt_div = a_tag.select_one(".txt")
        title = txt_div.get_text(strip=True) if txt_div else "无标题"
        time_div = a_tag.select_one(".time")
        pub_date = "未知时间"
        if time_div:
            day = time_div.select_one("p").get_text(strip=True)   # 05
            ym = time_div.select_one("span").get_text(strip=True) # 2025-11
            pub_date = f"{ym}-{day}"
        items_data.append({
            "title": title,
            "url": url,
            "date": pub_date,
            "source": "电气工程学院"
        })
    return items_data

def fetch_see_detail(info):
    url = info["url"]
    print(f"  正在抓取详情: {info['title']}...")
    try:
        res = requests.get(url, headers=headers, timeout=60)
        res.encoding = 'utf-8'
        
        if "jaccount.sjtu.edu.cn" in res.url:
            # print(f"[需登录] 无法直接抓取正文，使用列表页信息兜底")
            return {
                "type": 0, #0代表需要登录的
                "title": info['title'],  
                "url": url,
                "date": info['date'],  
                "source": "电气工程学院",
                "content": "[权限受限] 该通知可能涉及奖学金或内部名单，需校内身份访问。请点击标题跳转登录 JAccount 查看详情。",
                "attachments": []
            }
        
        soup = BeautifulSoup(res.text, 'html.parser')
        cont = soup.select_one("div.xw-cont .txt")
        body = cont.get_text(separator=' ', strip=True) if cont else "无正文内容"
        attachments = []
        for link in cont.select("a"):
            href = link.get('href', '')
            link_text = link.get_text(strip=True)
    
            if any(href.lower().endswith(ext) for ext in FILE_EXTENSIONS):
                    
                if href.startswith('/'):
                    full_url = "https://see.sjtu.edu.cn/" + href
                else:
                    full_url = href
                attachments.append({
                    "name": link_text,
                    "url": full_url
                })

        return {
            "type":1,
            "title": info['title'], 
            "url": url,
            "date": info['date'],
            "source": "电气工程学院",
            "content": body,
            "attachments": attachments if attachments else "<无附件>"
        }

    except Exception as e:
        print(f"抓取异常: {e}")
        return None

def fetch_see_data():
    all_data = []
    for url in urls:
        try:
            print(f"[电气工程学院] 正在访问: {url}")
            res = requests.get(url, headers=headers, timeout=60)
            if res.status_code != 200:
                print("列表页请求失败")
                return []
            
            items = parse_see_list(res.text)
        
            for item in items[:3]:
                detail = fetch_see_detail(item)
                if detail:
                    detail['category'] = "通知公告"
                    all_data.append(detail)
                time.sleep(0.5)
        except Exception as e:
            print(f"电气学院爬虫异常: {e}")
    return all_data

if __name__ == "__main__":
    print("[电气工程学院] 开始抓取...")
    data = fetch_see_data()
    print(f"抓取完成: {len(data)} 条")
    with open("SPIDER/lite_debug/all_see_notices.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)