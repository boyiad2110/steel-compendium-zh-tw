> **上游歷史參考，非本站現行治理或待辦。** 本站規則見 [中文化治理入口](../../index.md)；不得直接執行本文的推送、部署或私有字型流程。

# Statblock Feature Style (`data-sb-featstyle`) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the `data-sb-featstyle` (card | flat) statblock preference per the approved design (`2026-06-12-statblock-feature-style.md` in this directory), restructure the statblock CSS kill rules to exact specificity floors (closes workspace FOLLOWUPS #8), and fix the five dead scheme-first selectors.

**Architecture:** CSS-only layout change riding the existing statblock DOM (zero steel-etl changes). The new preference follows the established `data-sb-*` contract: attribute on `<html>`, stamped by the `overrides/main.html` early-apply and `settings-panel.js`, persisted in `localStorage["mkdocs:fontPrefs"]` under `prefs.statblock.featstyle`, bundled by the three presets. Read the design doc first — it locks all decisions.

**Tech Stack:** MkDocs Material (no JS build step — ES5-safe vanilla JS served as-is), Brave via playwright-core for e2e (`tests/e2e/*.e2e.cjs` pattern), `node:test` unit tests (untouched but run for regression). All commands run via `devbox run --`.

**Repos touched:** `v2` (CSS, JS, template, tests, repo docs) and the **workspace** repo (DESIGN.md, FOLLOWUPS.md archive). Two separate git repos — commit in each.

---

## Pre-flight

- [ ] Read the design doc: `v2/.repo-docs/plans/2026-06-12-statblock-feature-style.md`
- [ ] Read `v2/.repo-docs/troubleshooting.md` § "Statblock/ability-card CSS edits have no visible effect" (the contested-pseudo-element footgun this plan restructures)
- [ ] Confirm a built site exists at `v2/site/` (`ls v2/site/index.html`). If missing: `cd v2 && devbox run -- mkdocs build` (~145s)

---

### Task 1: Failing e2e test (RED)

**Files:**
- Create: `v2/tests/e2e/statblock-featstyle.e2e.cjs`

The fixture page `Browse/monster/arixx/arixx/` is a solo monster: multiple features **and** a villain-actions band. Statblocks are client-rendered from a JSON island (`div.sc-statblock-mount` → `steel-statblock.js` mounts `.sb-wrap`), so every navigation must wait for `.sb-wrap`.

- [ ] **Step 1.1: Write the test file**

