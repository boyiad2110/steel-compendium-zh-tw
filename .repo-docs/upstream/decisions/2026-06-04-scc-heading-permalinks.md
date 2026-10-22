---
title: SCC-aware heading permalinks (reuse the ¶ anchor icon)
status: accepted
date: 2026-06-04
related:
  - 2026-05-23-scc-permalink-system
  - 2026-05-31-retire-scc-address-bar-rewrite
---

> **上游歷史參考，非本站現行治理或待辦。** 本站規則見 [中文化治理入口](../../index.md)；不得直接執行本文的推送、部署或私有字型流程。

# SCC-aware Heading Permalinks

## Context

The page-title SCC permalink was surfaced as a single, oversized "🔗 Copy permalink"
button next to each page H1 (`scc-permalink-copy.js`). It was visually heavy, lived
only on the H1, and ignored the fact that most sub-headings on the big book-faithful
aggregate pages (class/chapter/ancestry) are themselves SCC-coded items with their own
stable `/scc/<code>/` redirect stubs.

mkdocs-material already renders a hover-revealed heading-anchor (¶) icon on every
heading via `toc: permalink: true` (class `.headerlink`). We wanted to reuse that
existing affordance to expose **per-heading** permalinks — stable SCC links where the
heading maps to a code, plain in-page `#anchor` links where it does not.

The hard part was telling the two apart at render time, and doing it without
depending on roadmap item 3 (in-page anchor-qualified cross-reference targets).

## Decision

- **Generator marks coded headings.** `steel-etl`'s `RenderSubtree`
  (`internal/content/render_subtree.go`) now emits an `attr_list` marker
  `{data-scc="<code>"}` on each descendant heading whose section classified to an SCC
  code. Structural headings (Basics, "1st-Level Features", advancement tables, etc.)
  get no marker. `attr_list` (already enabled) turns this into a `data-scc` attribute
  on the rendered `<hN>` without disturbing the toc-generated `id` or the `.headerlink`.
  - This required deferring `PageBody` rendering + generator writes to a post-walk pass
    in `internal/pipeline/pipeline.go`, because a parent page is visited before its
    children are classified — so the section→SCC map must be complete before any page
    body is rendered.
- **`scc-base` meta on every page.** `overrides/main.html` emits
  `<meta name="scc-base" content="{site_url}scc/">` so the client can compose
  `${scc-base}${code}/` deploy-correctly. The existing `<meta name="scc-permalink">`
  (page-level full URL) is kept and now consumed by the new script for the H1.
- **Client reuses the ¶ icon.** `docs/javascripts/scc-headerlinks.js` wires each
  heading's `.headerlink`: H1 → page `scc-permalink`; heading with `data-scc` →
  `${scc-base}${code}/`; otherwise the friendly page URL + `#id`. Click **copies to the
  clipboard and keeps** Material's native jump-to-anchor (no `preventDefault`).
  SCC-backed anchors get `.headerlink--scc` (accent color) so the durable, bookmarkable
  links are visually distinct from fragile in-page anchors.
- **Removed:** `scc-permalink-copy.js` and its `.scc-permalink-copy*` CSS; the
  page-title button is gone.

Roadmap item 3 is **not** a prerequisite: every SCC code already has a page-level
redirect stub pointing at that item's own canonical standalone page, so an SCC link
copied from an aggregate heading resolves correctly to that item's page (the
restructure-resilient behavior SCC exists for). Anchor-qualified targets are unneeded.

## Alternatives Considered

- **Keep the ¶ as a pure anchor and add a second copy icon per heading** — more DOM and
  a second affordance, against the "reuse the existing icon" goal. Rejected.
- **Inject `data-scc` on the H1 too via the site builder's H1 injection** — would unify
  the client path, but the H1 is added by `injectH1`/`injectHRAfterH1` with branchy
  logic; keeping the H1 on the existing, working `scc-permalink` meta is simpler.
- **Copy-only (suppress navigation)** — loses the native jump; "copy + jump" keeps both.

## Consequences

- Built HTML: ~284 pages carry `data-scc` `<hN>` attributes; `scc-base` meta on every
  page. Verified `data-scc` renders as a real attribute alongside the toc `id` + `.headerlink`.
- Per-heading permalink copy is light: the script scopes to `.md-content` and iterates
  only headings (tens per page), so it does not re-introduce the per-link DOM-walk cost
  that caused the ~31s render (see `2026-05-31-disable-link-previews-perf.md`).
- The clipboard holds a stable `/scc/<code>/` URL for any SCC-coded heading, copyable
  directly from the aggregate page it appears on.
