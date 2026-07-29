---
name: zhimeng-agent
description: "Automated daily tasks via macOS launchd — daily reports, email organizing, desktop cleanup, and tech news aggregation synced to Git/Notion/Feishu/Obsidian."
---

# zhimeng-agent

Automated daily task runner using macOS launchd scheduling. Use when the user mentions "日报生成", "邮箱整理", "桌面整理", "科技新闻", "定时任务", "launchd", "zhimeng", or "自动化任务".

Generates daily work reports from Git commits, organizes Gmail, cleans up desktop/downloads, and aggregates tech news — syncing results to Git, Notion, Feishu, and Obsidian.

## Key files

- `tasks/config.py` — unified configuration (paths, schedule hours, API keys)
- `tasks/sync_utils.py` — multi-platform sync utility
- `tasks/daily_report/main.py` — daily report generator
- `tasks/email_organizer/main.py` — Gmail auto-archiver
- `tasks/desktop_organizer/main.py` — desktop/downloads cleanup
- `tasks/tech_news/main.py` — HN + GitHub trending aggregator
- `tasks/launchd/install.sh` — launchd plist installer

## Tasks

| Task | Schedule | What it does | Sync targets |
|------|----------|-------------|-------------|
| daily-report | 00:00 | Git commits + Claude Code sessions → structured report | Git, Notion, Feishu, Obsidian |
| email-organizer | 02:00 | Archive notification emails via himalaya CLI | Obsidian |
| desktop-organizer | 04:00 | Move files by type from Desktop/Downloads (no deletions) | Obsidian |
| tech-news | 07:00 | HN top stories + GitHub trending → daily briefing | Obsidian, Feishu |

## Workflow

1. **Always dry-run first** to verify output before syncing:
   ```bash
   poetry run python -m tasks.<task_name>.main --dry-run
   ```
2. Review the generated content.
3. Run without `--dry-run` to sync to configured platforms:
   ```bash
   poetry run python -m tasks.<task_name>.main
   ```

## Launchd management

```bash
# Install all scheduled tasks
cd apps/zhimeng-agent/tasks/launchd && ./install.sh install

# Check status / run immediately / uninstall
./install.sh status
./install.sh run daily-report
./install.sh uninstall
```

## Configuration

Set API keys in `.env`:

```bash
FEISHU_APP_ID=your_app_id
FEISHU_APP_SECRET=your_app_secret
OPENAI_API_KEY=your_api_key      # optional, for summaries
NOTION_TOKEN=your_token           # optional
```

Edit `tasks/config.py` for paths, schedule hours, and Feishu recipient IDs.

## Troubleshooting

- **Task not running:** `launchctl list | grep zhimeng` to verify it is loaded; `launchctl start com.zhimeng.<task>` to trigger manually.
- **Python env issues:** `poetry env info --path` to confirm virtualenv; `poetry run python -c "from tasks.config import config; print(config)"` to test imports.
- **Logs:** `tail -f logs/<task>.log` (stdout) or `logs/<task>.error.log` (stderr).
