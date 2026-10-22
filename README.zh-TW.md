# Steel Compendium 正體中文版

保留 [Steel Compendium v2](https://github.com/SteelCompendium/v2) 的功能與設計，優先提供 **Heroes 所有職業的 1 級創角資料**。尚未核准或來源不符的內容保留英文。

## 開發

Python 3.13、Node.js 22 以上：

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.lock.txt
.venv\Scripts\python -m mkdocs serve -f mkdocs.zh-TW.yml
```

開啟 http://127.0.0.1:8000/ 。中文設定繼承上游，不修改生成的規則文件。英文基準可用 `mkdocs build -f mkdocs.yml -d site-en` 重現。

```powershell
.venv\Scripts\python scripts/l10n/verify.py
```

完整驗證執行 Python 來源／回退測試、全部上游 JavaScript 單元測試、中文正式建置與產物檢查；報告輸出至 `reports/`。瀏覽器驗收需實測桌面／手機、深淺色、即時導覽、搜尋、收藏與匯出；現有 `tests/e2e/` 保留上游回歸案例，設定實際瀏覽器路徑後可執行。

## 翻譯治理

- `l10n/catalog.json` 是獨立 Master 的 APPROVED 快照；書本來源及網站 Master ID 記錄於檔內。
- Book Master 只供匯入定稿，後續不直接覆寫本站。新 Book 核准擷取檔可用 `scripts/l10n/refresh.py` 比對，輸出變更提案。
- 同原文仍需符合語境；僅核准、原文雜湊相符且對應唯一的紀錄可顯示。不同譯文衝突、原文變更、缺譯與連結適配失敗均保留英文。
- 草稿與審核筆記留在 Master，不進公開快照。網站與 CI 不連線讀取 Google Sheet。
- 更新快照時，透過連接器執行 `capture-master.mjs` 的 `captureMaster`：先後讀取同一 Master 修改時間，以 metadata 確認 Records／UI 的有界範圍。函式只回傳 APPROVED 投影；不要儲存或印出原始草稿。以 `import_master.py <approved-capture.json> <candidate.json>` 驗證並生成候選，再用 `refresh.py <candidate.json>` 試跑；確認差異後加 `--apply`，最後執行完整驗證。UI 候選的 Source Hash 也必須與原文一致。
- 只修改顯示；SCC、URL、錨點、原始資料與計算值不變。譯文替換保留原有連結；無法確定連結對應時整段回退英文。
- **工程接線完成、翻譯核准與畫面驗收分開記錄**；已匯入筆數或已有中文名稱皆不代表完整中文化。

## 優先順序與進度

P0 基礎 → P1 Heroes 1 級創角 → P2 成長與玩家規則 → P3 Heroes 其餘內容 → P4 其他書籍與工具。

`scripts/l10n/inventory.py` 產生上游頁面與跨優先度依賴清單，加 `--write-manifest` 可重建 `l10n/p1-manifest.json` 的九職業首批範圍。中文建置產生 `reports/coverage.md`、`coverage.json` 與 `p1-missing.json`，逐頁記錄英文區塊、來源雜湊及缺譯／連結適配／顯示接點等原因。職業綜合頁包含高等級資料，不能拿整頁比例推論 1 級創角完成率。

## 上游同步與發布

上游固定版本記錄於 `l10n/upstream.json`。`upstream` 保留原始倉庫，中文工作在 `codex/` 分支。更新應以同步 PR 審查，跑完整驗證與創角旅程回歸後合併；不要執行上游 `just update` 的推送步驟。

原站生成內容已使用明確的 Markdown 路徑，沒有 Wiki 連結。中文建置停用 `roamlinks`，避免該外掛對每個連結重掃全站檔案，並保留原本的相對連結。

獨立站使用 `.github/workflows/zh-tw.yml` 手動部署。發布時必須提供本站 URL，使 canonical、SCC 分享與 sitemap 指向中文版。保留全部英文頁面，未完成的 P4 不刪除、不隱藏。

## 授權與字型

原站倉庫標示 CC0，遊戲內容仍適用 [DRAW STEEL Creator License](https://www.mcdmproductions.com/draw-steel-creator-license)。保留必要聲明及第三方授權。

中文版不包含原作者另外購買的 Berlingske Slab 字型；使用原站 OFL 字型與 Noto Sans TC 繁體中文後備字型。所有字型、換行與高度不以像素完全一致為驗收標準。
