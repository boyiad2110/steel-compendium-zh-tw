> **上游歷史參考，非本站現行治理或待辦。** 本站規則見 [中文化治理入口](../../index.md)；不得直接執行本文的推送、部署或私有字型流程。

# ADR: Data islands must be found without their attributes (instant-nav script stripping)

**Date:** 2026-06-09
**Status:** Accepted
**Related:** [2026-05-31 Disable link previews](2026-05-31-disable-link-previews-perf.md) (same `navigation.instant` subsystem)

## Context

The Features index (`Browse/feature/`) renders its "Search & Filter" surface entirely
client-side: `steel-etl` emits a JSON **data island** —

```html
<div class="sc-browse-mount">
  <script type="application/json" class="sc-browse-data">[ …1.2 MB of feature JSON… ]</script>
</div>
```

— and `docs/javascripts/steel-feature-browser.js` `mount()` reads it, then replaces the
mount's contents with the live filter UI. It located the island via
`root.querySelector("script.sc-browse-data")`.

This rendered fine on **direct page loads** but the section came up **empty when reached
via client-side navigation** (e.g. feature index → a class folder → back to the index).
A prior fix (commit `1f1a5014bf`) already re-ran the mount on every `document$` emission,
so the mount *was* firing on instant nav — yet still produced nothing.

Root cause (confirmed in a real browser): **Material's `navigation.instant` recreates
inline `<script>` elements to force them to execute, and in doing so strips *all* their
attributes** — both `class="sc-browse-data"` and `type="application/json"` are gone after
a client-side nav; only the text body survives. So `script.sc-browse-data` matched nothing,
`mount()` hit its early-return guard, and the UI never built. Direct loads worked only
because the original attributes were still intact.

This is environment-dependent and easy to miss locally: a local `mkdocs build` + static
serve did **not** reproduce it, but the deployed site did, because the behaviour lives in
Material's instant-navigation runtime.

## Decision

Find the island by **falling back to the only `<script>` the mount ever contains** when
the precise selector misses:

```js
var island = root.querySelector("script.sc-browse-data") || root.querySelector("script");
```

The precise selector still wins on direct loads; the bare-`<script>` fallback covers the
instant-nav case. The generated markup is unchanged (`steel-etl` keeps emitting the
class/type — they are correct and useful on first paint); only the reader is made tolerant.

## Consequences

- "Search & Filter" renders on both direct loads and instant navigation.
- Any future inline-`<script>` **data island** that must be located after an instant nav
  cannot rely on its `class`/`type`/`id` — Material strips them. Either scope a fallback to
  the container (as here) or use a non-`<script>` carrier (`<template>`/hidden element),
  which Material does not recreate.
- The recreated bare `<script>` body (`[ {…} ]`) is a valid JS array-literal expression, so
  it evaluates harmlessly and throws no error — which is also why the failure was silent.
