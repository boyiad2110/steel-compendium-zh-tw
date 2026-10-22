> **上游歷史參考，非本站現行治理或待辦。** 本站規則見 [中文化治理入口](../../index.md)；不得直接執行本文的推送、部署或私有字型流程。

# No Mike Versioning

**Status:** accepted
**Date:** 2025-12-01

## Context

MkDocs supports multi-version deployment via the `mike` tool, which maintains separate builds per version on the `gh-pages` branch. The question was whether v2 needed versioned deployments.

## Options Considered

### Use mike for versioned deploys
- Pros: Can maintain multiple versions simultaneously; supports version dropdown
- Cons: Additional complexity; Draw Steel content updates frequently and old versions become incorrect quickly

### Single-branch deploy with mkdocs gh-deploy
- Pros: Simpler build and deploy; always shows latest content; no stale versions
- Cons: No way to view previous versions of the site

## Decision

Use `mkdocs gh-deploy --force` for single-branch deployment. No version management.

## Consequences

- Simpler CI pipeline (just `mkdocs gh-deploy --force`)
- Always up to date with latest content
- No rollback to previous content versions via the site (git history serves that need)

## Outcome

Appropriate for a living reference site. Content updates weekly; versioning would just create stale copies.
