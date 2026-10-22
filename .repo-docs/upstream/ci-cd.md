---
repo: v2
doc: ci-cd
updated: 2026-09-23
---

> **上游歷史參考，非本站現行治理或待辦。** 本站規則見 [中文化治理入口](../index.md)；不得直接執行本文的推送、部署或私有字型流程。

# CI/CD

## Deployment

The site deploys to GitHub Pages at steelcompendium.io/v2.

### Manual deploy

From the workspace root:

```bash
just deploy-v2
```

Or from the v2 directory:

```bash
just update          # generate content, build docs, commit, push
```

### Build steps

1. `steel-etl gen` -- runs ETL pipeline
2. `steel-etl site` -- maps output to MkDocs structure + generates SCC stubs
3. `transform_indexes.py` -- grid card layout transform
4. `git add docs/ && git commit && git push` -- deploy

### Verification before deploy

- `mkdocs build` exits 0 (it currently emits one pre-existing link warning for
  `Read/heroes/treasures.md` → `…/swashbuckler/fancy-footwork.md`; not a regression)
- SCC stubs count matches expected (~1,419)
- Spot-check a few SCC redirect URLs manually

## GitHub Actions deploy (`.github/workflows/ci.yml`)

Every push to `main` triggers the `ci` workflow, which runs `mkdocs build` and publishes
`site/` through GitHub's **Pages artifact** (`actions/upload-pages-artifact` +
`actions/deploy-pages`). The repo's Pages source must be **"GitHub Actions"**. Note the
split of responsibilities: the `justfile` `update` recipe generates and commits `docs/` to
`main`; the **workflow only builds and deploys** the already-committed `docs/` — it does
not run `steel-etl`.

**Licensed fonts (SC-320, SC-335).** The body face, Berlingske Slab, is licensed from
Playtype and must never be in a public git repo. **This build does not carry it:** the
root site (`SteelCompendium.github.io`) hosts the files for the whole domain at
`/fonts/licensed/berlingske-slab/`, and v2's `custom_font.css` references that path. The
v2 workflow needs no secret and no private checkout. It still refuses to deploy if a
licensed font file is ever tracked in v2, because `just fonts` keeps a gitignored
local-preview copy. Rules: workspace `ARCHITECTURE.md` → "Licensed fonts"; EULA record:
[decisions/2026-09-23-licensed-berlingske-slab.md](decisions/2026-09-23-licensed-berlingske-slab.md).

One-time repo settings this depends on: Pages source **"GitHub Actions"**, and the
`github-pages` environment's deployment-branch policy allowing **`main`**.

### Build performance (~14 min as of 2026-06-05)

Measured step breakdown of a typical run (`gh run view <id> --json jobs`):

- **Checkout (`fetch-depth: 0`): ~248s** — fetches the full ~800 MB git history.
- **`mkdocs gh-deploy`: ~557s** (the deploy step before SC-320 moved it to a Pages artifact) — almost entirely the `mkdocs build` (single-threaded,
  CPU-bound; ~614s locally for 3,097 pages). Push is small.

Profiling found two bottlenecks: (1) Material re-rendering the **whole 3,097-item nav tree
on every page** (~half the build; fixable with **`navigation.prune`**, tested 614s→222s),
and (2) the `roamlinks` plugin doing a full `os.walk` per bare-filename link (~15%).

**Full investigation, numbers, and recommended fixes:** see
[decisions/2026-06-05-ci-deploy-build-time-perf.md](decisions/2026-06-05-ci-deploy-build-time-perf.md).
The fix was verified locally but **deliberately left unapplied** — closed at Scott's
request 2026-06-18 because ~14 min is acceptable; see workspace
`docs/roadmap-archive/2026-06-18-completed.md` (was ROADMAP #5). Reopen with a new
Linear ticket if deploy time becomes a pain point again.
