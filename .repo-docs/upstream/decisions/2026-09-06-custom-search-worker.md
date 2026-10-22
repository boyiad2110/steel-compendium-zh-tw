> **上游歷史參考，非本站現行治理或待辦。** 本站規則見 [中文化治理入口](../../index.md)；不得直接執行本文的推送、部署或私有字型流程。

# Custom search worker (MiniSearch) behind Material's search UI

**Date:** 2026-09-06 · **Status:** accepted · **Ticket:** SC-306

## Context

Users reported that typing an item's exact name buried it. Replaying the
production index through Material's own worker showed only 52% of unique-title
pages ranked #1 (46% for class abilities). Causes: id-less card headings glued
onto section titles by Material's indexer (fixed in steel-etl, same ticket), a
hard-wired trailing wildcard on every term, OR semantics with no exact-match
bonus, stop-word removal, and sub-1 boosts on statblocks. The wildcard and OR
behaviour live inside Material's worker bundle and are not configurable.

## Decision

Keep Material's search UI, index plugin and `search_index.json`; replace only
the worker. `overrides/main.html` rewrites `__config.search` before the bundle
runs, pointing at `docs/javascripts/sc-search-worker.js`, which speaks
Material's 4-message protocol and delegates ranking to `sc-search-core.js`
(MiniSearch 7.2.0, vendored). Ranking: AND, prefix on the last term only, no
stop words, score × title tier (exact 100 / prefix 10 / all-terms 3), page
boost as tie-breaker (root docs only — see below), grouped per page.

**Embed exclusion depends on tag identity, not just the attribute.** Material's
search parser (`material/plugins/search/plugin.py`) tracks
`data-search-exclude` elements in a set keyed by **tag name only**, so the
attribute on a card's own `<div>`/`<section>`/`<article>` root stops excluding
at the first nested close of that same tag — a card containing another element
of its own root tag reopens indexing partway through. steel-etl's `spliceCards`
instead wraps each spliced card in
`<address class="sc-embed" data-search-exclude="">…</address>`: `address` never
otherwise occurs inside a card, so the tag-name key is unique and the whole
subtree is reliably skipped. `address` is block-level under python-markdown,
carries no Material styling, and is a generic-container ARIA role, so v2 CSS
only needs to neutralize its default rendering: `.sc-embed { display: contents;
font-style: inherit; }` (`steel-redesign.css`), plus a widened kit selector in
`steel-kit.css` to keep kit-embedded cards matching.

**Boost applies to root docs only.** steel-etl stamps a page's `search.boost`
on every indexed chunk of that page, but the ranking core applies it only to
the page's root doc (`location` without `#`) — not to its heading-anchor
sections. A boosted class page's empty `{data-scc}` heading section otherwise
ties the exact-title tier with the real leaf page and wins the tie on boost,
burying the leaf page the query actually named.

## Consequences

- Exact-title queries rank #1 98.2% on the bench (`just search-bench --gate`),
  up from a 51.8% production baseline; class abilities 100/100 (from 46/100);
  all 8 named regression queries rank their expected page #1. Part A alone
  (index-input fixes, Material's stock worker) already reaches 75.4% / 85/100
  with embed pollution at 0 — the remaining gap is lunr's trailing-wildcard /
  OR / stop-word behaviour, which Part B (this worker) replaces. Worker setup
  is ~1.6 s on 7,936 docs; index size is 5.80 MB (production 5.85 MB).
- Material upgrades can break the hook (`__config` shape) or the protocol; the
  bench and `tests/e2e/search.e2e.cjs` are the tripwire. The hook fails soft
  (stock worker stays) — a silent regression, hence the gate. A Material
  upgrade that fixes the `data-search-exclude` tag-name-keyed parser bug above
  does not break us (the `<address>` wrapper still excludes correctly either
  way); one that changes the skip semantics themselves (e.g. matches by
  attribute presence across nested same-tag elements, or drops
  `data-search-exclude` support) could.
- Alternatives rejected: Algolia (third party, eligibility), `indexing: titles`
  (loses body search), forking Material's TS worker (build chain for no gain).
  A purpose-built entity search (typeahead + facets on the Bestiary tab) remains
  the long-term direction and could replace this worker.

## Addendum 2026-09-23 — book results (SC-329)

The index now includes Read-tab (book) sections that no Browse page carries (steel-etl
`search_uncovered_only: [Read]`; covered headings are `data-search-exclude`). Book
results rank at the default boost, below boosted Browse pages. The worker appends the
book to a book result group's page title ("Combat · Draw Steel: Heroes") via
`BOOK_LABELS`, which mirrors `site.yaml` `books:` and is drift-tested. Display-only:
scores use the raw title. Spec: workspace
`docs/superpowers/specs/2026-09-23-book-search-gap-fill-design.md`.

Read sections rank at the default boost (1) — below boosted Browse pages but level
with unboosted ones such as section landing/index pages, so five exact-title lookups
(Environmental Hazards, Power Fixtures, Titles, Artifact, Ancestries) now rank their
Browse landing #2 behind the same-named book intro; the exact-title sweep moved
98.0% → 97.0%, still well above the ≥95% gate.
