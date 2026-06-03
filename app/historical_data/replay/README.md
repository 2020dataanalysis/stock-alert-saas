# Replay Module

## Purpose

Historical replay subsystem.

Provides replay APIs, replay services, replay templates, and replay JavaScript.

## Responsibilities

- Replay sessions
- Replay quotes
- Replay catalog
- Replay UI

## Structure

routes.py
service.py
templates/
static/

## Ownership Rules

Replay consumes historical bars.

Replay does not own bar storage.