> **上游歷史參考，非本站現行治理或待辦。** 本站規則見 [中文化治理入口](../../index.md)；不得直接執行本文的推送、部署或私有字型流程。

# Live Settings Panel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the standalone `/preferences/` page with an in-place, high-fantasy "Settings" drawer (opened from a gear icon in the header) that applies all changes live, and add a content-size slider users can drag to set reading text size exactly.

**Architecture:** All settings logic moves into a small browser bundle plus one pure, unit-tested core module. A gear button is injected into the Material header; it opens a steel-styled drawer (right-side on desktop, bottom sheet on mobile) built entirely in JS. Controls write to the existing `localStorage["mkdocs:fontPrefs"]` schema (plus a new `contentScale` key) and apply instantly by toggling `<html>` attributes / CSS custom properties — the same mechanism the current page uses, so the anti-FOUC early-apply script in `overrides/main.html` keeps working. The old page becomes a thin redirect note and is dropped from the nav.

**Tech Stack:** MkDocs Material 9.7.x, vanilla ES5-safe JS (no build step — files are served as-is), CSS custom properties, `node:test` for pure-logic unit tests, Playwright (MCP) for E2E verification. Devbox provides `node`/`mkdocs` (`devbox run -- <cmd>`).

---

## Testing reality (read first)

This is a static MkDocs site with **no JS bundler or test runner wired in**. To keep TDD honest without adding heavy tooling:

- **Pure logic** (storage parsing, width/scale normalization, slider↔value mapping) lives in `docs/javascripts/settings-core.js` as a UMD module and is covered by real `node:test` unit tests (zero new dependencies). This is the TDD core.
- **DOM / visual behavior** (button injection, drawer open/close, live CSS effects, mobile layout) is verified with Playwright MCP against a locally-served build. These are scripted, deterministic checks, not vibes.

Run the unit tests with: `cd v2 && devbox run -- node --test tests/`

---

## File Structure

**New files:**

- `v2/docs/javascripts/settings-core.js` — Pure, side-effect-free helpers (UMD): storage load/save, `clampScale`, `normalizeWidth`, `clampEm`, `widthToControls`, `controlsToWidth`, plus the numeric range constants. No DOM. Unit-tested.
- `v2/tests/settings-core.test.js` — `node:test` unit tests for `settings-core.js`.
- `v2/docs/javascripts/settings-panel.js` — Browser IIFE: imports `window.SettingsCore`, holds the apply functions (fonts, width, content-scale, compact, theme, card-style), injects the header gear button, builds the drawer + scrim once, binds every control with live apply, handles open/close/Esc/focus, and "Reset all". Replaces `preferences.js`.
- `v2/docs/stylesheets/steel-settings.css` — High-fantasy styling for the gear button, scrim, drawer (right-side → bottom sheet), and the control widgets (steel sliders, toggles, selects). Uses `--fx-*` tokens from `steel-redesign.css`.

**Modified files:**

- `v2/mkdocs.yml` — Add `stylesheets/steel-settings.css` (after `steel-redesign.css`); in `extra_javascript` replace `javascripts/preferences.js` with `javascripts/settings-core.js` **and** `javascripts/settings-panel.js` (core first).
- `v2/overrides/main.html` — Extend the inline early-apply script to also set `--sc-content-scale` from `saved.contentScale`.
- `v2/docs/stylesheets/extra.css` — Add `:root { --sc-content-scale: 1; }` and a base `.md-typeset { font-size: calc(.8rem * var(--sc-content-scale)); }`; multiply the compact `.md-typeset` font-size by the same var.
- `v2/docs/stylesheets/mobile.css` — Multiply the mobile `.md-typeset` font-size by `--sc-content-scale`.
- `v2/static_content/docs/preferences.md` — Replace the full control page with a short "settings moved to the gear icon" redirect note (source of truth; copied to `docs/` on build).
- `v2/docs/preferences.md` — Mirror the redirect note (committed build artifact; `cleanDocsDir` protects it, so keep it in sync by hand).
- `v2/docs/.nav.yml` — Remove the `preferences.md` entry.

**Deleted files:**

- `v2/docs/javascripts/preferences.js` — Superseded by `settings-core.js` + `settings-panel.js`.

---

### Task 1: Pure settings-core module (TDD)

**Files:**
- Create: `v2/docs/javascripts/settings-core.js`
- Test: `v2/tests/settings-core.test.js`

- [ ] **Step 1: Write the failing tests**

Create `v2/tests/settings-core.test.js`:

```js
const test = require("node:test");
const assert = require("node:assert");
const C = require("../docs/javascripts/settings-core.js");

test("clampScale clamps to [0.8, 1.4] and snaps to 0.05", () => {
  assert.strictEqual(C.clampScale(1), 1);
  assert.strictEqual(C.clampScale(0.5), 0.8);   // below min
  assert.strictEqual(C.clampScale(2), 1.4);     // above max
  assert.strictEqual(C.clampScale("1.07"), 1.05); // snap down to step
  assert.strictEqual(C.clampScale("1.08"), 1.1);  // snap up to step
  assert.strictEqual(C.clampScale("abc"), 1);   // NaN -> default
  assert.strictEqual(C.clampScale(undefined), 1);
});

test("normalizeWidth handles units, keywords, bare numbers", () => {
  assert.strictEqual(C.normalizeWidth("61em"), "61em");
  assert.strictEqual(C.normalizeWidth("1200px"), "1200px");
  assert.strictEqual(C.normalizeWidth("90%"), "90%");
  assert.strictEqual(C.normalizeWidth(" 61EM "), "61em"); // trim + lowercase
  assert.strictEqual(C.normalizeWidth("full"), "none");
  assert.strictEqual(C.normalizeWidth("none"), "none");
  assert.strictEqual(C.normalizeWidth("default"), "default");
  assert.strictEqual(C.normalizeWidth("72"), "72em");     // bare number -> em
  assert.strictEqual(C.normalizeWidth("garbage"), null);
  assert.strictEqual(C.normalizeWidth(""), null);
  assert.strictEqual(C.normalizeWidth(null), null);
});

test("clampEm clamps to [44, 100] and snaps to step", () => {
  assert.strictEqual(C.clampEm(60), 60);
  assert.strictEqual(C.clampEm(10), 44);
  assert.strictEqual(C.clampEm(200), 100);
  assert.strictEqual(C.clampEm("63"), 64); // snap to 2em step
  assert.strictEqual(C.clampEm("xyz"), 80); // NaN -> default
});

test("widthToControls maps stored width to slider state", () => {
  assert.deepStrictEqual(C.widthToControls("none"), { full: true, em: 80 });
  assert.deepStrictEqual(C.widthToControls("100%"), { full: true, em: 80 });
  assert.deepStrictEqual(C.widthToControls(undefined), { full: true, em: 80 });
  assert.deepStrictEqual(C.widthToControls("default"), { full: true, em: 80 });
  assert.deepStrictEqual(C.widthToControls("60em"), { full: false, em: 60 });
  assert.deepStrictEqual(C.widthToControls("200em"), { full: false, em: 100 }); // clamp max
});

test("controlsToWidth serializes slider state", () => {
  assert.strictEqual(C.controlsToWidth({ full: true, em: 80 }), "none");
  assert.strictEqual(C.controlsToWidth({ full: false, em: 60 }), "60em");
});

test("width round-trips through controls", () => {
  const r = C.widthToControls(C.controlsToWidth({ full: false, em: 64 }));
  assert.deepStrictEqual(r, { full: false, em: 64 });
});

test("loadPrefs tolerates bad JSON and missing key", () => {
  assert.deepStrictEqual(C.loadPrefs({ getItem: () => "{not json" }), {});
  assert.deepStrictEqual(C.loadPrefs({ getItem: () => null }), {});
  assert.deepStrictEqual(C.loadPrefs({ getItem: () => '{"compact":true}' }), { compact: true });
});
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd v2 && devbox run -- node --test tests/`
Expected: FAIL — `Cannot find module '../docs/javascripts/settings-core.js'`.

