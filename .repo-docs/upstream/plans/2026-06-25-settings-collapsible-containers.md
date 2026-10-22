> **上游歷史參考，非本站現行治理或待辦。** 本站規則見 [中文化治理入口](../../index.md)；不得直接執行本文的推送、部署或私有字型流程。

# Settings Drawer — Consistent Collapsible Containers Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the **Featureblocks** and **Fonts** collapsible sections of the v2 Settings drawer render as the same bordered, collapsible "box" container the **Statblocks** section already uses, so all three read as consistent units.

**Architecture:** This is a **pure CSS change** in one file (`docs/stylesheets/steel-settings.css`). The settings drawer is injected by `settings-panel.js`, which already wraps all three sections in `<details class="sc-set__group sc-set__group--{sb,fb,fonts}">`. Today only `--sb` gets the bordered-box chrome, and only `--sb`/`--fonts` get the custom disclosure-triangle marker (`--fb` is missing from both, so Featureblocks shows the raw browser marker and no border). Rather than enumerate the three modifier classes, we retarget the box + marker rules to `details.sc-set__group` — a selector that matches exactly the three collapsible groups (the non-collapsible Reading / Page-width groups are `<div>`, not `<details>`). No JS change is required.

**Tech Stack:** Plain CSS (no preprocessor), MkDocs Material, devbox-managed toolchain.

## Global Constraints

- **Work in an isolated worktree, never the shared main checkout.** Use `just wt-new <name>` / `just wt-finish <name>` from the workspace root (`/home/vexa/code/steel_compendium/workspace`). See workspace `CLAUDE.md` rule 1.
- **Only `docs/stylesheets/` is touched.** This is on the v2 "safe to edit" list. Do **not** edit generated content (`docs/Browse/`, `docs/Read/`, `docs/scc/`).
- **All toolchain commands run under devbox:** prefix with `devbox run --` (e.g. `devbox run -- mkdocs build`). Go/node/just/mkdocs are not on the system PATH.
- **No `navigation.instant` concern:** this is CSS only — no script mount/teardown is involved.
- **Keep the `--sb` / `--fb` / `--fonts` modifier classes in the JS markup.** They stay as semantic hooks; only the CSS selectors that consume them change. Do not edit `settings-panel.js`.

---

## File Structure

- `docs/stylesheets/steel-settings.css` — the only file modified. Two rule blocks change:
  1. The collapsible-summary marker block (currently lines ~121–134), enumerated for `--fonts` + `--sb`.
  2. The bordered-box block (currently lines ~136–146), scoped to `--sb` only.

Both become scoped to `details.sc-set__group`.

---

### Task 1: Generalize collapsible-group container styling to all three sections

**Files:**
- Modify: `docs/stylesheets/steel-settings.css:121-146`

**Interfaces:**
- Consumes: the existing markup from `docs/javascripts/settings-panel.js` — three sections rendered as `<details class="sc-set__group sc-set__group--sb">` (line 297), `<details class="sc-set__group sc-set__group--fb">` (line 427), and `<details class="sc-set__group sc-set__group--fonts">` (line 446). These selectors are unchanged by this task.
- Produces: a shared `details.sc-set__group` container style. After this task, **all three** collapsible groups have an identical bordered box, dark-tint background, collapsed-state padding, and custom `▸`/`▾` disclosure triangle.

- [ ] **Step 1: Create the worktree**

From the workspace root, make an isolated environment so the edit never touches the shared main checkout:

```bash
cd /home/vexa/code/steel_compendium/workspace
just wt-new settings-containers
```

This creates `../worktrees/settings-containers` with every submodule (including `v2`) on a branch named `settings-containers`. Do all remaining steps inside `../worktrees/settings-containers/v2`.

- [ ] **Step 2: Capture the "before" baseline (build the site)**

```bash
cd ../worktrees/settings-containers/v2
devbox run -- mkdocs build
```

Expected: build completes (warnings about missing generated nav pages are fine — the settings drawer is JS-injected onto every page). This confirms the CSS file is syntactically valid before editing and gives you a `site/` to open for the visual check.

- [ ] **Step 3: Retarget the collapsible-summary marker block**

In `docs/stylesheets/steel-settings.css`, replace the enumerated `--fonts` / `--sb` marker block:

```css
.sc-set__group--fonts > summary,
.sc-set__group--sb > summary {
  cursor: pointer;
  list-style: none;
}
.sc-set__group--fonts > summary::-webkit-details-marker,
.sc-set__group--sb > summary::-webkit-details-marker { display: none; }
.sc-set__group--fonts > summary::after,
.sc-set__group--sb > summary::after {
  content: " \25B8";
  color: var(--fx-metal, var(--md-default-fg-color--lighter));
}
.sc-set__group--fonts[open] > summary::after,
.sc-set__group--sb[open] > summary::after { content: " \25BE"; }
```

with the `details.sc-set__group` form (this pulls Featureblocks into the custom-marker styling it was missing):

```css
details.sc-set__group > summary {
  cursor: pointer;
  list-style: none;
}
details.sc-set__group > summary::-webkit-details-marker { display: none; }
details.sc-set__group > summary::after {
  content: " \25B8";
  color: var(--fx-metal, var(--md-default-fg-color--lighter));
}
details.sc-set__group[open] > summary::after { content: " \25BE"; }
```

