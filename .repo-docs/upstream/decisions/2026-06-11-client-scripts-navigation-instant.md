> **上游歷史參考，非本站現行治理或待辦。** 本站規則見 [中文化治理入口](../../index.md)；不得直接執行本文的推送、部署或私有字型流程。

# ADR: Client scripts that mount page content must be navigation.instant-safe

**Date:** 2026-06-11
**Status:** Accepted
**Related:** [2026-06-09 Data islands must be found without their attributes](2026-06-09-instant-nav-strips-script-attrs.md)
(the attribute-stripping half of this) · [2026-05-31 Disable link previews](2026-05-31-disable-link-previews-perf.md)
(same `navigation.instant` subsystem)

## Context

The site enables Material's **`navigation.instant`** (`mkdocs.yml` → `theme.features`).
Instead of a full page load, internal link clicks fetch the target page and **swap the
`<body>` content in place** (an SPA-like router). This is great for speed but breaks the
naïve "run once on load" assumption two different ways.

The bug that surfaced it: the new **statblock** pages render entirely client-side from a
JSON data island (`steel-etl` emits it, `docs/javascripts/steel-statblock.js` mounts it into
the `.sb-wrap` DOM). On a **direct load / refresh** a statblock rendered fine, but the
**first time you opened one by clicking through** from the Bestiary it came up blank — a hard
reload then "fixed" it. We had seen the same class of failure before on the Features
**Search & Filter** index and the **Bestiary** browser.

There are **two independent hazards**, and a client script that builds page content must
handle **both** or it fails on instant navigation:

### Hazard 1 — `DOMContentLoaded` fires only on the first hard load

Under `navigation.instant`, navigating to a page does **not** re-fire `DOMContentLoaded`
(the document was already loaded; only the body changed). So:

```js
document.addEventListener("DOMContentLoaded", init); // ❌ runs once, never again
```

…never runs `init()` for any page reached by clicking a link. The script context persists
across swaps, so the listener is stale.

### Hazard 2 — Material recreates inline `<script>`s and strips their attributes

To force inline scripts in the swapped-in body to execute, Material **recreates every
`<script>` element**, and in doing so **drops all of its attributes** — both `class` and
`type` are gone after an instant nav (confirmed in a real browser; see the 2026-06-09 ADR).
So a selector like:

```js
document.querySelectorAll('script[type="application/json"].sc-statblock-data'); // ❌ matches nothing post-nav
```

…finds the island on a direct load but **nothing** after instant navigation. This one is
especially nasty because a local `mkdocs build` + static serve does **not** reproduce it —
the behaviour lives in Material's instant-nav runtime, so it only shows on the deployed site.

## Decision

**Any client script that mounts/enhances page content must run on every navigation, and must
locate its data without relying on stripped `<script>` attributes.** Concretely:

**1. Register with `document$`, not `DOMContentLoaded`.** `document$` is Material's RxJS
observable that emits the new document on **every** navigation (initial + instant). Standard
guard so it still works if Material/the observable is absent:

```js
function init() { /* idempotent: see below */ }
if (typeof document$ !== "undefined" && document$ && typeof document$.subscribe === "function") {
  document$.subscribe(init);
} else if (document.readyState !== "loading") {
  init();
} else {
  document.addEventListener("DOMContentLoaded", init);
}
```

**2. Wrap a JSON island in a container element and find it by the CONTAINER.** Material
recreates `<script>`s (stripping `class`/`type`) but does **not** recreate other elements, so
a wrapper `<div>`'s class survives. Emit:

```html
<div class="sc-statblock-mount"><script type="application/json" class="sc-statblock-data">…</script></div>
```

and read it via the container, falling back to any child `<script>`:

```js
document.querySelectorAll(".sc-statblock-mount").forEach(function (host) {
  var s = host.querySelector("script.sc-statblock-data") || host.querySelector("script");
  // JSON.parse(s.textContent) — textContent always survives; render; host.replaceWith(node)
});
```

This is the same shape as `.sc-browse-mount` (Features) and `.sc-bestiary-mount` (Bestiary).

**3. Make `init()` idempotent and clean up per-nav side effects.** `init()` re-runs on every
navigation, so it must not double-mount (mounting *replaces* the mount container, so the next
`querySelectorAll` finds nothing — naturally idempotent) and must **tear down listeners it
registered on `window`/`document`**. `steel-statblock.js`'s sticky mini-header adds
`window` scroll/resize handlers; without teardown each visited statblock would leak one,
pinning a detached node and recomputing `getBoundingClientRect` forever. Track them and
remove them at the top of `init()`.

## Scope applied (2026-06-11)

| Script | Island in production? | Change |
|--------|----------------------|--------|
| `steel-statblock.js` | **Yes** — the only statblock render path | `document$` + `.sc-statblock-mount` container + sticky-listener teardown (the live bug) |
| `steel-ability-cards.js` | No — abilities ship as build-time HTML | `document$` registration (hardened; dormant no-op today) |
| `steel-traits.js` | No — traits ship as build-time HTML | `document$` registration (hardened; dormant no-op today) |

Already-correct precedents (no change needed): `steel-feature-browser.js`,
`steel-bestiary-browser.js`, `settings-panel.js`, `browse-enhancements.js`,
`reading-progress.js`, `scc-headerlinks.js`, `keyboard-nav.js`, `tablesort.js`,
`ability-cards.js`.

## Consequences

- Statblocks render on both direct loads and instant navigation; no per-nav listener leak.
- **Checklist for any new client script that touches page content:** (a) register via
  `document$`; (b) if it reads a JSON island, wrap the island in a `*-mount` container and
  find it by that container, never by the `<script>`'s `class`/`type`; (c) keep `init()`
  idempotent and tear down any `window`/`document` listeners it adds.
- **Local builds won't catch Hazard 2.** Verify instant-nav behaviour on the deployed site
  (click *through* to the page), not just a local static serve.
- A recreated bare `<script>` body still gets evaluated as JS on instant nav. A JSON **array**
  island (`[…]`) is a harmless expression; a JSON **object** island (`{…}`) is not a valid
  statement and logs a benign `SyntaxError`. It does not affect rendering (we read the body as
  text), but prefer the container/`textContent` read precisely so execution is irrelevant.
