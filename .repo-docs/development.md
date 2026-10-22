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

中文建置的 `SC_SITE_URL` 預設是本地網址。如 shell 留有正式網址，先設回本地，避免驗收時分享與 canonical 指向正式站：

```powershell
$env:SC_SITE_URL = 'http://127.0.0.1:8000/'
.venv\Scripts\python.exe -m mkdocs serve -f mkdocs.zh-TW.yml
```

原站 `justfile` 依賴上游多 repo 工作區；其中的 `serve`／`build` 使用英文設定並嘗試取得私有字型，`update` 預設還會 commit／push。本站中文化日常工作不用這些命令，也不用 `just clean_docs` 或 `just deploy-v2`。

## 驗證層級

### 翻譯接線、程式、樣式或快照變更

```powershell
.venv\Scripts\python.exe scripts/l10n/verify.py
```

此入口依序執行 Python 翻譯與 CI 測試、上游與本站 JavaScript 單元測試、中文完整建置、建置產物檢查，將各步驟結果寫入 `reports/verification.json`。讀取實際結果；不能以開始執行或舊報告當作通過。

依本批變更執行 [人工驗收清單](workflow.md)，並在真實瀏覽器測試受影響功能。即時導覽問題也能在本地重現：由站內連結跳頁測試，不能只重新整理或逐頁直接開啟。現有 `tests/e2e/` 可作回歸參考，執行前確認其瀏覽器與本地 URL 設定。

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
