---
repo: v2
doc: project
updated: 2026-05-23
---

> **上游歷史參考，非本站現行治理或待辦。** 本站規則見 [中文化治理入口](../index.md)；不得直接執行本文的推送、部署或私有字型流程。

# Project

## Vision

Provide the most usable, searchable, and linkable online reference for the Draw Steel TTRPG rules. Every piece of content has a permanent SCC-based URL that survives site reorganization.

## Audiences

- **Players**: browsing classes, abilities, ancestries, kits, and other character options
- **Directors**: referencing rules chapters, conditions, complications
- **Content creators**: linking to specific rules with stable permalinks

## Glossary

| Term | Meaning |
|------|---------|
| SCC | Steel Compendium Classification -- hierarchical code identifying every piece of content (e.g., `mcdm.heroes.v1/class/fury`) |
| Browse | Tab section with modular rules pages organized by content type |
| Bestiary | Tab section with modular Monsters-book pages (monster groups, statblocks, malice, terrain, retainers); monster group pages are lore-only |
| Read | Tab section with full rulebook chapters in book order, grouped per book (book-faithful, everything inline) |
| Composite | A generated page that aggregates traits and abilities into a parent page (e.g., all fury abilities merged into the fury class page) |
| Group | A remapping that nests related content under a parent directory (e.g., kit signature abilities under `Kits/`) |
| Static content | Hand-authored files in `static_content/docs/` that override generated content |
| steel-etl | The Go CLI tool that parses annotated markdown and generates all output formats |

## Related Repos

| Repo | Relationship |
|------|-------------|
| `steel-etl/` | Generates all content; the `site` command builds this repo's `docs/` directory |
| `data/data-rules/` | Source markdown that steel-etl reads |
| `draw-steel-elements/` | Obsidian plugin -- consumes the same ETL output in a different directory structure |
| `steelCompendium.github.io/` | GitHub Pages deployment target |
