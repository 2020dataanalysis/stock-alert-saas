You’re right. We should create a project-readable architecture file.

Create this:

````bash
cd /Users/ultrasupersam/apps/stock-alert-platform/stock-alert-saas

echo "================ CREATE ARCHITECTURE README BRANCH ================"
git switch -c docs/add-architecture-map

echo "================ CREATE ARCHITECTURE README ================"
cat > docs/ARCHITECTURE_MAP.md <<'EOF'
# Stock Alert SaaS Architecture Map

This file explains the project structure so any future AI/helper can understand the codebase from the folder tree.

## Core Rule

Folder names should describe capabilities.

Code should be organized by what it owns, writes, reads, or displays.

## Main App Areas

```text
app/
├── web/              # Main FastAPI app, shared templates, dashboard routes
├── live/             # Live trading/replay workstation UI
├── market_state/     # Market-state engine and replay/simulation workstation
├── scalp_state/      # Scalp-state classification module
├── statistics/       # Statistics product page and frontend JS
├── historical_data/  # Historical market-data storage, imports, analytics, replay
├── services/         # Shared app services
├── storage/          # Shared SQLite/storage utilities
└── streamer/         # Live Schwab quote streamer
````

## Historical Data Mental Model

```text
historical_data/
├── bars/             # Owns historical_bars storage and access
├── imports/          # Writes/imports bars from Schwab/backfills
├── bar_analytics/    # Reads bars directly and calculates statistics/patterns
├── replay/           # Historical replay UI/API/services
└── routes.py         # Thin router/orchestration layer
```

## Dependency Direction

```text
imports/
    writes to bars/

bar_analytics/
    reads from bars/

statistics/
    displays results from historical_data APIs

replay/
    handles replay-specific pages, APIs, and JS

market_state/
    handles state replay/simulation/backtesting behavior
```

## Naming Rules

* `bars/` means code that owns or directly manages `historical_bars`.
* `imports/` means code that creates/imports historical bars.
* `bar_analytics/` means code that reads historical bars and calculates derived results.
* `statistics/` is the product/UI module for viewing statistics.
* `replay/` should contain replay-specific routes, services, templates, and JS.
* Avoid vague folders like `core/` unless there is no clearer domain name.

## Refactor Rule

Before adding a new feature:

1. Run `tree app/<module>/`
2. Identify whether the feature owns data, writes data, reads data, displays data, or simulates behavior.
3. Place files based on capability, not convenience.
4. If code is unused but may be useful later, move it to a clearly named deprecated folder instead of deleting immediately.

## Current Cleanup Direction

The historical_data folder is being organized toward:

```text
historical_data/
├── bars/
├── imports/
├── bar_analytics/
├── replay/
└── routes.py
```

The purpose is to make it possible to understand the module from the tree layout alone.
EOF

echo "================ VERIFY README ================"
cat docs/ARCHITECTURE_MAP.md

echo "================ STATUS ================"
git status

```

This gives you a portable file you can paste to any AI later.
```
