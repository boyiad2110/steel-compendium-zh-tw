---
repo: v2
doc: development
updated: 2026-07-02
---

> **上游歷史參考，非本站現行治理或待辦。** 本站規則見 [中文化治理入口](../index.md)；不得直接執行本文的推送、部署或私有字型流程。

# Development

## Prerequisites

- Python 3.x with pip
- Go toolchain (via devbox -- see workspace CLAUDE.md)
- `just` command runner (via devbox)

## Setup

```bash
# From workspace root, activate devbox
devbox run --

# Install Python dependencies
pip install mkdocs-material mkdocs-roamlinks-plugin mkdocs-awesome-nav-plugin

# Generate content and build docs/
cd v2
just update push=false

# Preview locally (runs `just fonts` first)
just serve
```

**Licensed fonts.** The deployed site loads Berlingske Slab from the root site's
`/fonts/licensed/`, which `mkdocs serve` can't reach. So for local preview, `just fonts`
clones the private `SteelCompendium/licensed-fonts` repo into `.licensed-fonts/` and
installs a copy into `docs/stylesheets/licensed-fonts/`. Each `@font-face` falls back to
that copy. Both paths are gitignored — **never commit the font files**; the repo is
public and the Playtype license forbids it. Without access to that repo, body text
renders in Zilla Slab. Rules: workspace `ARCHITECTURE.md` → "Licensed fonts".

## Development Workflow

### Editing presentation (CSS, JS, templates)

1. Run `just serve` for live preview
2. Edit files in `docs/javascripts/`, `docs/stylesheets/`, or `overrides/`
3. MkDocs auto-reloads on save

### Overriding generated content

1. Find the generated file under `docs/` (e.g., `docs/Browse/index.md`)
2. Copy it to the same path under `static_content/docs/`
3. Edit the copy -- `steel-etl site` copies `static_content/` last, so your version wins
4. Run `just update push=false` to verify

### Modifying site structure

Site structure is controlled by `site.yaml`, not by moving files. To change which content appears in which section, edit `site.yaml` and re-run `just update push=false`.

### Modifying the content pipeline

Content generation is handled by `steel-etl`. See `steel-etl/CLAUDE.md` for that workflow.

## Build Process

`just update` runs these steps:

1. `steel-etl gen` -- full ETL pipeline (parse, classify, output)
2. Embed steel-etl version into `mkdocs.yml` copyright
3. `steel-etl site` -- map output into MkDocs structure, generate SCC stubs
4. `transform_indexes.py` -- convert Browse index pages to grid card layouts
5. (Optional) commit and push

## Testing

Three layers:

**Unit (node:test).** Every interactive feature splits pure logic into a
`docs/javascripts/<name>-core.js` UMD module with a matching `tests/<name>-core.test.js`.
Run with an explicit glob — this Node version rejects a bare directory argument:

```bash
node --test tests/*.test.js
```

**e2e (`tests/e2e/*.e2e.cjs`).** Real-browser checks driving the locally installed
Brave via playwright-core + `executablePath` (the Playwright MCP / chrome channel is
broken in this environment). Each file documents its own run recipe; the shape is:

```bash
mkdocs build
python3 -m http.server 8124 --directory site &
node tests/e2e/page-titles.e2e.cjs        # H1 visible on containers, hidden on card leaves
node tests/e2e/cardhead-mobile.e2e.cjs    # statblock name doesn't letter-wrap at 390px
```

Both also accept `E2E_BASE=https://steelcompendium.io/v2/` to run against production.

**Manual smoke** after a build:

- `mkdocs build` exits 0 with no new warnings
- Redirect stubs work (visit `/v2/scc/{any-code}/` directly)
- Heading ¶ anchors copy `/scc/…` on coded headings (see troubleshooting.md)
- `navigation.instant` behaviors (mini-TOC, tray, pins mount exactly once per swap)
  reproduce **only on the deployed site** — recheck after deploy, not just locally

The steel-etl side has Go tests for all site-builder transforms (`internal/site/*_test.go`).

## Troubleshooting

See [troubleshooting.md](troubleshooting.md).

## My Table custom links

`sc-pins-core.js` owns validation and insertion; `sc-pins.js` mounts the form
next to `.sc-pins-mount` on each Material navigation. Existing version-1 saved pins
remain compatible. Custom links use the same `{path,title,kind,ts}` records with
`kind: "Custom links"`. Same-origin URLs become root-relative paths, preserving
queries and anchors. Re-adding a path updates its display name and group. New custom
links at the 200-item limit are rejected without evicting a saved pin.

Only HTTP(S) URLs and root-relative paths are accepted, including when reading
storage. Labels render as escaped text. User-defined categories are tracked in SC-178.
Browser coverage: `tests/e2e/pins-custom-links.e2e.cjs` (set `E2E_BASE` and optionally
`PLAYWRIGHT_PATH` to your installed playwright-core module).

### Saved heading excerpts

`sc-pins-sections.js` loads same-site heading fragments and SCC permalinks on demand.
SCC HTML stubs resolve through their canonical target (bounded to the same site root,
without executing scripts). DOM ranges include everything after the selected heading
through, but excluding, the next equal-or-higher heading; this works across nested
wrappers and includes subordinate headings and tables. Missing headings fail explicitly.

The board presents native collapsible sections, preserving open states during mutations
and aborting old requests on rerender/navigation. Excerpts preserve book markup but strip
scripts and page controls, resolve relative resource/link URLs against the source, namespace
IDs, and wrap wide tables for horizontal scrolling. They are read-only excerpts; live
page tools remain on the original page. External links are never fetched. No HTML is
stored in localStorage. `tests/e2e/pins-sections.e2e.cjs` covers the Monsters examples,
SCC resolution, missing anchors, section boundaries and reload behavior.

### My Table layout

The add-section form is collapsed behind a button with `aria-expanded` and
`aria-controls`. Opening focuses the name field; Cancel, Escape, and successful save
close the form and restore focus to the trigger. Validation errors keep it open.
Save confirmation lives in the visible toolbar's live region. The title and category
headings use compact, board-scoped styles. Custom categories remain SC-178.
`tests/e2e/pins-layout.e2e.cjs` covers the disclosure, focus, save/cancel and mobile layout.
