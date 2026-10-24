# 本地開發與驗證

以下命令從 repo 根目錄執行，使用 PowerShell。Python 3.13、Node.js 22 以上；現有 CI 使用 Python 3.13、Node.js 24。

## 安裝與預覽

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
.venv\Scripts\python.exe -m mkdocs serve -f mkdocs.zh-TW.yml
```

已存在 `.venv` 時直接使用。預覽在 <http://127.0.0.1:8000/>，先等首次建置完成；全站建置可能需要數分鐘。交付時保持預覽可用，若已停止則提供重新啟動方式。

修改 `scripts/l10n/` 的 Python 翻譯器後，須停止並重新執行 MkDocs 服務，確保載入新的模組；不能只靠文件監看重建或瀏覽器重新整理。交付前對照實際服務回應與本次建置產物，確認正在驗收的網址使用同一版程式。臨時另開埠號檢查後，應統一回原驗收入口並停止不再使用的臨時服務。

預覽交付由 Agent 確認唯一服務、完成必要重啟，並讀取驗收入口的實際回應，逐一核對本批受影響內容；只有服務啟動訊息、HTTP 200 或磁碟建置通過，均不能證明該網址已載入修正版。穩定驗收時可用 `.venv\Scripts\python.exe -m http.server 8000 --bind 127.0.0.1 --directory site` 提供已驗證的 `site/` 固定產物，直接比對 HTTP 回應與檔案；此模式沒有自動重建，更新內容後須重新建置再交付。

中文建置的 `SC_SITE_URL` 預設是本地網址。如 shell 留有正式網址，先設回本地，避免驗收時分享與 canonical 指向正式站：

```powershell
$env:SC_SITE_URL = 'http://127.0.0.1:8000/'
.venv\Scripts\python.exe -m mkdocs serve -f mkdocs.zh-TW.yml
```

原站 `justfile` 依賴上游多 repo 工作區；其中的 `serve`／`build` 使用英文設定並嘗試取得私有字型，`update` 預設還會 commit／push。本站中文化日常工作不用這些命令，也不用 `just clean_docs` 或 `just deploy-v2`。

## 驗證層級與證據沿用

開發預設跑受影響的單元測試與精確文字／連結檢查。穩定交付前先跑全部便宜測試，失敗先修正，再進入完整驗證；不要用全站建置排查局部錯誤。verify.py 會執行 Python 與 JavaScript 兩套測試，任一失敗便略過建置／產物檢查；建置失敗只略過產物檢查。

| 修改內容 | 需要重新取得的本地證據 |
|---|---|
| 治理、驗收紀錄或 PR 說明 | 文件檢查；沿用網站建置、畫面與內容驗收 |
| 僅測試程式 | 重跑相關測試；網站輸入及環境未變可沿用建置／畫面 |
| 譯文、來源、顯示接線或樣式 | 相關測試；穩定後完整驗證，重查受影響的頁面／功能 |
| 共用解析、依賴或建置設定 | 完整驗證；依影響擴大畫面檢查，無法確認時保守重驗 |

沿用時能指出原成功版本及後續差異，並確認相關輸入、依賴、設定與預覽產物未變；證據不存在、不完整或有新失敗則重驗。只有時間經過、文件收尾或再次推送，不構成網站證據失效。這不豁免最新 CI：CI 仍按整個 PR 累積差異執行。

成功只讀摘要，失敗讀相關錯誤；大型完整日誌留檔。優先使用既有工具並等待 CI 狀態變更／完成，避免無新資訊的重複查詢。

### 翻譯接線、程式、樣式或快照變更

```powershell
.venv\Scripts\python.exe scripts/l10n/verify.py
```

此入口依序執行 Python 翻譯與 CI 測試、上游與本站 JavaScript 單元測試、中文完整建置、建置產物檢查，將各步驟結果寫入 `reports/verification.json`。讀取實際結果；不能以開始執行或舊報告當作通過。

報告維持頂層陣列及 step／exitCode／seconds，新增 status（passed／failed／skipped）；略過步驟 exitCode 為 null、seconds 為 0 並列 reason。執行步驟的 stdout／stderr 合併保存在 reports/verification-<step>.log，報告以 log 連結；失敗附有界 error 摘要。啟動錯誤回報失敗與錯誤資訊；任一步驟 failed，入口退出碼為 1。既有 CI 會上傳整個 reports/，不需修改 workflow。

依 [人工驗收清單](workflow.md) 在真實瀏覽器檢查受影響功能；固定一組必要代表頁，有特殊路徑或回歸風險才加測。主頁、章節、獨立特性／招式頁、靜態索引卡、動態卡片各自的受影響接點不能互相代替；未受影響者沿用有效證據。即時導覽要由站內連結跳頁實測；可參考 `tests/e2e/`。

### 內容一致性與卡片結構檢查

- 完整驗證前，用實際生成來源做局部對照：相同核准紀錄在 Browse／Read 的介紹、短句、點數／速選及適用卡片，都應取用同一核准內容並保留各自原連結。測試須涵蓋實際來源結構，不能只用手寫片段或核對 catalog 有紀錄；未核准／來源變更的內容仍須英文回退。
- 對頁面自連結，測試要走過 MkDocs hook 的實際輸入形態；若 MkDocs 將來源連結改寫成 `./`，就明確用 `href="./"` 覆蓋原始 `.md` 連結測試。逐項確認該頁核准文字仍能安全適配、原目的地保留；不得只在 hook 前的 Markdown 測成功。Browse 與 Read 頁面範圍條件也要用實際章節標題測試，包含子標題及已翻譯標題，不可因最近標題改變而漏掉同一族裔的短句或卡片欄位。
- 列出本批所有呈現種類及實際路徑。靜態索引卡另查關鍵字、射程、目標、成本／來源等可見欄位；名稱或風味句已中文不代表整張卡完成。每種受影響模板至少選一個實際頁面檢查，其他同模板項目用程式比對摘要。
- 翻譯前後保留元件結構：inline 欄位不能因 Markdown 轉換多包 p；檢查標題層級、段落、原有數字強調、連結及結果列。卡片變高時先比較相同視窗／縮放／顯示設定下的 DOM、computed margin／padding／line-height 與欄位高度，先修結構，再判斷是否真需 CSS 調整；不以縮字或負 margin 掩蓋新增段落。
- 修正後加入針對原因的回歸測試，並在最後建置實測受影響頁與站內跳頁。記錄實際結果及未測限制，不能用另一種卡片已通過來代替。

以上是 B03 的必要預防項目，案例與原有測試見 [B03](batches/B03.md) 與 [test_l10n.py](../tests/test_l10n.py)。不新增全站逐頁截圖要求；證據沿用仍依上表。

### 純治理／說明文件變更

執行 `git diff --check`，確認新治理文件的本地連結與命令路徑存在、沒有現行互斥規則，且差異沒有混入生成內容、翻譯快照或程式變動。歷史文件外部工作區連結可保持原狀，但必須標示為上游參考。純文件修改不需重跑全站建置，不能因此宣稱程式測試已通過。

本地與 CI 共用不需額外套件的文件檢查入口：

```powershell
.venv\Scripts\python.exe scripts/ci/check.py docs --base origin/develop
.venv\Scripts\python.exe -m unittest discover -s tests -p test_ci.py
```

檢查現行治理文件的本地 inline／reference Markdown 連結、圖片路徑、必要命令路徑、批次段落、CLAUDE 共用入口及差異空白。排除程式碼區塊與外部網址，不檢查錨點是否存在；上游封存不逐頁驗證，現行文件指向封存的本地路徑仍須存在。檢查結果為 `reports/ci-docs.json`。

### 發布驗證

取得發布授權並選定已驗收 commit 後，用實際網址：

```powershell
$env:SC_SITE_URL = 'https://boyiad2110.github.io/steel-compendium-zh-tw/'
.venv\Scripts\python.exe scripts/l10n/verify.py
```

完成後回到本地工作時將環境變數設回本地網址。發布的人工閘門見 [workflow.md](workflow.md)。

## 分支與整合

`develop` 是 GitHub 預設分支，也是本站中文化工作的整合目標；每個批次都必須透過 PR 合併，不直接將批次內容推送到 `develop`，不預設推送到 `main`。

每批從最新 `develop` 建立 `codex/` 工作分支，在該分支實作並推送，建立目標為 `develop` 的 Draft PR。使用者明確驗收通過後，補上紀錄、確認最新 PR 檢查通過，再轉為可審查並合併，最後更新本地 `develop`。上游同步與純文件批次也適用，修改意見維持在同一 PR。詳細步驟見 [工作流程](workflow.md)。

目前未新增 GitHub 分支保護或自動辨識驗收的機制；執行者依本流程管理，不能宣稱已程式封鎖直接推送。

## CI 的實際行為

- [zh-tw.yml](../.github/workflows/zh-tw.yml) 保留固定的 `check` job，每個 PR 都會執行；不以 workflow 層級的 `paths-ignore` 跳過整個必要檢查。
- 分類器 [scripts/ci/check.py](../scripts/ci/check.py) 讀取整個 PR 的檔案差異，包含分頁、刪除及重新命名前路徑；讀取前後確認 base／head 與檔數一致。不要只看最新一筆 commit。
- 只有 `AGENTS.md`、`CLAUDE.md`、`README.md`、`README.zh-TW.md`、`.impeccable.md`、`.github/pull_request_template.md` 及 `.repo-docs/**/*.md` 可走 `docs`。其他檔案一律 `full`，包含 `docs/**/*.md`、快照、樣式、程式、CI、驗證腳本與依賴設定。
- API 失敗、差異不完整、讀取期間版本變更、空差異、達到 API 3,000 檔上限或無法確認時，保守走 `full`；分類程式本身執行失敗則 job 失敗，不回報假成功。
- `docs` 只跑 CI 分類／文件測試與文件檢查，不安裝全站 Python 依賴、不設定 Node、不建置網站。`full` 額外執行既有完整驗證。任一步驟失敗即 `check` 失敗；不是把略過的驗證當作通過。
- 分類模式與原因寫入 Actions Summary；兩條路徑共用單一 `localization-reports` artifact，留存分類、文件報告及適用的完整驗證結果，避免重複上傳。
- 同一 PR 有新提交時取消舊版檢查，只跑最新版；手動建置／部署不自動取消前一個執行。PR 與手動執行使用不同 concurrency group。
- 完整路徑啟用 pip 下載快取，以 `requirements.lock.txt` 雜湊為依據；仍執行安裝，不重用舊建置產物，也不省略測試。
- 手動執行需提供 `site_url`，無論差異皆走 `full`，`deploy` 預設 `false`。
- 只有手動指定 `deploy: true` 才進行中文 Pages 部署，且要先通過 check 工作；操作者必須先有使用者的發布授權。
- [ci.yml](../.github/workflows/ci.yml)：保留上游流程，部署 job 限定 `SteelCompendium/v2`，不是本站發布入口。
- 現在沒有每次 push 就部署的設定，也沒有 CI 自動確認人工驗收的機制。

可用指定路徑在本地確認分類規則（只模擬分類，不執行或宣稱遠端 CI 通過）：

```powershell
.venv\Scripts\python.exe scripts/ci/check.py classify --files README.md .repo-docs/batches/CI-01.md
.venv\Scripts\python.exe scripts/ci/check.py classify --files README.md docs/index.md
.venv\Scripts\python.exe scripts/ci/check.py classify --event workflow_dispatch --files README.md
```

依序應得到 `docs`、`full`、`full`。CI 流程本身的變更 PR 仍走完整驗證；只有之後真正純文件的 PR 才會省下全站建置，不能把這次 CI 優化 PR 最後一筆文件提交誤判成純文件 PR。

## 報告與追蹤

`site/`、`.work/`、`reports/`、`outputs/`、`.venv/` 及 `node_modules/` 為本地／生成資料。`reports/` 不納入 Git；需要長期保留的 QA 結論、限制、驗收證據及版本寫入 [批次紀錄](batches/README.md)。不要遞迴掃描或修改工具安裝目錄、依賴 junction 或其他專案。

上游版本更新先核對 [upstream.json](../l10n/upstream.json)，在 `codex/` 分支整理同步 PR、文字差異、過期譯文及失效對應，再驗證受影響內容。一般本地預覽不需要取得 `steel-etl` 或重新生成上游規則。

## 驗收預覽與畫面交付檢查

- 每批記錄單一驗收 URL、服務命令、PID／埠號、建置 commit 與建置時間。啟動前確認目標埠是否已占用；若已存在服務，先核對程序命令及來源，只停止已確認屬本批且應替換的程序，不依埠號盲目終止。
- 網站來源改動後重建並核對實際 URL 與產物版本；Python hooks 改動須重啟 MkDocs（固定 site 則使用新建置程序）。僅文件／紀錄變更且產物未變，不重建、重啟或重拍截圖。HTTP 200 本身不能證明版本正確。
- 臨時替代埠只作診斷，交付前回到單一入口並清理本批多餘服務。預覽逾時先查監聽程序與回應，不先要求使用者調整防火牆／代理；畫面仍舊時先查程序與產物版本。
- 受影響接點檢查 heading 結構、首字／成本／換行與互動；視覺問題對照原英文 DOM 與 computed style，避免只用 CSS 掩蓋結構錯誤。檢查範圍依上方證據沿用規則。
- 匯出截斷等問題比較中英文原站與相同操作條件，記錄是否為上游既有、中文新增或尚無法判斷，以及受影響範圍與處置。未修復限制不得報為已修復。
- 收尾以最新 PR head 的實際 Actions check-run／結論及 run URL 為證；statuses 或 runs 查詢為空時交叉核對 GitHub CLI／Actions，無法確認就不合併。

以上為人工執行與紀錄要求，未新增自動預覽版本驗證或視覺測試工具；案例見 [B01 檢討](b01-retrospective.md)。
