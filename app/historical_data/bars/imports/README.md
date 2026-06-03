# Bar Imports

## Purpose

Create and update historical bars.

## Responsibilities

- Schwab downloads
- Historical imports
- Historical backfills

## Files

schwab_importer.py
    Provider integration.

import_service.py
    Import orchestration.

backfill_service.py
    Missing-data recovery.

## Ownership Rules

Imports do not own historical bars.

Imports use bars CRUD.