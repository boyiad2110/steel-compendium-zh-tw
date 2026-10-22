---
title: SCC-based permalink system
status: superseded
superseded_by: 2026-05-31-retire-scc-address-bar-rewrite
date: 2026-05-23
---

> **上游歷史參考，非本站現行治理或待辦。** 本站規則見 [中文化治理入口](../../index.md)；不得直接執行本文的推送、部署或私有字型流程。

# SCC-based Permalink System

> **Superseded 2026-05-31** by [Retire the SCC address-bar rewrite](2026-05-31-retire-scc-address-bar-rewrite.md).
> Layers 3 (address-bar rewrite) and 4 (manifest) were removed: they made
> `location.href` disagree with the built path and broke mkdocs-material's
> runtime search/sitemap fetch on direct page loads. Layers 1 (redirect stubs)
> and 2 (canonical, now self-canonical) remain. The historical record below is
> kept for context.

## Context

The v2 site organizes content under `Browse/` by type (class, ancestry, kit, etc.). As the site evolves, this hierarchy may change -- pages could be rearranged, categories renamed, or sections split. Any saved links would break.

Every piece of content already has a permanent SCC (Steel Compendium Classification) code in its frontmatter. We needed a way to make these codes usable as stable URLs.

## Decision

Implement a 4-layer permalink system:

1. **Raw HTML redirect stubs** at `scc/{code}/index.html` -- work without JavaScript, use relative URLs for deploy-prefix independence
2. **Canonical link override** in Jinja2 -- pages with SCC point canonical to the permalink URL
3. **Address-bar rewrite** via `history.replaceState` -- inline `<head>` script for initial load, monkey-patched `pushState` for instant-nav, `hashchange` listener for anchors
4. **Build-time manifest** mapping friendly paths to SCC paths -- enables synchronous lookup during instant-nav

## Alternatives Considered

- **Server-side redirects**: not possible on static GitHub Pages hosting
- **MkDocs aliases plugin**: doesn't support the SCC path format and adds build complexity
- **JavaScript-only (no stubs)**: breaks for JS-disabled users and search engines

## Consequences

- 1,419 redirect stub files added to `docs/scc/` (regenerated on each build)
- ~170 KB `scc-manifest.js` shipped to every page (~30 KB gzipped, cached after first load)
- Users always see SCC URLs in their address bar — including during instant-nav, since the `pushState` monkey-patch consults the manifest and substitutes synchronously
- Must keep `overrides/main.html` site_meta block in sync with mkdocs-material upgrades
- If mkdocs-material changes its instant-nav `pushState` call signature, the monkey-patch may need re-validation