- [ ] **Step 3: Write the module to make them pass**

Create `v2/docs/javascripts/settings-core.js`:

```js
/*
 * settings-core.js — pure, DOM-free settings helpers.
 * UMD: exports for `node:test`, attaches to window.SettingsCore in the browser.
 * Loaded BEFORE settings-panel.js in mkdocs.yml.
 */
;(function (root, factory) {
  if (typeof module === "object" && module.exports) {
    module.exports = factory();
  } else {
    root.SettingsCore = factory();
  }
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  var STORAGE_KEY = "mkdocs:fontPrefs";

  var SCALE_MIN = 0.8, SCALE_MAX = 1.4, SCALE_STEP = 0.05, SCALE_DEFAULT = 1;
  var WIDTH_MIN_EM = 44, WIDTH_MAX_EM = 100, WIDTH_STEP_EM = 2, WIDTH_DEFAULT_EM = 80;

  function clampScale(value) {
    var n = parseFloat(value);
    if (!isFinite(n)) return SCALE_DEFAULT;
    if (n < SCALE_MIN) n = SCALE_MIN;
    if (n > SCALE_MAX) n = SCALE_MAX;
    var steps = Math.round((n - SCALE_MIN) / SCALE_STEP);
    return Math.round((SCALE_MIN + steps * SCALE_STEP) * 100) / 100;
  }

  function normalizeWidth(raw) {
    if (raw === null || raw === undefined) return null;
    var v = String(raw).trim().toLowerCase();
    if (v === "") return null;
    if (v === "full") return "none";
    if (v === "none") return "none";
    if (v === "default") return "default";
    if (/^\d+(\.\d+)?(em|rem|px|%)$/.test(v)) return v;
    if (/^\d+(\.\d+)?$/.test(v)) return v + "em";
    return null;
  }

  function clampEm(value) {
    var n = parseFloat(value);
    if (!isFinite(n)) return WIDTH_DEFAULT_EM;
    if (n < WIDTH_MIN_EM) n = WIDTH_MIN_EM;
    if (n > WIDTH_MAX_EM) n = WIDTH_MAX_EM;
    return Math.round(n / WIDTH_STEP_EM) * WIDTH_STEP_EM;
  }

  function widthToControls(width) {
    var norm = normalizeWidth(width);
    if (!norm || norm === "none" || norm === "default") {
      return { full: true, em: WIDTH_DEFAULT_EM };
    }
    var m = /^(\d+(?:\.\d+)?)em$/.exec(norm);
    if (m) return { full: false, em: clampEm(m[1]) };
    // percent/px or anything else -> treat as full width, keep default slider
    return { full: true, em: WIDTH_DEFAULT_EM };
  }

  function controlsToWidth(controls) {
    if (!controls || controls.full) return "none";
    return clampEm(controls.em) + "em";
  }

  function loadPrefs(storage) {
    try {
      return JSON.parse(storage.getItem(STORAGE_KEY) || "{}") || {};
    } catch (e) {
      return {};
    }
  }

  function savePrefs(storage, prefs) {
    storage.setItem(STORAGE_KEY, JSON.stringify(prefs));
  }

  return {
    STORAGE_KEY: STORAGE_KEY,
    SCALE_MIN: SCALE_MIN, SCALE_MAX: SCALE_MAX, SCALE_STEP: SCALE_STEP, SCALE_DEFAULT: SCALE_DEFAULT,
    WIDTH_MIN_EM: WIDTH_MIN_EM, WIDTH_MAX_EM: WIDTH_MAX_EM, WIDTH_STEP_EM: WIDTH_STEP_EM, WIDTH_DEFAULT_EM: WIDTH_DEFAULT_EM,
    clampScale: clampScale,
    normalizeWidth: normalizeWidth,
    clampEm: clampEm,
    widthToControls: widthToControls,
    controlsToWidth: controlsToWidth,
    loadPrefs: loadPrefs,
    savePrefs: savePrefs
  };
});
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `cd v2 && devbox run -- node --test tests/`
Expected: PASS — all tests green (7 test blocks).

- [ ] **Step 5: Commit**

```bash
cd /home/vexa/code/steel_compendium/workspace/v2
git add docs/javascripts/settings-core.js tests/settings-core.test.js
git commit -m "feat(v2): add unit-tested settings-core helpers for live settings panel"
```

---

### Task 2: Content-scale CSS plumbing

Make the content (`.md-typeset`) font-size respond to a `--sc-content-scale` multiplier across the three states it's set in (desktop default, mobile, compact), so the slider in Task 4 has something to drive. No new selectors fight each other: the base rule goes in `extra.css` (loads before `mobile.css`), so mobile's later rule still wins on small screens, and the compact rule keeps its higher attribute specificity.

**Files:**
- Modify: `v2/docs/stylesheets/extra.css`
- Modify: `v2/docs/stylesheets/mobile.css`

- [ ] **Step 1: Add the default var and base scaled font-size in `extra.css`**

In `v2/docs/stylesheets/extra.css`, replace the top block:

```css
/* The tables used to display abilities should not have headers to avoid sorttable tables */
th:empty {
    display: none;
}

.md-grid {
    max-width: var(--md-max_width);
}
```

with:

```css
/* The tables used to display abilities should not have headers to avoid sorttable tables */
th:empty {
    display: none;
}

.md-grid {
    max-width: var(--md-max_width);
}

/* Reading-content size multiplier, driven live by the settings panel
   (settings-panel.js sets --sc-content-scale on <html>). The base rule below
   restates Material's .8rem default so scale=1 is a no-op; mobile.css (loaded
   AFTER this file) and the compact rule (higher specificity) re-apply the same
   multiplier for their own base sizes. */
:root {
    --sc-content-scale: 1;
}

.md-typeset {
    font-size: calc(0.8rem * var(--sc-content-scale));
}
```

- [ ] **Step 2: Multiply the compact font-size by the var in `extra.css`**

In `v2/docs/stylesheets/extra.css`, change:

```css
[data-compact="true"] .md-typeset {
    font-size: 0.85rem;
    line-height: 1.5;
}
```

to:

```css
[data-compact="true"] .md-typeset {
    font-size: calc(0.85rem * var(--sc-content-scale));
    line-height: 1.5;
}
```

- [ ] **Step 3: Multiply the mobile font-size by the var in `mobile.css`**

In `v2/docs/stylesheets/mobile.css`, change:

```css
    /* Ensure body text stays readable */
    .md-typeset {
        font-size: 0.95rem;
    }
```

to:

```css
    /* Ensure body text stays readable (scaled live by the settings panel) */
    .md-typeset {
        font-size: calc(0.95rem * var(--sc-content-scale));
    }
