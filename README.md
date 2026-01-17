# SJTU News Watchdog(交大校园通知AI助手)
![School](https://img.shields.io/badge/School-SJTU-blue)
![Language](https://img.shields.io/badge/Language-Python-orange)
### Current Status: 🚧 Development (Phase 1: Spider Ready) 
### Maintainers: [@LazySheep006](https://github.com/LazySheep006), [@geniustanker](https://github.com/geniustanker), [@kiny007](https://github.com/kiny007)


### 项目简介 (Introduction)
本项目旨在解决“交大官网通知分散、难以即时获取”的痛点。 这是一个自动化的 爬虫 + AI 摘要 + 邮件推送 系统。它会定期抓取 SJTU 计算机系（及其他学院）的通知，利用 LLM (DeepSeek/GPT) 生成简报，并推送到用户的邮箱。

### 系统架构 (Architecture)
- Spider (Done): 抓取官网（支持 AJAX 动态加载），提取标题、日期、正文。
- Database (Todo): 本地 SQLite 存储，通过 URL 进行去重，防止重复推送。
- AI Summarizer (Todo): 调用大模型 API，将长篇正文总结为核心摘要。
- Notifier (Todo): 通过 SMTP 服务发送 HTML 格式的日报邮件。
- Automation (Todo): 部署于 GitHub Actions，每日定时触发。

### 数据接口协议 (Data Interface)
爬虫模块 (spider.py) 现已完成。后端逻辑调用 get_latest_notices() 将返回如下格式的列表：
```json
[
    {
        "title": "关于2026年寒假放假的通知",
        "url": "https://cs.sjtu.edu.cn/...",
        "date": "2026-01-15",
        "content": "根据学校校历安排，现将寒假放假事项通知如下...（正文全文）",
        "source": "CS-SJTU"
    },
    ...
]
```
### 现有工作 (Progress)
#### 爬虫模块 (spider.py) - @LazySheep006
- [x] CS 官网适配：已解决 xsgz-tzgg-xssw 板块的 AJAX 异步加载问题。
- [x] 完成了原电院的四个网站和教务处的通知的爬取
- [x] 还有四到五个其余模块的通知渠道

- [x] 详情页解析：实现了进入详情页抓取正文 (div.xw-cont) 的逻辑。
接口封装：提供了 fetch_all_notices() 供后端直接调用。

### 后续工作计划
请geniustanker接手后续开发，建议在 **分支 feature/db-and-ai** 上进行：

- [x] 数据库搭建 (`database.py`)

使用 `sqlite3` 初始化数据库。

实现 `is_new(url)` 函数：判断该新闻是否已存在。

实现 `save_notice(data)` 函数：存储抓取到的新闻和生成的摘要。

- [x] AI 模块接入 (`ai_module.py`)   **这里我来做吧**

申请 DeepSeek 或 OpenAI API Key。

编写 Prompt：“请总结这篇校园通知的关键信息（时间、地点、事件）”。

- [ ] 邮件发送 (`mailer.py`)

配置 SMTP (QQ/163邮箱)。

编写发送函数，支持 HTML 格式（让邮件好看一点）。

- [ ] 主程序串联 (main.py)

编写 main() 函数，串联：爬取 -> 去重 -> AI总结 -> 存库 -> 发信。