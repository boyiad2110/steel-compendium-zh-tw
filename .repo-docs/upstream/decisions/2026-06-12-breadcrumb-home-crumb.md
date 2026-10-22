> **上游歷史參考，非本站現行治理或待辦。** 本站規則見 [中文化治理入口](../../index.md)；不得直接執行本文的推送、部署或私有字型流程。

# Breadcrumb home crumb reads "Home"

**Status:** accepted
**Date:** 2026-06-12

## Context

Breadcrumbs (Material's `navigation.path` feature) were enabled in commit
`17fd006` ("Playing with breadcrumbs"). Material renders the leading breadcrumb
from `nav.homepage.title`, which mkdocs derives from the H1 of `docs/index.md` --
`# Xentis' Draw Steel Compendium`. That full title eats most of the breadcrumb
bar, especially on mobile.

## Options Considered

### Front-matter `title: Home` on `docs/index.md`
- Pros: one line; idiomatic mkdocs; leaves the visible H1 untouched (still
  renders "Xentis' Draw Steel Compendium" on the landing page).
- Cons: also feeds the home page's browser `<title>`, which becomes
  `Home - Steel Compendium: Draw Steel Rules` (was just the site name).

### Override `overrides/partials/path-item.html`
- Pros: surgical -- touches only the breadcrumb, no browser-title change.
- Cons: copies an upstream auto-generated partial that can drift on Material
  upgrades; more to maintain.

## Decision

Front-matter `title: Home` on `docs/index.md`. The browser-title side effect is
conventional and acceptable; avoiding a forked Material partial is worth more
than keeping the home `<title>` as the bare site name.

`docs/index.md` is a hand-maintained file -- the `clean_docs` justfile recipe
explicitly preserves it across `steel-etl site` regenerations, so the edit is
durable.

## Consequences

- Breadcrumb root reads "Home"; far shorter on mobile.
- Home page browser tab title is now `Home - Steel Compendium: Draw Steel Rules`.
- Visible landing-page H1 is unchanged.

## Outcome

Leave blank if recent. Fill in once there's real experience to report.