```

- [ ] **Step 4: Verify the CSS is well-formed via a build**

Run: `cd /home/vexa/code/steel_compendium/workspace/v2 && devbox run -- mkdocs build 2>&1 | tail -5`
Expected: build completes with no CSS-related errors (warnings about nav/links are pre-existing and fine). If `mkdocs build` errors because generated content under `docs/Browse|Read|Bestiary` is missing, run `cd /home/vexa/code/steel_compendium/workspace && just deploy-v2` once to populate it, then re-run the build.

- [ ] **Step 5: Commit**

```bash
cd /home/vexa/code/steel_compendium/workspace/v2
git add docs/stylesheets/extra.css docs/stylesheets/mobile.css
git commit -m "feat(v2): make content font-size respond to --sc-content-scale"
```

---

### Task 3: High-fantasy settings panel CSS

Style the gear button, scrim, drawer (right-side on desktop, bottom sheet ≤76.25em), and control widgets using the existing steel tokens. Open state is driven by `data-sc-settings="open"` on `<html>` (set by JS in Task 4).

**Files:**
- Create: `v2/docs/stylesheets/steel-settings.css`

- [ ] **Step 1: Write the stylesheet**

Create `v2/docs/stylesheets/steel-settings.css`:

```css
/* ============================================================
   steel-settings.css — live Settings drawer + header gear.
   Loads AFTER steel-redesign.css so it can use --fx-* tokens.
   Open state: <html data-sc-settings="open"> (set by settings-panel.js).
   ============================================================ */

/* ── Header gear button (sits among Material header buttons) ── */
.sc-settings-toggle {
  cursor: pointer;
}
.sc-settings-toggle svg {
  width: 1.2rem;
  height: 1.2rem;
  fill: currentColor;
}

/* ── Scrim ── */
.sc-settings-scrim {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.25s ease, visibility 0s linear 0.25s;
  z-index: 1000;
}
[data-sc-settings="open"] .sc-settings-scrim {
  opacity: 1;
  visibility: visible;
  transition: opacity 0.25s ease;
}

/* ── Drawer (desktop: right slab) ── */
.sc-settings-drawer {
  position: fixed;
  top: 0;
  right: 0;
  height: 100%;
  width: min(24rem, 92vw);
  z-index: 1001;
  display: flex;
  flex-direction: column;
  background: var(--fx-card-bg, var(--md-default-bg-color));
  border-left: 1px solid var(--fx-metal-line, var(--md-default-fg-color--lightest));
  box-shadow: var(--fx-bevel), -10px 0 30px rgba(0, 0, 0, 0.4);
  transform: translateX(100%);
  transition: transform 0.28s cubic-bezier(0.2, 0.8, 0.2, 1);
  overflow: hidden;
}
[data-sc-settings="open"] .sc-settings-drawer {
  transform: translateX(0);
}

/* Filigree top accent */
.sc-settings-drawer::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: var(--fx-metal-grad);
  opacity: 0.9;
}

/* ── Drawer header ── */
.sc-settings-head {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 1.1rem 0.75rem;
  border-bottom: 1px solid var(--fx-metal-faint, var(--md-default-fg-color--lightest));
}
.sc-settings-head h2 {
  margin: 0;
  flex: 1;
  font-family: var(--md-large-header-font);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  font-size: 1.15rem;
  line-height: 1;
  color: var(--sc-steel-lighter, var(--md-default-fg-color));
  text-shadow: var(--fx-emboss);
}
.sc-settings-close {
  appearance: none;
  border: 1px solid var(--fx-metal-line, var(--md-default-fg-color--lightest));
  background: var(--md-code-bg-color);
  color: var(--md-default-fg-color);
  border-radius: 0.3rem;
  width: 1.9rem;
  height: 1.9rem;
  font-size: 1.1rem;
  line-height: 1;
  cursor: pointer;
}
.sc-settings-close:hover {
  border-color: var(--md-accent-fg-color);
  color: var(--md-accent-fg-color);
}

/* ── Scrollable body ── */
.sc-settings-body {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem 1.1rem 1.1rem;
  -webkit-overflow-scrolling: touch;
}

/* ── Control groups ── */
.sc-set__group {
  margin: 0 0 1.1rem;
}
.sc-set__group > h3,
.sc-set__group > summary {
  margin: 0 0 0.5rem;
  font-family: var(--md-small-header-font);
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--md-default-fg-color--light);
}
.sc-set__group--fonts > summary {
  cursor: pointer;
  list-style: none;
}
.sc-set__group--fonts > summary::-webkit-details-marker { display: none; }
.sc-set__group--fonts > summary::after {
  content: " ▸";
  color: var(--fx-metal, var(--md-default-fg-color--lighter));
}
.sc-set__group--fonts[open] > summary::after { content: " ▾"; }

.sc-set__row {
  margin: 0 0 0.85rem;
}
.sc-set__row:last-child { margin-bottom: 0; }
.sc-set__row label.sc-set__label {
  display: block;
  font-weight: 600;
  font-size: 0.8rem;
  margin-bottom: 0.35rem;
  color: var(--md-default-fg-color);
}
.sc-set__hint {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.72rem;
  color: var(--md-default-fg-color--lighter);
}

/* Selects */
.sc-set__select {
  width: 100%;
  padding: 0.5rem 0.55rem;
  border: 1px solid var(--fx-metal-line, var(--md-default-fg-color--lightest));
  border-radius: 0.3rem;
  background: var(--md-code-bg-color);
  color: var(--md-default-fg-color);
  font-size: 0.85rem;
  font-family: inherit;
}
.sc-set__select:focus {
  outline: 2px solid var(--md-accent-fg-color);
  outline-offset: -1px;
}
[data-md-color-scheme="slate"] .sc-set__select { color-scheme: dark; }
[data-md-color-scheme="slate"] .sc-set__select option {
  background: var(--md-default-bg-color);
  color: var(--md-default-fg-color);
}

/* Toggle row (checkbox + text) */
.sc-set__toggle {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  cursor: pointer;
}
.sc-set__toggle input { width: 1.05rem; height: 1.05rem; flex: 0 0 auto; }
.sc-set__toggle span { font-size: 0.82rem; }

