# 本地開發與驗證

以下命令從 repo 根目錄執行，使用 PowerShell。Python 3.13、Node.js 22 以上；現有 CI 使用 Python 3.13、Node.js 24。

## 安裝與預覽

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
.venv\Scripts\python.exe -m mkdocs serve -f mkdocs.zh-TW.yml
```

已存在 `.venv` 時直接使用。預覽在 <http://127.0.0.1:8000/>，先等首次建置完成；全站建置可能需要數分鐘。交付時保持預覽可用，若已停止則提供重新啟動方式。

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

此入口依序執行 Python 翻譯測試、上游與本站 JavaScript 單元測試、中文完整建置、建置產物檢查，將各步驟結果寫入 `reports/verification.json`。讀取實際結果；不能以開始執行或舊報告當作通過。

依本批變更執行 [人工驗收清單](workflow.md)，並在真實瀏覽器測試受影響功能。即時導覽問題也能在本地重現：由站內連結跳頁測試，不能只重新整理或逐頁直接開啟。現有 `tests/e2e/` 可作回歸參考，執行前確認其瀏覽器與本地 URL 設定。

### 純治理／說明文件變更

執行 `git diff --check`，確認新治理文件的本地連結與命令路徑存在、沒有現行互斥規則，且差異沒有混入生成內容、翻譯快照或程式變動。歷史文件外部工作區連結可保持原狀，但必須標示為上游參考。純文件修改不需重跑全站建置，不能因此宣稱程式測試已通過。

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

- [zh-tw.yml](../.github/workflows/zh-tw.yml)：PR 執行驗證；手動執行需提供 `site_url`，`deploy` 預設 `false`。
- 只有手動指定 `deploy: true` 才進行中文 Pages 部署，且要先通過 check 工作；操作者必須先有使用者的發布授權。
- [ci.yml](../.github/workflows/ci.yml)：保留上游流程，部署 job 限定 `SteelCompendium/v2`，不是本站發布入口。
- 現在沒有每次 push 就部署的設定，也沒有 CI 自動確認人工驗收的機制。

## 報告與追蹤

`site/`、`.work/`、`reports/`、`outputs/`、`.venv/` 及 `node_modules/` 為本地／生成資料。`reports/` 不納入 Git；需要長期保留的 QA 結論、限制、驗收證據及版本寫入 [批次紀錄](batches/README.md)。不要遞迴掃描或修改工具安裝目錄、依賴 junction 或其他專案。

上游版本更新先核對 [upstream.json](../l10n/upstream.json)，在 `codex/` 分支整理同步 PR、文字差異、過期譯文及失效對應，再驗證受影響內容。一般本地預覽不需要取得 `steel-etl` 或重新生成上游規則。
