# Remote Access and Health Monitoring

## Architecture

```text
Internet
→ ngrok HTTPS tunnel
→ Mac mini
→ FastAPI SaaS
→ SQLite + Schwab Streamer
```

---

# Reserved ngrok Domain

```text
https://moody-habitable-bush.ngrok-free.dev
```

---

# Start FastAPI

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

# Remote Access URLs

## Base URL

```text
https://moody-habitable-bush.ngrok-free.dev
```

## Human-Facing Pages

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

Supported methods:

```text
GET
HEAD
```

Expected response:

```json
{"status":"ok"}
```

---

# FastAPI Health Route

```python
@app.api_route("/health", methods=["GET", "HEAD"])
def health():
    return {"status": "ok"}
```

This supports:
- uptime monitoring
- automated observability
- orchestration systems
- external health checks

---

# UptimeRobot Configuration

## Monitor Type

```text
HTTP / Website Monitoring
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

# Operational Requirements

Remote access requires BOTH processes running.

## FastAPI

```bash
uvicorn app.web.dashboard:app --host 0.0.0.0 --port 8000
```

## ngrok

```bash
ngrok http --domain=moody-habitable-bush.ngrok-free.dev 8000
```

If either process stops:
- remote access fails
- uptime monitoring fails
- external users cannot access the SaaS

---

# Current Monitoring Stack

```text
UptimeRobot
→ ngrok HTTPS tunnel
→ Mac mini
→ FastAPI SaaS
```

This provides:
- external uptime checks
- remote outage detection
- email alerting
- remote browser access

---

# Future Improvements

Potential future enhancements:

- persistent launchctl services
- automatic ngrok startup
- authenticated admin access
- reverse proxy via Nginx
- custom domain
- Prometheus/Grafana metrics
- heartbeat telemetry dashboard
- process supervision