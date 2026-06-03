# Stock Alert SaaS Architecture Map

This file explains the project structure so any future AI/helper, new developer, or future version of Sam can understand the codebase from the folder tree.

The goal is that a tree layout plus this file should explain ownership, dependencies, and where new code belongs.

---

## Core Rule

Folder names should describe responsibility.

Code should be organized by what it owns, creates, reads, displays, or simulates.

For the historical data module, the most important ownership rule is:

```text
bars/ owns historical_bars CRUD.
```

That means the `bars/` module is the source of truth for the `historical_bars` dataset.

---

## Main App Areas

```text
app/
├── web/              # Main FastAPI app, shared templates, dashboard routes
├── live/             # Live trading workstation UI
├── market_state/     # Market-state engine and replay/simulation workstation
├── scalp_state/      # Scalp-state classification module
├── statistics/       # Statistics product/UI page
├── historical_data/  # Historical bars, studies, replay, and related APIs
├── services/         # Shared application services
├── storage/          # Shared SQLite/storage utilities
└── streamer/         # Live Schwab quote streamer
```

---

# Historical Data Module

Current structure:

```text
historical_data/
├── bars/
│   ├── __init__.py
│   ├── repository.py
│   ├── service.py
│   └── imports/
│       ├── __init__.py
│       ├── backfill_service.py
│       ├── import_service.py
│       └── schwab_importer.py
│
├── replay/
│   ├── __init__.py
│   ├── catalog_service.py
│   ├── date_service.py
│   ├── quote_service.py
│   ├── routes.py
│   ├── service.py
│   ├── static/
│   │   └── js/
│   │       ├── replay.js
│   │       └── replay_catalog.js
│   └── templates/
│       ├── replay.html
│       └── replay_catalog.html
│
├── studies/
│   ├── __init__.py
│   ├── gaps/
│   │   ├── __init__.py
│   │   ├── gap_analysis_service.py
│   │   ├── gap_opening_summary_service.py
│   │   ├── watchlist_gap_opening_service.py
│   │   └── watchlist_gap_service.py
│   ├── openings/
│   │   ├── __init__.py
│   │   └── opening_pattern_service.py
│   └── statistics/
│       ├── __init__.py
│       └── statistics_service.py
│
├── __init__.py
└── routes.py
```

Ignore `__pycache__/` folders. They are generated Python cache files and are not part of the architecture.

---

## historical_data/bars

```text
bars/
├── repository.py
├── service.py
└── imports/
```

### Responsibility

`bars/` owns CRUD for the `historical_bars` dataset.

CRUD means:

```text
C = Create bars
R = Read bars
U = Update bars
D = Delete bars
```

### Rule

Only `bars/` should know the database details for `historical_bars`.

That includes:

- Table name
- SQL queries
- Indexes
- SQLite database path
- Insert/upsert behavior
- Read/count behavior

Other modules should not directly query the `historical_bars` table.

They should call functions exposed by `bars/`.

---

## historical_data/bars/repository.py

### Responsibility

Low-level database access for `historical_bars`.

This file is allowed to know SQL.

Examples of responsibilities:

```text
CREATE TABLE historical_bars
INSERT / UPSERT historical_bars
SELECT historical_bars
COUNT historical_bars
```

---

## historical_data/bars/service.py

### Responsibility

API-facing helper layer around bars.

It wraps repository calls and returns response-style dictionaries for routes and other modules.

This file should remain thin unless true bar-specific business rules are added later.

---

## historical_data/bars/imports

```text
bars/imports/
├── backfill_service.py
├── import_service.py
└── schwab_importer.py
```

### Responsibility

Creates or updates bars through the `bars/` module.

This folder exists under `bars/` because these files only exist to populate the `historical_bars` dataset.

### Meaning

```text
bars/imports/
    creates or updates bars

bars/
    owns CRUD
```

### Files

```text
schwab_importer.py
```

Gets historical bar data from Schwab and converts it into the application’s bar format.

```text
import_service.py
```

Imports Schwab bar data into the local `historical_bars` dataset.

```text
backfill_service.py
```

Runs batch/backfill operations for symbols and watchlists.

---

## historical_data/studies

