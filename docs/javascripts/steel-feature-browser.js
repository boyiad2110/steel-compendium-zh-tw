/* ============================================================
   Steel Compendium — steel-feature-browser.js
   Client-side SEARCH · SORT · FILTER for the feature tree, plus the
   shared PREVIEW-CARD renderer used by the leaf index pages.

   Styling lives in steel-indexes.css (.sc-prev / .sc-browse …).

   TWO exports on window.SCBrowse:
     • card(item, opts)  → HTML string for one .sc-prev card.
                           Build-time (steel-etl) emits this exact markup
                           on leaf index pages; pass {context:false} there.
     • mount(rootEl)     → turns a container that holds a
                           <script type="application/json" class="sc-browse-data">
                           data island into a live filter surface.

   Item shape:
     { kind:"feature"|"trait"|"ability", name, klass, level, href,
       flavor,                                  // 1-line summary / atmosphere
       // trait:
       action?, grants?, benefits?, tag?,        // action accents the spine
       // ability:
       action, cost, keywords?, conditions?, distance?, targets?,
       cost_tier? }
       // conditions[] = Draw Steel conditions the ability's MECHANICAL text
       // mentions (inflicts / requires / removes — not distinguished; flavor
       // excluded). Derived build-side in steel-etl internal/site/conditions.go.
       // cost_tier = the Cost facet's key, derived CLIENT-SIDE in mount() via
       // Core.costFacetValue(it.cost) — "Signature" | "none" | "<amount>" |
       // "other" (SC-92). Stamped on abilities only; left undefined on
       // features/traits so the "No cost" chip never selects the 971
       // non-ability items (undefined !== "none" to FacetCore.matchesPicks).
   ============================================================ */