/* Slider row */
.sc-set__sliderwrap {
  display: flex;
  align-items: center;
  gap: 0.7rem;
}
.sc-set__range {
  flex: 1;
  -webkit-appearance: none;
  appearance: none;
  height: 4px;
  border-radius: 3px;
  background: var(--fx-metal-grad, var(--md-default-fg-color--lighter));
  outline: none;
}
.sc-set__range::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 1.05rem;
  height: 1.05rem;
  border-radius: 50%;
  background: var(--fx-metal-bright, #fff);
  border: 1px solid var(--fx-metal, #888);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.4);
  cursor: pointer;
}
.sc-set__range::-moz-range-thumb {
  width: 1.05rem;
  height: 1.05rem;
  border-radius: 50%;
  background: var(--fx-metal-bright, #fff);
  border: 1px solid var(--fx-metal, #888);
  cursor: pointer;
}
.sc-set__range:disabled { opacity: 0.4; }
.sc-set__value {
  min-width: 3.2rem;
  text-align: right;
  font-variant-numeric: tabular-nums;
  font-size: 0.82rem;
  color: var(--md-default-fg-color--light);
}

/* ── Footer ── */
.sc-settings-foot {
  padding: 0.75rem 1.1rem;
  border-top: 1px solid var(--fx-metal-faint, var(--md-default-fg-color--lightest));
}
.sc-settings-reset {
  width: 100%;
  padding: 0.55rem 1rem;
  border: 1px solid var(--fx-metal-line, var(--md-default-fg-color--lightest));
  border-radius: 0.3rem;
  background: var(--md-code-bg-color);
  color: var(--md-default-fg-color);
  font-size: 0.82rem;
  cursor: pointer;
}
.sc-settings-reset:hover {
  background: var(--md-accent-fg-color--transparent);
  border-color: var(--md-accent-fg-color);
}

/* ── Mobile: bottom sheet ── */
@media screen and (max-width: 76.25em) {
  .sc-settings-drawer {
    top: auto;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    height: auto;
    max-height: 82vh;
    border-left: none;
    border-top: 1px solid var(--fx-metal-line, var(--md-default-fg-color--lightest));
    border-radius: 0.9rem 0.9rem 0 0;
    box-shadow: var(--fx-bevel), 0 -10px 30px rgba(0, 0, 0, 0.45);
    transform: translateY(100%);
  }
  [data-sc-settings="open"] .sc-settings-drawer {
    transform: translateY(0);
  }
  /* Grab handle */
  .sc-settings-head::before {
    content: "";
    position: absolute;
    top: 0.4rem; left: 50%;
    transform: translateX(-50%);
    width: 2.4rem; height: 0.25rem;
    border-radius: 3px;
    background: var(--fx-metal, var(--md-default-fg-color--lighter));
    opacity: 0.6;
  }
  .sc-settings-head { position: relative; padding-top: 1.25rem; }
}

/* Respect reduced motion */
@media (prefers-reduced-motion: reduce) {
  .sc-settings-drawer,
  .sc-settings-scrim { transition: none; }
}
```

- [ ] **Step 2: Verify it parses via a build**

Run: `cd /home/vexa/code/steel_compendium/workspace/v2 && devbox run -- mkdocs build 2>&1 | tail -5`
Expected: build completes (the new file isn't referenced yet — wiring happens in Task 5 — so this only confirms the file itself is syntactically harmless if included; it is not yet loaded).

- [ ] **Step 3: Commit**

```bash
cd /home/vexa/code/steel_compendium/workspace/v2
git add docs/stylesheets/steel-settings.css
git commit -m "feat(v2): add high-fantasy settings drawer stylesheet"
```

---

### Task 4: Settings panel behavior (settings-panel.js)

Build the gear button, drawer, and all bindings. Replaces `preferences.js`.

**Files:**
- Create: `v2/docs/javascripts/settings-panel.js`

- [ ] **Step 1: Write the panel script**

Create `v2/docs/javascripts/settings-panel.js`:

```js
/*
 * settings-panel.js — live, in-place settings drawer.
 * Requires window.SettingsCore (settings-core.js, loaded first).
 * Injects a gear button into the Material header and a steel drawer into <body>.
 * Applies changes instantly via <html> attributes / CSS custom properties,
 * persisting to localStorage["mkdocs:fontPrefs"] (shared with the early-apply
 * script in overrides/main.html).
 */
(function () {
  "use strict";

  var C = window.SettingsCore;
  if (!C) return; // core must load first

  var FONT_VARS = {
    large: "--md-large-header-font",
    small: "--md-small-header-font",
    text: "--md-text-font",
    code: "--md-code-font"
  };
  var WIDTH_VAR = "--md-max_width";
  var SCALE_VAR = "--sc-content-scale";

  var FONT_OPTIONS = {
    large: [
      ['"Beaufort W01 Heavy", var(--md-text-font), serif', "Beaufort (default)"],
      ['"Test Newzald", var(--md-text-font), serif', "Test Newzald"],
      ['"Source Serif 4"', "Source Serif 4"],
      ['"Inter", var(--md-text-font), sans-serif', "Inter"],
      ['"system-ui", var(--md-text-font), serif', "System UI"]
    ],
    small: [
      ['"Test Newzald", var(--md-text-font), serif', "Test Newzald (default)"],
      ['"Beaufort W01 Heavy", var(--md-text-font), serif', "Beaufort"],
      ['"Source Serif 4"', "Source Serif 4"],
      ['"Inter", var(--md-text-font), sans-serif', "Inter"],
      ['"system-ui", var(--md-text-font), serif', "System UI"]
    ],
    text: [
      ['"BerlingskeSlab-DBd", Georgia, "Times New Roman", serif', "Berlingske Slab (default)"],
      ['"Source Serif 4"', "Source Serif 4"],
      ['"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Ubuntu, "Helvetica Neue", Arial, "Noto Sans", sans-serif', "Inter"],
      ['-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Ubuntu, "Helvetica Neue", Arial, "Noto Sans", sans-serif', "System UI"]
    ],
    code: [
      ['"JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace', "JetBrains Mono (default)"],
      ['"Fira Code", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace', "Fira Code"],
      ['ui-monospace, SFMono-Regular, Menlo, Consolas, monospace', "System Monospace"]
    ]
  };

  var GEAR =
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 15.5A3.5 3.5 0 0 1 8.5 12 3.5 3.5 0 0 1 12 8.5a3.5 3.5 0 0 1 3.5 3.5 3.5 3.5 0 0 1-3.5 3.5m7.43-2.53c.04-.32.07-.64.07-.97 0-.33-.03-.66-.07-1l2.11-1.63c.19-.15.24-.42.12-.64l-2-3.46c-.12-.22-.39-.31-.61-.22l-2.49 1c-.52-.39-1.06-.73-1.69-.98l-.37-2.65A.506.506 0 0 0 14 2h-4c-.25 0-.46.18-.5.42l-.37 2.65c-.63.25-1.17.59-1.69.98l-2.49-1c-.22-.09-.49 0-.61.22l-2 3.46c-.13.22-.07.49.12.64L2.57 11c-.04.34-.07.67-.07 1 0 .33.03.65.07.97l-2.11 1.66c-.19.15-.25.42-.12.64l2 3.46c.12.22.39.3.61.22l2.49-1.01c.52.4 1.06.74 1.69.99l.37 2.65c.04.24.25.42.5.42h4c.25 0 .46-.18.5-.42l.37-2.65c.63-.26 1.17-.59 1.69-.99l2.49 1.01c.22.08.49 0 .61-.22l2-3.46c.12-.22.07-.49-.12-.64z"/></svg>';

  // ---------- apply (side-effecting) ----------
  function applyFonts(prefs) {
    var r = document.documentElement.style;
    Object.keys(FONT_VARS).forEach(function (k) {
      if (prefs[k]) r.setProperty(FONT_VARS[k], prefs[k]);
      else r.removeProperty(FONT_VARS[k]);
    });
  }
  function applyWidth(value) {
    var r = document.documentElement.style;
    if (!value || value === "default") r.removeProperty(WIDTH_VAR);
    else r.setProperty(WIDTH_VAR, value);
  }
  function applyContentScale(scale) {
    var r = document.documentElement.style;
    var n = C.clampScale(scale);
    if (n === C.SCALE_DEFAULT) r.removeProperty(SCALE_VAR);
    else r.setProperty(SCALE_VAR, String(n));
  }
  function applyCompact(on) {
    document.documentElement.setAttribute("data-compact", on ? "true" : "false");
  }
  function applySiteTheme(name) {
    if (!name || name === "steel") document.documentElement.removeAttribute("data-sc-theme");
    else document.documentElement.setAttribute("data-sc-theme", name);
  }
  function applyCardStyle(style) {
    if (!style || style === "classic") document.documentElement.removeAttribute("data-card-style");
    else document.documentElement.setAttribute("data-card-style", style);
  }
  function applyAll(prefs) {
    applyFonts(prefs);
    applyWidth(prefs.width);
    applyContentScale(prefs.contentScale);
    applyCompact(!!prefs.compact);
    applySiteTheme(prefs.siteTheme);
    applyCardStyle(prefs.cardStyle);
  }

  var prefs = C.loadPrefs(localStorage);
  applyAll(prefs); // re-assert (covers contentScale even if inline early-apply predates it)

  function persist() { C.savePrefs(localStorage, prefs); }

  // ---------- DOM helpers ----------
  function el(tag, cls, html) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (html != null) n.innerHTML = html;
    return n;
  }
  function fillSelect(sel, options, selected) {
    sel.innerHTML = "";
    options.forEach(function (o) {
      var opt = document.createElement("option");
      opt.value = o[0];
      opt.textContent = o[1];
      if (selected && selected === o[0]) opt.selected = true;
      sel.appendChild(opt);
    });
  }

  // ---------- build drawer (once) ----------
  function buildDrawer() {
    if (document.getElementById("sc-settings-drawer")) return;

    var scrim = el("div", "sc-settings-scrim");
    scrim.id = "sc-settings-scrim";

    var drawer = el("aside", "sc-settings-drawer");
    drawer.id = "sc-settings-drawer";
    drawer.setAttribute("role", "dialog");
    drawer.setAttribute("aria-modal", "true");
    drawer.setAttribute("aria-label", "Display settings");
    drawer.setAttribute("tabindex", "-1");
    drawer.hidden = false;

    drawer.innerHTML =
      '<div class="sc-settings-head">' +
        '<h2>Settings</h2>' +
        '<button type="button" class="sc-settings-close" aria-label="Close settings">&times;</button>' +
      '</div>' +
      '<div class="sc-settings-body">' +

        '<div class="sc-set__group"><h3>Theme</h3>' +
          '<div class="sc-set__row">' +
            '<label class="sc-set__label" for="set-site-theme">Color theme</label>' +
            '<select class="sc-set__select" id="set-site-theme">' +
              '<option value="steel">Steel (default)</option>' +
              '<option value="parchment">Parchment</option>' +
              '<option value="obsidian">Obsidian</option>' +
            '</select>' +
            '<span class="sc-set__hint">Use the header toggle for light / dark.</span>' +
          '</div>' +
        '</div>' +

        '<div class="sc-set__group"><h3>Reading</h3>' +
          '<div class="sc-set__row">' +
            '<label class="sc-set__label" for="set-scale">Text size</label>' +
            '<div class="sc-set__sliderwrap">' +
              '<input class="sc-set__range" id="set-scale" type="range">' +
              '<span class="sc-set__value" id="set-scale-val">100%</span>' +
            '</div>' +
            '<span class="sc-set__hint">Scales body text, headings, and tables.</span>' +
          '</div>' +
          '<div class="sc-set__row">' +
            '<label class="sc-set__toggle">' +
              '<input id="set-compact" type="checkbox">' +
              '<span>Compact mode &mdash; tighter spacing for dense display</span>' +
            '</label>' +
          '</div>' +
          '<div class="sc-set__row">' +
            '<label class="sc-set__label" for="set-card-style">Ability card style</label>' +
            '<select class="sc-set__select" id="set-card-style">' +
              '<option value="classic">Classic (default)</option>' +
              '<option value="modern">Modern</option>' +
            '</select>' +
            '<span class="sc-set__hint">Classic uses Draw Steel glyph badges; Modern uses colored borders. Changing this reloads the page.</span>' +
          '</div>' +
        '</div>' +

        '<div class="sc-set__group"><h3>Page width</h3>' +
          '<div class="sc-set__row">' +
            '<label class="sc-set__toggle">' +
              '<input id="set-fullwidth" type="checkbox">' +
              '<span>Full width</span>' +
            '</label>' +
          '</div>' +
          '<div class="sc-set__row">' +
            '<label class="sc-set__label" for="set-width">Max width</label>' +
            '<div class="sc-set__sliderwrap">' +
              '<input class="sc-set__range" id="set-width" type="range">' +
              '<span class="sc-set__value" id="set-width-val">80em</span>' +
            '</div>' +
          '</div>' +
        '</div>' +

        '<details class="sc-set__group sc-set__group--fonts"><summary>Fonts</summary>' +
          '<div class="sc-set__row">' +
            '<label class="sc-set__label" for="set-font-large">Large headers (H1&ndash;H2)</label>' +
            '<select class="sc-set__select" id="set-font-large"></select>' +
          '</div>' +
          '<div class="sc-set__row">' +
            '<label class="sc-set__label" for="set-font-small">Small headers (H3&ndash;H6)</label>' +
            '<select class="sc-set__select" id="set-font-small"></select>' +
          '</div>' +
          '<div class="sc-set__row">' +
            '<label class="sc-set__label" for="set-font-text">Body text</label>' +
            '<select class="sc-set__select" id="set-font-text"></select>' +
          '</div>' +
          '<div class="sc-set__row">' +
            '<label class="sc-set__label" for="set-font-code">Code</label>' +
            '<select class="sc-set__select" id="set-font-code"></select>' +
          '</div>' +
        '</details>' +

      '</div>' +
      '<div class="sc-settings-foot">' +
        '<button type="button" class="sc-settings-reset" id="set-reset">Reset all to defaults</button>' +
      '</div>';

    document.body.appendChild(scrim);
    document.body.appendChild(drawer);

    bindDrawer(drawer, scrim);
  }

  // ---------- open / close ----------
  var lastFocus = null;
  function openDrawer() {
    var drawer = document.getElementById("sc-settings-drawer");
    if (!drawer) return;
    lastFocus = document.activeElement;
    document.documentElement.setAttribute("data-sc-settings", "open");
    var btn = document.getElementById("sc-settings-toggle");
    if (btn) btn.setAttribute("aria-expanded", "true");
    drawer.focus();
  }
  function closeDrawer() {
    document.documentElement.removeAttribute("data-sc-settings");
    var btn = document.getElementById("sc-settings-toggle");
    if (btn) btn.setAttribute("aria-expanded", "false");
    if (lastFocus && typeof lastFocus.focus === "function") lastFocus.focus();
  }
  function isOpen() {
    return document.documentElement.getAttribute("data-sc-settings") === "open";
  }

  // ---------- bind controls ----------
  function bindDrawer(drawer, scrim) {
    drawer.querySelector(".sc-settings-close").addEventListener("click", closeDrawer);
    scrim.addEventListener("click", closeDrawer);
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && isOpen()) closeDrawer();
    });

    // Fonts
    var fontIds = { large: "set-font-large", small: "set-font-small", text: "set-font-text", code: "set-font-code" };
    Object.keys(fontIds).forEach(function (k) {
      var sel = drawer.querySelector("#" + fontIds[k]);
      fillSelect(sel, FONT_OPTIONS[k], prefs[k]);
      sel.addEventListener("change", function () {
        prefs[k] = sel.value;
        applyFonts(prefs);
        persist();
      });
    });

    // Site theme
    var themeSel = drawer.querySelector("#set-site-theme");
    themeSel.value = prefs.siteTheme || "steel";
    themeSel.addEventListener("change", function () {
      if (!themeSel.value || themeSel.value === "steel") delete prefs.siteTheme;
      else prefs.siteTheme = themeSel.value;
      applySiteTheme(prefs.siteTheme);
      persist();
    });

    // Content scale slider
    var scale = drawer.querySelector("#set-scale");
    var scaleVal = drawer.querySelector("#set-scale-val");
    scale.min = String(C.SCALE_MIN);
    scale.max = String(C.SCALE_MAX);
    scale.step = String(C.SCALE_STEP);
    var curScale = C.clampScale(prefs.contentScale);
    scale.value = String(curScale);
    scaleVal.textContent = Math.round(curScale * 100) + "%";
    scale.addEventListener("input", function () {
      var n = C.clampScale(scale.value);
      scaleVal.textContent = Math.round(n * 100) + "%";
      applyContentScale(n);
    });
    scale.addEventListener("change", function () {
      var n = C.clampScale(scale.value);
      if (n === C.SCALE_DEFAULT) delete prefs.contentScale;
      else prefs.contentScale = n;
      applyContentScale(n);
      persist();
    });

    // Compact
    var compact = drawer.querySelector("#set-compact");
    compact.checked = !!prefs.compact;
    compact.addEventListener("change", function () {
      if (compact.checked) prefs.compact = true;
      else delete prefs.compact;
      applyCompact(compact.checked);
      persist();
    });

    // Card style (reloads — markup parity with prior behavior)
    var card = drawer.querySelector("#set-card-style");
    card.value = prefs.cardStyle || "classic";
    card.addEventListener("change", function () {
      if (!card.value || card.value === "classic") delete prefs.cardStyle;
      else prefs.cardStyle = card.value;
      applyCardStyle(prefs.cardStyle);
      persist();
      location.reload();
    });

    // Page width: full toggle + em slider
    var full = drawer.querySelector("#set-fullwidth");
    var width = drawer.querySelector("#set-width");
    var widthVal = drawer.querySelector("#set-width-val");
    width.min = String(C.WIDTH_MIN_EM);
    width.max = String(C.WIDTH_MAX_EM);
    width.step = String(C.WIDTH_STEP_EM);

    function syncWidthUI(state) {
      full.checked = state.full;
      width.value = String(state.em);
      width.disabled = state.full;
      widthVal.textContent = state.full ? "full" : state.em + "em";
    }
    function commitWidth(live) {
      var state = { full: full.checked, em: C.clampEm(width.value) };
      var w = C.controlsToWidth(state);
      widthVal.textContent = state.full ? "full" : state.em + "em";
      width.disabled = state.full;
      applyWidth(w);
      if (!live) {
        if (w === "none") delete prefs.width;
        else prefs.width = w;
        persist();
      }
    }
    syncWidthUI(C.widthToControls(prefs.width));
    full.addEventListener("change", function () { commitWidth(false); });
    width.addEventListener("input", function () { commitWidth(true); });
    width.addEventListener("change", function () { commitWidth(false); });

    // Reset all
    drawer.querySelector("#set-reset").addEventListener("click", function () {
      prefs = {};
      applyAll(prefs);
      // resync controls
      Object.keys(fontIds).forEach(function (k) {
        drawer.querySelector("#" + fontIds[k]).selectedIndex = 0;
      });
      themeSel.value = "steel";
      scale.value = String(C.SCALE_DEFAULT);
      scaleVal.textContent = "100%";
      compact.checked = false;
      card.value = "classic";
      syncWidthUI(C.widthToControls(undefined));
      persist();
    });
  }

  // ---------- inject header button ----------
  function injectButton() {
    if (document.getElementById("sc-settings-toggle")) return;
    var header = document.querySelector(".md-header__inner");
    if (!header) return;
    var btn = document.createElement("button");
    btn.type = "button";
    btn.id = "sc-settings-toggle";
    btn.className = "md-header__button md-icon sc-settings-toggle";
    btn.setAttribute("aria-label", "Open display settings");
    btn.setAttribute("aria-expanded", "false");
    btn.innerHTML = GEAR;
    btn.addEventListener("click", function () {
      if (isOpen()) closeDrawer(); else openDrawer();
    });
    // Place just before the palette toggle if present, else before search, else append.
    var anchor = header.querySelector('[data-md-component="palette"]')
              || header.querySelector('label[for="__search"]')
              || header.querySelector(".md-header__option");
    if (anchor) header.insertBefore(btn, anchor);
    else header.appendChild(btn);
  }

  function init() {
    injectButton();
    buildDrawer();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
  // Re-assert after Material instant navigation (header/body may be re-rendered).
  if (typeof document$ !== "undefined") {
    document$.subscribe(init);
  }
})();
```

- [ ] **Step 2: Lint-check the script parses (no build needed)**

Run: `cd /home/vexa/code/steel_compendium/workspace/v2 && devbox run -- node --check docs/javascripts/settings-panel.js && echo OK`
Expected: `OK` (syntax valid; `node --check` does not execute browser globals).

- [ ] **Step 3: Commit**

```bash
cd /home/vexa/code/steel_compendium/workspace/v2
git add docs/javascripts/settings-panel.js
git commit -m "feat(v2): add live settings drawer behavior (gear button + panel)"
```

---

### Task 5: Wire assets in + extend early-apply, remove old script

**Files:**
- Modify: `v2/mkdocs.yml`
- Modify: `v2/overrides/main.html`
- Delete: `v2/docs/javascripts/preferences.js`

- [ ] **Step 1: Add the stylesheet in `mkdocs.yml`**

In `v2/mkdocs.yml`, change the `extra_css` block ending:

```yaml
  - stylesheets/steel-redesign.css
  - stylesheets/steel-ability-cards.css
  - stylesheets/steel-traits.css
  - stylesheets/steel-indexes.css
