const test = require("node:test");
const assert = require("node:assert/strict");
const Core = require("../docs/javascripts/l10n-core.js");
const Search = require("../docs/javascripts/sc-search-core.js");
const MS = require("../docs/javascripts/vendor/minisearch.min.js");
const MiniSearch = MS.default || MS;

test("approved labels are exact; custom or modified names fall back unchanged", () => {
  assert.equal(Core.label(" Human ", { human: "人類" }), "人類");
  assert.equal(Core.label("My Human", { human: "人類" }), "My Human");
});

test("Chinese substrings and English aliases find the same page", () => {
  const engine = Search.createEngine(MiniSearch, [
    { location: "Browse/ancestry/human/", title: "人類", aliases: ["Human"], text: "選擇你的族裔特性。", boost: 3 },
    { location: "Browse/rule/other/", title: "Other", text: "A human hero." }
  ]);
  for (const q of ["人類", "Human", "族裔"]) {
    assert.equal(engine.search(q).items[0][0].location, "Browse/ancestry/human/");
  }
  assert.match(Search.highlight("選擇族裔", Search.tokenize("族裔")), /<mark>族<\/mark><mark>裔<\/mark>/);
});
