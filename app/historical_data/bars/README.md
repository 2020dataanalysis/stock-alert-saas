# Bars Module

## Purpose

Owns the historical_bars dataset.

This module is the authoritative owner of historical bar storage.

## Responsibilities

- Create bars
- Read bars
- Update bars
- Delete bars

## Files

repository.py
    Database persistence layer.

service.py
    Business logic layer.

imports/
    Creates and updates historical bars.

## Ownership Rules

No other module should directly access the historical_bars table.

Consumers should use the bars module.