```

to (insert `steel-settings.css` right after `steel-redesign.css` so it can use the `--fx-*` tokens):

```yaml
  - stylesheets/steel-redesign.css
  - stylesheets/steel-settings.css
  - stylesheets/steel-ability-cards.css
  - stylesheets/steel-traits.css
  - stylesheets/steel-indexes.css
```

- [ ] **Step 2: Swap the scripts in `mkdocs.yml`**

In `v2/mkdocs.yml`, change:

```yaml
  - javascripts/tablesort.js
  - javascripts/preferences.js
  - javascripts/ability-cards.js
```

to (core must precede the panel):

```yaml
  - javascripts/tablesort.js
  - javascripts/settings-core.js
  - javascripts/settings-panel.js
  - javascripts/ability-cards.js
```

- [ ] **Step 3: Extend the early-apply script in `overrides/main.html`**

In `v2/overrides/main.html`, change the inline `<script>` body inside `{% block extrahead %}`:

```js
            if (s.width) r.setProperty("--md-max_width",   s.width);
            if (s.compact) document.documentElement.setAttribute("data-compact", "true");
```

to:

```js
            if (s.width) r.setProperty("--md-max_width",   s.width);
            if (s.contentScale && s.contentScale != 1) r.setProperty("--sc-content-scale", s.contentScale);
            if (s.compact) document.documentElement.setAttribute("data-compact", "true");
