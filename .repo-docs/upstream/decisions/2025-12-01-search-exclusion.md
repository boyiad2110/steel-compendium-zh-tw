> **上游歷史參考，非本站現行治理或待辦。** 本站規則見 [中文化治理入口](../../index.md)；不得直接執行本文的推送、部署或私有字型流程。

# Search Exclusion for Read and Full Book

**Status:** accepted
**Date:** 2025-12-01

## Context

With the tabbed navigation layout, the same content appears under Browse, Read, and Full Book. MkDocs search would index all three copies, producing duplicate (or triplicate) results for every query.

## Options Considered

### No exclusion
- Pros: Zero build complexity
- Cons: Every search returns 2-3 duplicate results per match; confusing UX

### Exclude Read and Full Book from search
- Pros: Only Browse pages appear in search; clean, deduplicated results
- Cons: Users can't search within Read or Full Book sections directly

## Decision

Inject `search: exclude: true` YAML front matter into all Read and Full Book markdown files at build time. Only Browse pages are indexed.

## Consequences

- Search results are clean and deduplicated
- Build pipeline must inject front matter (handles both files with and without existing front matter)
- Users searching while on a Read page still get Browse results, which may require navigating to Browse

## Outcome

Effective. Eliminates the biggest UX complaint from v1's search experience.
