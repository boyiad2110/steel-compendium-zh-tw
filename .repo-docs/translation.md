# 翻譯來源、核准與快照

## 資料權責

| 來源 | 用途 | 不應拿來做什麼 |
|---|---|---|
| [SC Master](https://docs.google.com/spreadsheets/d/1RvYstzyZWqQfXDPnTwQUscSd-UJZK6uCFEOVg0Q931c/edit) | 本站獨立管理術語、名稱、規則、UI、來源對應及核准狀態 | 不由網站或 CI 即時讀取 |
| [SC Master 資料夾](https://drive.google.com/drive/u/0/folders/1uVuIlU1tdi1KOrX0WU6v0yLahRVW45Gk) | 管理位置；移動資料夾不改變試算表 ID | 不以資料夾位置取代 Sheet ID |
| [Book Master](https://docs.google.com/spreadsheets/d/1RAtKBsoL3HdPUZ0WNszdM7t2e_ac_Z3nBlpn7ud-cZ4/edit) | 可追溯的原書核准譯文來源 | 不直接覆寫本站既有核准或自動發布更新 |
| [catalog.json](../l10n/catalog.json) | 網站與 CI 使用的 APPROVED 快照 | 不存草稿、私人審核筆記或權杖 |
| [master.json](../l10n/master.json) | 本站 Master 識別與匯入資訊 | 不代表目前整批已驗收 |
| [upstream.json](../l10n/upstream.json) | 固定上游與書本版本 | 不因最新上游存在就自動升版 |

以檔案及 Master 中的實際紀錄為準，不在治理文件重複維護會變動的筆數或完成比例。

## 核准規則

1. Book Master 已 APPROVED 且原文、語境、版本吻合的定稿，可沿用核准並記錄原書紀錄 ID、來源 Sheet、版本及參考位置。
2. 不同來源版本、改寫、缺譯、多個候選或譯文衝突，先整理差異及候選供使用者確認，不自行標為 APPROVED。
3. 本站新譯文、必要 UI 字串及針對本站原文的調整，先為草稿；使用者明確核准後才納入核准快照。公開站與本地網站預覽均使用核准快照；待審譯文可在 Master 或審閱清單檢閱。
4. 人工畫面驗收不自動核准所有譯文；說「預覽有中文」也不等於核准所有頁面。核准需能對應具體紀錄或清楚列出的整批範圍。
5. SC Master 與批次紀錄若有狀態差異，先查明，不用批次文字覆蓋翻譯狀態。SC Master 管理譯文，批次檔管理範圍、驗收與發布證據。

## 快照更新流程

使用連接器讀取 Master，依 [capture-master.mjs](../scripts/l10n/capture-master.mjs) 在擷取前後確認修改時間，只輸出 APPROVED 投影；不要將整份草稿 Sheet 或私人筆記另存公開檔案。

```powershell
.venv\Scripts\python.exe scripts/l10n/import_master.py .work/approved-capture.json .work/candidate.json
.venv\Scripts\python.exe scripts/l10n/refresh.py .work/candidate.json
```

檢查新增、變更、移除與來源差異，確認屬於本批已核准內容後才執行：

```powershell
.venv\Scripts\python.exe scripts/l10n/refresh.py .work/candidate.json --apply
```

`--apply` 後依 [development](development.md) 先局部測試，穩定交付再完整驗證，不逐次匯入重建全站；這不代表部署。Book 更新只能產生提案，須經 SC 審核，不以 Book 匯入檔直接套用。

## 顯示與英文回退

- 保留來源雜湊與語境，採核准文字的精確對應，不做模糊比對或全文詞彙替換。
- 已確認只是排版的彎／直引號、省略號與標點周邊空白，不應直接視為缺譯；可記錄明確來源對應並在比對時作等價處理，保留快照原文與雜湊。詞句差異及連結語境仍分別檢查，不因標點適配放寬核准或啟用其他批次內容。
- 缺譯、原文已變而未重審、語境不符、候選衝突、連結無法安全保留時，該區塊維持英文，並說明原因。
- 分段匹配只在原文／譯文段落能安全對應時使用。原有連結無法適配時整段回退，不在英文句子裡任意塞入中文術語。
- UI、規則文字與名稱同樣需要核准。工程端可以處理顯示綁定，不可藉此自行新增未核准規則譯文。
- 同一紀錄在 Browse、Books、內嵌卡片、搜尋及匯出中共用對應；中英文名稱都能搜尋，機器欄位與連結目的地不翻譯。

建置輸出 `reports/coverage.json`、`coverage.md` 與 `p1-missing.json`。交付時將缺譯、來源差異、連結適配及顯示接線問題分開列示；它們是診斷資料，不是人工驗收證據。

## 族裔盤點與語境判讀

實作前一次盤點名稱、介紹、故事、UI、特性、成本／點數、條件、速選及直接引用，核對實際原文、Book／SC 與版本。程式處理大量精確比對，模型只讀摘要、差異及需語意判讀的段落；送審時提供必要原文與候選。缺譯、實質差異、排版、連結及接線問題分開列示，不重問已核准內容；來源／語境未變的盤點直接沿用。

連結目的地相同不保證中文標籤相同。先檢查整句及規則／敘事語境，再決定是否沿用：B01 強制移動 Distance 為「距離」，招式術語為「射程」；介紹 supernatural 為「超自然」，規則為「超常」。適配限制在明確紀錄、用途與路徑，不全站取代；新語境未確定時依核准規則送審。

使用者提供定稿時先檢查漏句、明顯誤譯、語病、數值與專有名詞，必要修正集中確認，其他內容保留。只在明確授權下同時寫入 Book 與 SC；寫後讀回內容、來源、核准狀態及既有格式，核對快照新增／變更／移除與未涉及紀錄。B01 的雙 Master 收錄不構成後續自動雙寫授權。案例及改善依據見 [B01 檢討](b01-retrospective.md)。
