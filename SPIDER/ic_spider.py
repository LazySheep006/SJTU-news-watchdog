import requests
from bs4 import BeautifulSoup
import time
import json
import re

FILE_EXTENSIONS = [".pdf", ".doc", ".docx", ".ppt",".pptx",".xls",".xlsx",".zip",".rar",".7z",".tar",".gz",".bz2",".txt",".md"]

API_URL = "https://icisee.sjtu.edu.cn/active/ajax_type_list.html"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Referer": "https://icisee.sjtu.edu.cn/"
}

CAT_MAP = {
    "xsgz-gzzd-txgz":"团学工作",
    "xsgz-gzzd-djdy":"党建德育",
    "xsgz-gzzd-zyfz":"职业发展",
    "xsgz-gzzd-xssw":"学生事务",
    "benkesheng-tzgg": "本科生通知"
}

def fetch_notice_page(cat_code, page_num=1):
    """
    获取公告列表页面的 HTML 内容

    Args:
        page_num (int): 页码

    Returns:
        str: 公告列表页面的 HTML 内容
    """
    payload = {
        "page": str(page_num),
        "cat_code": cat_code,
        "type": "",
        "search": "",
        "extend_id": "0",
        "template": "ajax_news_list2_left_search"
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, data=payload)
        if response.status_code == 200:
            data = response.json()
            return data.get('content', '')
        else:
            print(f"失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"异常: {e}")
        return None

def parse_notices(html_content):
    """
    解析公告列表页面，提取所有公告链接

    Args:
        html_content (str): 公告列表页面的 HTML 内容

    Returns:
        list: 所有公告链接的列表
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    notice_urls = []
    lis = soup.select("li a")
    for a in lis:
        notice_urls.append(a["href"])
    return notice_urls

def parse_notices_details(url):
    """
    解析公告详情页面，提取公告的详细信息

    Args:
        url (str): 公告详情页面的 URL

    Returns:
        dict: 一条公告的详细信息
    """
    try:
        res = requests.get(url, headers=HEADERS, timeout=60)
        res.encoding = 'utf-8'
        detail_soup = BeautifulSoup(res.text, 'html.parser')
        container = detail_soup.select_one("div.xwxq")

        if container:
            title_div = container.select_one(".tit")
            title = title_div.get_text(strip=True) if title_div else "无标题"
            time_p = container.select_one(".tit2")
            if time_p:
                match = re.search(r"\d{4}-\d{2}-\d{2}", time_p.get_text())
                if match:
                    pub_time = match.group()  # 拿到 "YYYY-MM-DD"
                else:
                    pub_time = "未知时间"
            else:
                pub_time = "未知时间"

            txt_div = container.select_one(".cont")
            body = txt_div.get_text(separator=' ', strip=True) if txt_div else "无内容"

            attachments = []
            if txt_div:
                for link in txt_div.select("a"):
                    href = link.get('href', '')
                    link_text = link.get_text(strip=True)

                    if any(href.lower().endswith(ext) for ext in FILE_EXTENSIONS):

                        if href.startswith('/'):
                            full_url = "https://icisee.sjtu.edu.cn" + href
                        else:
                            full_url = href

                        attachments.append({
                            "name": link_text,
                            "url": full_url
                        })

            return {
                "title": title,
                "url": url,
                "date": pub_time,
                "content": body,
                "attachments": attachments if attachments else "<无附件>",
                "source": "集成电路学院"
            }

        else:
            print("未找到内容容器 (div.xwxq)")
    except Exception as e:
        print(f"抓取详情页失败: {e}")

def get_latest_notices(cat_code, cat_name, page_num=1):
    """
    获取最新公告的详细信息

    Args:
        cat_code (str): 公告类别代码
        page_num (int): 页码

    Returns:
        list: 最新公告的详细信息列表
    """
    section_data = []
    print(f"[集成电路学院] 正在爬取: {cat_name} ({cat_code})...")

    html = fetch_notice_page(cat_code, page_num)
    if html:
        notice_urls = parse_notices(html)[:3]
        print(f"  - 第 {page_num} 页准备爬取 {len(notice_urls)} 条链接")
        for notice_url in notice_urls:
            details = parse_notices_details(notice_url)
            if details:
                details['category'] = cat_name 
                section_data.append(details)
            time.sleep(0.5)
    return section_data

def fetch_ic_data():
    all_data = []
    for cat_code, cat_name in CAT_MAP.items():
        notices = get_latest_notices(cat_code, cat_name, page_num=1)
        all_data.extend(notices)
    return all_data

if __name__ == "__main__":
    all_notices = fetch_ic_data()
    print(f"共抓取到 {len(all_notices)} 条公告")
    with open("SPIDER/lite_debug/all_ic_notices.json", "w", encoding="utf-8") as f:
        json.dump(all_notices, f, ensure_ascii=False, indent=2)