```

- [ ] **Step 4: Delete the obsolete script**

```bash
cd /home/vexa/code/steel_compendium/workspace/v2
git rm docs/javascripts/preferences.js
```

- [ ] **Step 5: Build to confirm wiring**

Run: `cd /home/vexa/code/steel_compendium/workspace/v2 && devbox run -- mkdocs build 2>&1 | tail -8`
Expected: build completes; grep confirms the new assets landed:
`grep -l "settings-panel.js" site/index.html && grep -l "steel-settings.css" site/index.html`
Expected: both print `site/index.html`.

- [ ] **Step 6: Commit**

```bash
cd /home/vexa/code/steel_compendium/workspace/v2
git add mkdocs.yml overrides/main.html
git commit -m "feat(v2): wire settings panel assets, drop standalone preferences.js"
```

---

### Task 6: Retire the standalone preferences page

Convert the page to a short redirect note and drop it from the nav. `static_content/docs/preferences.md` is the source (copied over `docs/preferences.md` on build); both `docs/preferences.md` and `docs/.nav.yml` are protected by `cleanDocsDir`, so edit them directly too.

**Files:**
- Modify: `v2/static_content/docs/preferences.md`
- Modify: `v2/docs/preferences.md`
- Modify: `v2/docs/.nav.yml`

- [ ] **Step 1: Replace the static-source page with a redirect note**

Overwrite `v2/static_content/docs/preferences.md` with:

```markdown
---
search:
  exclude: true
