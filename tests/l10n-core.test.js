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

test("dynamic feature labels are resolved within their ancestry context", (t) => {
  const previousWindow = global.window;
  const previousDocument = global.document;
  const browserScript = require.resolve("../docs/javascripts/l10n.js");
  delete require.cache[browserScript];
  let island = {
    getAttribute(name) {
      return name === "data-labels" ? JSON.stringify({ level: "等級" })
        : JSON.stringify({ "wode-elf": { "1 point": "1 費" } });
    }
  };
  global.window = { SCL10nCore: Core };
  global.document = {
    readyState: "loading",
    getElementById: () => island,
    addEventListener() {}
  };
  try {
    require(browserScript);
    assert.equal(global.window.SCL10n.label("1 Point", "wode-elf"), "1 費");
    assert.equal(global.window.SCL10n.label("1 Point", "high-elf"), "1 Point");
    assert.equal(global.window.SCL10n.label("Level", "high-elf"), "等級");
    island = {
      getAttribute(name) {
        return name === "data-labels" ? "{}"
          : JSON.stringify({ "high-elf": { "1 point": "1 費" } });
      }
    };
    assert.equal(global.window.SCL10n.label("1 Point", "high-elf"), "1 費");
  } finally {
    delete require.cache[browserScript];
    if (previousWindow === undefined) delete global.window; else global.window = previousWindow;
    if (previousDocument === undefined) delete global.document; else global.document = previousDocument;
  }
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
