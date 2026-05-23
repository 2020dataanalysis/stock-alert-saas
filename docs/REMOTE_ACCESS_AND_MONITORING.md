# Remote Access and Health Monitoring

## Ngrok Domain

https://moody-habitable-bush.ngrok-free.dev

## Start FastAPI

```bash
uvicorn app.web.dashboard:app --host 0.0.0.0 --port 8000
Start ngrok








Correct — the explanatory text should also live inside the README so future-you (or another developer) has the full operational context in one place.

Better version:

````bash
mkdir -p docs

cat > docs/REMOTE_ACCESS_AND_MONITORING.md <<'EOF'
# Remote Access and Health Monitoring

## Overview

This project supports:

- Remote browser access
- External uptime monitoring
- Internet-accessible HTTPS endpoint
- Machine-readable health checks

Current architecture:

```text
Internet
→ ngrok HTTPS tunnel
→ Mac mini
→ FastAPI SaaS on localhost:8000
````

---

# Ngrok Configuration

## Reserved Domain

```text
https://moody-habitable-bush.ngrok-free.dev
```

## Start FastAPI

Run from the project root:

```bash
uvicorn app.web.dashboard:app --host 0.0.0.0 --port 8000
```

Important:

```text
--host 0.0.0.0
```

is required for external access through ngrok.

---

# Start ngrok

Run in a separate terminal:

```bash
ngrok http --domain=moody-habitable-bush.ngrok-free.dev 8000
```

This tunnels:

```text
https://moody-habitable-bush.ngrok-free.dev/*
→ http://localhost:8000/*
```

---

# Remote URLs

## Human Access

Base URL:

```text
https://moody-habitable-bush.ngrok-free.dev
```

Examples:

```text
/status
/settings
/charts
/alerts
/logs
```

Humans should use the base domain and navigate normally.

---

# Health Monitoring

## Health Endpoint

Machine monitoring uses:

```text
/health
```

Example:

```text
https://moody-habitable-bush.ngrok-free.dev/health
```

The endpoint should support:

```text
GET
HEAD
```

Expected response:

```json
{"status":"ok"}
```

---

# UptimeRobot Configuration

## Monitor Type

```text
HTTP / website monitoring
```

## Monitor URL

```text
https://moody-habitable-bush.ngrok-free.dev/health
```

## Free Tier Details

```text
5 minute monitoring interval
Email alerts
50 monitors included
```

---

# Important Notes

## Why /health Exists

Production systems typically expose dedicated health endpoints:

```text
/health
/healthz
/live
/ready
```

These endpoints are intended for:

* uptime monitoring
* orchestration systems
* automated observability tools

They are separate from human-facing pages like `/status`.

---

# UptimeRobot HEAD Requests

UptimeRobot may issue:

```text
HEAD /health
```

instead of:

```text
GET /health
```

Therefore the FastAPI route must allow both methods.

Example:

```python
@app.api_route("/health", methods=["GET", "HEAD"])
def health():
    return {"status": "ok"}
```

---

# Operational Requirements

Remote access requires BOTH processes running:

## FastAPI

```bash
uvicorn app.web.dashboard:app --host 0.0.0.0 --port 8000
```

## ngrok

```bash
ngrok http --domain=moody-habitable-bush.ngrok-free.dev 8000
```

If either process stops:

* remote access fails
* uptime monitoring fails

---

# Current Monitoring Stack

```text
UptimeRobot
→ ngrok HTTPS tunnel
→ Mac mini
→ FastAPI SaaS
```

This provides:

* external uptime checks
* remote outage detection
* email alerting
* remote browser access
  EOF

```
```
