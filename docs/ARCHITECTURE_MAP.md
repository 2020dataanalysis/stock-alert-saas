# Stock Alert SaaS Architecture Map

## Purpose

This document explains the architecture, ownership boundaries, and responsibilities of the Stock Alert SaaS platform.

The goal is that a new engineer (or any AI assistant) can understand the system by reading this document and the project tree.

---

# System Architecture

```text
app/
├── streamer/         # Live quote ingestion
├── data_streams/     # Streaming providers
├── data_adapters/    # External provider adapters
├── signals/          # Alert engines and detectors
│
├── historical_data/  # Historical market-data subsystem
├── market_state/     # Market-state engine
├── scalp_state/      # Scalp-state engine
│
├── live/             # Live trading workstation UI
├── statistics/       # Statistics product UI
├── web/              # Main dashboard/UI
│
├── services/         # Shared application services
├── storage/          # Database/storage layer
├── config/           # Configuration
└── deploy/           # Deployment assets
```

---

# Historical Data Architecture

```text
historical_data/
├── bars/
│   ├── repository.py
│   ├── service.py
│   └── imports/
│
├── replay/
│
├── studies/
│   ├── gaps/
│   ├── openings/
│   └── statistics/
│
└── routes.py
```

---

# Ownership Rules

## bars/

Owns the historical_bars dataset.

Responsibilities:

- Create bars
- Read bars
- Update bars
- Delete bars

Files:

```text
bars/
├── repository.py
└── service.py
```

The bars module is the owner of historical bar storage.

No other module should directly access the historical_bars table.

---

## bars/imports/

Creates and updates historical bars.

Files:

```text
bars/imports/
├── backfill_service.py
├── import_service.py
└── schwab_importer.py
```

Responsibilities:

- Schwab downloads
- Historical imports
- Historical backfills
- Dataset creation

Uses bars CRUD.

---

## studies/

Reads historical bars and produces analysis.

```text
studies/
├── gaps/
├── openings/
└── statistics/
```

Examples:

- Gap analysis
- Opening analysis
- Statistical analysis
- Watchlist studies

Studies consume bars.

Studies do not own bar CRUD.

---

## replay/

Historical replay subsystem.

Contains:

- Replay routes
- Replay services
- Replay UI
- Replay templates
- Replay JavaScript

```text
replay/
├── routes.py
├── service.py
├── templates/
└── static/
```

Replay consumes historical bars for visualization and simulation.

---

# Statistics Naming Clarification

There are two different statistics areas.

## Historical Statistics

```text
historical_data/studies/statistics/
```

Purpose:

- Analyze historical bars
- Generate historical statistics
- Research and study datasets

---

## Statistics Product

```text
app/statistics/
```

Purpose:

- User-facing statistics UI
- Routes
- Templates
- JavaScript

The Statistics Product may consume historical studies but does not own them.

---

# Dependency Rules

Allowed:

```text
bars/imports -> bars

studies -> bars

replay -> bars

routes -> bars
routes -> studies
routes -> replay
```

Not Allowed:

```text
bars -> studies
bars -> replay
bars -> UI
```

The bars module owns historical bar data.

---

# Future Refactor Direction

Possible future refinement:

```text
bars/
├── repository.py
├── queries.py
└── imports/
```

or

```text
bars/
├── crud.py
├── queries.py
└── imports/
```

This would provide a clearer separation between writes and reads.

Not required today.

---

# How To Use This Document

When asking an AI for help:

1. Provide:

```bash
tree app -I "__pycache__"
```

2. Provide:

```text
docs/ARCHITECTURE_MAP.md
```

3. Provide the tree for the module being modified.

This gives enough context for an AI to understand ownership, dependencies, and intended architecture.

---

# Architectural Principle

Organize code by ownership and responsibility.

Questions to ask:

- Who owns the data?
- Who writes the data?
- Who reads the data?
- Who displays the data?

Folders should answer those questions without opening files.
