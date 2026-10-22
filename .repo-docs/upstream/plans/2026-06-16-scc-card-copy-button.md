> **上游歷史參考，非本站現行治理或待辦。** 本站規則見 [中文化治理入口](../../index.md)；不得直接執行本文的推送、部署或私有字型流程。

# SCC Card Copy-Link Button Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a non-intrusive, hover-revealed button to statblock, featureblock, and ability card pages that copies the page's stable SCC permalink URL to the clipboard.

**Architecture:** Pure v2-side change — **no `steel-etl`/Go changes**. These three card types (`.sb-wrap`, `.fb-wrap`, `.sc-ability`) hide their page `<h1>` via CSS, which also hides the `<h1>`'s native heading-permalink (¶) copy affordance that `scc-headerlinks.js` wires elsewhere. The page already emits `<meta name="scc-permalink" content="…/scc/<code>/">` on exactly those leaf pages (any page whose frontmatter has `scc`). A new client module reads that meta and injects one copy button into the page's primary card. Logic that is brittle/testable (which element is a card, cleaning the meta value) is extracted into a DOM-free UMD `*-core.js` module with `node:test` unit tests; the thin DOM-wiring module mirrors the existing `scc-headerlinks.js` and is `navigation.instant`-safe via `document$`. This follows the repo's established `settings-core.js` (tested) + `settings-panel.js` (untested wiring) split.

**Tech Stack:** Vanilla ES5-style browser JS (UMD for `node:test`), CSS, MkDocs Material (`document$` instant-navigation), `node:test` via devbox.

---

## Background facts (verified against the codebase)

