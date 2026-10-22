/* Idempotent on Material document$ swaps. No observer over user-authored content. */
(function () {
  "use strict";
  let previous = null, labels = {};
  function currentLabels() {
    const island = document.getElementById("sc-l10n-labels");
    if (island !== previous) {
      previous = island;
      try { labels = JSON.parse(island ? island.getAttribute("data-labels") || "{}" : "{}"); } catch (_) { labels = {}; }
    }
    return labels;
  }
  window.SCL10n = {
    label: function (s) { return window.SCL10nCore.label(s, currentLabels()); },
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
