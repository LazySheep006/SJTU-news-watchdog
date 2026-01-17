# Contributing to SJTU News Watchdog

欢迎参与本项目的开发！为了保证代码质量和自动化流程的稳定运行，请遵循以下开发规范。

## 分支管理 (Branch Strategy)

我们采用 **Feature Branch Workflow**：

1.  **`main`**: 主分支，对应线上稳定版本。GitHub Actions 会每天定时运行此分支的代码。
2.  **`dev` / `feature-*`**: 开发分支。

**开发流程**：
1.  从 `main` 切出一个新分支：`git checkout -b feature/new-spider`
2.  在本地开发并测试。
3.  提交代码并推送到远程仓库。
4.  在 GitHub 上发起 **Pull Request (PR)** 合并到 `main`。
5.  等待 Code Review 或自动检查通过后合并。

## 如何添加新的爬虫源

如果你想添加一个新的学院通知来源，请按以下步骤操作：

1.  **新建文件**：在 `SPIDER/` 目录下新建 `xxx_spider.py`。
2.  **实现函数**：必须包含一个返回列表的函数，数据结构如下：
    ```python
    [
      {
        "title": "通知标题",
        "url": "通知链接",
        "date": "2024-01-01",
        "source": "学院名称(作为分类依据)",
        "content": "原始内容(用于AI总结)"
      },
      ...
    ]
    ```
3.  **注册爬虫**：在根目录的 `spider.py` 中导入你的模块，并在 `run_all_spiders()` 函数中调用它，将结果添加到 `all_data_categorized` 字典中。

## 数据库变更

本项目使用了 Supabase 的 RPC 函数来绕过 RLS 限制。如果你修改了数据表结构（`users` 表），请务必：

1.  同步更新 `db_ai.py` 中的数据库操作代码。
2.  如果是前端相关变更，需要在 Supabase SQL Editor 中更新对应的 `manage_subscription` 或 `get_subscriber_count` 函数。
3.  在 PR 中说明 SQL 变更内容。

## 提交前的检查清单

在提交 PR 之前，请在本地运行一次完整流程，确保没有报错：

```bash
# 1. 确保安装了依赖
pip install -r requirements.txt

# 2. 运行总流程
python main.py
```

# *Happy Coding!* 🚀