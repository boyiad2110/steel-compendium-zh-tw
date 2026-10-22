> **上游歷史參考，非本站現行治理或待辦。** 本站規則見 [中文化治理入口](../../index.md)；不得直接執行本文的推送、部署或私有字型流程。

# Decision Log

Architectural and design decisions for the Steel Compendium v2 site.

## Why Log Decisions

- Context doesn't survive in memory. Recording why a choice was made prevents relitigating it later.
- Small decisions compound. A record of what worked (and what didn't) builds a navigable history of the project's evolution.

## What to Log

Every decision, regardless of size:
- Library and plugin choices
- Content structure changes
- UI/UX approaches tried and abandoned
- Link format and build pipeline decisions
- Convention choices
- Reverted experiments

## How to Create a Record

1. Copy the template below into a new file
2. Name it `YYYY-MM-DD-short-description.md`
3. Fill in all sections
4. Set the status

## Filename Convention

`YYYY-MM-DD-short-description.md` -- files sort chronologically. Multiple decisions on the same date are fine.

## Status Definitions

| Status | Meaning |
|--------|---------|
| `proposed` | Under consideration, not yet implemented |
| `accepted` | Chosen and implemented |
| `tried` | Implemented but didn't work out |
| `superseded` | Replaced by a later decision |
| `deprecated` | Being phased out |

## Template

```markdown
# Title

**Status:** proposed | accepted | tried | superseded | deprecated
**Date:** YYYY-MM-DD

## Context

Why was this decision needed?

## Options Considered

### Option A
- Pros: ...
- Cons: ...

### Option B
- Pros: ...
- Cons: ...

## Decision

What was chosen and why.

## Consequences

- Positive outcomes
- Accepted tradeoffs

## Outcome

Leave blank if recent. Fill in once there's real experience to report.
```

## Index

| Date | Decision | Status |
|------|----------|--------|
| 2025-12-01 | [Tabbed navigation layout](2025-12-01-tabbed-navigation-layout.md) | accepted |
| 2025-12-01 | [Search exclusion for Read and Full Book](2025-12-01-search-exclusion.md) | accepted |
| 2025-12-01 | [No mike versioning](2025-12-01-no-mike-versioning.md) | accepted |
| 2026-03-01 | [Switch data-md-linked to v3 branch](2026-03-01-switch-to-v3-branch.md) | accepted |
| 2026-03-15 | [Grid card index layouts](2026-03-15-grid-card-index-layouts.md) | accepted |
| 2026-03-28 | [Hover preview with anchor fragments](2026-03-28-hover-preview-anchors.md) | superseded |
| 2026-05-23 | [SCC-based permalink system](2026-05-23-scc-permalink-system.md) | superseded |
| 2026-05-31 | [Retire the SCC address-bar rewrite](2026-05-31-retire-scc-address-bar-rewrite.md) | accepted |
| 2026-05-31 | [Disable link previews for performance](2026-05-31-disable-link-previews-perf.md) | accepted |
| 2026-06-05 | [CI deploy build-time performance investigation](2026-06-05-ci-deploy-build-time-perf.md) | proposed |
| 2026-06-09 | [Data islands must be found without their attributes (instant-nav script stripping)](2026-06-09-instant-nav-strips-script-attrs.md) | accepted |
| 2026-06-11 | [Client scripts that mount page content must be navigation.instant-safe](2026-06-11-client-scripts-navigation-instant.md) | accepted |
| 2026-06-12 | [Breadcrumb home crumb reads "Home"](2026-06-12-breadcrumb-home-crumb.md) | accepted |
| 2026-09-06 | [Custom search worker (MiniSearch) behind Material's search UI](2026-09-06-custom-search-worker.md) | accepted |
| 2026-09-23 | [Licensed Berlingske Slab: self-hosted, never in git, deployed by Pages artifact](2026-09-23-licensed-berlingske-slab.md) | accepted |
