> **上游歷史參考，非本站現行治理或待辦。** 本站規則見 [中文化治理入口](../../index.md)；不得直接執行本文的推送、部署或私有字型流程。

# Hover Preview with Anchor Fragments

**Status:** superseded (by [2026-05-31 Disable link previews for performance](2026-05-31-disable-link-previews-perf.md) — previews caused a ~31s render on link-heavy pages and are now disabled)
**Date:** 2026-03-28

## Context

MkDocs Material's `navigation.instant.preview` feature shows a hover popup when users mouse over internal links. However, it needs anchor fragments (`#heading-slug`) to scroll the preview to the correct section. Upstream links didn't include anchors.

## Options Considered

### No hover previews
- Pros: No build complexity
- Cons: Users must click through to see linked content; slower reference workflow

### Add anchor fragments at build time
- Pros: Hover previews show relevant section; fast reference without page navigation
- Cons: Complex perl one-liner in justfile; anchor slugs must match MkDocs heading slug algorithm; fragile if slug algorithm changes

### Request anchors from upstream
- Pros: Clean separation of concerns
- Cons: Upstream format serves multiple consumers; not all need anchors

## Decision

Added a perl substitution in the justfile that appends `#slug` anchors to all internal `.md` links. The slug is derived by lowercasing the filename, stripping non-alphanumeric characters, and replacing spaces with hyphens -- matching MkDocs Material's heading ID algorithm.

## Consequences

- Hover previews work and show the relevant section
- Build pipeline has an additional text transformation step
- If MkDocs Material changes its heading slug algorithm, anchors may break
- Multiple iterations were needed to get the regex right (visible in commit history)

## Outcome

Works well after several debugging rounds. Hover previews are one of the most-used features for quick reference during play.
