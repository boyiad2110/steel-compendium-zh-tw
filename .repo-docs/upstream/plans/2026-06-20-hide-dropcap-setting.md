> **上游歷史參考，非本站現行治理或待辦。** 本站規則見 [中文化治理入口](../../index.md)；不得直接執行本文的推送、部署或私有字型流程。

# Hide Drop Caps Setting Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a single global on/off setting to the v2 site that removes the engraved drop cap from lead trait cards.

**Architecture:** Follow the existing user-preference pattern exactly (mirrors the `Compact mode` toggle): a boolean `prefs.noDropcap` persisted in the `mkdocs:fontPrefs` localStorage store; stamped as a `data-no-dropcap` attribute on `<html>` by both the no-FOUC early-apply script (`overrides/main.html`) and the live drawer (`settings-panel.js`); one CSS selector in `steel-traits.css` suppresses the drop-cap `::first-letter` rule when the attribute is present. Default (attribute absent) = current behavior, drop caps shown.

**Tech Stack:** Vanilla ES5 JS (no build step), CSS, MkDocs Material `overrides/` Jinja template.

## Global Constraints

- **Never edit generated content.** All files in this plan are under safe-to-edit paths (`docs/javascripts/`, `docs/stylesheets/`, `overrides/`, `static_content/`, workspace `DESIGN.md`). Do not touch `docs/Browse/`, `docs/Read/`, or `docs/scc/`.
- **Client JS must be `navigation.instant`-safe.** `settings-panel.js` already registers via `document$` and keeps `init()` idempotent — preserve that; do not add `DOMContentLoaded` handlers.
- **Persistence convention:** store only the non-default. `noDropcap` is written as `true` when on and `delete`d when off (mirrors `prefs.compact`). Absent ≡ `false` ≡ drop caps shown.
- **Both color schemes:** the change is a structural suppression (no new colors), so it works in light and dark automatically — no scheme-specific CSS needed.
- All paths below are relative to the `v2/` repo root unless prefixed with `workspace`.

---

### Task 1: Suppress the drop cap via a `data-no-dropcap` CSS gate

**Files:**
- Modify: `docs/stylesheets/steel-traits.css:129-135`

**Interfaces:**
- Consumes: nothing (first task).
- Produces: the contract that `<html data-no-dropcap>` hides all lead-trait drop caps. Tasks 2 and 3 stamp that attribute.

- [ ] **Step 1: Scope the drop-cap rule to the absence of the attribute**

In `docs/stylesheets/steel-traits.css`, the current block is:

```css
/* optional engraved drop cap on the opening paragraph (modifier) */
.sc-trait--lead .sc-trait__body > p:first-of-type { overflow: hidden; }
.sc-trait--lead .sc-trait__body > p:first-of-type::first-letter {
  font-family: var(--md-large-header-font); font-size: 3.15em; line-height: .72;
  float: left; margin: .06em .12em 0 0; padding-top: .04em;
  color: var(--fx-metal-bright); text-shadow: var(--fx-emboss);
}
```

Replace it with (only the `::first-letter` selector is gated; the `overflow:hidden` float-container rule stays unconditional — it is harmless with no floated letter):

```css
/* optional engraved drop cap on the opening paragraph (modifier).
   Suppressed globally by the "Hide drop caps" setting (data-no-dropcap on <html>). */
.sc-trait--lead .sc-trait__body > p:first-of-type { overflow: hidden; }
:root:not([data-no-dropcap]) .sc-trait--lead .sc-trait__body > p:first-of-type::first-letter {
  font-family: var(--md-large-header-font); font-size: 3.15em; line-height: .72;
  float: left; margin: .06em .12em 0 0; padding-top: .04em;
  color: var(--fx-metal-bright); text-shadow: var(--fx-emboss);
}
```

- [ ] **Step 2: Verify the rule is syntactically valid and the selector changed**

Run: `grep -n "data-no-dropcap" docs/stylesheets/steel-traits.css`
Expected: one line — the `:root:not([data-no-dropcap]) .sc-trait--lead …::first-letter {` selector.

- [ ] **Step 3: Commit**

```bash
git add docs/stylesheets/steel-traits.css
git commit -m "feat(v2): gate lead-trait drop cap on data-no-dropcap"
```

---

### Task 2: Seed `data-no-dropcap` in the no-FOUC early-apply script

**Files:**
- Modify: `overrides/main.html:81`

**Interfaces:**
- Consumes: the `data-no-dropcap` CSS contract from Task 1; the `mkdocs:fontPrefs` object already parsed into `s` at `overrides/main.html:72`.
- Produces: `data-no-dropcap="true"` stamped on `<html>` before first paint when `s.noDropcap` is truthy. Task 3 keeps it in sync live.

