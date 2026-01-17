import requests
from bs4 import BeautifulSoup
import time
import json


FILE_EXTENSIONS = [".pdf", ".doc", ".docx", ".ppt",".pptx",".xls",".xlsx",".zip",".rar",".7z",".tar",".gz",".bz2",".txt",".md"]

SCHOOL_CONFIG = {
    "计算机学院":{
        "BASE_URL" : "https://cs.sjtu.edu.cn/",
        "API_URL" : "https://cs.sjtu.edu.cn/active/ajax_type_list.html",
        "TEMPLATE" : "ajax_news_list1_search",
        "CAT_MAP" : {
                    "xsgz-tzgg-xssw": "学生事务",
                    "xsgz-tzgg-djdy": "党建德育",
                    "xsgz-tzgg-txgz": "团学工作",
                    "xsgz-tzgg-zyfz": "职业发展",
                    "bks_notice": "本科生通知" 
                    },
        "HEADERS" : {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "X-Requested-With": "XMLHttpRequest",
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "Referer": "https://cs.sjtu.edu.cn/xsgz-tzgg-xssw.html"
                    }
                },
    "自动化与感知学院":{
        "BASE_URL" : "https://sais.sjtu.edu.cn/",
        "API_URL" : "https://sais.sjtu.edu.cn/active/ajax_type_list.html",
        "TEMPLATE" : "ajax_news_list1_search",
        "CAT_MAP" : {
                    "tzgg":"通知公告",
                    "bks_tzgg":"本科生通知"
                    },
        "HEADERS": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Referer": "https://sais.sjtu.edu.cn/tzgg.html" 
        },
    },
    # "集成电路学院":{
    #     "BASE_URL" : "https://icisee.sjtu.edu.cn/",
    #     "API_URL" : "https://icisee.sjtu.edu.cn/active/ajax_type_list.html",
    #     "TEMPLATE" : "ajax_news_list2_left_search",
    #     "CAT_MAP" : {
    #                 "xsgz-gzzd-txgz":"团学工作",
    #                 "xsgz-gzzd-djdy":"党建德育",
    #                 "xsgz-gzzd-zyfz":"职业发展",
    #                 "benkesheng-tzgg": "本科生通知"
    #                 },
    #     "HEADERS": {
    #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    #         "X-Requested-With": "XMLHttpRequest",
    #         "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    #         "Referer": "https://icisee.sjtu.edu.cn/"
    #     },
    # } 小小吐槽一下，集成电路学院居然改掉了好多逻辑，感觉不太好弄在一个文件的了，要不然就是屎山了
}

def fetch_notice_page(api_url, headers,template,cat_code, page_num=1):#之后每一次github actions运行默认是第一页
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
        "template": template
    }
    
    try:
        response = requests.post(api_url, headers=headers, data=payload)
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
    # for url in notice_url:
    #     print(url)
    return notice_urls

def parse_notices_details(url, base_url,headers):
    """
    解析公告详情页面，提取公告的详细信息
    Args:
        url (str): 公告详情页面的 URL
    Returns:
        dict: 一条公告的详细信息
    """
    try:
        res = requests.get(url, headers=headers,timeout=60)
        res.encoding = 'utf-8' 
        detail_soup = BeautifulSoup(res.text, 'html.parser')
        container = detail_soup.select_one("div.xw-cont")

        if container:
            title_div = container.select_one(".tit")
            title = title_div.get_text(strip=True) if title_div else "无标题"
            time_p = container.select_one(".jj p")
            if time_p:
                raw_time = time_p.get_text(strip=True)
                pub_time = raw_time.replace("发布日期：", "")
            else:
                pub_time = "未知时间"
                            
            txt_div = container.select_one(".txt")
            body = txt_div.get_text(separator=' ', strip=True) if txt_div else "无内容"

            attachments = []
            if txt_div:
                for link in txt_div.select("a"):
                    href = link.get('href', '')
                    link_text = link.get_text(strip=True)
                    
                    if any(href.lower().endswith(ext) for ext in FILE_EXTENSIONS):
                        
                        if href.startswith('/'):
                            full_url = base_url + href
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
                "attachments": attachments if attachments else "<无附件>" 
            }
                
        else:
            print("未找到内容容器 (div.xw-cont)")       
    except Exception as e:
        print(f"抓取详情页失败: {e}")

def get_latest_notices(school_name, api_url, base_url, headers, template, cat_code, cat_name, pages=1):
    """
    获取指定板块的最新公告
    Args:
        cat_code (str): 公告类别代码
        cat_name (str): 公告类别名称
        pages (int): 要获取的页数
    Returns:
        list: 最新公告的列表
    """
    section_data = []
    print(f"[{school_name}] 正在爬取: {cat_name} ({cat_code})...")
    
    for p in range(1, pages + 1):
        html = fetch_notice_page(api_url,headers,template,cat_code, p)
        if not html:
            continue
            
        urls = parse_notices(html)
        target_urls = urls[:3] #只爬3条，毕竟每天都运行，节省时间和算力量
        print(f"  - 第 {p} 页准备爬取 {len(target_urls)} 条链接")

        for url in target_urls:
            if not url.startswith("http"):
                url = base_url + url

            details = parse_notices_details(url, base_url,headers)
            if details:
                details['category'] = cat_name 
                details['source'] = school_name
                section_data.append(details)
        
            time.sleep(0.5)
            
    return section_data

def fetch_cs_sais_data():
    all_data = []
    for school_name, config in SCHOOL_CONFIG.items():
        curr_api = config['API_URL']
        curr_base = config['BASE_URL']
        curr_cats = config['CAT_MAP']
        headers = config['HEADERS']
        template = config['TEMPLATE']
        for cat_code, cat_name in curr_cats.items():
            
            notices = get_latest_notices(
                school_name=school_name,
                api_url=curr_api,
                base_url=curr_base,
                headers=headers,
                template=template,
                cat_code=cat_code,
                cat_name=cat_name,
                pages=1
            )
            all_data.extend(notices) 
            
    return all_data

#本地测试
if __name__ == "__main__":
    data = fetch_cs_sais_data()
    print(f"所有学院爬取完成，共 {len(data)} 条。")
    # 保存
    with open("SPIDER/lite_debug/all_cs_sais_notices.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