---

# Preferences

Settings now live in the **gear icon** at the top-right of every page — open it to
adjust fonts, text size, page width, theme, compact mode, and card style. Changes
apply instantly and are saved in your browser, so there's no separate page to visit.

<p><button type="button" class="sc-settings-reset" style="max-width: 18rem"
   onclick="document.getElementById('sc-settings-toggle') && document.getElementById('sc-settings-toggle').click()">
   Open settings
</button></p>
```

- [ ] **Step 2: Mirror it to the committed build artifact**

Copy the same content to the protected build artifact so the repo stays consistent without a full rebuild:

```bash
cd /home/vexa/code/steel_compendium/workspace/v2
cp static_content/docs/preferences.md docs/preferences.md
```

- [ ] **Step 3: Remove the page from the nav**

In `v2/docs/.nav.yml`, change:

```yaml
nav:
   - index.md
   - Browse
   - Read
   - Bestiary
   - preferences.md
```

to:

```yaml
nav:
   - index.md
   - Browse
   - Read
   - Bestiary
```

- [ ] **Step 4: Build and confirm the page is gone from nav but still reachable**

Run: `cd /home/vexa/code/steel_compendium/workspace/v2 && devbox run -- mkdocs build 2>&1 | tail -5`
Then: `test -f site/preferences/index.html && echo "page exists" ; grep -c "preferences/" site/index.html || true`
Expected: `page exists` prints (old bookmarks still resolve), and the top-nav tabs in `site/index.html` no longer list a Preferences tab (the grep count for a nav link should be 0 or only incidental).

- [ ] **Step 5: Commit**

```bash
cd /home/vexa/code/steel_compendium/workspace/v2
git add static_content/docs/preferences.md docs/preferences.md docs/.nav.yml
git commit -m "feat(v2): retire standalone preferences page (redirect note + drop nav tab)"
```

---

### Task 7: End-to-end verification (desktop + mobile)

Drive the built site with Playwright (MCP) to confirm live behavior, persistence, and the mobile bottom sheet. Uses the Playwright MCP tools (`browser_navigate`, `browser_evaluate`, `browser_resize`, `browser_snapshot`, `browser_click`).

**Files:** none (verification only).

- [ ] **Step 1: Serve the built site in the background**

Run: `cd /home/vexa/code/steel_compendium/workspace/v2 && devbox run -- mkdocs serve -a 127.0.0.1:8123` (run in background).
Expected: server logs "Serving on http://127.0.0.1:8123/". If it errors on missing generated content, run `cd /home/vexa/code/steel_compendium/workspace && just deploy-v2` once, then re-serve.

- [ ] **Step 2: Desktop — gear opens drawer**

- `browser_resize` to 1280×900.
- `browser_navigate` to `http://127.0.0.1:8123/`.
- `browser_evaluate`: `() => !!document.getElementById('sc-settings-toggle')` → Expected: `true`.
- `browser_click` the element with id `sc-settings-toggle`.
- `browser_evaluate`: `() => document.documentElement.getAttribute('data-sc-settings')` → Expected: `"open"`.

- [ ] **Step 3: Desktop — text-size slider applies live and persists**

- `browser_evaluate`:
  ```js
  () => {
    const s = document.getElementById('set-scale');
    s.value = '1.3';
    s.dispatchEvent(new Event('input', { bubbles: true }));
    s.dispatchEvent(new Event('change', { bubbles: true }));
    return {
      cssVar: getComputedStyle(document.documentElement).getPropertyValue('--sc-content-scale').trim(),
      stored: JSON.parse(localStorage.getItem('mkdocs:fontPrefs')).contentScale,
      label: document.getElementById('set-scale-val').textContent
    };
  }
  ```
  Expected: `{ cssVar: "1.3", stored: 1.3, label: "130%" }`.
- `browser_evaluate`: confirm body text actually grew —
  ```js
  () => parseFloat(getComputedStyle(document.querySelector('.md-typeset')).fontSize)
  ```
  Record the value; reset scale to 1.0 via the slider and confirm the font-size shrinks back.

- [ ] **Step 4: Desktop — page-width full toggle + slider**

- `browser_evaluate`:
  ```js
  () => {
    const f = document.getElementById('set-fullwidth');
    const w = document.getElementById('set-width');
    f.checked = false; f.dispatchEvent(new Event('change', { bubbles: true }));
    w.value = '60'; w.dispatchEvent(new Event('change', { bubbles: true }));
    return {
      cssVar: getComputedStyle(document.documentElement).getPropertyValue('--md-max_width').trim(),
      stored: JSON.parse(localStorage.getItem('mkdocs:fontPrefs')).width
    };
  }
  ```
  Expected: `{ cssVar: "60em", stored: "60em" }`. Then re-check `#set-fullwidth` and confirm `--md-max_width` clears and `width` is removed from storage.

- [ ] **Step 5: Desktop — Esc and scrim close; persistence across reload**