```js
/*
 * statblock-featstyle.e2e.cjs — e2e for the data-sb-featstyle preference
 * (card vs flat feature frames inside statblocks) + the FOLLOWUPS #8
 * specificity-paydown regression guards.
 *
 * Same harness as settings-panel.e2e.cjs (Brave via playwright-core):
 *   cd v2
 *   devbox run -- mkdocs build                                   # ~145s
 *   devbox run -- python3 -m http.server 8124 --directory site &
 *   devbox run -- node tests/e2e/statblock-featstyle.e2e.cjs
 *
 * Env overrides: E2E_BASE (default http://127.0.0.1:8124/),
 *                BRAVE_PATH (default /opt/brave.com/brave/brave).
 */
"use strict";
const fs = require("fs");
const path = require("path");
const os = require("os");

function resolvePlaywrightCore() {
  try { return require("playwright-core"); } catch (_) {}
  try { return require("playwright"); } catch (_) {}
  const npx = path.join(os.homedir(), ".npm", "_npx");
  let best = null, bestVer = "";
  try {
    for (const hash of fs.readdirSync(npx)) {
      const dir = path.join(npx, hash, "node_modules", "playwright-core");
      const pkg = path.join(dir, "package.json");
      if (fs.existsSync(pkg)) {
        const ver = JSON.parse(fs.readFileSync(pkg, "utf8")).version || "";
        if (ver > bestVer) { bestVer = ver; best = dir; }
      }
    }
  } catch (_) {}
  if (best) return require(best);
  throw new Error("playwright-core not found (install it, or `npx playwright` once to populate ~/.npm/_npx)");
}

const BASE = process.env.E2E_BASE || "http://127.0.0.1:8124/";
const BRAVE = process.env.BRAVE_PATH || "/opt/brave.com/brave/brave";
const PAGE = BASE + "Browse/monster/arixx/arixx/"; // solo: features + villain band

let failures = 0;
function check(name, cond, detail) {
  console.log((cond ? "PASS" : "FAIL") + " - " + name + (detail ? "  (" + detail + ")" : ""));
  if (!cond) failures++;
}

// Computed snapshot of the idx-th feature in the main list (idx 1 = has a `+`
// sibling, so it carries the separator in flat mode). Pass idx as the
// page.evaluate argument: `page.evaluate(FEAT_PROBE, 1)`.
const FEAT_PROBE = (idx) => {
  const f = document.querySelectorAll(".sb__features > .sb__feat")[idx];
  const s = getComputedStyle(f);
  const b = getComputedStyle(f, "::before");
  return {
    borderLeftWidth: s.borderLeftWidth, borderLeftStyle: s.borderLeftStyle,
    background: s.backgroundColor,
    beforeDisplay: b.display, beforeOpacity: b.opacity, beforeBlend: b.mixBlendMode
  };
};

(async () => {
  const { chromium } = resolvePlaywrightCore();
  const browser = await chromium.launch({ executablePath: BRAVE, headless: true, args: ["--no-sandbox"] });
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 } });
  const page = await ctx.newPage();

  await page.goto(PAGE, { waitUntil: "networkidle" });
  await page.waitForSelector(".sb-wrap");

  // ---- default = card ----
  check("default: data-sb-featstyle stamped as card",
    await page.evaluate(() => document.documentElement.getAttribute("data-sb-featstyle") === "card"));
  let f = await page.evaluate(FEAT_PROBE, 1);
  check("card: 3px solid action-colored left border", f.borderLeftWidth === "3px" && f.borderLeftStyle === "solid",
    f.borderLeftWidth + " " + f.borderLeftStyle);
  check("card: tinted container background (dark scheme rgba(0,0,0,0.16))",
    f.background === "rgba(0, 0, 0, 0.16)", f.background);
  check("card: no separator/watermark pseudo", f.beforeDisplay === "none", f.beforeDisplay);

  // ---- light scheme card tint (dead scheme-first selector regression) ----
  await page.evaluate(() => document.body.setAttribute("data-md-color-scheme", "default"));
  f = await page.evaluate(FEAT_PROBE, 1);
  check("card/light: light tint applies (rgba(0,0,0,0.022))",
    f.background === "rgba(0, 0, 0, 0.022)", f.background);
  await page.evaluate(() => document.body.setAttribute("data-md-color-scheme", "slate"));

  // ---- hover guard (kill rule floor) ----
  await page.hover(".sb__features > .sb__feat:nth-of-type(2)");
  const hov = await page.evaluate(() => {
    const el = document.querySelectorAll(".sb__features > .sb__feat")[1];
    const s = getComputedStyle(el);
    return { transform: s.transform, boxShadow: s.boxShadow };
  });
  check("card: no hover lift", hov.transform === "none" && hov.boxShadow === "none",
    hov.transform + " / " + hov.boxShadow);

  // ---- switch to flat via the drawer control ----
  await page.click("#sc-settings-toggle");
  await page.evaluate(() => {
    const s = document.getElementById("set-sb-featstyle");
    s.value = "flat"; s.dispatchEvent(new Event("change", { bubbles: true }));
  });
  check("flat: attribute flips",
    await page.evaluate(() => document.documentElement.getAttribute("data-sb-featstyle") === "flat"));
  check("flat: stored in prefs.statblock.featstyle",
    await page.evaluate(() => JSON.parse(localStorage.getItem("mkdocs:fontPrefs")).statblock.featstyle === "flat"));
  check("flat: preset re-derives to Custom",
    await page.evaluate(() => document.getElementById("set-sb-preset").value === "custom"));

  f = await page.evaluate(FEAT_PROBE, 1);
  check("flat: separator pseudo visible (display/opacity/blend reclaimed)",
    f.beforeDisplay === "block" && f.beforeOpacity === "1" && f.beforeBlend === "normal",
    f.beforeDisplay + "/" + f.beforeOpacity + "/" + f.beforeBlend);
  check("flat: card chrome gone (no left border, no bg)",
    (f.borderLeftStyle === "none" || f.borderLeftWidth === "0px") && f.background === "rgba(0, 0, 0, 0)",
    f.borderLeftStyle + " " + f.borderLeftWidth + " " + f.background);
  const first = await page.evaluate(FEAT_PROBE, 0);
  check("flat: FIRST feature shows no watermark (kill rule intact)",
    first.beforeDisplay === "none", first.beforeDisplay);

  // ---- villain band features follow featstyle ----
  const band = await page.evaluate(() => {
    const feats = document.querySelectorAll(".sb__band-body .sb__feat");
    if (feats.length < 2) return { n: feats.length };
    const b = getComputedStyle(feats[1], "::before");
    return { n: feats.length, beforeDisplay: b.display };
  });
  check("flat: band has 2+ features and second shows separator",
    band.n >= 2 && band.beforeDisplay === "block", JSON.stringify(band));

  // ---- presets bundle featstyle ----
  await page.evaluate(() => {
    const s = document.getElementById("set-sb-preset");
    s.value = "sourcebook"; s.dispatchEvent(new Event("change", { bubbles: true }));
  });
  check("preset: Sourcebook → flat",
    await page.evaluate(() => document.documentElement.getAttribute("data-sb-featstyle") === "flat"));
  await page.evaluate(() => {
    const s = document.getElementById("set-sb-preset");
    s.value = "steel"; s.dispatchEvent(new Event("change", { bubbles: true }));
  });
  check("preset: Steel Card → card",
    await page.evaluate(() => document.documentElement.getAttribute("data-sb-featstyle") === "card"));

  // ---- legacy prefs migration (matched pair: main.html early-apply + panel) ----
  await page.evaluate(() => localStorage.setItem("mkdocs:fontPrefs",
    JSON.stringify({ statblock: { kwusage: "text" } })));
  await page.reload({ waitUntil: "networkidle" });
  await page.waitForSelector(".sb-wrap");
  check("migration: legacy non-crest prefs → flat",
    await page.evaluate(() => document.documentElement.getAttribute("data-sb-featstyle") === "flat"));
  await page.evaluate(() => localStorage.setItem("mkdocs:fontPrefs",
    JSON.stringify({ statblock: { kwusage: "crest" } })));
  await page.reload({ waitUntil: "networkidle" });
  await page.waitForSelector(".sb-wrap");
  check("migration: legacy crest prefs → card",
    await page.evaluate(() => document.documentElement.getAttribute("data-sb-featstyle") === "card"));
  await page.evaluate(() => localStorage.removeItem("mkdocs:fontPrefs"));

  await ctx.close();
  await browser.close();
  console.log("\n" + (failures === 0 ? "ALL CHECKS PASSED" : failures + " CHECK(S) FAILED"));
  process.exit(failures === 0 ? 0 : 1);
})().catch((e) => { console.error("SCRIPT ERROR:", e.stack || e.message); process.exit(2); });
```