- [ ] **Step 4: Retarget the bordered-box block**

Immediately below, replace the `--sb`-only box block. Change this:

```css
/* ── Statblock group: clearly-isolated bordered box (collapsible) ── */
.sc-set__group--sb {
  border: 1px solid var(--fx-metal-line, var(--md-default-fg-color--lightest));
  border-radius: 0.55rem;
  padding: 0.75rem 0.85rem 0.85rem;
  background: rgba(0, 0, 0, 0.14);
}
[data-md-color-scheme="default"] .sc-set__group--sb { background: rgba(0, 0, 0, 0.02); }
/* collapsed: the summary is the whole box — drop its heading margin */
.sc-set__group--sb:not([open]) { padding-bottom: 0.75rem; }
.sc-set__group--sb:not([open]) > summary { margin-bottom: 0; }
```

to this (note the updated comment — the box is no longer statblock-specific):

```css
/* ── Collapsible groups (Statblocks / Featureblocks / Fonts): each is a
   clearly-isolated bordered box. Non-collapsible groups (Reading, Page
   width) are <div>, so this <details>-scoped rule leaves them untouched. ── */
details.sc-set__group {
  border: 1px solid var(--fx-metal-line, var(--md-default-fg-color--lightest));
  border-radius: 0.55rem;
  padding: 0.75rem 0.85rem 0.85rem;
  background: rgba(0, 0, 0, 0.14);
}
[data-md-color-scheme="default"] details.sc-set__group { background: rgba(0, 0, 0, 0.02); }
/* collapsed: the summary is the whole box — drop its heading margin */
details.sc-set__group:not([open]) { padding-bottom: 0.75rem; }
details.sc-set__group:not([open]) > summary { margin-bottom: 0; }
```

Leave the `/* ── Statblock group ... ── */` heading's downstream rules (the `.sc-set__sub` fieldsets that only exist inside Statblocks) exactly as they are — they are unaffected.

- [ ] **Step 5: Rebuild and confirm the CSS is valid**

```bash
devbox run -- mkdocs build
```

Expected: build completes with no new errors. (mkdocs copies the stylesheet verbatim; a build failure here would only signal a stray file issue, not CSS syntax — Step 6 is the real verification.)

- [ ] **Step 6: Visual verification — all three containers match**

Open any built page and exercise the drawer. Either serve locally:

```bash
devbox run -- mkdocs serve
```

then visit `http://127.0.0.1:8000`, **or** open a file from `site/` directly in a browser. Per the project's documented browser path, you can drive Brave headless via playwright-core (`executablePath: /opt/brave.com/brave/brave`) to capture a screenshot if you want a durable artifact.

Click the **gear** icon in the header to open Settings, then confirm:

1. **Statblocks, Featureblocks, and Fonts each sit in an identical bordered box** — same border, corner radius, and dark-tint background. (Reading and Page width remain plain, borderless groups — they must NOT gain a box.)
2. **Each of the three has the same `▸` disclosure triangle when collapsed and `▾` when open** — in particular Featureblocks no longer shows the default browser marker.
3. **Collapsed boxes look tidy** — the summary fills the box with no extra gap beneath it.
4. Toggle the OS/site theme to **light** (`data-md-color-scheme="default"`) and confirm the lighter `rgba(0,0,0,0.02)` tint applies to all three boxes.

Expected: all three collapsible sections are visually consistent; the two non-collapsible groups are unchanged.

- [ ] **Step 7: Commit inside the v2 submodule**

```bash
git add docs/stylesheets/steel-settings.css
git commit -m "style(v2): unify settings collapsible group containers (statblocks/featureblocks/fonts)"
```

- [ ] **Step 8: Land the change**

From the workspace root, finish the worktree — this pushes the v2 submodule branch and bumps the superproject pointer:

```bash
cd /home/vexa/code/steel_compendium/workspace
just wt-finish settings-containers
```

Then deploy the v2 site so the change goes live (the recipe regenerates + commits generated output itself; never hand-commit it):

```bash
just deploy-v2
```

Expected: v2 site rebuilds and deploys with the unified settings containers.

---

## Self-Review

**1. Spec coverage:** The request was "make the Featureblocks and Fonts expansions into similar containers" to the Statblocks one. Task 1 retargets both the bordered-box block and the marker block to `details.sc-set__group`, which covers all three sections — Featureblocks gains both the box and the triangle marker it lacked; Fonts gains the box. ✅

**2. Placeholder scan:** No TBD/TODO/"handle edge cases" placeholders; every CSS edit shows the exact before/after text. ✅

**3. Type consistency:** Selector name `details.sc-set__group` is used identically in Steps 3 and 4. The modifier classes `--sb`/`--fb`/`--fonts` referenced in the Interfaces block match the actual markup in `settings-panel.js` (lines 297 / 427 / 446). The marker glyphs `\25B8` (▸) and `\25BE` (▾) are preserved verbatim from the original. ✅

**Note on testing:** This is a presentational CSS-only change with no behavioral logic, so there is no meaningful unit test to add (the existing `settings-core.test.js` covers preference logic, which is untouched). Verification is the build + structured visual check in Steps 5–6.