- `browser_evaluate`: dispatch `new KeyboardEvent('keydown', {key:'Escape'})` on `document`; confirm `data-sc-settings` attribute is gone.
- `browser_navigate` to reload `http://127.0.0.1:8123/`; `browser_evaluate` that a previously-set pref (e.g. set `contentScale` to 1.2 first, persist, reload) is re-applied: `getComputedStyle(document.documentElement).getPropertyValue('--sc-content-scale').trim()` → Expected matches stored value, with **no flash** (it's set by the inline early-apply in `main.html`).

- [ ] **Step 6: Mobile — bottom sheet layout**

- `browser_resize` to 390×844.
- `browser_navigate` to `http://127.0.0.1:8123/`.
- `browser_click` `#sc-settings-toggle`.
- `browser_evaluate`:
  ```js
  () => {
    const d = document.getElementById('sc-settings-drawer');
    const r = d.getBoundingClientRect();
    return { atBottom: Math.abs(r.bottom - window.innerHeight) < 2, fullWidth: r.width >= window.innerWidth - 2 };
  }
  ```
  Expected: `{ atBottom: true, fullWidth: true }`.
- `browser_take_screenshot` for a visual sanity check of the high-fantasy styling on mobile.

- [ ] **Step 7: Stop the server**

Stop the background `mkdocs serve` process.

- [ ] **Step 8: Record results**

No commit. If any check fails, fix in the relevant task's files and re-run. Note: the card-style control intentionally reloads the page (parity with prior behavior); verify changing it doesn't throw, but a full reload is expected.

---

### Task 8: Docs sync, follow-ups, and final commit

**Files:**
- Modify: `v2/.repo-docs/conventions.md` (or the closest UI-architecture doc — confirm during the task)
- Modify: `/home/vexa/code/steel_compendium/workspace/FOLLOWUPS.md`

- [ ] **Step 1: Document the settings panel in repo docs**

Add a short subsection to `v2/.repo-docs/conventions.md` (verify it's the right home with `grep -rn "preferences" v2/.repo-docs`; if a more specific doc owns UI/JS, use that):

```markdown
### Live settings panel

User display settings are delivered by a gear button injected into the Material
header (`docs/javascripts/settings-panel.js`), which opens a steel-styled drawer
(`docs/stylesheets/steel-settings.css`) — a right-side panel on desktop, a bottom
sheet on mobile. All settings write to `localStorage["mkdocs:fontPrefs"]` and apply
live via `<html>` attributes / CSS custom properties. Pure parsing/normalization
logic is unit-tested in `tests/settings-core.test.js` against the DOM-free
`docs/javascripts/settings-core.js` (`devbox run -- node --test tests/`).

The anti-FOUC early-apply script in `overrides/main.html` reads the same storage key
to set fonts, width, `--sc-content-scale`, compact, theme, and card-style before paint.
The standalone `/preferences/` page is retired to a redirect note (still reachable for
old bookmarks) and removed from `docs/.nav.yml`.
```

- [ ] **Step 2: Log the card-style reload as a follow-up**

Append to `/home/vexa/code/steel_compendium/workspace/FOLLOWUPS.md` a new numbered section (use the next free number; check the file first):

```markdown
## N. Settings panel: card-style toggle still triggers a full page reload

The "Ability card style" control in the live settings drawer calls `location.reload()`
on change (carried over from the old preferences page), which conflicts with the
"change settings without navigating away / see it live" goal for that one control.
Investigate whether classic↔modern can be made a pure CSS/attribute swap (it toggles
`data-card-style` on `<html>`); if any card markup is build-time only, document why the
reload is required and consider a lighter in-place re-render instead.
```

- [ ] **Step 3: Run the full unit-test suite once more**

Run: `cd /home/vexa/code/steel_compendium/workspace/v2 && devbox run -- node --test tests/`
Expected: PASS.

- [ ] **Step 4: Commit**

```bash
cd /home/vexa/code/steel_compendium/workspace
git add v2/.repo-docs/conventions.md FOLLOWUPS.md
git commit -m "docs(v2): document live settings panel; log card-style reload follow-up"
```

---

## Self-Review

**Spec coverage:**
- "Change settings without navigating away" → gear button + drawer (Tasks 3–5). ✓
- "Hidden sidebar / popup" → right-side drawer / bottom sheet (Task 3). ✓
- "Unobtrusive, see effects live" → all controls apply on `input`/`change`; drawer overlays content so changes are visible behind it (Tasks 3–4). ✓
- "Adjust overall UI element sizes via a slider, exact size while dragging" → content-scale slider with live `input` apply (Tasks 2, 4). ✓ (scoped to reading content per the confirmed decision).
- "Match high-fantasy style" → `--fx-*` tokens, embossed labels, steel slider/crest styling (Task 3). ✓
- "Display well on mobile" → bottom-sheet layout + grab handle + verification at 390px (Tasks 3, 7). ✓
- "Use existing Material plugins/extensions if helpful" → reuses Material header button classes (`md-header__button md-icon`), instant-nav `document$` re-binding, and the existing palette toggle for light/dark rather than reinventing it (Tasks 4, 6). No third-party plugin adds a settings drawer, so a custom overlay is the right call; noted. ✓
- "More user-friendly where it didn't make sense" → page-width text-input-with-Apply replaced by a live slider + Full-width toggle; fonts tucked into a collapsible `<details>` to reduce mobile clutter; "Reset all" added; standalone page retired to a redirect (Tasks 4, 6). ✓

**Placeholder scan:** No TBD/TODO/"add error handling" placeholders; every code step shows complete content. Storage parsing guards bad JSON; `clampScale`/`clampEm`/`normalizeWidth` fail safe to defaults. ✓

**Type/name consistency:** `SettingsCore` API names (`clampScale`, `normalizeWidth`, `clampEm`, `widthToControls`, `controlsToWidth`, `loadPrefs`, `savePrefs`, and the `SCALE_*`/`WIDTH_*` constants) are defined in Task 1 and used identically in Task 4. CSS hooks are consistent across files: `--sc-content-scale` (Tasks 2, 4, 5), `data-sc-settings="open"` (Tasks 3, 4), element ids `sc-settings-toggle` / `sc-settings-drawer` / `sc-settings-scrim` and control ids `set-*` (Tasks 3-comment, 4, 6, 7). Storage key `mkdocs:fontPrefs` matches the existing schema and the early-apply script (Tasks 4, 5). ✓

---

## Post-merge changes

Changes made after this plan merged to `main`, recorded here so the plan stays a faithful history. The code blocks above show the **as-originally-built** state; the values below are the current ones.

1. **Card-size slider added (2026-06-07).** A second scale slider, **Card size**, was added to the Reading group. The generated `.sc-ability`/`.sc-trait` cards size everything in `rem`/`px`, so they don't follow `--sc-content-scale`; the card slider drives a new `--sc-card-scale` applied as CSS **`zoom`** on top-level cards (in `extra.css`), scaling text, padding, badges, power-roll panel, and height proportionally. Nested cards (an ability or sub-trait inside a trait) are reset to `zoom:1` so they inherit the parent's zoom instead of compounding it. Backed by a new unit-tested `clampCardScale` helper (`CARD_MIN=0.7, CARD_MAX=1.2, CARD_STEP=0.05`), a `cardScale` storage key, and early-apply in `overrides/main.html`. Gotcha: `zoom` applies at the render layer, so `getComputedStyle().fontSize` reports the *unzoomed* value — assert on rendered geometry (`getBoundingClientRect`) instead.

   **Index-grid coverage (2026-06-09).** The original card-scale rule only zoomed `.sc-ability`/`.sc-trait`, so the slider had no effect on index/landing pages, which use card *grids* instead: `.sc-cards` (Browse landing, `steel-redesign.css`), `.sc-folders` (folder nav) and `.sc-prevs` (preview + JS browse results, `steel-indexes.css`). The `extra.css` zoom rule now also targets those three grid *containers* (not each cell), so tracks, gaps, and contents scale together and the `auto-fill` grids reflow to more/fewer columns as the scale changes. Verified with Brave-headless screenshots at scale 1.0 vs 0.7 on a `.sc-folders`, a `.sc-cards`, and a `.sc-prevs` page.

2. **Page-width max raised 100em → 500em (2026-06-07).** `WIDTH_MAX_EM` changed from `100` to `500` in `settings-core.js` (slider now spans 44–500em, step 2). Unit tests and the E2E updated accordingly.

3. **Real-browser E2E exists.** Despite the original plan's "Playwright doesn't work here" finding, the Playwright **MCP** is the only broken piece — `tests/e2e/settings-panel.e2e.cjs` drives the locally-installed **Brave** via `playwright-core` + `executablePath` and covers the whole drawer (30 assertions). See `.repo-docs/troubleshooting.md`.