```text
studies/
├── gaps/
├── openings/
└── statistics/
```

### Responsibility

Reads bars and produces analysis.

Studies do not own CRUD.

Studies should not directly access the `historical_bars` table.

They should call the `bars/` module to read bar data.

---

## historical_data/studies/gaps

```text
studies/gaps/
├── gap_analysis_service.py
├── gap_opening_summary_service.py
├── watchlist_gap_opening_service.py
└── watchlist_gap_service.py
```

### Responsibility

Gap-related historical studies.

Examples:

- Calculate gap days
- Classify gap buckets
- Calculate statistics for gap buckets
- Summarize gap/opening behavior
- Run gap studies across the watchlist

---

## historical_data/studies/openings

```text
studies/openings/
└── opening_pattern_service.py
```

### Responsibility

Opening-range behavior studies.

Examples:

- Group intraday bars by day
- Analyze first N minutes after the open
- Calculate opening return, opening high, and opening low

---

## historical_data/studies/statistics

```text
studies/statistics/
└── statistics_service.py
```

### Responsibility

General historical statistics based on bars.

This is separate from the top-level `app/statistics/` module.

Important distinction:

```text
app/statistics/
    Product/UI page for viewing statistics

app/historical_data/studies/statistics/
    Historical-data calculation logic
```

---

## historical_data/replay

```text
replay/
├── catalog_service.py
├── date_service.py
├── quote_service.py
├── routes.py
├── service.py
├── templates/
└── static/
```

### Responsibility

Historical replay subsystem.

It contains:

- Replay API routes
- Replay page routes
- Replay services
- Replay templates
- Replay JavaScript

Replay is kept separate because it is a user workflow, not just a data calculation.

---

## historical_data/routes.py

### Responsibility

Historical data API surface.

This file should ideally stay thin over time.

It can import from:

```text
bars/
studies/
replay/
```

Long term, if this file becomes too large, split route groups into domain route modules.

---

# Dependency Rules

## Allowed

```text
bars/imports -> bars
studies      -> bars
replay       -> bars or replay services
routes       -> bars
routes       -> studies
routes       -> replay
```

## Not Allowed

```text
bars -> studies
bars -> replay
bars -> UI
studies -> SQL historical_bars directly
replay -> SQL historical_bars directly unless intentionally documented
```

---

# New Feature Placement Rules

Before adding a new file, ask:

## Does it own the historical_bars table?

Put it in:

```text
historical_data/bars/
```

## Does it create or update bars?

Put it in:

```text
historical_data/bars/imports/
```

## Does it analyze bars?

Put it in:

```text
historical_data/studies/<study_type>/
```

Examples:

```text
studies/gaps/
studies/openings/
studies/statistics/
studies/volatility/
studies/vwap/
studies/patterns/
```

## Does it belong to replay?

Put it in:

```text
historical_data/replay/
```

## Is it shared across the whole app?

Consider:

```text
app/services/
app/storage/
```

---

# Future Growth Notes

Possible future study folders:

```text
studies/volatility/
studies/vwap/
studies/patterns/
studies/ml_features/
```

Possible future datasets:

```text
historical_data/quotes/
historical_data/options/
historical_data/snapshots/
```

If those are added, each dataset should own its own CRUD like `bars/` does.

Example:

```text
historical_data/
├── bars/
├── quotes/
├── options/
└── studies/
```

Do not rename `historical_data/` to `historical_bars/` unless the module will permanently contain only bars.

---

# How To Give Context To Any AI

When asking an AI to help with this project, provide:

```bash
tree app/historical_data -I "__pycache__"
cat docs/ARCHITECTURE_MAP.md
```

For a smaller task, also provide:

```bash
tree app/<module-being-changed> -I "__pycache__"
```

This should allow the AI to understand the architecture without needing every file first.

---

# Refactor Rule

Before adding a feature:

1. Identify whether the code owns data, creates data, reads data, displays data, or simulates behavior.
2. Place the file based on responsibility.
3. Prefer clear capability folders over vague names like `core/`.
4. If code is unused but may be useful later, move it to a clearly named deprecated folder before deleting permanently.
5. Keep each Git branch focused on one structural change.
