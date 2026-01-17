import requests
from bs4 import BeautifulSoup
import time
import json
from urllib.parse import urljoin  

FILE_EXTENSIONS = [".pdf", ".doc", ".docx", ".ppt",".pptx",".xls",".xlsx",".zip",".rar",".7z",".tar",".gz",".bz2",".txt",".md"]

LIST_URL = "https://jwc.sjtu.edu.cn/xwtg/jxyx.htm"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

def parse_jwc_list(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    items_data = []
    news_items = soup.select("div.Newslist li") 
    
    for li in news_items:
        div_time = li.select_one("div.sj")
        if not div_time: continue # 防止空行报错

        day = div_time.select_one("h2").get_text(strip=True)
        month_year = div_time.select_one("p").get_text(strip=True)
        pub_date = month_year.replace('.', '-') + '-' + day
        
        a_tag = li.select_one("a")
        if not a_tag: continue
        
        href = a_tag.get("href", "")
        urlc = urljoin(LIST_URL, href)

        title_tag = a_tag.select_one("h2")
        title = title_tag.get_text(strip=True)
        items_data.append({
            "title": title,
            "url": urlc,
            "date": pub_date,
            "source": "教务处"
        })
        
    return items_data

def fetch_jwc_detail(info):
    url = info["url"]
    print(f"  正在抓取详情: {info['title'][:15]}...")
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=60)
        res.encoding = 'utf-8' 
        
        if res.status_code != 200:
            print("详情页请求失败")
            return None
            
        soup = BeautifulSoup(res.text, 'html.parser')
        
        content = soup.select_one("div.v_news_content")
        if content:
            useful_images = content.select("p.vsbcontent_img img")
            for img in useful_images:
                src = img.get("src")
                if src:
                    full_img_url = urljoin(url, src)
                    img.replace_with(f"[附录图片: {full_img_url}]\n")
            body = content.get_text(separator=' ', strip=True)
        else:
            body = "无正文内容"

        attachments = []
        att_links = soup.select("div.Newslist2 ul li a") 
        
        for link in att_links:
            href = link.get('href', '')
            link_text = link.get_text(strip=True)
            
            if any(href.lower().endswith(ext) for ext in FILE_EXTENSIONS):
                full_url = urljoin(url, href) 
                
                attachments.append({
                    "name": link_text,
                    "url": full_url
                })

        return {
            "title": info['title'],
            "url": url,
            "date": info['date'],
            "content": body,
            "category": "教育运行",
            "source": "教务处",
            "attachments": attachments if attachments else "<无附件>"
        }
    except Exception as e:
        print(f"抓取异常: {e}")
        return None

def fetch_jwc_data():
    all_data = []
    print(f"[教务处] 正在访问: {LIST_URL}")
    
    try:
        res = requests.get(LIST_URL, headers=HEADERS, timeout=60)
        res.encoding = 'utf-8' # 防止列表页乱码
        
        if res.status_code != 200:
            print(f"列表页请求失败: {res.status_code}")
            return []
            
        items = parse_jwc_list(res.text)

        for item in items[:3]:
            detail = fetch_jwc_detail(item)
            if detail:
                all_data.append(detail)
            time.sleep(0.5)
            
    except Exception as e:
        print(f"教务处爬虫异常: {e}")      
    return all_data

if __name__== "__main__":
    data = fetch_jwc_data()
    print(f"全部完成，共抓取: {len(data)} 条")
    with open("SPIDER/lite_debug/all_jwc_notices.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("数据已保存为 SPIDER/lite_debug/all_jwc_notices.json")