(function () {
  "use strict";

  // Pure source/subclass model + matching, loaded before this script in mkdocs.yml.
  var Core = (typeof window !== "undefined" && window.SCFeatureBrowserCore) || null;

  // Shared per-facet pick matching (any/all modes), loaded before this script.
  var FacetCore = (typeof window !== "undefined" && window.SCFacetCore) || null;

  // action type → crest glyph (DrawSteelGlyphs) + eyebrow label. PLACEHOLDER
  // glyphs, same set as steel-ability-cards.js — swap in one place when the
  // official action glyphs arrive.
  var ACTIONS = {
    main:      { glyph: "l", label: "Main Action" },
    maneuver:  { glyph: "f", label: "Maneuver" },
    triggered: { glyph: ")", label: "Triggered Action" },
    move:      { glyph: "o", label: "Move Action" },
    none:      { glyph: "*", label: "No Action" },
    trait:     { glyph: "*", label: "Trait" }
  };

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }
  // Display-only lookup. Item IDs, facet values and source JSON stay English.
  function ancestryContext(it) {
    var match = String(it && it.href || "").match(/^(?:trait|ability)\/([a-z0-9-]+)\//);
    return match ? match[1] : "";
  }
  function display(s, context) { return window.SCL10n ? window.SCL10n.label(s, context) : s; }
  // minimal **bold** for distance values ("Melee **1**")
  function md(s) { return esc(s).replace(/\*\*(.+?)\*\*/g, "<b>$1</b>"); }
  function ordinal(n) { return n + (["th", "st", "nd", "rd"][(n % 100 - 20) % 10] || ["th", "st", "nd", "rd"][n % 100] || "th"); }

  function metaCell(l, v, raw) {
    return '<span class="sc-prev__meta"><span class="l">' + esc(l) + '</span>' +
      '<span class="v">' + (raw ? v : esc(v)) + '</span></span>';
  }

  function traitCard(it, ctx) {
    // Traits and plain features share the recessed niche (accent + crest); the
    // level lives in the tag, so the eyebrow carries "<Source> <noun> · <subclass?>".
    // The noun reflects the real type: "Trait" only for ancestry/monster traits,
    // "Feature" for the plain feature umbrella.
    var context = ancestryContext(it);
    var noun = it.kind === "feature" ? "Feature" : "Trait";
    var eyebrow = esc(display(it.klass ? it.klass + " " + noun : noun, context));
    if (it.subclass) eyebrow += " · " + esc(it.subclass);
    var tag = it.tag
      ? '<div class="sc-prev__tag">' + esc(display(it.tag, context)) + '</div>'
      : '<div class="sc-prev__tag">' + esc(display("Level", context)) + ' <span class="num">' + esc(it.level) + '</span></div>';
    var marker = "";
    if (it.grants) marker = esc(display("Grants " + it.grants, context));
    else if (it.options > 1) marker = esc(display(it.options + " options", context));
    else if (it.options === 1) marker = "1 option";
    var foot = marker
      ? '<div class="sc-prev__foot"><span class="sc-prev__grant"><span class="dot"></span>' + marker + "</span></div>"
      : "";
    return '<a class="sc-prev sc-prev--trait sc-fil" data-action="trait" href="' + esc(it.href || "#") + '">' +
      '<div class="sc-prev__head">' +
        '<span class="sc-crest sc-prev__crest"><span class="sc-prev__glyph">' + esc(ACTIONS.trait.glyph) + '</span></span>' +
        '<div class="sc-prev__titles">' +
          '<div class="sc-prev__eyebrow"><span class="sc-prev__dia"></span>' + eyebrow + '</div>' +
          '<h3 class="sc-prev__name">' + esc(display(it.name, context)) + '</h3></div>' + tag + '</div>' +
      (it.flavor ? '<div class="sc-prev__flavor">' + esc(display(it.flavor, context)) + '</div>' : "") +
      foot + '</a>';
  }

  function abilityCard(it, ctx) {
    var context = ancestryContext(it);
    var act = it.action || "main";
    var a = ACTIONS[act] || ACTIONS.main;
    var cost = it.cost || "";
    var costHTML = /^\d/.test(cost)
      ? cost.replace(/^(\d+)\s*/, '<span class="num">$1</span> ')
      : esc(display(cost, context));
    var tag = cost ? '<div class="sc-prev__tag">' + costHTML + '</div>' : "";
    // keyword chips, then condition chips (SC-90) — a card filtered to "prone"
    // shows on its face why it matched. Mirrors renderAbilityPrev in
    // steel-etl/internal/site/feature_index.go; keep the two in step.
    var chips = (it.keywords || []).map(function (k) {
      return '<span class="sc-prev__chip">' + esc(display(k, context)) + '</span>';
    }).concat((it.conditions || []).map(function (c) {
      return '<span class="sc-prev__chip sc-prev__chip--cond">' + esc(display(c, context)) + '</span>';
    }));
    var kw = chips.length ? '<div class="sc-prev__kw">' + chips.join("") + '</div>' : "";
    var foot = [];
    if (ctx) foot.push(metaCell(display("from", context), esc(display(it.klass, context)) + " · " + display("Lv", context) + " " + it.level, true));
    if (it.distance) foot.push(metaCell(display("distance", context), md(display(it.distance, context)), true));
    if (it.targets) foot.push(metaCell(display("targets", context), display(it.targets, context)));
    var footHTML = foot.length ? '<div class="sc-prev__foot">' + foot.join("") + "</div>" : "";
    // Subclass rides the action eyebrow ("Maneuver · Black Ash"), matching the
    // trait card — abilities otherwise never surface their subclass.
    var eyebrow = esc(display(a.label, context)) + (it.subclass ? " · " + esc(display(it.subclass, context)) : "");
    return '<a class="sc-prev sc-prev--ability sc-fil" data-action="' + esc(act) + '" href="' + esc(it.href || "#") + '">' +
      '<div class="sc-prev__head">' +
        '<span class="sc-crest sc-prev__crest"><span class="sc-prev__glyph">' + esc(a.glyph) + '</span></span>' +
        '<div class="sc-prev__titles">' +
          '<div class="sc-prev__eyebrow"><span class="sc-prev__dia"></span>' + eyebrow + '</div>' +
          '<h3 class="sc-prev__name">' + esc(display(it.name, context)) + '</h3></div>' + tag + '</div>' +
      (it.flavor ? '<div class="sc-prev__flavor">' + esc(display(it.flavor, context)) + '</div>' : "") +
      kw + footHTML + '</a>';
  }

  function card(it, opts) {
    var ctx = !opts || opts.context !== false;       // default: show class·level context
    return it.kind === "ability" ? abilityCard(it, ctx) : traitCard(it, ctx);
  }

  /* ── facet definitions: which fields become chip rows ───────────────────── */
  function uniqueSorted(arr, items, key, num) {
    var seen = {};
    items.forEach(function (it) {
      var v = it[key];
      if (v == null) return;
      (Array.isArray(v) ? v : [v]).forEach(function (x) { seen[x] = true; });
    });
    var out = Object.keys(seen);
    out.sort(num ? function (a, b) { return a - b; } : function (a, b) { return a.localeCompare(b); });
    return out;
  }

  function mount(root) {
    // Material's `navigation.instant` recreates inline <script> elements to force
    // execution, but strips ALL their attributes (class + type) — keeping only the
    // text body. So after a client-side nav the data island is a bare <script> with
    // no `sc-browse-data` class. Try the precise selector first (direct page loads),
    // then fall back to the only <script> the mount ever contains (instant nav).
    var island = root.querySelector("script.sc-browse-data") || root.querySelector("script");
    if (!island) return;
    var items;
    try { items = JSON.parse(island.textContent); } catch (e) { return; }

    // SC-92: Cost facet tier, derived client-side from the island's existing
    // `cost` field. Abilities only — leaving it undefined on features/traits
    // is what keeps the "No cost" chip from also selecting the 971 non-ability
    // items (matchesPicks("none") never matches an undefined value).
    items.forEach(function (it) {
      if (it.kind === "ability") it.cost_tier = Core.costFacetValue(it.cost);
    });

    // Source facet: one merged OR-group rendered by sourceFacetHTML — class chips
    // with nested class-scoped subclass chips, then plain childless sources. The
    // klass/subclass dimensions are kept out of the generic `facets` array.
    var srcModel = Core.buildSourceModel(items);

    var facets = [
      { key: "kind",     label: "Type",    values: ["feature", "ability", "trait"], display: cap },
      { key: "level",    label: "Level",   values: uniqueSorted(null, items, "level", true), display: function (v) { return "Lv " + v; } },
      { key: "action",   label: "Action",  values: uniqueSorted(null, items, "action"), display: function (v) { return (ACTIONS[v] || {}).label || cap(v); }, dot: actionColor },
      // SC-92. cost_tier is stamped on abilities only (above); scalar (one
      // cost per ability), so no any/all toggle — mirrors Type/Level/Action.
      { key: "cost_tier", label: "Cost", values: Core.costTierValues(items), display: Core.costTierDisplay },
      { key: "keywords", label: "Keyword", values: uniqueSorted(null, items, "keywords") },
      // SC-90. Matches ANY mention of the condition in the ability's mechanical
      // text (inflict / require / remove are not distinguished); flavor text is
      // excluded build-side. Array-valued, so it gets the any/all toggle free.
      { key: "conditions", label: "Condition", values: uniqueSorted(null, items, "conditions"), display: cap },
      { key: "feature_source", label: "Track", values: uniqueSorted(null, items, "feature_source"), display: cap }
    ].filter(function (f) { return f.values.length > 1; });

    // any/all toggle only where AND is satisfiable: array-valued fields (keywords).
    facets.forEach(function (f) { f.multi = FacetCore.isMultiValued(items, f.key); });

    var state = { q: "", sort: "name", sel: {}, mode: {} };
    facets.forEach(function (f) { state.sel[f.key] = {}; state.mode[f.key] = "any"; });
    state.sel.klass = {};
    state.sel.subclass = {};

    root.innerHTML =
      '<div class="sc-browse">' +
        '<div class="sc-browse__bar">' +
          '<div class="sc-browse__search">' + searchSvg() +
            '<input type="search" placeholder="Search features by name…" aria-label="Search features"></div>' +
          '<div class="sc-browse__sort"><label for="scbsort">Sort</label>' +
            '<select id="scbsort">' +
              '<option value="name">Name A–Z</option>' +
              '<option value="level">Level ↑</option>' +
              '<option value="level-desc">Level ↓</option>' +
              '<option value="class">Class</option>' +
            '</select></div>' +
        '</div>' +
        '<div class="sc-browse__facets">' +
          (function () {
            var rows = facets.map(facetRow);
            var kindIdx = -1;
            facets.forEach(function (f, i) { if (f.key === "kind") kindIdx = i; });
            rows.splice(kindIdx + 1, 0, sourceFacetHTML(srcModel)); // kindIdx -1 → splice at 0
            return rows.join("");
          })() +
        '</div>' +
        '<div class="sc-browse__head">' +
          '<span class="sc-browse__count"></span>' +
          '<button class="sc-browse__clear" hidden>Clear filters</button>' +
        '</div>' +
        '<div class="sc-browse__results"></div>' +
      '</div>';

    var elSearch = root.querySelector(".sc-browse__search input");
    var elSort = root.querySelector("#scbsort");
    var elCount = root.querySelector(".sc-browse__count");
    var elClear = root.querySelector(".sc-browse__clear");
    var elResults = root.querySelector(".sc-browse__results");

    elSearch.addEventListener("input", function () { state.q = this.value.trim().toLowerCase(); render(); });
    elSort.addEventListener("change", function () { state.sort = this.value; render(); });
    elClear.addEventListener("click", function () {
      state.q = ""; elSearch.value = "";
      facets.forEach(function (f) { state.sel[f.key] = {}; });
      facets.forEach(function (f) { state.mode[f.key] = "any"; });
      root.querySelectorAll(".sc-facet-mode.is-all").forEach(function (b) {
        b.classList.remove("is-all"); b.textContent = "any"; b.setAttribute("aria-pressed", "false");
        b.title = "Match any selected value (OR) — click to require all (AND)";
      });
      state.sel.klass = {}; state.sel.subclass = {};
      root.querySelectorAll(".sc-chip.is-on").forEach(function (c) { c.classList.remove("is-on"); c.setAttribute("aria-pressed", "false"); });
      render();
    });
    root.querySelectorAll(".sc-chip").forEach(function (chip) {
      chip.addEventListener("click", function () {
        var k = chip.dataset.facet, v = chip.dataset.value;
        if (state.sel[k][v]) { delete state.sel[k][v]; chip.classList.remove("is-on"); chip.setAttribute("aria-pressed", "false"); }
        else { state.sel[k][v] = true; chip.classList.add("is-on"); chip.setAttribute("aria-pressed", "true"); }
        render();
      });
    });
    root.querySelectorAll(".sc-facet-mode").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var k = btn.dataset.facet;
        var all = state.mode[k] !== "all";
        state.mode[k] = all ? "all" : "any";
        btn.textContent = all ? "all" : "any";
        btn.title = all
          ? "Match all selected values (AND) — click to return to any (OR)"
          : "Match any selected value (OR) — click to require all (AND)";
        btn.classList.toggle("is-all", all);
        btn.setAttribute("aria-pressed", all ? "true" : "false");
        render();
      });
    });

    function matches(it) {
      if (state.q) {
        var context = ancestryContext(it);
        var hay = (it.name + " " + display(it.name, context) + " " + (it.flavor || "") + " " +
          (it.keywords || []).join(" ") + " " + (it.keywords || []).map(function (value) { return display(value, context); }).join(" ")).toLowerCase();
        if (hay.indexOf(state.q) === -1) return false;
      }
      for (var k in state.sel) {
        if (k === "klass" || k === "subclass") continue; // handled as one OR-group below
        if (!FacetCore.matchesPicks(it[k], state.sel[k], state.mode[k])) return false;
      }
      if (!Core.matchesSource(it, state.sel.klass, state.sel.subclass)) return false;
      return true;
    }

    function sortFn(a, b) {
      switch (state.sort) {
        case "level":      return (a.level - b.level) || a.name.localeCompare(b.name);
        case "level-desc": return (b.level - a.level) || a.name.localeCompare(b.name);
        case "class":      return (a.klass || "").localeCompare(b.klass || "") || (a.level - b.level) || a.name.localeCompare(b.name);
        default:           return a.name.localeCompare(b.name);
      }
    }

    function render() {
      var list = items.filter(matches).sort(sortFn);
      var any = state.q
        || Object.keys(state.sel.klass).length
        || Object.keys(state.sel.subclass).length
        || facets.some(function (f) { return Object.keys(state.sel[f.key]).length; });
      elClear.hidden = !any;
      elCount.innerHTML = "<b>" + list.length + "</b> of " + items.length + " features";
      elResults.innerHTML = list.length
        ? '<div class="sc-prevs">' + list.map(function (it) { return card(it, { context: true }); }).join("") + "</div>"
        : '<div class="sc-browse__empty">No features match these filters.</div>';
    }
    render();
  }

  /* helpers for facet rendering */
  function cap(s) { return String(s).charAt(0).toUpperCase() + String(s).slice(1); }
  function actionColor(v) {
    return { main: "var(--sc-act-main)", maneuver: "var(--sc-act-maneuver)", triggered: "var(--sc-act-triggered)",
      move: "var(--sc-act-move)", none: "var(--sc-act-none)", trait: "var(--sc-act-trait)" }[v] || "var(--fx-metal)";
  }
  // source → chip-dot colour for the Source facet (grouping/ranking lives in
  // SCFeatureBrowserCore.buildSourceModel).
  function srcColor(s) {
    return { class: "var(--sc-src-class)", ancestry: "var(--sc-src-ancestry)", kit: "var(--sc-src-kit)",
      other: "var(--sc-src-other)" }[s] || "var(--fx-metal)";
  }
  function facetRow(f) {
    var chips = f.values.map(function (v) {
      var dot = f.dot ? '<span class="sc-chip__dot" style="color:' + f.dot(v) + '"></span>' : "";
      var label = f.display ? f.display(v) : v;
      return '<button type="button" class="sc-chip" role="button" aria-pressed="false" data-facet="' + f.key + '" data-value="' + esc(v) + '">' +
        dot + esc(label) + '</button>';
    }).join("");
    var modeBtn = f.multi
      ? '<button type="button" class="sc-facet-mode" data-facet="' + f.key + '" aria-pressed="false" ' +
        'title="Match any selected value (OR) — click to require all (AND)">any</button>'
      : "";
    return '<div class="sc-browse__facet"><span class="lbl">' + esc(f.label) + '</span>' +
      '<div class="sc-browse__chips">' + modeBtn + chips + '</div></div>';
  }
  // merged Source facet: a class chip (filters klass) leading its class-scoped
  // subclass chips (filter the composite klass+subclass), then a plain row of
  // childless sources (ancestries / kits / subclass-less classes).
  function sourceChip(klass, color) {
    var dot = color ? '<span class="sc-chip__dot" style="color:' + color + '"></span>' : "";
    return '<button type="button" class="sc-chip sc-chip--class" aria-pressed="false" ' +
      'data-facet="klass" data-value="' + esc(klass) + '">' + dot + esc(klass) + '</button>';
  }
  function subChip(klass, sub) {
    return '<button type="button" class="sc-chip sc-chip--sub" aria-pressed="false" ' +
      'data-facet="subclass" data-value="' + esc(Core.subKey(klass, sub)) + '">' + esc(sub) + '</button>';
  }
  function sourceFacetHTML(model) {
    var groups = model.classes.map(function (c) {
      var subs = c.subclasses.map(function (s) { return subChip(c.klass, s); }).join("");
      return '<div class="sc-srcgroup">' + sourceChip(c.klass, srcColor("class")) +
        '<span class="sc-subchips">' + subs + '</span></div>';
    });
    var plain = model.plain.map(function (p) { return sourceChip(p.klass, srcColor(p.source)); }).join("");
    if (plain) groups.push('<div class="sc-srcgroup sc-srcgroup--plain">' + plain + '</div>');
    return '<div class="sc-browse__facet sc-browse__facet--src"><span class="lbl">Source</span>' +
      '<div class="sc-srcgroups">' + groups.join("") + '</div></div>';
  }
  function searchSvg() {
    return '<svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>';
  }

  window.SCBrowse = { card: card, mount: mount, ACTIONS: ACTIONS };

  // Auto-mount any data island. The Search & Filter UI is the only purely
  // client-side surface (folder/preview cards are pre-rendered HTML), so the
  // mount MUST run on every page view. Under Material's `navigation.instant`,
  // page swaps don't re-fire DOMContentLoaded — subscribe to `document$`
  // (Material's per-navigation observable) when present, else fall back.
  function init() {
    document.querySelectorAll(".sc-browse-mount").forEach(mount);
  }
  if (typeof document$ !== "undefined" && document$ && typeof document$.subscribe === "function") {
    document$.subscribe(init);
  } else if (document.readyState !== "loading") {
    init();
  } else {
    document.addEventListener("DOMContentLoaded", init);
  }
})();