- [ ] **Step 1: Add the early-apply line next to the Compact line**

In `overrides/main.html`, find (line 81):

```javascript
            if (s.compact) document.documentElement.setAttribute("data-compact", "true");
```

Add immediately after it:

```javascript
            if (s.noDropcap) document.documentElement.setAttribute("data-no-dropcap", "true");
```

- [ ] **Step 2: Verify**

Run: `grep -n "data-no-dropcap" overrides/main.html`
Expected: one line inside the early-apply `<script>` block (around line 82).

- [ ] **Step 3: Commit**

```bash
git add overrides/main.html
git commit -m "feat(v2): seed data-no-dropcap in early-apply (no FOUC)"
```

---

### Task 3: Add the live drawer toggle in `settings-panel.js`

**Files:**
- Modify: `docs/javascripts/settings-panel.js` — `applyAll` (≈156-167), Reading group markup (≈252-257), `bindDrawer` Compact binding (≈561-569), Reset handler (≈622-641), plus a new `applyDropcap` fn near `applyCompact` (≈104-106).

**Interfaces:**
- Consumes: the `data-no-dropcap` CSS contract (Task 1); `prefs` object, `persist()`, and the existing drawer/bind/reset scaffolding.
- Produces: a Reading-group checkbox `#set-no-dropcap` that toggles `prefs.noDropcap` and applies `data-no-dropcap` live; reset clears it. This is the user-facing surface — no later task consumes it.

- [ ] **Step 1: Add the `applyDropcap` side-effect fn**

In `docs/javascripts/settings-panel.js`, immediately after `applyCompact` (currently lines 104-106):

```javascript
  function applyCompact(on) {
    document.documentElement.setAttribute("data-compact", on ? "true" : "false");
  }
```

add:

```javascript
  function applyDropcap(off) {
    // absent attribute ≡ drop caps shown; only stamp the explicit "hide" state
    if (off) document.documentElement.setAttribute("data-no-dropcap", "true");
    else document.documentElement.removeAttribute("data-no-dropcap");
  }
```

- [ ] **Step 2: Call it from `applyAll`**

In `applyAll` (currently lines 156-167), after the `applyCompact(!!prefs.compact);` line, add:

```javascript
    applyDropcap(!!prefs.noDropcap);
```

- [ ] **Step 3: Add the checkbox markup to the Reading group**

In `buildDrawer`, the Reading group currently ends with the Compact row (lines 252-257):

```javascript
          '<div class="sc-set__row">' +
            '<label class="sc-set__toggle">' +
              '<input id="set-compact" type="checkbox">' +
              '<span>Compact mode &mdash; tighter spacing for dense display</span>' +
            '</label>' +
          '</div>' +
```

Add a new row immediately after that closing `'</div>' +`, still inside the Reading `sc-set__group`:

```javascript
          '<div class="sc-set__row">' +
            '<label class="sc-set__toggle">' +
              '<input id="set-no-dropcap" type="checkbox">' +
              '<span>Hide drop caps &mdash; remove the large engraved first letter on lead trait cards</span>' +
            '</label>' +
          '</div>' +
```

- [ ] **Step 4: Bind the checkbox in `bindDrawer`**

In `bindDrawer`, after the Compact binding block (currently lines 561-569):

```javascript
    // Compact
    var compact = drawer.querySelector("#set-compact");
    compact.checked = !!prefs.compact;
    compact.addEventListener("change", function () {
      if (compact.checked) prefs.compact = true;
      else delete prefs.compact;
      applyCompact(compact.checked);
      persist();
    });
```

add:

```javascript
    // Hide drop caps
    var noDropcap = drawer.querySelector("#set-no-dropcap");
    noDropcap.checked = !!prefs.noDropcap;
    noDropcap.addEventListener("change", function () {
      if (noDropcap.checked) prefs.noDropcap = true;
      else delete prefs.noDropcap;
      applyDropcap(noDropcap.checked);
      persist();
    });
```

- [ ] **Step 5: Reset the checkbox in the Reset handler**

In the `#set-reset` click handler (currently lines 622-641), after `compact.checked = false;`, add:

```javascript
      noDropcap.checked = false;
```

(`prefs = {}` already clears the stored value and `applyAll(prefs)` already calls `applyDropcap(false)`; this line just resyncs the control.)

- [ ] **Step 6: Verify all five edits are present and consistent**

