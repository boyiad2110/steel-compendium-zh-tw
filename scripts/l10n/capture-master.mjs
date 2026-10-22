// Connector-neutral, approved-only capture. Call with grounded metadata and bounded tab readers.
// Never write the raw rows (which can include drafts or review notes) into the repository.
export async function captureMaster(readMetadata, readTab, expectedId) {
  const before = await readMetadata();
  if (before.id !== expectedId || !before.modifiedTime) throw new Error("Master identity/version unavailable");
  const tabs = await Promise.all([readTab("Records"), readTab("UI")]);
  const after = await readMetadata();
  if (after.id !== before.id || after.modifiedTime !== before.modifiedTime) throw new Error("Master changed during capture");
  const records = [], seen = new Set();
  const required = ["Record ID", "Kind", "Source Text", "Target Text", "Status", "Scope", "Source Hash"];
  for (const rows of tabs) {
    if (!Array.isArray(rows) || !rows.length) throw new Error("Missing tab/header");
    const headers = rows[0];
    if (required.some(h => !headers.includes(h))) throw new Error("Missing required header");
    const get = (row, header) => String(row[headers.indexOf(header)] ?? "");
    for (const row of rows.slice(1)) {
      if (get(row, "Status") !== "APPROVED") continue;
      const record = {
        id: get(row, "Record ID"), kind: get(row, "Kind"), source: get(row, "Source Text"),
        target: get(row, "Target Text"), status: "APPROVED", scope: get(row, "Scope"),
        sourceHash: get(row, "Source Hash"), sourceRecordId: get(row, "Book Record ID"),
        sourceSheetId: get(row, "Book Sheet ID"), reference: get(row, "Book Reference"),
        bookVersion: get(row, "Book Version"), context: get(row, "Context")
      };
      if (!record.id || !record.source || !record.target || !/^[a-f0-9]{64}$/.test(record.sourceHash) || seen.has(record.id)) throw new Error("Invalid approved record or duplicate ID: " + record.id);
      seen.add(record.id);
      records.push(record);
    }
  }
  return { format: "steel-compendium-master-approved/v1", master: { spreadsheetId: before.id, modifiedTime: before.modifiedTime }, records };
}
