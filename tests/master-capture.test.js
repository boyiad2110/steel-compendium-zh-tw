const test = require("node:test");
const assert = require("node:assert/strict");
const crypto = require("node:crypto");

const HEADERS = ["Record ID", "Kind", "Source Text", "Target Text", "Status", "Scope", "Source Hash"];
const hash = s => crypto.createHash("sha256").update(s).digest("hex");

test("Master capture excludes drafts before returning data", async () => {
  const { captureMaster } = await import("../scripts/l10n/capture-master.mjs");
  const result = await captureMaster(async () => ({ id: "master", modifiedTime: "version" }),
    async tab => tab === "Records" ? [HEADERS, ["a", "names", "Human", "人類", "APPROVED", "heroes", hash("Human")]]
      : [HEADERS, ["private-draft", "ui", "Home", "草稿", "DRAFT", "ui", hash("Home")]], "master");
  assert.equal(result.records.length, 1);
  assert.ok(!JSON.stringify(result).includes("private-draft"));
});

test("Master capture rejects mixed versions and duplicate approvals", async () => {
  const { captureMaster } = await import("../scripts/l10n/capture-master.mjs");
  let calls = 0;
  await assert.rejects(() => captureMaster(async () => ({ id: "master", modifiedTime: String(calls++) }), async () => [HEADERS], "master"), /changed/);
  const rows = [HEADERS, ["a", "names", "Human", "人類", "APPROVED", "heroes", hash("Human")]];
  await assert.rejects(() => captureMaster(async () => ({ id: "master", modifiedTime: "version" }), async () => rows, "master"), /duplicate/);
});
