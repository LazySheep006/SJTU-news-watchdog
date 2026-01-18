# SJTU News Watchdog(交大校园通知AI助手)
![School](https://img.shields.io/badge/School-SJTU-blue)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.10-green)

一个基于 AI 的自动化校园通知聚合系统。它每天自动爬取上海交通大学各大源的通知，利用大模型生成一句话摘要，并根据用户的订阅偏好通过邮件精准推送。

**订阅页面**: [https://news-sub.lazysheep.site](https://news-sub.lazysheep.site)

## 主要功能

* **多源聚合**：目前支持计算机学院、自动化与感知学院、电气工程学院、集成电路学院、教务处等多个来源。
* **AI 智能摘要**：利用 GitHub Models (GPT-4.1-mini) 为每条新闻生成简短摘要，拒绝标题党。
* **增量更新**：智能去重，每天只推送最新的内容。
* **个性化订阅**：用户可选择感兴趣的板块，系统仅推送相关内容。
* **零成本运行**：基于 GitHub Actions + Supabase + GitHub Pages 构建，无需租赁服务器。

## 技术栈

* **后端**: Python (Requests, BeautifulSoup, Lxml)
* **AI**: Azure AI Inference SDK (GitHub Models)
* **数据库**: Supabase (PostgreSQL + RLS + RPC)
* **前端**: HTML5, Tailwind CSS, Alpine.js (通过 GitHub Actions 自动注入环境变量)
* **CI/CD**: GitHub Actions (定时任务 + 自动部署)

## 快速开始 (本地开发)

### 1. 环境准备
确保你安装了 Python 3.10+。
先fork到你的GitHub仓库

```bash
git clone [https://github.com/your-username/sjtu-news-watchdog.git](https://github.com/your-username/sjtu-news-watchdog.git)
cd sjtu-news-watchdog
pip install -r requirements.txt
```
### 2. 配置环境变量
在本地根目录创建一个 .env 文件（不要提交到 GitHub），填入以下内容：

```yml
# Supabase 配置
SUPABASE_URL=你的_SUPABASE_URL
SUPABASE_KEY=你的_SUPABASE_SERVICE_ROLE_KEY

# AI 配置 (GitHub Models)
SJTU_new=你的_GITHUB_MODELS_TOKEN

# 邮件配置
EMAIL_PASSWORD=你的邮箱授权码
# 注意：发件人邮箱需要在 mailer.py 中配置
```
### 3. 运行流程
项目采用模块化设计，通过 `main.py` 统一调度：
```bash
python main.py
```
Step 1: 运行爬虫，生成 data/today.json。

Step 2: 运行 AI 摘要与数据库查重，生成 data/new_updates.json。

Step 3: 读取增量文件，发送邮件。

## 安全说明
### 前端安全: 
- 订阅页面使用 Supabase 的 anon key。为了保护数据，数据库已配置 RLS (行级安全策略) 并禁用了公开 SELECT 权限。所有数据交互通过 Postgres RPC (远程函数) 进行。

### 后端安全: 
- 爬虫与发信逻辑运行在 GitHub Actions 的隔离环境中。

### License
[MIT License](LICENSE)