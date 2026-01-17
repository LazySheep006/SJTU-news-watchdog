import os
import json
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = None

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def init_db():
    if supabase:
        print("Supabase 连接配置已就绪。")
    else:
        print("数据库未连接。")


def is_url_exists(url):
    try:
        response = supabase.table("notices").select("url", count="exact").eq("url", url).execute()
        return response.count > 0
    except Exception as e:
        return False

def save_notice(item, ai_summary):
    try:
        data = {
            "title": item.get("title"),
            "url": item.get("url"),
            "date": item.get("date"),
            "content": item.get("content"),
            "summary": ai_summary,
            "source": item.get("source"),
            "category": item.get("category"),
            "attachments": item.get("attachments", []) 
        }
        
        supabase.table("notices").insert(data).execute()
        print(f"[入库成功] {item.get('title')[:15]}...")
        
    except Exception as e:
        error_str = str(e)
        if "duplicate key" in error_str or "23505" in error_str:
             print(f"[重复跳过] 数据库中已存在")
        else:
            print(f"[入库失败] {error_str}")


#这个功能准备新开一个github仓库来运行一个前端的用户管理系统，目前先这样写着
def add_user(email, name, subscriptions):
    try:
        data = {
            "email": email,
            "name": name,
            "subscriptions": subscriptions, 
            "is_active": True
        }
        
        supabase.table("users").upsert(data, on_conflict="email").execute()
        print(f"[用户管理] 已同步用户: {name} <{email}>")
        
    except Exception as e:
        print(f"[用户管理] 添加用户失败: {e}")

def get_active_users():
    try:
        response = supabase.table("users").select("*").eq("is_active", True).execute()
        return response.data
    except Exception as e:
        print(f"[用户管理] 获取列表失败: {e}")
        return []

if __name__ == "__main__":
    init_db()