import smtplib
import json
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
import os
from supabase import create_client, Client

SMTP_SERVER = "smtp.163.com"  # 如果是163，填 smtp.163.com
SMTP_PORT = 465              # SSL加密端口通常是 465
SENDER_EMAIL = "lazysheep0066@163.com"
PASSWORD = os.environ.get("EMAIL_PASSWORD")
# ===========================================

# ================= Supabase 配置 =================
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
# ===========================================

def send_daily_report(receiver_email, user_name, user_subs, json_data):
    """
    根据用户订阅分发邮件
    :param receiver_email: 收件人邮箱
    :param user_name: 用户姓名
    :param user_subs: 用户订阅列表, 如 ["计算机学院", "学生事务"]
    :param json_data: 完整的 notices.json 字典对象
    """
    
    # 数据过滤与展平逻辑
    # 我们遍历 JSON 中每个学院的列表，筛选出符合订阅要求的项
    personal_notices = []
    for department, items in json_data.items():
        for item in items:
            if item["summary"] == "<graduate>":
                continue
            # 匹配逻辑：如果学院名在订阅里
            if department in user_subs:
                # 补充来源字段方便 HTML 显示
                item['source_dept'] = department
                personal_notices.append(item)

    if not personal_notices:
        return False

    # 构建 HTML 正文
    html_content = f"""
    <html>
    <body style="font-family: 'Source Han Sans CN', 'Noto Sans CJK SC', 'Microsoft YaHei', sans-serif;">
        <h2 style="color: #000000; border-bottom: 2px solid #D32F2F; padding-bottom: 10px;">
            {user_name}同学，您好！
        </h2>
        <p style="color: #333;">SJTU News Watchdog 为您发现以下 <b>{len(personal_notices)}</b> 条新通知（点击<b style="color: #D32F2F;">红色标题</b>可以跳转原文）：</p>
        <table border="0" cellpadding="10" cellspacing="0" style="width: 100%; border-collapse: collapse;">
    """

    for item in personal_notices:
        # 处理附件显示
        attachments = item.get('attachments', [])
        attach_html = ""
        if isinstance(attachments, list) and len(attachments) > 0:
            attach_html = "<br><span style='font-size: 0.8em; color: #2e7d32;'>📎 附件: "
            attach_links = [f"<a href='{a['url']}'>{a['name']}</a>" for a in attachments]
            attach_html += " | ".join(attach_links) + "</span>"

        # 核心行
        row = f"""
            <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 15px 0;">
                    <div style="font-size: 0.85em; color: #888;">{item.get('date')} | {item.get('source_dept')}</div>
                    <div style="font-weight: bold; font-size: 1.1em; margin: 5px 0;">
                        <a href="{item.get('url')}" style="color: #d32f2f; text-decoration: none;">{item.get('title')}</a>
                    </div>
                    <div style="color: #555; font-size: 0.95em; background: #fdfdfd; padding: 8px; border-left: 3px solid #004052;">
                        🤖 <b>AI 摘要：</b>{item.get('summary')}
                    </div>
                    {attach_html}
                </td>
            </tr>
        """
        html_content += row

    html_content += """
        </table>
        <p style="margin-top: 20px; font-size: 0.8em; color: #aaa; text-align: center;">
            此邮件由自动化系统生成，请勿直接回复。
        </p>
    </body>
    </html>
    """

    # 发送邮件
    message = MIMEText(html_content, 'html', 'utf-8')
    message['From'] = formataddr(["SJTU Watchdog", SENDER_EMAIL])
    message['To'] = formataddr([user_name, receiver_email])
    message['Subject'] = Header(f"【SJTU WatchDog订阅】今日有{len(personal_notices)}条更新", 'utf-8')

    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SENDER_EMAIL, PASSWORD)
        server.sendmail(SENDER_EMAIL, [receiver_email], message.as_string())
        server.quit()
        print(f"✅ [Mailer] 成功发送至: {receiver_email}")
        return True
    except Exception as e:
        print(f"❌ [Mailer] 发送至 {receiver_email} 失败: {e}")
        return False

def send_all_subscribed_emails():
    """
    从 Supabase 读取用户并分发个性化邮件的主函数
    """
    # 加载通知数据 (notices.json)
    try:
        with open('data/new_updates.json', 'r', encoding='utf-8') as f:
            full_data = json.load(f)
    except FileNotFoundError:
        print("❌ 找不到 new_updates.json 文件")
        return

    # 从 Supabase 获取所有活跃用户
    # 假设表名为 'users'，字段有 email, name, subscriptions, is_active
    try:
        response = supabase.table("users").select("email, name, subscriptions")\
            .eq("is_active", True).execute()
        users = response.data
    except Exception as e:
        print(f"❌ Supabase 读取失败: {e}")
        return

    if not users:
        print("ℹ️ 没有活跃用户需要发送邮件。")
        return

    print(f"🚀 开始为 {len(users)} 个用户处理订阅邮件...")

    # 循环遍历每个用户，发送个性化日报
    for user in users:
        email = user.get('email')
        name = user.get('name', '同学')
        subs = user.get('subscriptions', []) # 这是一个列表，如 ["计算机学院"]

        # 调用你写的那个函数
        success = send_daily_report(
            receiver_email=email,
            user_name=name,
            user_subs=subs,
            json_data=full_data
        )
        
        if success:
            # 更新数据库，记录最后发送时间
            # supabase.table("users").update({"last_sent": "now()"}).eq("email", email).execute()
            pass

# ================= 运行 =================
if __name__ == "__main__":
    send_all_subscribed_emails()