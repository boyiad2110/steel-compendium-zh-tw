---
title: Retire the SCC address-bar rewrite
status: accepted
date: 2026-05-31
supersedes: 2026-05-23-scc-permalink-system
---

> **上游歷史參考，非本站現行治理或待辦。** 本站規則見 [中文化治理入口](../../index.md)；不得直接執行本文的推送、部署或私有字型流程。

# Retire the SCC Address-Bar Rewrite

## Context

The [SCC-based permalink system](2026-05-23-scc-permalink-system.md) rewrote the
browser address bar to the SCC permalink (`/scc/<code>/`) on every page that had
an `scc` frontmatter field. It did this with an inline `history.replaceState`, an
injected `<base>` tag, a `pushState` monkey-patch for instant navigation, a
`hashchange` listener, a `<head>` `MutationObserver`, and a build-time
`scc-manifest.js` friendly→SCC path map.

This made `location.href` disagree with where the page was actually built. The
friendly Browse path is 3 segments (`Browse/<type>/<item>`) while the SCC path is
a *different, non-constant* depth (`scc/<source>/<type>/<item>` is +1; dotted
`feature.ability.<class>.level-N/<item>` codes are −2). mkdocs-material computes
its runtime fetch URLs as `new URL(config.base, location.href)` — resolved against
the **address bar**, not `document.baseURI`/`<base>`. So once the bar held the
deeper SCC path, the search index and sitemap fetched from the wrong directory:

```
/v2/scc/mcdm.heroes.v1/class/censor/  --(../../..)-->  /v2/scc/   ✗  (search_index.json 404)
/v2/Browse/class/censor/              --(../../..)-->  /v2/       ✓
```

This broke in-page search on any directly-loaded SCC-permalinked page. It was the
**second** depth-mismatch bug from the same root cause (the first was instant-nav,
worked around earlier). Every mkdocs-material upgrade was a re-audit risk because
the system fought the framework's URL resolution.

## Decision

Retire the address-bar rewrite entirely. The friendly Browse URL is the real,
canonical, indexable location. The SCC permalink stays a **stable, shareable
redirect entry point**, surfaced to humans on demand.

Remaining permalink layers (simpler, no framework-fighting):

1. **Redirect stubs** at `scc/{code}/index.html` — unchanged; resolve the SCC URL
   to the friendly page for anyone who has/shares an SCC link.
2. **Self-canonical** — the friendly page emits `<link rel="canonical">` to itself
   (`page.canonical_url`). Previously it pointed at the SCC URL, which was a
   `noindex` redirect stub — a circular, self-defeating canonical.
3. **Copy affordance** — `docs/javascripts/scc-permalink-copy.js` reads the kept
   `<meta name="scc-permalink">` and renders a "🔗 Copy permalink" button next to
   the page title, so a reader can grab the stable SCC link on demand.

Removed: `scc-permalink.js`, `scc-manifest.js` (and its steel-etl generator), the
inline `replaceState`/`<base>` script, the `pushState` monkey-patch, the
`MutationObserver`, and the `hashchange` rewrite.

## Alternatives Considered

- **Patch `config.base` to absolute before the bundle boots** (keep the rewrite):
  a correct, minimal fix, but it adds a *fourth* piece of machinery defending a
  premise that keeps costing bugs; the next framework-internal URL computation is
  a future patch waiting to happen.
- **Invert routing — serve pages at SCC paths, redirect friendly→SCC**: makes
  `location` honest so the framework "just works", but requires reworking
  steel-etl's section→path mapping, the Browse nav/IA, and the cross-reference
  link system, and bakes the ugly dotted SCC code into every visible URL. Far more
  work, worse UX; rejected.

## Consequences

- In-page search works on directly-loaded pages (the original bug, gone by
  construction — nothing lies about `location` anymore).
- Net code reduction on both the build (steel-etl) and runtime (v2) sides; no
  client-side routing layer to maintain across mkdocs-material upgrades.
- The address bar shows the **friendly** URL at rest. A bar-copied link is the
  friendly path; the guaranteed-stable SCC link is the copy button + canonical.
  If Browse is ever restructured, retired friendly paths can be given redirect
  stubs at that time.
- Google Analytics now records friendly paths as `page_path` (the bar is no longer
  rewritten to SCC).
