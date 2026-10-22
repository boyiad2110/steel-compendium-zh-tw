> **上游歷史參考，非本站現行治理或待辦。** 本站規則見 [中文化治理入口](../../index.md)；不得直接執行本文的推送、部署或私有字型流程。

# Switch data-md-linked to v3 Branch

**Status:** accepted
**Date:** 2026-03-01

## Context

The `data-md-linked` repo evolved its content format. The v3 branch introduced link placeholders (`REL_PATH_PREFIX`/`REL_PATH_SUFFIX`) and a restructured directory layout that better supports the v2 site's tabbed navigation.

## Options Considered

### Stay on default branch
- Pros: No migration effort
- Cons: Missing link placeholder support; content structure didn't match v2's needs cleanly

### Switch to v3 branch
- Pros: Link placeholders enable proper cross-reference resolution; directory structure aligns with Browse/Read/Full Book layout
- Cons: Justfile must be updated to clone v3 specifically; tied to a specific branch

## Decision

Changed `just update` to clone `data-md-linked` branch `v3` instead of the default branch. Updated link rewriting logic to handle the new placeholder format.

## Consequences

- Build pipeline is coupled to the `v3` branch format
- Cross-references work correctly across the restructured site layout
- If upstream changes branch naming or placeholder format, justfile must be updated

## Outcome

Successful migration. Link resolution is more reliable than the previous approach.
