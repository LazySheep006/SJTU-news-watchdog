import spider
import database
import ai_module
import mailer  # 导入邮件模块
import time


def job():
    print("🚀 任务启动：SJTU News Watchdog")

    # 1. 初始化数据库
    database.init_db()

    # 2. 爬取最新通知
    print("🕷️ 正在抓取官网数据...")
    try:
        notices = spider.get_latest_notices(pages=1)
        print(f"📦 抓取到 {len(notices)} 条通知")
    except Exception as e:
        print(f"❌ 爬虫模块出错: {e}")
        return

    # 用于存放本次发现的所有新通知
    new_notices_buffer = []

    # 3. 遍历处理
    for item in notices:
        url = item.get('url')
        title = item.get('title')

        # 4. 检查是否是新的
        if database.is_new(url):
            print(f"✨ 发现新通知: {title}")

            # 5. 生成 AI 摘要
            content = item.get('content')
            print("   🤖 正在生成摘要...", end='', flush=True)
            summary = ai_module.generate_summary(content)
            print(" [完成]")

            # 6. 存入数据库
            database.save_notice(item, summary)

            # 7. 加入待发送列表 (把生成的摘要也放进去)
            item['summary'] = summary
            new_notices_buffer.append(item)

            # 休息一下
            time.sleep(1)
        else:
            print(f"💤 已存在，跳过: {title}")

    # 8. 批量发送邮件
    if new_notices_buffer:
        print(f"📧 正在发送日报，共 {len(new_notices_buffer)} 条新内容...")
        # ⚠️ 如果你刚才把 mailer.py 里的密码删了，记得在环境变量里配置，或者在这里临时硬编码测试
        success = mailer.send_daily_report(new_notices_buffer)
        if success:
            print("🎉 任务圆满完成！邮件已送达。")
    else:
        print("📭 今日无新通知，无需发送邮件。")


if __name__ == "__main__":
    job()