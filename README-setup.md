
Use this as your startup README section for the local MVP.

````markdown
# Stock Alert SaaS — Local Startup

## Project Structure

Parent folder:

```bash
/Users/ultrasupersam/apps/stock-alert-platform
````

Repos:

```bash
2024schwab/
stock-alert-saas/
```

---

# 1. Start Web Dashboard

Open terminal:

```bash
cd /Users/ultrasupersam/apps/stock-alert-platform/stock-alert-saas

source ../.venv/bin/activate

python -m uvicorn app.web.dashboard:app --reload
```

Dashboard:

```text
http://127.0.0.1:8000
```

Pages:

```text
/status
/charts
/alerts
/settings
/logs
```

---

# 2. Start Streamer

Open SECOND terminal:

```bash
cd /Users/ultrasupersam/apps/stock-alert-platform/stock-alert-saas

source ../.venv/bin/activate

python -u -m app.streamer.quote_streamer_config
```

Expected startup:

```text
FAVORITE SYMBOLS: [...]
MOVERS WATCHLIST: [...]
FINAL STREAM WATCHLIST: [...]
QUOTE: {...}
```

---

# 3. Verify Streamer Health

Latest quotes:

```bash
sqlite3 data/market_data.db "
SELECT symbol, timestamp
FROM quotes
ORDER BY id DESC
LIMIT 10;
"
```

Streamer mode:

```bash
sqlite3 data/market_data.db "
SELECT * FROM streamer_control;
"
```

---

# 4. Provider Errors

Recent Schwab/provider failures:

```bash
sqlite3 data/market_data.db "
SELECT
    timestamp,
    provider,
    symbol,
    error_type,
    message
FROM provider_errors
ORDER BY id DESC
LIMIT 20;
"
```

---

# 5. Restart Streamer

```bash
pkill -f quote_streamer_config

cd /Users/ultrasupersam/apps/stock-alert-platform/stock-alert-saas

source ../.venv/bin/activate

python -u -m app.streamer.quote_streamer_config
```

---

# 6. Logs

Streamer stdout:

```bash
tail -f logs/streamer.out.log
```

Streamer stderr:

```bash
tail -f logs/streamer.err.log
```

---

# 7. Git Workflow

Create feature branch:

```bash
git checkout -b feature/my-feature
```

Create fix branch:

```bash
git checkout -b fix/my-fix
```

Commit:

```bash
git add .
git commit -m "description"
```

Merge back:

```bash
git checkout master
git merge feature/my-feature
```

---

# 8. Database

SQLite DB:

```text
data/market_data.db
```

Tables:

```text
quotes
alerts
streamer_control
provider_errors
```

```
```

[1]: https://chatgpt.com/c/69fe2060-2f58-83e8-89d6-c8a6afef0d3b "SaaS Web Down Fix"
[2]: https://chatgpt.com/c/69f7ff76-e718-83e8-8bfd-f1b42fec3e24 "ML Alert for Stock Gaps"
[3]: https://chatgpt.com/c/69f9ed9f-1194-8326-9a75-bcb00751ac11 "SaaS Streamer Next Steps"
[4]: https://chatgpt.com/c/69fc108a-6b40-83e8-8e05-96082ffabb78 "Git Branching Workflow"
[5]: https://chatgpt.com/c/69f2d1d4-5968-83e8-8b1f-845a64740997 "BigQuery Pub/Sub Integration"
[6]: https://chatgpt.com/c/69fd5f9a-276c-83e8-87c9-15ed284b04fe "Streamer Control Design"
[7]: file://my_files/file_00000000e9a471fd956814138a5aa5a2 "Pasted text.txt"
[8]: file://my_files/file_000000007d9071fd92f3723a1999c270 "Pasted text.txt"
[9]: file://my_files/file_00000000d77c722fafb73348446e4c50 "Pasted text.txt"
[10]: file://my_files/file_000000002d5471f5841554b6adbcc1ad "Pasted text.txt"
[11]: file://my_files/file_000000003d1871fdb70da1524a140e24 "Pasted text.txt"
[12]: file://my_files/file_00000000bae071f8bc4cadbfdd1a2feb "Screenshot 2026-05-06 at 4.18.56 PM.png"
[13]: file://my_files/file_00000000b6b071f88e77e491456b7eb4 "Screenshot 2026-05-06 at 4.31.25 PM.png"
