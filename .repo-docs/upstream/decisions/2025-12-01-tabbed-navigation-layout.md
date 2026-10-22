> **上游歷史參考，非本站現行治理或待辦。** 本站規則見 [中文化治理入口](../../index.md)；不得直接執行本文的推送、部署或私有字型流程。

# Tabbed Navigation Layout

**Status:** accepted
**Date:** 2025-12-01

## Context

The v1 site had a single flat navigation structure. Users needed both quick reference lookup (find one ability) and sequential reading (learn the rules chapter by chapter). A single structure couldn't serve both needs well.

## Options Considered

### Single navigation (v1 approach)
- Pros: Simple, one copy of content
- Cons: Hard to browse by category and read sequentially; search returns duplicates if content appears in multiple places

### Tabbed layout with Browse / Read / Full Book
- Pros: Each tab serves a different use case; Browse for lookup, Read for learning, Full Book for complete reference
- Cons: Same content exists in multiple structures; requires search deduplication

## Decision

Adopted tabbed navigation with three main sections: Browse (modular category pages), Read (sequential chapters), and Full Book (single-page rulebook). A Bestiary tab was added later for monster content.

## Consequences

- Users can switch between lookup and reading modes
- Requires search exclusion on Read/Full Book to prevent duplicate results
- Build pipeline must restructure upstream content into three parallel directory structures
- `justfile` complexity increased to handle the restructuring

## Outcome

Works well. Users at the table use Browse for quick lookups; new players use Read to learn the system.