- [ ] **Step 1.2: Run against the CURRENT build to verify it fails**

```bash
cd v2
devbox run -- python3 -m http.server 8124 --directory site &
devbox run -- node tests/e2e/statblock-featstyle.e2e.cjs
```

Expected: **FAIL** — "default: data-sb-featstyle stamped as card" fails (attribute doesn't exist yet), the card-chrome checks fail, `#set-sb-featstyle` evaluate throws or checks fail. Leave the server running for Task 4. If everything passes, STOP — something is wrong with the test.

- [ ] **Step 1.3: Commit (v2 repo)**

```bash
cd v2
git add tests/e2e/statblock-featstyle.e2e.cjs
git commit -m "test: failing e2e for statblock data-sb-featstyle (card/flat)"
```

---

### Task 2: CSS restructure (`steel-statblock.css`)

**Files:**
- Modify: `v2/docs/stylesheets/steel-statblock.css` (header comment lines 7–19; FEATURES section lines 207–283; BANDS lines 354–379; WIDE line 443; PRINT line 468; scheme-first selectors lines 143–146)

All "old" text below is verbatim from the current file — use exact string replacement.

- [ ] **Step 2.1: Update the file-header preference list**

Old (lines 9–11):
```
     data-sb-kwusage    crest | text | grid | ledger   keyword + usage block
                        (crest = the only mode with a crest + eyebrow;
                         it also gives features the sub-card frame)
```
New:
```
     data-sb-kwusage    crest | text | grid | ledger   keyword + usage block
                        (crest = the only mode with a crest + eyebrow)
     data-sb-featstyle  card | flat                    feature frame: own card with
                        action-colored spine, or flat list + diamond separators
```

- [ ] **Step 2.2: Replace the flatten/kill rules with the floor-pinned kill block**

Old (the three rules + FOOTGUN comment, currently lines 217–225):
```css
/* flatten the raised ability plate; kill watermark + hover (high specificity) */
.sb .sb__features .sc-ability, .sb .sb__band-body .sc-ability {
  margin: 0; border: none; border-radius: 9px; background: none; box-shadow: none; overflow: visible; transition: none; padding: 0;
}
/* FOOTGUN: this also hides the feature-separator ::before below (same pseudo-
   element, same (0,3,0) specificity, earlier props win when uncontested) — the
   separator rules re-declare display/opacity/mix-blend-mode to claw it back. */
.sb .sb__features .sc-ability::before, .sb .sb__band-body .sc-ability::before { display: none; }
.sb .sb__features .sc-ability:hover, .sb .sb__band-body .sc-ability:hover { transform: none; box-shadow: none; }
```
New:
```css
/* ── KILL BLOCK — neutralize the steel-ability-cards.css plate chrome ──
   Every statblock feature is `article.sc-ability.sb__feat`, so the kills
   select .sb__feat directly and sit at EXACT specificity floors. This file
   loads after steel-ability-cards.css, so equal specificity wins by order:
     .md-typeset .sc-ability                                   (0,2,0) plate
     [data-md-color-scheme="default"] .md-typeset .sc-ability  (0,3,0) light plate
     .md-typeset .sc-ability::before                           (0,2,0) watermark
     .md-typeset .sc-ability:hover                             (0,3,0) hover lift
   The featstyle mode rules below outrank these (attribute anchor) or out-order
   them (same file, later) — keep ALL mode rules AFTER this block. */
.sb .sb__feat {
  margin: 0; border: none; background: none; box-shadow: none;
  overflow: visible; transition: none; padding: 0;
}
[data-md-color-scheme="default"] .sb .sb__feat { background: none; }
/* An element has ONE ::before: flat mode repurposes this same pseudo as the
   feature separator (re-declaring display/opacity/mix-blend-mode); this kill
   still matters for the FIRST feature (no `+` sibling), which would otherwise
   show the ability-card watermark. */
.sb .sb__feat::before { display: none; }
.sb .sb__feat:hover { transform: none; box-shadow: none; }
```
(Note: `border-radius: 9px` deliberately moves out of the kill into the card rule.)

- [ ] **Step 2.3: Delete the dead crest frame chrome; retitle the crest section**

Old (lines 239–243):
```css
/* ── crest mode (the only one with a crest + eyebrow; also the sub-card frame) ── */
[data-sb-kwusage="crest"] .sb__feat {
  background: rgba(0,0,0,.16); border-left: 3px solid var(--act); border-radius: 9px; padding: .7rem .85rem .78rem;
}
[data-md-color-scheme="default"] [data-sb-kwusage="crest"] .sb__feat { background: rgba(0,0,0,.022); }
```
New:
```css
/* ── crest mode (the only one with a crest + eyebrow) ── */
```
(The crest head rules that follow — `.sb__feat-head` grid, crest size, eyebrow, name size — stay untouched.)

- [ ] **Step 2.4: Re-anchor the main feature-list separators to flat mode, and add the card chrome**

Old (lines 253–283, the whole non-crest block):
```css
/* ── non-crest modes → flat features with stylized-hr separators (line + dots + diamond) ── */
:not([data-sb-kwusage="crest"]) .sb__features { gap: 0; }
:not([data-sb-kwusage="crest"]) .sb__feat { padding: .9rem .2rem; }
/* the separator pseudos sit at the border-box top edge, so the visual gap is
   margin-top above the divider and padding-top below it — keep them EQUAL or
   the diamond drifts off-center (the flatten rule above zeroes .sb__feat's own
   padding, so these two values are the whole gap). */
:not([data-sb-kwusage="crest"]) .sb__feat + .sb__feat { position: relative; margin-top: 1.25rem; padding-top: 1.25rem; }
:not([data-sb-kwusage="crest"]) .sb__feat + .sb__feat::before {
  /* display/opacity/mix-blend-mode: undo the watermark kill above (display:none)
     and the etched-watermark styling from steel-ability-cards.css (opacity .045
     + overlay blend) — all three leak onto this same ::before and made the line
     invisible no matter what the background below was set to. */
  display: block; opacity: 1; mix-blend-mode: normal;
  content: ""; position: absolute; top: -2px; left: 5%; right: 5%; height: 4px;
  /* matches the site's stylized <hr> (steel-redesign.css): center-out steel
     line + two seed dots flanking the haloed diamond (the ::after below). */
  background:
    linear-gradient(to right, transparent, var(--fx-metal-line)) no-repeat left center,
    linear-gradient(to left,  transparent, var(--fx-metal-line)) no-repeat right center,
    radial-gradient(circle, var(--fx-metal) 1.4px, transparent 1.9px) no-repeat calc(50% - 24px) center,
    radial-gradient(circle, var(--fx-metal) 1.4px, transparent 1.9px) no-repeat calc(50% + 24px) center;
  background-size: calc(50% - 30px) 1px, calc(50% - 30px) 1px, 4px 4px, 4px 4px;
}
:not([data-sb-kwusage="crest"]) .sb__feat + .sb__feat::after {
  content: ""; position: absolute; top: 0; left: 50%; width: 8px; height: 8px; margin: -4px 0 0 -4px;
  background: var(--fx-metal); transform: rotate(45deg);
  box-shadow: 0 0 0 4px var(--sb-plate-solid), 0 0 0 5px var(--fx-metal-faint);
}
```
New:
```css
/* ════════════════════════════════════════════════════════════
   FEATURE FRAME — data-sb-featstyle: card | flat
   (independent of data-sb-kwusage; spec:
    .repo-docs/plans/2026-06-12-statblock-feature-style.md)
   ════════════════════════════════════════════════════════════ */
/* card = each feature in its own container with an action-colored spine
   (the original statblock design's sub-card frame). */
[data-sb-featstyle="card"] .sb__feat {
  background: rgba(0,0,0,.16); border-left: 3px solid var(--act);
  border-radius: 9px; padding: .7rem .85rem .78rem;
}
/* scheme attr lives on <body>, data-sb-* on <html> — html-anchored attr FIRST */
[data-sb-featstyle="card"] [data-md-color-scheme="default"] .sb__feat { background: rgba(0,0,0,.022); }

/* flat = flat features with stylized-hr separators (line + dots + diamond) */
[data-sb-featstyle="flat"] .sb__features { gap: 0; }
[data-sb-featstyle="flat"] .sb__feat { padding: .9rem .2rem; }
/* the separator pseudos sit at the border-box top edge, so the visual gap is
   margin-top above the divider and padding-top below it — keep them EQUAL or
   the diamond drifts off-center (the kill block zeroes .sb__feat's own
   padding, so these two values are the whole gap). */
[data-sb-featstyle="flat"] .sb__feat + .sb__feat { position: relative; margin-top: 1.25rem; padding-top: 1.25rem; }
[data-sb-featstyle="flat"] .sb__feat + .sb__feat::before {
  /* this ::before doubles as the ability-card watermark (display:none'd by the
     kill block, opacity .045 + overlay blend in steel-ability-cards.css) —
     a rule repurposing a contested pseudo re-declares all three. */
  display: block; opacity: 1; mix-blend-mode: normal;
  content: ""; position: absolute; top: -2px; left: 5%; right: 5%; height: 4px;
  /* matches the site's stylized <hr> (steel-redesign.css): center-out steel
     line + two seed dots flanking the haloed diamond (the ::after below). */
  background:
    linear-gradient(to right, transparent, var(--fx-metal-line)) no-repeat left center,
    linear-gradient(to left,  transparent, var(--fx-metal-line)) no-repeat right center,
    radial-gradient(circle, var(--fx-metal) 1.4px, transparent 1.9px) no-repeat calc(50% - 24px) center,
    radial-gradient(circle, var(--fx-metal) 1.4px, transparent 1.9px) no-repeat calc(50% + 24px) center;
  background-size: calc(50% - 30px) 1px, calc(50% - 30px) 1px, 4px 4px, 4px 4px;
}
[data-sb-featstyle="flat"] .sb__feat + .sb__feat::after {
  content: ""; position: absolute; top: 0; left: 50%; width: 8px; height: 8px; margin: -4px 0 0 -4px;
  background: var(--fx-metal); transform: rotate(45deg);
  box-shadow: 0 0 0 4px var(--sb-plate-solid), 0 0 0 5px var(--fx-metal-faint);
}
```

- [ ] **Step 2.5: Re-anchor the band-body separators**

Old (lines 354–373):
```css
/* non-crest features inside a band still get flat separators.
   centering: gap above divider = band-body flex gap (.55rem) + margin-top,
   gap below = padding-top — so margin-top is .65rem minus the flex gap. */
:not([data-sb-kwusage="crest"]) .sb__band-body .sb__feat + .sb__feat { position: relative; margin-top: .1rem; padding-top: .65rem; }
:not([data-sb-kwusage="crest"]) .sb__band-body .sb__feat + .sb__feat::before {
  /* see the .sb__features separator above: re-enable the ::before that the
     watermark-kill rule hides and strip the watermark opacity/blend. */
  display: block; opacity: 1; mix-blend-mode: normal;
  content: ""; position: absolute; top: -2px; left: 5%; right: 5%; height: 4px;
  background:
    linear-gradient(to right, transparent, var(--fx-metal-line)) no-repeat left center,
    linear-gradient(to left,  transparent, var(--fx-metal-line)) no-repeat right center,
    radial-gradient(circle, var(--fx-metal) 1.4px, transparent 1.9px) no-repeat calc(50% - 24px) center,
    radial-gradient(circle, var(--fx-metal) 1.4px, transparent 1.9px) no-repeat calc(50% + 24px) center;
  background-size: calc(50% - 30px) 1px, calc(50% - 30px) 1px, 4px 4px, 4px 4px;
}
:not([data-sb-kwusage="crest"]) .sb__band-body .sb__feat + .sb__feat::after {
  content: ""; position: absolute; top: 0; left: 50%; width: 8px; height: 8px; margin: -4px 0 0 -4px;
  background: var(--fx-metal); transform: rotate(45deg); box-shadow: 0 0 0 4px var(--sb-plate-solid), 0 0 0 5px var(--fx-metal-faint);
}
```
New: identical bodies, with the three `:not([data-sb-kwusage="crest"])` anchors replaced by `[data-sb-featstyle="flat"]` and the lead comment replaced by:
```css
/* flat-mode features inside a band get the same separators.
   centering: gap above divider = band-body flex gap (.55rem) + margin-top,
   gap below = padding-top — so margin-top is .65rem minus the flex gap. */
```

- [ ] **Step 2.6: Re-anchor the villain-inline gap and the wide-mode exception**

Old (line 379):
```css
[data-sb-kwusage="crest"][data-sb-villain="inline"] .sb__band--villain .sb__band-body { gap: .65rem; }
```
New:
```css
[data-sb-featstyle="card"][data-sb-villain="inline"] .sb__band--villain .sb__band-body { gap: .65rem; }
```

Old (line 443):
```css
[data-sb-wide="on"]:not([data-sb-kwusage="crest"]) .sb__feat { margin-bottom: 0; }
```
New:
```css
[data-sb-wide="on"][data-sb-featstyle="flat"] .sb__feat { margin-bottom: 0; }
```

- [ ] **Step 2.7: Fix the remaining dead scheme-first selectors**

Old (lines 143–146):
```css
[data-md-color-scheme="default"] [data-sb-meta="grid"] .sb__meta .sb__field,
[data-md-color-scheme="default"] [data-sb-meta="gridc"] .sb__meta .sb__field,
[data-md-color-scheme="default"] [data-sb-kwusage="grid"] .sb__ku .sb__field,
[data-md-color-scheme="default"] [data-sb-disttarget="grid"] .sb__dt .sb__field { background: rgba(0,0,0,.022); }
```
New (html-anchored attr first; scheme attr is on `<body>`):
```css
[data-sb-meta="grid"] [data-md-color-scheme="default"] .sb__meta .sb__field,
[data-sb-meta="gridc"] [data-md-color-scheme="default"] .sb__meta .sb__field,
[data-sb-kwusage="grid"] [data-md-color-scheme="default"] .sb__ku .sb__field,
[data-sb-disttarget="grid"] [data-md-color-scheme="default"] .sb__dt .sb__field { background: rgba(0,0,0,.022); }
```

- [ ] **Step 2.8: Print — strip the card background**

Old (line 468):
```css
  .sb__stat, .sb__chars, .sb__field, .sb__feat .sc-ability__pr, .sb__feat .sc-ability__section { background: none !important; }
```
New (colored `border-left` intentionally kept — it's the action-type semantic, mirrors ability-card print):
```css
  .sb__stat, .sb__chars, .sb__field, .sb__feat, .sb__feat .sc-ability__pr, .sb__feat .sc-ability__section { background: none !important; }
```

- [ ] **Step 2.9: Commit (v2 repo)**

```bash
cd v2
git add docs/stylesheets/steel-statblock.css
git commit -m "feat: data-sb-featstyle frame modes; pin kill rules to specificity floors

Closes workspace FOLLOWUPS #8: card chrome decoupled from kwusage and
actually renders; no :not() anchors; separator re-claim hacks replaced by
clean layering. Also fixes 4 dead scheme-first selectors (scheme lives on
<body>, data-sb-* on <html>)."
```

---

### Task 3: JS wiring (`settings-panel.js` + `overrides/main.html`)

**Files:**
- Modify: `v2/docs/javascripts/settings-panel.js` (lines 29–38 keys/defaults/presets; line ~147 prefs load; Features fieldset markup line ~302; `pieceIds` map line ~569)
- Modify: `v2/overrides/main.html` (early-apply `sbD`, lines 84–88)

- [ ] **Step 3.1: Register the key, default, and preset bundles**

Old (lines 29–38):
```js
  var SB_KEYS = ["kwusage", "disttarget", "meta", "charline", "charbox", "villain", "wide", "stickymeta"];
  var SB_DEFAULTS = {
    kwusage: "crest", disttarget: "grid", meta: "grid", charline: "two",
    charbox: "off", villain: "banded", wide: "off", stickymeta: "on"
  };
  // Presets are bundles of the per-piece attrs (stickymeta is a web-extra, not in presets).
  var SB_PRESETS = {
    steel:      { kwusage: "crest", disttarget: "grid", meta: "grid", charline: "two", charbox: "off", villain: "banded", wide: "off" },
    sourcebook: { kwusage: "text", disttarget: "text", meta: "ledger", charline: "one", charbox: "on", villain: "inline", wide: "off" },
    index:      { kwusage: "grid", disttarget: "grid", meta: "gridc", charline: "two", charbox: "onword", villain: "banded", wide: "off" }
  };
```
New:
```js
  var SB_KEYS = ["kwusage", "featstyle", "disttarget", "meta", "charline", "charbox", "villain", "wide", "stickymeta"];
  var SB_DEFAULTS = {
    kwusage: "crest", featstyle: "card", disttarget: "grid", meta: "grid", charline: "two",
    charbox: "off", villain: "banded", wide: "off", stickymeta: "on"
  };
  // Presets are bundles of the per-piece attrs (stickymeta is a web-extra, not in presets).
  var SB_PRESETS = {
    steel:      { kwusage: "crest", featstyle: "card", disttarget: "grid", meta: "grid", charline: "two", charbox: "off", villain: "banded", wide: "off" },
    sourcebook: { kwusage: "text", featstyle: "flat", disttarget: "text", meta: "ledger", charline: "one", charbox: "on", villain: "inline", wide: "off" },
    index:      { kwusage: "grid", featstyle: "flat", disttarget: "grid", meta: "gridc", charline: "two", charbox: "onword", villain: "banded", wide: "off" }
  };
```

- [ ] **Step 3.2: Legacy migration at prefs load**

Old (line ~147):
```js
  var prefs = C.loadPrefs(localStorage);
```
New:
```js
  var prefs = C.loadPrefs(localStorage);
  // Legacy migration (matched pair with the early-apply in overrides/main.html):
  // prefs saved before data-sb-featstyle existed get it derived from kwusage,
  // so non-crest custom/Sourcebook/Index users keep their flat look.
  if (prefs.statblock && !prefs.statblock.featstyle && prefs.statblock.kwusage && prefs.statblock.kwusage !== "crest") {
    prefs.statblock.featstyle = "flat";
  }
```

- [ ] **Step 3.3: Add the drawer row (first row of the Features fieldset)**

Old (line ~302):
```js
          '<fieldset class="sc-set__sub"><legend>Features</legend>' +
            '<div class="sc-set__row">' +
              '<label class="sc-set__label" for="set-sb-kwusage">Keyword + usage' +
```
New:
```js
          '<fieldset class="sc-set__sub"><legend>Features</legend>' +
            '<div class="sc-set__row">' +
              '<label class="sc-set__label" for="set-sb-featstyle">Feature style' +
                sbHelp("Each feature in its own card with a colored left border, or a flat list separated by diamond rules.") + '</label>' +
              '<select class="sc-set__select" id="set-sb-featstyle">' +
                '<option value="card">Cards</option>' +
                '<option value="flat">Flat + separators</option>' +
              '</select>' +
            '</div>' +
            '<div class="sc-set__row">' +
              '<label class="sc-set__label" for="set-sb-kwusage">Keyword + usage' +
```

- [ ] **Step 3.4: Bind the control**

Old (lines 569–572):
```js
    var pieceIds = {
      kwusage: "set-sb-kwusage", disttarget: "set-sb-disttarget", meta: "set-sb-meta",
      charline: "set-sb-charline", charbox: "set-sb-charbox", villain: "set-sb-villain"
    };
```
New:
```js
    var pieceIds = {
      kwusage: "set-sb-kwusage", featstyle: "set-sb-featstyle", disttarget: "set-sb-disttarget",
      meta: "set-sb-meta", charline: "set-sb-charline", charbox: "set-sb-charbox", villain: "set-sb-villain"
    };
```
(`applyStatblocks`, `detectSbPreset`, `syncUI`, Reset — all data-driven off `SB_KEYS`/`SB_PRESETS`/`pieceIds`; no further changes.)

- [ ] **Step 3.5: Early-apply in `overrides/main.html`**

Old (lines 86–88):
```js
            var sb = s.statblock || {};
            var sbD = {kwusage:"crest",disttarget:"grid",meta:"grid",charline:"two",charbox:"off",villain:"banded",wide:"off",stickymeta:"on"};
            for (var sk in sbD) document.documentElement.setAttribute("data-sb-"+sk, sb[sk] || sbD[sk]);
```
New:
```js
            var sb = s.statblock || {};
            // Legacy migration (matched pair with settings-panel.js prefs load):
            // pre-featstyle prefs with a non-crest kwusage keep their flat look.
            if (!sb.featstyle && sb.kwusage && sb.kwusage !== "crest") sb.featstyle = "flat";
            var sbD = {kwusage:"crest",featstyle:"card",disttarget:"grid",meta:"grid",charline:"two",charbox:"off",villain:"banded",wide:"off",stickymeta:"on"};
            for (var sk in sbD) document.documentElement.setAttribute("data-sb-"+sk, sb[sk] || sbD[sk]);
```

- [ ] **Step 3.6: Commit (v2 repo)**

```bash
cd v2
git add docs/javascripts/settings-panel.js overrides/main.html
git commit -m "feat: Feature style drawer control + featstyle preset bundles and legacy migration"
```

---

### Task 4: Rebuild + GREEN run (full verification)

- [ ] **Step 4.1: Rebuild the site** (template change ⇒ full build required)

```bash
cd v2
devbox run -- mkdocs build
```
Expected: clean build, ~145s.

- [ ] **Step 4.2: Run the new e2e** (server from Task 1 still up; restart if not)

```bash
cd v2
devbox run -- node tests/e2e/statblock-featstyle.e2e.cjs
```
Expected: **ALL CHECKS PASSED**. If the separator checks fail, diagnose with `getComputedStyle(el, "::before")` per `.repo-docs/troubleshooting.md` — do NOT iterate blind on backgrounds.

- [ ] **Step 4.3: Run the existing e2e + unit tests (regression)**

```bash
cd v2
devbox run -- node tests/e2e/settings-panel.e2e.cjs
devbox run -- node --test tests/
```
Expected: ALL CHECKS PASSED / all unit tests pass. Then stop the http server.

- [ ] **Step 4.4: Visual spot-check (screenshots for the user)**

Using the same Brave harness, capture `Browse/monster/arixx/arixx/` in card mode (default) and flat mode (set `document.documentElement.setAttribute("data-sb-featstyle","flat")`), dark scheme, full statblock in frame. Save to `/tmp/sb-featstyle-card.png` and `/tmp/sb-featstyle-flat.png`; show both to the user before the docs task.

---

### Task 5: v2 repo docs

**Files:**
- Modify: `v2/.repo-docs/troubleshooting.md` (§ "Statblock/ability-card CSS edits have no visible effect", lines ~53–83)
- Modify: `v2/CLAUDE.md` (the contested-pseudo-element bullet in Key Rules)

- [ ] **Step 5.1: Update the troubleshooting entry** — the mechanism survives, the example rules changed. In the **Cause** list, replace item 2:

Old:
```
2. `steel-statblock.css`'s watermark-kill rule
   (`.sb .sb__features .sc-ability::before { display: none }`) hides it entirely,
   at the same (0,3,0) specificity as the separator rules.
```
New:
```
2. `steel-statblock.css`'s watermark-kill rule
   (`.sb .sb__feat::before { display: none }`) hides it entirely — since the
   2026-06-12 featstyle restructure it sits at (0,2,0), deliberately BELOW the
   (0,3,0) separator rules, but it still display:none's every feature ::before
   that no mode rule repurposes (e.g. the first feature, and every feature in
   card mode).
```
Append after the **Fix** paragraph:
```
**2026-06-12 update:** the kill rules are now pinned to exact specificity floors and
the separators are anchored on `[data-sb-featstyle="flat"]` (see
`plans/2026-06-12-statblock-feature-style.md`). The re-declaration rule still
applies: any rule repurposing a contested pseudo-element declares
`display`/`opacity`/`mix-blend-mode` itself.
```

- [ ] **Step 5.2: Update the `v2/CLAUDE.md` bullet** — in the Key Rules bullet beginning "**Before iterating on pseudo-element CSS…**", replace the parenthetical `(ability-card watermark, statblock watermark-kill `display:none`, separator)` with `(ability-card watermark, statblock watermark-kill `display:none`, flat-mode separator)` — no other change; the rule stays true.

- [ ] **Step 5.3: Commit (v2 repo)**

```bash
cd v2
git add .repo-docs/troubleshooting.md CLAUDE.md .repo-docs/plans/2026-06-12-statblock-feature-style-implementation.md
git commit -m "docs: featstyle restructure notes in troubleshooting + CLAUDE.md; implementation plan"
```

---

### Task 6: Workspace repo docs

**Files:**
- Modify: `DESIGN.md` (preference-system section + component table + open-debts line)
- Modify: `FOLLOWUPS.md` (remove #8)
- Create/append: `docs/followups-archive/2026-06-12-completed.md`

- [ ] **Step 6.1: DESIGN.md** — three edits:
  1. In **The user-preference system**, the example list `(e.g. `data-card-style`, `data-sb-kwusage`, `data-sb-meta`…)` → `(e.g. `data-card-style`, `data-sb-featstyle`, `data-sb-kwusage`…)`.
  2. In the statblock row of **Component systems**, change the design-spec cell from `…/redesign/statblocks/README.md` — **the** spec` to `…/redesign/statblocks/README.md` — **the** spec, plus the `data-sb-featstyle` addendum (`v2/.repo-docs/plans/2026-06-12-statblock-feature-style.md`)`.
  3. In **Open design debts** (end of Component systems), delete `statblock crest-mode CSS specificity decision (`FOLLOWUPS.md` #8),`.

- [ ] **Step 6.2: Archive FOLLOWUPS #8** — create `docs/followups-archive/2026-06-12-completed.md` with the standard archive header (copy the first 6 lines of `2026-06-11-completed.md`, dated 2026-06-12), then the full #8 section retitled `## Statblock CSS: kwusage mode rules silently lose to the flatten rule; `:not()` scope leak (was FOLLOWUPS #8)` with **Status:** done and a one-line resolution: `Resolved 2026-06-12 by the data-sb-featstyle preference (design decision: both looks, user-selectable; kill rules pinned to specificity floors; :not() anchors removed). Spec: v2/.repo-docs/plans/2026-06-12-statblock-feature-style.md`. Delete the `## 8.` section from `FOLLOWUPS.md`. **Then grep live docs for stale references:** `grep -rn "FOLLOWUPS.*#8\|#8" CLAUDE.md DESIGN.md steel-etl/docs/*.md steel-etl/CLAUDE.md v2/CLAUDE.md v2/.repo-docs/*.md` — fix any hits (DESIGN.md handled in 6.1).

- [ ] **Step 6.3: Commit (workspace repo)**

```bash
cd /home/vexa/code/steel_compendium/workspace
git add DESIGN.md FOLLOWUPS.md docs/followups-archive/2026-06-12-completed.md
git commit -m "docs: statblock feature-style preference shipped; archive FOLLOWUPS #8"
```

---

## Out of scope / notes

- **No deploy** — the user decides when to run `just deploy-v2`.
- **Frozen archive** (`reference/design-system/…/statblocks/README.md`) stays untouched.
- The crest **head** rules and the `data-sb-kwusage` values are unchanged — only the frame moved.
- `settings-core.js` is untouched (no unit-test changes).
