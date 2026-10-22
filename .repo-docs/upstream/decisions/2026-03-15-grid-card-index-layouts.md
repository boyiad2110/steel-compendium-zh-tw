> **上游歷史參考，非本站現行治理或待辦。** 本站規則見 [中文化治理入口](../../index.md)；不得直接執行本文的推送、部署或私有字型流程。

# Grid Card Index Layouts

**Status:** accepted
**Date:** 2026-03-15

## Context

Upstream `_Index.md` files contain markdown tables listing all entries in a category. While functional, tables are dense and don't invite browsing. The Browse section needed a more visual, scannable layout.

## Options Considered

### Keep raw markdown tables
- Pros: Zero build complexity; content matches upstream exactly
- Cons: Visually dense; poor browsing UX; not mobile-friendly

### Transform tables to grid card layouts at build time
- Pros: Visual, scannable layout; groups entries by category; uses MkDocs Material grid card CSS
- Cons: Requires Python script in build pipeline; layout diverges from upstream source

### Hand-author all index pages
- Pros: Full control over layout
- Cons: Must be maintained manually for every content update; error-prone

## Decision

Created `scripts/transform_indexes.py` that parses `_Index.md` tables and renders them as `<div class="browse-index">` grid layouts. Groups entries by category when a second table column exists, or by URL path structure when it doesn't.

## Consequences

- Index pages are visually appealing and scannable
- Build pipeline has an additional Python step
- New categories upstream are automatically handled (table parsing is generic)
- Hand-authored overrides in `static_content/` can still replace any generated index

## Outcome

Significant UX improvement. Grid layouts make the Browse section feel like a reference app rather than a file listing.
