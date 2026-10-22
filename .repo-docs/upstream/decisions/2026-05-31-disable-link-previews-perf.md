> **上游歷史參考，非本站現行治理或待辦。** 本站規則見 [中文化治理入口](../../index.md)；不得直接執行本文的推送、部署或私有字型流程。

# ADR: Disable Hover/Link Previews for Performance

**Date:** 2026-05-31
**Status:** Accepted
**Supersedes (operationally):** [2026-03-28 Hover preview anchors](2026-03-28-hover-preview-anchors.md) — that feature is now disabled.

## Context

Pages felt extremely sluggish — the `Read/chapter/classes` page took **~31 seconds** to
become interactive after the HTML was already in the browser cache (page request served in
5 ms; the cost was entirely client-side, not network).

Systematic profiling (Chrome DevTools Performance, recorded reload of the classes page):

- **Bottom-up self time:** `resolve` ~16s, `URL` ~5.8s, `getElements` ~5s, `extract` ~4s.
- **Call tree:** ~all time under `run microtask (innerFrom.ts)` — i.e. RxJS, which is
  mkdocs-material's own runtime, **not** the repo's custom JavaScript.

The signature (`new URL()` + `resolve` per anchor, plus `getElements`/`extract` to
pre-wire tooltip content) is exactly what `material.extensions.preview` does: at render
time it walks **every** anchor on the page, resolves each link's target, and prepares
preview extraction. The classes page has **8,494 links**, so the pass is pathological.
`navigation.instant` then re-runs this work on every client-side navigation.

This was confirmed by an isolation test: disabling the preview features (keeping
`navigation.instant` and all custom JS unchanged) collapsed render time from ~31s to
~1–2s.

Key finding: page weight (2.3 MB HTML) and the repo's custom JS enhancements
(`ability-cards.js`, `tablesort.js`, etc.) were **red herrings**. The old site served the
same heavy pages with no such slowness because it had none of the preview/instant link
processing. The regression was added logic, not content size.

## Decision

Disable hover/link previews:

- Comment out `navigation.instant.preview` in `theme.features`.
- Comment out the `material.extensions.preview` markdown extension block.
- Keep `navigation.instant` enabled (it is not the dominant cost).
- Keep all custom JavaScript unchanged.

## Consequences

- Link-heavy pages (class/chapter aggregates) render in ~1–2s instead of ~31s.
- Internal links no longer show hover preview cards.
- Re-enabling previews later must **scope the `targets` include narrowly** to exclude
  link-dense aggregate pages (the per-anchor cost scales with link count). A render-time
  pass over thousands of anchors is the failure mode to avoid.
- The 2.3 MB search index and large per-page HTML remain (separate, lower-impact concerns
  tracked in the workspace `FOLLOWUPS.md`); they were not the cause of the click-to-render
  slowness.
