# Stock Alert SaaS — Setup and Deployment

## 1. Project Structure

    ~/apps/stock-alert-platform/
    ├── schwab-api-client/
    │   ├── .venv/
    │   ├── private/
    │   └── requirements.txt
    └── stock-alert-saas/
        ├── .venv-frontend/
        ├── .venv-backend/
        ├── .env
        ├── app/
        ├── config/
        ├── data/
        ├── deploy/launchd/
        ├── scripts/
        ├── requirements-frontend.txt
        └── requirements-backend.txt

The Schwab SDK is an independent reusable Python library.

The frontend communicates with the backend through an internal
HTTP API and reads persisted application data.

The backend owns Schwab API access, market data acquisition,
OAuth authentication, streaming and historical updates.

## 2. Install Python Environments

### Schwab SDK

    cd ~/apps/stock-alert-platform/schwab-api-client
    python3.14 -m venv .venv
    .venv/bin/python -m pip install -r requirements.txt -e .

### SaaS Frontend

    cd ~/apps/stock-alert-platform/stock-alert-saas
    python3.14 -m venv .venv-frontend
    .venv-frontend/bin/python -m pip install -r requirements-frontend.txt

### SaaS Backend

    cd ~/apps/stock-alert-platform/stock-alert-saas
    python3.14 -m venv .venv-backend
    .venv-backend/bin/python -m pip install -r requirements-backend.txt

The backend requirements include the local Schwab SDK.

## 3. Configuration

Provide the application configuration in:

    stock-alert-saas/.env

Provide Schwab credentials and authorization data in:

    schwab-api-client/private/credentials.json
    schwab-api-client/private/refresh_token.json

Never commit credentials, tokens or .env files.

## 4. Manual Startup

Run these commands from the SaaS repository root.

Do not start duplicate processes if LaunchAgents are already running.

### Backend API

    .venv-backend/bin/python -m uvicorn app.backend.api:app --host 127.0.0.1 --port 8004

### Backend Orchestrator

    .venv-backend/bin/python -u -m app.backend.orchestrator

The orchestrator acquires market hours and movers.
Interactive OAuth recovery is available when run from a terminal.

### Frontend Dashboard

    .venv-frontend/bin/python -m uvicorn app.web.dashboard:app --host 0.0.0.0 --port 8003

### Quote Streamer

    .venv-backend/bin/python -u -m app.streamer.quote_streamer

### Historical Data Updater

    .venv-backend/bin/python -u scripts/update_historical_data.py

## 5. Automated Deployment — macOS LaunchAgents

Five LaunchAgent templates are provided in deploy/launchd/.

| Service | Schedule |
|---|---|
| web | Continuous |
| backend | Continuous |
| orchestrator | Every 5 minutes |
| streamer | Weekdays at 6:00 AM |
| history | Weekdays at 2:00 PM |

Schedules use the Mac's local timezone.
Trading sessions are determined using Schwab market hours.

For a fresh installation, generate the LaunchAgent files:

    mkdir -p ~/Library/LaunchAgents ~/Library/Logs

    .venv-backend/bin/python -c '
    from pathlib import Path
    home = Path.home()
    for template in Path("deploy/launchd").glob("*.plist"):
        target = home / "Library/LaunchAgents" / template.name
        if target.exists():
            print("Already exists:", target)
            continue
        target.write_text(template.read_text().replace("__HOME__", str(home)))
        print("Installed:", target)
    '

Load the services:

    for service in backend orchestrator web streamer history; do
        launchctl bootstrap "gui/$(id -u)" \
            "$HOME/Library/LaunchAgents/com.stockalert.$service.plist"
    done

Restart an existing service:

    launchctl kickstart -k "gui/$(id -u)/com.stockalert.web"

## 6. Application URLs

Frontend:

    http://127.0.0.1:8003/

Pages:

    /status
    /live
    /charts
    /gappers
    /alerts
    /alert-rules
    /settings
    /logs

Internal backend health:

    http://127.0.0.1:8004/health

The backend API is restricted to localhost.

## 7. Databases

Market data:

    data/market_data.db

System events and provider errors:

    data/logs.db

Recent quotes:

    sqlite3 data/market_data.db \
        "SELECT symbol, timestamp FROM quotes ORDER BY id DESC LIMIT 10;"

Streamer control:

    sqlite3 data/market_data.db "SELECT * FROM streamer_control;"

Recent provider errors:

    sqlite3 data/logs.db \
        "SELECT * FROM provider_errors ORDER BY id DESC LIMIT 20;"

## 8. Logs

LaunchAgent logs are located in:

    ~/Library/Logs/

Examples:

    tail -f ~/Library/Logs/com.stockalert.web.log
    tail -f ~/Library/Logs/com.stockalert.backend.log
    tail -f ~/Library/Logs/com.stockalert.orchestrator.log
    tail -f ~/Library/Logs/com.stockalert.streamer.log
    tail -f ~/Library/Logs/com.stockalert.history.log

Each service also has a corresponding -error.log file.

## 9. Git Workflow

Create a feature branch:

    git switch -c feature/my-feature

After implementation and testing:

    git add .
    git commit -m "Describe change"
    git switch master
    git merge feature/my-feature
    git push origin master
    git branch -d feature/my-feature

## 10. Dependency Management

Maintain separate frozen requirements for each environment.

Frontend:

    .venv-frontend/bin/python -m pip freeze > requirements-frontend.txt

Backend:

    .venv-backend/bin/python -m pip freeze > requirements-backend.txt

After freezing backend dependencies, normalize the local Schwab
SDK dependency to ../schwab-api-client for portability.

The Schwab SDK maintains its own requirements.txt.

Never commit virtual environment directories.