- **Meta source:** `v2/overrides/main.html:60-67` emits `<meta name="scc-permalink" content="{{ config.site_url }}scc/{{ page.meta.scc }}/">` whenever `page.meta.scc` is set. Statblock/featureblock/ability leaf pages carry `scc` frontmatter, so the meta is present. Index/preview pages do **not** get a per-card meta — by design we do not add buttons there (matches the user's "those are fine" note).
- **The three card types each hide their H1** (so each loses the ¶ copy affordance):
  - `v2/docs/stylesheets/steel-statblock.css:51-52` → `.md-typeset:has(> .sb-wrap) > h1:first-child { display:none }`
  - `v2/docs/stylesheets/steel-featureblock.css:32-33` → `.md-typeset:has(> .fb-wrap) …`
  - `v2/docs/stylesheets/steel-ability-cards.css:205-206` → `.md-typeset:has(> .sc-ability) …`
  - **Trait pages keep their H1** (`.sc-trait` is not in any hide rule), so they already have a working ¶ — out of scope.
- **The gate that means "this is a primary card page":** in all three hide rules the card is a **direct child of `.md-typeset`** (`:has(> .X)`). The wiring module reuses this exact condition (`card.parentElement.classList.contains("md-typeset")`) so it injects only on real card pages and never on embedded cards (a kit's nested signature ability, a statblock's nested feature, an index preview).
- **Distinguishing a standalone ability from an embedded one:** embedded statblock features are `class="sc-ability sb__feat"` (`statblock_card.go:99`), standalone ability page cards are `class="sc-ability"` without `sb__feat`. The core's `cardKind` rejects any element carrying the `sb__feat` token.
- **`querySelector` document order:** on a statblock page the `.sb-wrap` element precedes its descendant `.sc-ability` features, so `content.querySelector(".sb-wrap, .fb-wrap, .sc-ability")` returns the wrapper, not a nested feature. On an ability page (no wrapper) it returns the standalone `.sc-ability`. This single query yields the correct primary card for all three page types.
- **All three card hosts are `position: relative`** (`steel-statblock.css:65`, `steel-featureblock.css:39`, `steel-ability-cards.css:39`) — so an absolutely-positioned child button anchors to the card. `.sc-ability` additionally has `overflow:hidden`, so the button and its "Copied" label must sit inside the card bounds (top-right, within padding).
- **Test command** (run from `v2/`): `devbox run -- node --test docs/javascripts/<file>.test.js`. Devbox's `node` script `cd`s into `v2/`, so test paths are `v2`-relative.
- **Reference design** (the pattern we are porting): `reference/design-system/handoff/preview/comp-ability-card.html:72-86,184-189` — a persistent cost badge with hover-revealed `.ops` utility buttons "tucked just beneath it", each a `<span class="op" title="Copy permalink">` holding a thin-line link SVG. We reuse that link SVG verbatim.

---

## File Structure

- **Create** `v2/docs/javascripts/scc-card-copy-core.js` — DOM-free UMD module. Two pure functions: `cardKind(className)` and `cleanPermalink(raw)`. The brittle, unit-tested logic.
- **Create** `v2/docs/javascripts/scc-card-copy-core.test.js` — `node:test` unit tests for the core.
- **Create** `v2/docs/javascripts/scc-card-copy.js` — thin DOM-wiring module. Reads the meta, finds the primary card, injects the button, wires clipboard + flash, subscribes to `document$`. Mirrors `scc-headerlinks.js`.
- **Create** `v2/docs/stylesheets/steel-copylink.css` — button styling: hover-reveal (desktop), faint-persistent (touch), per-card-type positioning, copied flash, print-hidden.
- **Modify** `v2/mkdocs.yml` — register the new CSS and the two new JS files (core before wiring).
- **Modify** `v2/DESIGN.md` — one-line note in the component map for the new `.sc-copylink` hover utility.

---

## Task 1: Core logic module (DOM-free, unit-tested)

**Files:**
- Create: `v2/docs/javascripts/scc-card-copy-core.js`
- Test: `v2/docs/javascripts/scc-card-copy-core.test.js`

- [ ] **Step 1: Write the failing test**

Create `v2/docs/javascripts/scc-card-copy-core.test.js`:

```js
const test = require("node:test");
const assert = require("node:assert");
const C = require("./scc-card-copy-core.js");

test("cardKind detects the statblock wrapper", () => {
  assert.strictEqual(C.cardKind("sb-wrap"), "sb");
  assert.strictEqual(C.cardKind("md-typeset sb-wrap"), "sb");
});

test("cardKind detects the featureblock wrapper", () => {
  assert.strictEqual(C.cardKind("fb-wrap"), "fb");
});

test("cardKind detects a standalone ability card", () => {
  assert.strictEqual(C.cardKind("sc-ability"), "ability");
});

test("cardKind rejects an ability embedded in a statblock (sb__feat)", () => {
  assert.strictEqual(C.cardKind("sc-ability sb__feat"), "");
});

test("cardKind uses whole-token matching, not substring", () => {
  // "scc-ability-foo" must NOT match the "sc-ability" token.
  assert.strictEqual(C.cardKind("scc-ability-foo"), "");
});

test("cardKind returns '' for unrelated or empty class strings", () => {
  assert.strictEqual(C.cardKind("md-typeset"), "");
  assert.strictEqual(C.cardKind(""), "");
  assert.strictEqual(C.cardKind(null), "");
});

test("cleanPermalink trims whitespace", () => {
  assert.strictEqual(C.cleanPermalink("  https://x/scc/a/  "), "https://x/scc/a/");
});

test("cleanPermalink returns '' for empty / nullish input", () => {
  assert.strictEqual(C.cleanPermalink("   "), "");
  assert.strictEqual(C.cleanPermalink(null), "");
  assert.strictEqual(C.cleanPermalink(undefined), "");
});
```

- [ ] **Step 2: Run the test to verify it fails**

Run (from `v2/`): `devbox run -- node --test docs/javascripts/scc-card-copy-core.test.js`
Expected: FAIL — `Cannot find module './scc-card-copy-core.js'`.

- [ ] **Step 3: Write the minimal implementation**

Create `v2/docs/javascripts/scc-card-copy-core.js`:

```js
/*
 * scc-card-copy-core.js — pure, DOM-free helpers for the card copy-link button.
 * UMD: exports for `node:test`, attaches to window.SccCardCopy in the browser.
 * Loaded BEFORE scc-card-copy.js in mkdocs.yml.
 */
;(function (root, factory) {
  if (typeof module === "object" && module.exports) {
    module.exports = factory();
  } else {
    root.SccCardCopy = factory();
  }
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  // Classify a card element by its className string. Whole-token matching (split
  // on whitespace) so "scc-ability-foo" never matches the "sc-ability" token.
  // Embedded statblock features carry "sb__feat" and are rejected — only the
  // standalone ability page card qualifies.
  function cardKind(className) {
    var tokens = String(className == null ? "" : className).split(/\s+/);
    function has(c) { return tokens.indexOf(c) !== -1; }
    if (has("sb-wrap")) return "sb";
    if (has("fb-wrap")) return "fb";
    if (has("sc-ability") && !has("sb__feat")) return "ability";
    return "";
  }

  // Trim a meta value; "" signals "no usable permalink".
  function cleanPermalink(raw) {
    return (raw == null ? "" : String(raw)).trim();
  }

  return { cardKind: cardKind, cleanPermalink: cleanPermalink };
});
```

- [ ] **Step 4: Run the test to verify it passes**

Run (from `v2/`): `devbox run -- node --test docs/javascripts/scc-card-copy-core.test.js`
Expected: PASS — `# pass 8`, `# fail 0`.

- [ ] **Step 5: Commit**

```bash
git add v2/docs/javascripts/scc-card-copy-core.js v2/docs/javascripts/scc-card-copy-core.test.js
git commit -m "feat(v2): add DOM-free core for SCC card copy-link button"
```

---

## Task 2: DOM-wiring module

**Files:**
- Create: `v2/docs/javascripts/scc-card-copy.js`

This module has no unit test (it is DOM/browser wiring with no extractable logic left — the testable parts live in the core, matching the repo's `settings-panel.js` convention). It is verified end-to-end in Task 5.

- [ ] **Step 1: Write the module**

Create `v2/docs/javascripts/scc-card-copy.js`:

```js
/**
 * SCC card copy-link button.
 *
 * Statblock (.sb-wrap), featureblock (.fb-wrap), and ability (.sc-ability) card
 * pages hide their page <h1>, which also hides the native heading-permalink (¶)
 * copy affordance that scc-headerlinks.js wires elsewhere. This module restores a
 * copy affordance for those pages: it injects ONE small button into the page's
 * primary card that copies the stable /scc/<code>/ permalink (from the page's
 * <meta name="scc-permalink">) to the clipboard.
 *
 * Non-intrusive by design: the button is hidden until the card is hovered
 * (desktop) so it stays out of screenshots; on touch devices (no hover) it shows
 * faint-but-persistent (see steel-copylink.css). Hidden when printing.
 *
 * Gate: injects only when the primary card is a DIRECT child of .md-typeset — the
 * same condition the CSS uses to hide the H1 — so embedded cards (a statblock's
 * nested feature, a kit's signature ability, an index-page preview) never get a
 * button. Uses document$ so it re-runs under Material's navigation.instant, and is
 * idempotent (skips a card that already has a button). Adds no window/document
 * listeners; the per-button click handler dies with the card on body swap.
 */
(function () {
  "use strict";

  var Core = (typeof window !== "undefined" && window.SccCardCopy) || {};
  var SELECTOR = ".sb-wrap, .fb-wrap, .sc-ability";
  // Thin-line link icon, reused verbatim from the original card design mockup
  // (reference/design-system/handoff/preview/comp-ability-card.html).
  var ICON =
    '<svg viewBox="0 0 24 24" aria-hidden="true">' +
    '<path d="M10 14a4 4 0 0 0 5.66 0l3-3a4 4 0 0 0-5.66-5.66l-1 1"/>' +
    '<path d="M14 10a4 4 0 0 0-5.66 0l-3 3a4 4 0 0 0 5.66 5.66l1-1"/></svg>';

  function metaContent(name) {
    var m = document.querySelector('meta[name="' + name + '"]');
    return m ? m.getAttribute("content") : null;
  }

  function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(text);
    }
    // Fallback for non-secure contexts (e.g. http:// during local preview).
    return new Promise(function (resolve, reject) {
      try {
        var ta = document.createElement("textarea");
        ta.value = text;
        ta.setAttribute("readonly", "");
        ta.style.position = "absolute";
        ta.style.left = "-9999px";
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        document.body.removeChild(ta);
        resolve();
      } catch (e) {
        reject(e);
      }
    });
  }

  function flash(btn) {
    btn.classList.add("sc-copylink--copied");
    setTimeout(function () {
      btn.classList.remove("sc-copylink--copied");
    }, 1200);
  }

  function render() {
    var url = Core.cleanPermalink(metaContent("scc-permalink"));
    if (!url) return;

    var content = document.querySelector(".md-content");
    if (!content) return;

    var card = content.querySelector(SELECTOR);
    if (!card) return;

    var kind = Core.cardKind(card.className);
    if (!kind) return;

    // Primary-card gate: same condition as the CSS H1-hide rules.
    if (!card.parentElement || !card.parentElement.classList.contains("md-typeset")) return;

    // Idempotent under navigation.instant re-fires.
    if (card.querySelector(":scope > .sc-copylink")) return;

    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "sc-copylink";
    btn.setAttribute("data-card", kind);
    btn.setAttribute("aria-label", "Copy permalink");
    btn.setAttribute("title", "Copy permalink (" + url + ")");
    btn.innerHTML = ICON;
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      copyText(url).then(
        function () { flash(btn); },
        function () { /* clipboard blocked; nothing else to do */ }
      );
    });
    card.appendChild(btn);
  }

  if (typeof document$ !== "undefined") {
    document$.subscribe(render);
  } else {
    document.addEventListener("DOMContentLoaded", render);
  }
})();
```

- [ ] **Step 2: Syntax-check the module**

Run (from `v2/`): `devbox run -- node --check docs/javascripts/scc-card-copy.js`
Expected: no output, exit 0 (parse OK).

- [ ] **Step 3: Commit**

```bash
git add v2/docs/javascripts/scc-card-copy.js
git commit -m "feat(v2): wire SCC copy-link button onto card pages"
```

---

## Task 3: Stylesheet

**Files:**
- Create: `v2/docs/stylesheets/steel-copylink.css`

- [ ] **Step 1: Write the stylesheet**

Create `v2/docs/stylesheets/steel-copylink.css`:

```css
/* SCC card copy-link button (scc-card-copy.js).
   A small utility button injected into the top-right corner of statblock,
   featureblock, and ability cards — "tucked under the cost chip", matching the
   original card design's hover .ops toolbar. Copies the page's stable
   /scc/<code>/ permalink. Hidden until hover (desktop) so it stays out of
   screenshots; faint-but-persistent on touch; hidden in print. */

.sc-copylink {
  position: absolute;
  z-index: 4;
  width: 1.7rem;
  height: 1.7rem;
  padding: 0;
  display: grid;
  place-items: center;
  border-radius: 0.35rem;
  color: var(--md-default-fg-color--light);
  background: rgba(0, 0, 0, 0.4);
  border: 1px solid var(--md-default-fg-color--lightest);
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.18s ease, color 0.18s ease, border-color 0.18s ease;
}

.sc-copylink svg {
  width: 0.95rem;
  height: 0.95rem;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.7;
}

.sc-copylink:hover {
  color: var(--md-accent-fg-color);
  border-color: var(--md-accent-fg-color);
}

/* Reveal on card hover (desktop) and on keyboard focus (a11y). */
.sb-wrap:hover .sc-copylink,
.fb-wrap:hover .sc-copylink,
.sc-ability:hover .sc-copylink,
.sc-copylink:focus-visible {
  opacity: 1;
}

/* Touch devices have no hover: show faint-but-persistent so the affordance
   exists without being loud. */
@media (hover: none) {
  .sc-copylink {
    opacity: 0.4;
  }
}

/* Per-card-type placement: top-right, sat under the card's cost/EV chip. */
.sc-copylink[data-card="sb"] { top: 3.1rem; right: 0.7rem; }      /* under .sb__class (role + EV) */
.sc-copylink[data-card="ability"] { top: 3rem; right: 0.8rem; }   /* under .sc-ability__cost */
.sc-copylink[data-card="fb"] { top: 0.85rem; right: 0.85rem; }    /* fb head right corner is clear */

/* Transient "Copied" confirmation, placed to the LEFT of the button so it stays
   inside .sc-ability's overflow:hidden bounds. */
.sc-copylink--copied::after {
  content: "Copied";
  position: absolute;
  right: calc(100% + 0.35rem);
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.62rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  white-space: nowrap;
  color: var(--md-accent-fg-color);
}

@media print {
  .sc-copylink { display: none !important; }
}
```

- [ ] **Step 2: Commit**

```bash
git add v2/docs/stylesheets/steel-copylink.css
git commit -m "feat(v2): style SCC card copy-link button (hover/touch/print)"
```

---

## Task 4: Register assets in mkdocs.yml

**Files:**
- Modify: `v2/mkdocs.yml` (extra_css around line 126; extra_javascript around line 149)

- [ ] **Step 1: Add the stylesheet to `extra_css`**

In `v2/mkdocs.yml`, the `extra_css:` block currently ends with `- stylesheets/steel-bestiary.css`. Add the new stylesheet immediately after it:

```yaml
  - stylesheets/steel-bestiary.css
  - stylesheets/steel-copylink.css
```

- [ ] **Step 2: Add the JS to `extra_javascript`**

In `v2/mkdocs.yml`, the `extra_javascript:` block currently ends with `- javascripts/scc-headerlinks.js`. Add the core (first) then the wiring module after it — the core MUST load before the wiring module:

```yaml
  - javascripts/scc-headerlinks.js
  - javascripts/scc-card-copy-core.js
  - javascripts/scc-card-copy.js
```

- [ ] **Step 3: Verify the YAML still parses**

Run (from `v2/`): `devbox run -- python -c "import yaml; yaml.safe_load(open('mkdocs.yml'))" && echo OK`
Expected: `OK` (no traceback).

- [ ] **Step 4: Commit**

```bash
git add v2/mkdocs.yml
git commit -m "build(v2): register SCC card copy-link assets"
```

---

## Task 5: Build and verify end-to-end

**Files:** none (verification only)

- [ ] **Step 1: Re-run the core unit tests**

Run (from `v2/`): `devbox run -- node --test docs/javascripts/scc-card-copy-core.test.js`
Expected: `# pass 8`, `# fail 0`.

- [ ] **Step 2: Build the site**

From the workspace root, regenerate content + build the v2 site so the generated card pages exist:

Run: `devbox run -- just deploy-v2`
Expected: pipeline + MkDocs build complete with no errors. (A bare `cd v2 && mkdocs build` also works if generated `docs/Browse`/`docs/Read` content is already present from a prior run.)

- [ ] **Step 3: Serve and manually verify each card type**

Run (from `v2/`): `devbox run -- mkdocs serve`
Then in a browser (Brave — see memory `reference_playwright_mcp_broken`) check one page of each type:
- A **statblock** Browse page (any monster, e.g. a goblin statblock under `Browse/`).
- A **featureblock** page (a Monsters terrain/featureblock or a fixture).
- An **ability** page (any hero/class ability card).

For each, confirm:
1. **No button is visible** when the cursor is away from the card (screenshot-clean).
2. **Hovering the card reveals** the button in the top-right, under the cost/EV chip.
3. **Clicking copies** the `…/scc/<code>/` URL (paste to confirm) and flashes "Copied".
4. The button's `title` shows the full SCC URL on hover.

- [ ] **Step 4: Verify the touch (no-hover) presentation**

In the browser devtools, emulate a touch device (or use the `(hover: none)` media emulation). Confirm the button is **faintly persistent** (opacity ~0.4) and tapping it copies.

- [ ] **Step 5: Verify navigation.instant safety**

Still in `mkdocs serve`, navigate *client-side* (click an in-site link) from a non-card page to a statblock page, then to another statblock page, without a full reload. Confirm the button appears on each (the `document$` subscription re-runs) and that no page ever shows **two** buttons (idempotency). Note: per `v2/CLAUDE.md`, instant-nav bugs may only fully reproduce on the deployed site — if anything looks off locally, re-check on a real deploy preview.

- [ ] **Step 6: Confirm negative cases (no spurious buttons)**

Confirm a button does **NOT** appear on:
- An **index/preview** page that shows `.sb-prev` mini-statblocks (no per-card `scc-permalink` meta → gate returns early).
- A **trait** page (`.sc-trait`, keeps its H1 and native ¶ — `cardKind` returns `""`).
- The embedded ability features *inside* a statblock (only the wrapper gets the single button).

- [ ] **Step 7: Commit (if any positioning nudges were made)**

If Step 3 revealed that a `top`/`right` offset in `steel-copylink.css` needs adjustment for visual alignment under the chip, make the minimal edit and commit:

```bash
git add v2/docs/stylesheets/steel-copylink.css
git commit -m "style(v2): nudge SCC copy-link button alignment"
```

If no change was needed, skip this step.

---

## Task 6: Documentation

**Files:**
- Modify: `v2/DESIGN.md` (component map / utility-icon section)

- [ ] **Step 1: Add a component-map note**

In `v2/DESIGN.md`, near where UI utility icons are described (the "Never hand-draw new SVG icons" guidance around line 88), add a short note documenting the new pattern:

```markdown
- **Card copy-link button (`.sc-copylink`).** Statblock / featureblock / ability
  card pages hide their `<h1>` (and thus the native ¶ permalink), so
  `scc-card-copy.js` injects a small hover-revealed button in the card's top-right
  corner (under the cost/EV chip) that copies the page's `/scc/<code>/` permalink.
  Hidden until hover on desktop (screenshot-clean), faint-persistent on touch,
  hidden in print. Styling: `docs/stylesheets/steel-copylink.css`.
```

- [ ] **Step 2: Commit**

```bash
git add v2/DESIGN.md
git commit -m "docs(v2): note the .sc-copylink card copy-link pattern"
```

---

## Self-Review notes

- **Spec coverage:** copy SCC URL to clipboard (Task 2 click handler + meta read); non-intrusive / screenshot-safe (Task 3 hover-reveal, opacity 0 default, print hidden); mobile solution (Task 3 `@media (hover: none)` faint-persistent, chosen by the user); statblock + featureblock + ability scope (the `SELECTOR` + `cardKind`, chosen by the user). All covered.
- **No placeholders:** every code step contains the full file/diff content; every run step has an exact command and expected result.
- **Type/name consistency:** `cardKind` / `cleanPermalink` are defined in Task 1 and consumed by name in Task 2; the CSS class `.sc-copylink`, the `--copied` modifier, and the `data-card` values `sb|fb|ability` match across the JS (`btn.className`, `setAttribute("data-card", kind)`, `flash` → `sc-copylink--copied`) and the CSS selectors; the `cardKind` return values (`"sb"|"fb"|"ability"|""`) match the `data-card` placement rules.
- **Out of scope (intentional):** preview/embed cards on index pages and trait pages (covered already), and any `steel-etl` change (the page meta already carries the URL).
