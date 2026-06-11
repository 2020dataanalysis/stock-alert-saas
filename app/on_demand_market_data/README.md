# On-Demand Market Data API

This module exposes live Schwab-backed market data through browser/API routes.

## Purpose

Separate fetching market data from storing market data.

Fetching Schwab data should not automatically insert into the historical
database. Database importers, replay tools, Scalp State, statistics, and ML
pipelines can consume this module independently.

## Phase 1

```text
GET /api/market-data/history/{symbol}
py
PY
