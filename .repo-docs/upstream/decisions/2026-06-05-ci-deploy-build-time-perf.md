> **上游歷史參考，非本站現行治理或待辦。** 本站規則見 [中文化治理入口](../../index.md)；不得直接執行本文的推送、部署或私有字型流程。

# ADR: CI Deploy Build-Time Performance Investigation

**Date:** 2026-06-05
**Status:** Proposed — investigated and measured, **not yet applied** (changes deferred at
the user's request). This ADR records the findings so the work can be picked up later.
**Scope:** *Build/deploy wall-clock time* in CI. This is distinct from
[2026-05-31 Disable link previews](2026-05-31-disable-link-previews-perf.md) and ROADMAP
item 1, which are about *client-side page-load/render* time. Different problem, different
fix — don't conflate them.

## Context

The `ci` workflow (`v2/.github/workflows/ci.yml`) deploys to GitHub Pages on every push to
`main` and takes **~13–14 minutes** (sampled runs: 13m45s, 13m44s, 13m06s, 10m44s). Most
pushes to `main` are `chore: update v2 site content` commits from `steel-etl`, so this cost
is paid on nearly every content change.

### Measured step breakdown (run 27036833183, 13m45s)

Pulled via `gh run view <id> --json jobs`:

| Step | Time | Notes |
|------|-----:|-------|
| Check out the code (`fetch-depth: 0`) | **248s (4.1 min)** | Fetches full git history |
| Set up Python | 0s | |
| Cache site build (`.cache`) | 1s | **Does nothing** — see below |
| Install dependencies (`pip install …`) | 11s | No pip cache |
| **Run `mkdocs gh-deploy --force`** | **557s (9.3 min)** | The build dominates; push is small |

So the time splits into two real targets: a **~4 min checkout** and a **~9 min build**.

### The build is the bottleneck, and it is CPU-bound single-threaded

A clean local `mkdocs build` (no checkout, no push) measured with `/usr/bin/time -v`:

```
Documentation built in 614.11 seconds   (10:14 wall, 99% CPU on ONE core, 207 MB RSS)
```

3,097 markdown pages → 5,740 output files, 44 MB `docs/`. `mkdocs` is single-threaded
Python, so more CPU *cores* won't help; only per-core speed or less work will.

### Profiling pinned the cost to TWO things (cProfile, sorted by self time)

Run: `python -m cProfile -o mkdocs.prof mkdocs build` (profiler inflates total to ~1429s;
use the *ranking*, not absolute numbers).

**1. Navigation rendering — the dominant cost (~half the build).**

```
ncalls          tottime  cumtime  function
9594506/15490   170.4s   1047.1s  material/templates/partials/nav-item.html:227(macro)
188209859       123.8s    235.2s  jinja2/environment.py:485(getattr)
9594687          75.7s    333.0s  material/templates/partials/nav-item.html:110(macro)
11162275         28.4s     87.0s  material/templates/partials/nav-item.html:81(macro)
```

Material re-renders the **entire 3,097-item navigation tree on every one of the 3,097
pages** → an **O(pages × nav-size)** blowup (**9.5 million** `nav-item.html` macro calls).
This is a known large-site Material problem. With `navigation.tabs` + a deep `Browse` tree
(2,332 items) the sidebar is huge, and it is rebuilt per page.

**2. The `roamlinks` plugin — secondary (~15%).**

```
ncalls      tottime  cumtime  function
10873573    53.6s    251.9s   <frozen os>:286(walk)
10870547    39.7s     39.7s   posix.scandir
9762270     38.4s     52.8s   mkdocs/utils/__init__.py:177(get_relative_url)
10863965    34.6s     34.6s   posix.lstat
```

Root cause is in the **unmaintained** `mkdocs-roamlinks-plugin` v0.3.2
(`.venv/lib/python3.12/site-packages/mkdocs_roamlinks_plugin/plugin.py`):

- `AutoLinkReplacer.__call__` (lines 46–55): for every markdown link whose target is a
  **bare filename** (`AUTOLINK_RE` matches `[text](file.md)` / `.png` / `.jpg` with **no
  `/`**), it does a **full recursive `os.walk` of the entire `docs/` tree** — and has **no
  early `break`**, so it keeps walking all 5,740 files even after finding the match.
- `RoamLinkReplacer.__call__` (lines 125–136): same `os.walk` pattern for `[[wikilinks]]`.

Link census of the generated `docs/` (via `grep -rhoE`):

| Link shape | Count | Cost |
|------------|------:|------|
| Bare filename `[text](file.md)` (no slash) | **3,094** | **Triggers full `os.walk`, no break** |
| Roam `[[wikilink]]` | 0 | (none emitted) |
| Path-style `[text](../foo/bar.md)` (has slash) | 10,412 | Cheap — regex skips anything with `/` |

So ~3,094 links × 5,740 files ≈ **~18M filename comparisons** plus 3,094 full directory
traversals (`scandir`/`lstat`). The 10,412 path-style links — the majority — are free
because the regex excludes `/`. (Sample bare links: `[prone](prone.md)`,
`[academic](academic.md)`, `[Shining Armor](shining-armor.md)`.)

### Why the checkout is slow

`.git` is **~800 MB packed** (360k objects) for only 203 commits on `main` + 163 on
`gh-pages`. The largest blobs are `search/search_index.json` (~8 MB **each**) accumulating
on the `gh-pages` branch every deploy, plus `main` churning all 44 MB of `docs/` on every
`steel-etl` content commit. `fetch-depth: 0` fetches all of it.

## Measured fix: `navigation.prune`

Material's built-in `navigation.prune` renders only the visible branch of the nav per page
instead of the whole tree — directly targeting bottleneck #1. Tested locally by adding the
single line under `theme.features` and rebuilding:

| Build | Time |
|-------|-----:|
| Current | **614s** |
| + `navigation.prune` | **222s** |

**−393s (~64% faster build) from one line.** Build completed with no new warnings.

**Compatibility:** `navigation.prune` works with the features in use (`navigation.tabs`,
`navigation.tabs.sticky`, `navigation.top`, `navigation.instant`). Its only hard
incompatibility is `navigation.expand` (not used here).

**Trade-off (the one thing to eyeball):** the sidebar renders only the active branch's
ancestors/siblings rather than the full expanded tree. On a 3,097-page site this is
generally a *cleaner* UX, and `navigation.tabs` keeps top-level navigation intact — but it
is a visible change, so verify the nav still feels right before accepting.

## Recommended changes (priority order — NOT yet applied)

1. **Add `navigation.prune` to `mkdocs.yml`** under `theme.features` (after
   `navigation.top`). Tested: **−393s (~6.5 min)**. Highest value, one line. Eyeball the
   sidebar UX.
2. **Set `fetch-depth: 1` in `ci.yml`** (currently `0`). `mkdocs gh-deploy` → `ghp-import`
   force-pushes a fresh `gh-pages` and fetches that branch itself; it does **not** need
   `main`'s history. Expected **~−3.5 min** (248s → well under a minute). No plugin in use
   (`search`, `roamlinks`, `awesome-nav`) reads git history. Low risk; verify one deploy.
3. **(Optional, ~−60–90s) Fix the `roamlinks` O(links × files) walk.** Two clean paths:
   - Vendor a patched plugin that builds a `{simplified_name: path}` index **once** (e.g.
     on the `on_files` event) for O(1) lookup, and/or add a `break` after the match; or
   - Have `steel-etl` emit **full-path** links for those 3,094 bare links so `AUTOLINK_RE`
     (which excludes `/`) skips them entirely — same mechanism that already makes the
     10,412 path-style links free.
4. **(Cleanup) Remove the `Cache site build` step.** It caches `.cache`, which only
   Material's `social`/`optimize` plugins populate — neither is enabled, so the cache is
   always empty. Harmless but pointless. (Optionally add `cache: pip` to
   `actions/setup-python` instead; only ~11s, low value.)
5. **(Housekeeping) `gh-pages` / `.git` bloat.** `gh-pages` accumulates an ~8 MB
   `search_index.json` commit every deploy and is never pruned (→ ~800 MB `.git`).
   Periodically squashing/orphaning `gh-pages` history would shrink clones; combined with
   `fetch-depth: 1` on `main` this keeps CI checkout cheap long-term.

**Items 1 + 2 alone are expected to take CI from ~14 min to ~5 min**, both low-risk.

## Verification notes for whoever applies this

- Re-time locally: `mkdocs build` reports `Documentation built in N seconds`. Baseline is
  ~614s; with `navigation.prune` expect ~220s.
- Confirm the existing build warning is unrelated/pre-existing: `Read/heroes/treasures.md`
  links `../../Browse/feature/ability/swashbuckler/fancy-footwork.md` (target not found).
  `ci-cd.md` previously claimed "no warnings" — that is already false; don't treat it as a
  regression from these changes.
- After `fetch-depth: 1`, confirm `gh-deploy` still updates `gh-pages` correctly (the
  deployed site is served from `gh-pages`, built fresh each run).
