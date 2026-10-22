/* Approved exact-label helpers. Original values remain available to tool readers. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.SCL10nCore = factory();
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";
  function key(s) { return String(s || "").normalize("NFC").replace(/[‘’]/g, "'").replace(/\s+/g, " ").trim().toLowerCase(); }
  function label(s, labels) { return labels[key(s)] || s; }
  function original(el) {
    if (!el) return "";
    const direct = el.getAttribute("data-sc-original");
    if (direct != null) return direct;
    const copy = el.cloneNode(true);
    copy.querySelectorAll("[data-sc-original]").forEach(function (child) { child.textContent = child.getAttribute("data-sc-original"); });
    return copy.textContent;
  }
  return { key: key, label: label, original: original };
});
