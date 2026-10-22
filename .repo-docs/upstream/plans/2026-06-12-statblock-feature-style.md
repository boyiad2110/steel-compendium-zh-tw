> **上游歷史參考，非本站現行治理或待辦。** 本站規則見 [中文化治理入口](../../index.md)；不得直接執行本文的推送、部署或私有字型流程。

# Statblock "Feature style" preference — approved design

**Date:** 2026-06-12 · **Status:** approved design, pre-implementation
**Scope:** v2 only (`steel-statblock.css`, `settings-panel.js`, `overrides/main.html`, e2e tests). Zero `steel-etl` changes — the DOM contract is untouched. Content is frozen, as always.

## Why

The original statblock design (`reference/design-system/handoff/redesign/statblocks/README.md`)
gave each feature a **sub-card frame** — own container, tinted background, 3px left border in the
action color, no separators — in crest mode. A specificity bug (workspace `FOLLOWUPS.md` #8) meant
that chrome **never rendered**; a `:not()` scope leak made the diamond+line separators the de facto
look in every mode. This design makes the frame style an explicit, independent user preference,
restores the carded look as the default, and pays down the specificity debt for real (no kill-rule
arms race, no `:not()`, no pseudo-element re-claim hacks).

Decisions locked with the user (2026-06-12):

1. **Independent preference** — a new `data-sb-featstyle` attribute, orthogonal to `data-sb-kwusage`.
2. **Steel Card preset bundles `card`** — the site default look changes to carded features.
   Sourcebook and Index Card bundle `flat`.
3. **Approach #2 (debt paydown)** — restructure the flatten/kill rules to sit at exact specificity
   floors instead of out-muscling the mode rules.

## 1. The preference

| Attribute | Values | Effect |
|---|---|---|
| `data-sb-featstyle` | **card** (default) · flat | `card` = each feature in its own container: `background: rgba(0,0,0,.16)` (light scheme `rgba(0,0,0,.022)`), `border-left: 3px solid var(--act)`, `border-radius: 9px`, `padding: .7rem .85rem .78rem`; `.sb__features` keeps its `.65rem` gap; **no separators**. `flat` = flat features, gap 0, diamond+line separators (today's look). |

- Lives on `<html>` like every `data-sb-*` pref; always stamped (early-apply + `applyStatblocks`).
  Absent attribute degrades to a plain unframed flat list — consistent with the existing
  "absent ≠ default" contract.
- **Drawer row:** "Feature style" `<select>` (`Cards` / `Flat`), id `set-sb-featstyle`, in the
  Statblocks group next to "Keyword + usage". Existing `detectSbPreset` re-derives "Custom" on
  individual override once the key is registered.
- **Presets:** `steel: card` · `sourcebook: flat` · `index: flat`.
- **Crest decoupled:** `data-sb-kwusage="crest"` keeps only its head layout (heraldic crest,
  eyebrow, larger name). The frame chrome moves to `featstyle`. Crest+flat (the old de facto
  default) and text/grid/ledger+card are all reachable; both render correctly.
- **Applies inside villain/malice band bodies** the same as in the main feature list.

### Legacy prefs migration

Stored `prefs.statblock` predating this change has no `featstyle`. Derive:

```js
sb.featstyle || (sb.kwusage && sb.kwusage !== "crest" ? "flat" : "card")
```

i.e. users who chose Sourcebook/Index (or any non-crest custom) keep their flat look; everyone
else gets the restored card default. The expression is duplicated in the two places defaults
already live — `overrides/main.html` early-apply and `settings-panel.js` `SB_DEFAULTS` resolution —
commented as a matched pair (prevents a wrong-then-right flash on first paint after upgrade).

## 2. CSS restructure (`steel-statblock.css`) — the debt paydown

### Specificity floors

`steel-statblock.css` loads **after** `steel-ability-cards.css` (`mkdocs.yml` `extra_css` order),
so equal specificity suffices — ties break our way. What must be neutralized:

| Source rule (steel-ability-cards.css) | Specificity | Sets |
|---|---|---|
| `.md-typeset .sc-ability` | (0,2,0) | plate border/bg/shadow/padding/margin |
| `[data-md-color-scheme="default"] .md-typeset .sc-ability` | (0,3,0) | light-scheme plate bg |
| `.md-typeset .sc-ability::before` | (0,2,0) | etched watermark |
| `.md-typeset .sc-ability:hover` | (0,3,0) | hover lift + shadow |

(`.sc-fil` / `.sc-ability__ops` hover rules don't apply — the statblock renderer never emits them.)

### Kill block (replaces the old flatten rule)

Every statblock feature is `article.sc-ability.sb__feat`, so kills select **`.sb .sb__feat`**
directly — landing at exactly the needed floor without `:where()` gymnastics:

```css
/* one comment block stating the floor table above + "mode rules MUST follow this block" */
.sb .sb__feat { margin: 0; border: none; background: none; box-shadow: none;
                overflow: visible; transition: none; padding: 0; }      /* (0,2,0) = plate floor */
[data-md-color-scheme="default"] .sb .sb__feat { background: none; }    /* (0,3,0) = light floor */
.sb .sb__feat::before { display: none; }                                /* (0,2,0) = watermark floor */
.sb .sb__feat:hover { transform: none; box-shadow: none; }              /* (0,3,0) = hover floor */
```

The old `.sb .sb__features .sc-ability, .sb .sb__band-body .sc-ability` (0,3,0) monolith, its
FOOTGUN comment, and the separator rules' `display/opacity/mix-blend-mode` re-claim hacks are
**deleted** — mode rules now outrank the kills by specificity or same-file order, by construction.
(`border-radius` moves out of the kill into the card rule, where it belongs.)

### Mode rules — positively anchored, no `:not()` anywhere

All mode rules come **after** the kill block in the file. Card mode at (0,2,0) beats the flatten
kill by source order; everything attribute-anchored at (0,3,0)+ beats it outright.

```css
/* card mode (the restored design chrome, moved verbatim from the dead crest rules) */
[data-sb-featstyle="card"] .sb__feat { background: rgba(0,0,0,.16);
  border-left: 3px solid var(--act); border-radius: 9px; padding: .7rem .85rem .78rem; }
[data-sb-featstyle="card"] [data-md-color-scheme="default"] .sb__feat { background: rgba(0,0,0,.022); }

/* flat mode (today's separators, re-anchored from the leaky :not()) */
[data-sb-featstyle="flat"] .sb__features { gap: 0; }
[data-sb-featstyle="flat"] .sb__feat { padding: .9rem .2rem; }
[data-sb-featstyle="flat"] .sb__feat + .sb__feat { /* margin/padding + ::before line + ::after diamond */ }
[data-sb-featstyle="flat"] .sb__band-body .sb__feat + .sb__feat { /* band variant */ }
```

Separator pseudos keep declaring their full visual set (`display/content/position/background/
opacity/mix-blend-mode`) — no longer as a counter-hack, just self-contained styling that outranks
the (0,2,0) kills. `display: block` is load-bearing: flat mode **repurposes the same `::before`**
the watermark kill turns off (and the kill must stay, or the first feature — no `+` sibling —
would show the etched watermark). The "keep margin-top and padding-top EQUAL or the diamond
drifts" comment is preserved on the flat rules.

Rules to **delete**: `[data-sb-kwusage="crest"] .sb__feat { background … }` and its light-scheme
variant (the chrome moves to `featstyle`); all `:not([data-sb-kwusage="crest"])` anchors.
Crest's head-layout rules (crest/eyebrow/name-size, lines anchored on `[data-sb-kwusage="crest"]`
that don't touch the frame) stay as they are.

### Adjacent fix: dead scheme-first selectors

`data-md-color-scheme` lives on `<body>`; `data-sb-*` lives on `<html>`. Selectors written
`[data-md-color-scheme="default"] [data-sb-*] …` therefore **never match** — light-scheme users
have silently gotten dark-scheme tints. Flip the five occurrences (current lines 143–146 + 243;
243 is deleted anyway) to `[data-sb-*] [data-md-color-scheme="default"] …`, and write the new
card light-tint rule in that order from the start. Same root cause, same file, in scope.

### Interactions

- **Wide mode:** `[data-sb-wide="on"]:not([data-sb-kwusage="crest"]) .sb__feat { margin-bottom: 0 }`
  → `[data-sb-wide="on"][data-sb-featstyle="flat"] .sb__feat { margin-bottom: 0 }` (compound on
  `<html>`). Card mode keeps the existing `.8rem` column margins.
- **Villain inline / banded:** unchanged; band-body features pick up whichever featstyle is active.
- **Print:** add `.sb__feat` to the `background: none !important` strip list; the colored
  `border-left` stays (semantic, mirrors ability-card print treatment).
- **Both color schemes** covered (slate base + `default` overrides in the body-anchored order).

## 3. JS wiring

- `settings-panel.js`: add `featstyle` to `SB_KEYS`; `SB_DEFAULTS.featstyle = "card"` (with the
  legacy derivation above); add to all three `SB_PRESETS`; drawer row markup; id map entry
  (`featstyle: "set-sb-featstyle"`).
- `overrides/main.html`: add `featstyle` to the early-apply `sbD` defaults with the same
  derivation expression (matched-pair comment).
- No other JS changes — `applyStatblocks` and `detectSbPreset` are data-driven off `SB_KEYS`/
  `SB_PRESETS`.

## 4. Testing

Extend `v2/tests/e2e/settings-panel.e2e.cjs` (Brave via playwright-core, existing pattern):

1. **Default = card:** computed `border-left: 3px` in the action color + non-transparent
   background on `.sb__feat`; no visible separator pseudo between adjacent features.
2. **Switch to Flat via drawer:** separators appear (assert the `::before` line is actually
   visible — the 2026-06-11 regression class), card chrome gone.
3. **Presets:** selecting Sourcebook yields `data-sb-featstyle="flat"`; overriding Feature style
   under Steel Card flips the preset readout to "Custom".
4. **Regression guards (both modes):** ability-card watermark stays hidden; `:hover` produces no
   transform/shadow on features; light scheme gets the light card tint (covers the dead-selector
   fix).

Unit tests: none needed — `settings-core.js` logic is untouched; the new key flows through
existing data-driven code.

## 5. Docs & bookkeeping (workspace repo, at implementation time)

- `DESIGN.md`: add `data-sb-featstyle` to the user-preference examples and preset description;
  statblock component row gains this spec as a pointer alongside the frozen archive README;
  remove the `FOLLOWUPS.md` #8 entry from "open design debts".
- Workspace `FOLLOWUPS.md` #8 → resolved into `docs/followups-archive/` with a "was #8" handle
  (highest-numbered item; no renumbering ripple).
- The frozen design archive (`reference/design-system/…/statblocks/README.md`) stays untouched;
  this spec records the divergence: `featstyle` exists, frame chrome is decoupled from `kwusage`,
  and presets bundle it.