Run: `grep -n "noDropcap\|no-dropcap\|applyDropcap" docs/javascripts/settings-panel.js`
Expected: the `applyDropcap` definition, the `applyAll` call, the `#set-no-dropcap` markup, the bind block (`var noDropcap` + `.checked` + listener), and the reset `noDropcap.checked = false;` line — at least 6 hits.

- [ ] **Step 7: Run the existing JS unit tests (regression check)**

Run: `node --test docs/javascripts/`
Expected: PASS — all existing `settings-core` tests still green. (No new unit test: `noDropcap` is a pure pass-through boolean with no logic in `settings-core.js`, and its analog `Compact` has no test; the behavior is verified by the manual smoke test in Task 5.)

- [ ] **Step 8: Commit**

```bash
git add docs/javascripts/settings-panel.js
git commit -m "feat(v2): add Hide drop caps toggle to settings drawer"
```

---

### Task 4: Document the new preference

**Files:**
- Modify: `workspace DESIGN.md` (the user-preference system section, ≈134-174)
- Modify: `static_content/docs/preferences.md` (intro sentence, ≈8-10)

**Interfaces:**
- Consumes: the finished behavior from Tasks 1-3.
- Produces: docs-as-done. No code consumes this.

- [ ] **Step 1: Add a bullet to DESIGN.md's preference list**

In workspace `DESIGN.md`, in the `## The user-preference system` section, add a bullet (after the `Statblock-preview prefs` bullet, before the `New preferences must follow this pattern` bullet):

```markdown
- **Hide drop caps** (`data-no-dropcap` on `<html>`, a Reading-group checkbox) is a single
  global boolean (absent ≡ shown) that suppresses the engraved `::first-letter` drop cap on
  lead trait cards (`.sc-trait--lead`, `steel-traits.css`). Like `data-compact`, only the
  non-default ("hide") state is stored in `mkdocs:fontPrefs` (`noDropcap: true`) and seeded
  in the `overrides/main.html` early-apply.
```

- [ ] **Step 2: Mention it in the user-facing preferences page**

In `static_content/docs/preferences.md`, update the intro sentence (line 8-9) so the feature list reflects the new toggle. Change:

```markdown
adjust fonts, text size, page width, theme, compact mode, and card style. Changes
```

to:

```markdown
adjust fonts, text size, page width, theme, compact mode, drop caps, and card style. Changes
```

- [ ] **Step 3: Verify**

Run: `grep -n "data-no-dropcap" ../DESIGN.md && grep -n "drop caps" static_content/docs/preferences.md`
Expected: one hit in `DESIGN.md`, one in `preferences.md`.

- [ ] **Step 4: Commit**

```bash
git add ../DESIGN.md static_content/docs/preferences.md
git commit -m "docs: document Hide drop caps preference"
```

---

### Task 5: Manual smoke test on a local serve

**Files:** none (verification only).

**Interfaces:**
- Consumes: Tasks 1-3.
- Produces: confirmation the toggle works end-to-end.

- [ ] **Step 1: Serve the site locally**

Run: `devbox run -- bash -c 'cd v2 && mkdocs serve -a 127.0.0.1:8001'` (run in background; stop when done)

Note: the `navigation.instant` FOUC concern does **not** reproduce on a local serve — that's fine here; the early-apply line is structurally identical to the proven `data-compact` line, so local verification of the live toggle is sufficient.

- [ ] **Step 2: Find a page with a lead trait card**

Run: `grep -rl '"dropcap"\|sc-trait--lead' docs/ | head -3`
Expected: at least one generated page that renders a `.sc-trait--lead` card. Open it in the browser at `http://127.0.0.1:8001/...`.

If no page currently emits `dropcap`, instead confirm via DevTools on any page: set `document.documentElement.setAttribute('data-no-dropcap','true')` and verify the CSS rule for `.sc-trait--lead …::first-letter` shows as struck-out/not-matched in the Styles panel.

- [ ] **Step 3: Toggle and observe**

In the browser: open the gear → **Settings** → **Reading** → check **Hide drop caps**. Confirm the drop cap disappears instantly (no reload). Reload the page and confirm it stays hidden (early-apply, no flash of drop cap). Uncheck it and confirm the drop cap returns. Click **Reset all to defaults** and confirm the checkbox clears and the drop cap returns.

- [ ] **Step 4: Confirm and stop the server**

Stop the background `mkdocs serve`. No commit (verification only).

---

## Notes for the implementer

- **Do not run `just deploy-v2` to "ship" this.** Deploy is decided separately by the user. This plan ends at a verified local change committed to the branch.
- The `mkdocs serve` command assumes MkDocs is on the devbox PATH; if `mkdocs` isn't found, the DevTools fallback in Task 5 Step 2 is sufficient to verify the CSS gate.
