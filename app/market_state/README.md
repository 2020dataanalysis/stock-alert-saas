# Market State

Purpose:
Determine the current state of the market using derived features,
state classification, event tracking, and replay analysis.

Modules:

- engine     → feature calculation and state classification
- storage    → persistence layer
- live       → live market-state pipeline
- replay     → replay market-state pipeline
- events     → market-state event history
- web        → UI and API routes
