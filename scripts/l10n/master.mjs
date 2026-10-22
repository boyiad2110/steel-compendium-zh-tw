// Run with the Codex bundled Node and an adjacent node_modules junction to its dependencies.
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Workbook, SpreadsheetFile } from "@oai/artifact-tool";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const output = path.join(root, "outputs/master");
await fs.mkdir(output, { recursive: true });
const catalog = JSON.parse(await fs.readFile(path.join(root, "l10n/catalog.json"), "utf8"));
const wb = Workbook.create();
const readme = [
  ["項目", "說明"],
  ["名稱", "Steel Compendium Translation Master Sheet"],
  ["首個里程碑", "Heroes 所有職業的 1 級創角；其餘內容往後排。"],
  ["發布規則", "只發布 APPROVED；缺譯、過期或語境不符時顯示英文。"],
  ["獨立維護", "Book Master 僅作為定稿匯入來源；後續來源變更先比對，不直接覆寫核准譯文。"],
  ["核准來源", "https://docs.google.com/spreadsheets/d/" + catalog.bookSource.spreadsheetId + "/edit"],
  ["來源修改時間", "UTC " + catalog.bookSource.modifiedTime],
  ["匯入範圍", "僅 Book Master APPROVED 欄位；未匯入草稿及私人審核筆記。"],
  ["Records", "獨立翻譯紀錄。保留 Record ID；Source Hash 必須符合完整原文。"],
  ["UI", "網站介面候選文字；DRAFT 不進正式快照，核准後才發布。"],
  ["Milestones", "工程接線、譯文核准、畫面驗收分開記錄。"],
  ["Inventory", "固定上游版本的 P1 候選頁面與書籍來源；頁面數不是翻譯完成率。"],
  ["版本", "上游 0b9571dbd3ce9f75e8f886e5ccd94f8c858437c6；Heroes 1.01b"],
];
const headers = ["Record ID", "Kind", "Source Text", "Target Text", "Status", "Scope", "Source Hash", "Book Record ID", "Book Sheet ID", "Book Reference", "Book Version", "Context"];
const records = [headers, ...catalog.records.map(r => [r.id, r.kind, r.source, r.target, r.status, r.scope, r.sourceHash, r.sourceRecordId, r.sourceSheetId, r.reference, r.bookVersion, r.context])];
const uiRows = [headers, ...[
  ["home", "Home", "首頁"], ["browse", "Browse", "瀏覽"], ["books", "Books", "書籍"],
  ["search", "Search", "搜尋"], ["my-table", "My Table", "我的桌面"],
  ["copy-md", "Copy as Markdown", "複製為 Markdown"], ["png", "Download card as PNG", "下載卡片 PNG"],
  ["light", "Switch to light mode", "切換淺色模式"], ["dark", "Switch to dark mode", "切換深色模式"],
].map(([id, source, target]) => ["ui." + id, "ui", source, target, "DRAFT", "ui", "", "", "", "Steel Compendium UI", "", "網站介面；待核准"] )];
const milestones = [["階段", "範圍", "工程接線", "譯文核准", "畫面驗收"],
  ["P0", "快照、來源對應、導覽與搜尋", "IN_PROGRESS", "PARTIAL", "PENDING"],
  ["P1", "所有 Heroes 職業的 1 級創角", "IN_PROGRESS", "PARTIAL", "PENDING"],
  ["P2", "Heroes 角色成長與其餘玩家規則", "PENDING", "PENDING", "PENDING"],
  ["P3", "Heroes 其餘內容與主持人章節", "PENDING", "PENDING", "PENDING"],
  ["P4", "Monsters、Beastheart、Summoner 與其他工具", "PENDING", "PENDING", "PENDING"]];
let inventory = [["Path", "SCC", "Title", "Priority", "Translation Status", "Reason"]];
try {
  const data = JSON.parse(await fs.readFile(path.join(root, "reports/source-inventory.json"), "utf8"));
  inventory.push(...data.pages.filter(p => p.priority === "P1").map(p => [p.path, p.scc, p.title, p.priority, "PENDING", "逐欄核對核准譯文；名稱翻譯不代表全頁完成"]));
} catch (error) { if (error.code !== "ENOENT") throw error; }

for (const [name, rows] of [["README", readme], ["Records", records], ["UI", uiRows], ["Milestones", milestones], ["Inventory", inventory]]) {
  const sheet = wb.worksheets.add(name);
  const cols = rows[0].length;
  const column = n => String.fromCharCode(64 + n);
  const range = sheet.getRange(`A1:${column(cols)}${rows.length}`);
  // Literal source text must never be interpreted as a spreadsheet formula.
  range.values = rows.map(row => Array.from({ length: cols }, (_, i) => String(row[i] ?? "").replace(/^=/, "'=")));
  range.format.font = { name: "Arial", size: 11, color: "#000000" };
  range.format.rowHeight = 24;
  range.format.columnWidth = 24;
  sheet.getRange(`A1:${column(cols)}1`).format = { fill: "#EEEEEE", font: { bold: true }, wrapText: true, rowHeight: 32 };
  sheet.freezePanes.freezeRows(1);
  if (name === "Records" || name === "UI") {
    sheet.getRange(`C1:D${rows.length}`).format.columnWidth = 64;
    sheet.getRange(`C1:D${rows.length}`).format.wrapText = true;
    // Text can be long; editors expand individual rows when reviewing.
    sheet.getRange(`A1:A${rows.length}`).format.columnWidth = 48;
  } else if (name === "README") {
    sheet.getRange(`B1:B${rows.length}`).format.columnWidth = 105;
    range.format.wrapText = true;
    range.format.autofitRows();
  } else if (name === "Inventory") {
    sheet.getRange(`A1:B${rows.length}`).format.columnWidth = 65;
  } else {
    sheet.getRange(`B1:B${rows.length}`).format.columnWidth = 55;
  }
}
wb.recalculate();
console.log((await wb.inspect({ kind: "table", range: "Records!A1:F4", tableMaxRows: 4, tableMaxCols: 6, maxChars: 1800 })).ndjson);
for (const name of ["README", "Records", "UI", "Milestones", "Inventory"]) {
  const preview = await wb.render({ sheetName: name, range: name === "README" ? "A1:B8" : "A1:F4", scale: 1, format: "png" });
  await fs.writeFile(path.join(output, `${name}.png`), new Uint8Array(await preview.arrayBuffer()));
}
const file = await SpreadsheetFile.exportXlsx(wb);
await file.save(path.join(output, "steel-compendium-translation-master.xlsx"));
console.log(JSON.stringify({ approved: catalog.records.length, inventory: inventory.length - 1, output }));
