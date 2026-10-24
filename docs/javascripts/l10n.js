/* Idempotent on Material document$ swaps. No observer over user-authored content. */
(function () {
  "use strict";
  let previous = null, labels = {}, contextLabels = {};
  function currentLabels() {
    const island = document.getElementById("sc-l10n-labels");
    if (island !== previous) {
      previous = island;
      try {
        labels = JSON.parse(island ? island.getAttribute("data-labels") || "{}" : "{}");
        contextLabels = JSON.parse(island ? island.getAttribute("data-context-labels") || "{}" : "{}");
      } catch (_) { labels = {}; contextLabels = {}; }
    }
    return labels;
  }
  window.SCL10n = {
    label: function (s, context) {
      currentLabels();
      const scoped = context && contextLabels[context];
      const key = window.SCL10nCore.key(s);
      return scoped && Object.prototype.hasOwnProperty.call(scoped, key)
        ? scoped[key]
        : window.SCL10nCore.label(s, currentLabels());
    },
    original: window.SCL10nCore.original
  };
  function init() {
    const labels = currentLabels();
    const C = window.SCL10nCore;
    // Only framework-generated controls; inputs, editable content and stored user names are excluded.
    document.querySelectorAll(".sc-chrome button[title], .sc-pageact button[title]").forEach(function (el) {
      el.title = C.label(el.title, labels);
    });
  }
  if (window.document$ && window.document$.subscribe) window.document$.subscribe(init);
  else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once: true });
  else init();
})();
