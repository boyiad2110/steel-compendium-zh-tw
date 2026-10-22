# Steel Compendium 正體中文版

保留 [Steel Compendium v2](https://github.com/SteelCompendium/v2) 的功能、視覺與版面結構，優先中文化 **Heroes 所有職業的 1 級創角資料**。尚未核准或來源不符的文字保留英文。

- [專案治理與文件入口](.repo-docs/index.md)
- [開發與本地預覽](.repo-docs/development.md)
- [翻譯來源與核准規則](.repo-docs/translation.md)
- [批次、人工驗收與發布流程](.repo-docs/workflow.md)
- [批次紀錄](.repo-docs/batches/README.md)
- [既有公開預覽](https://boyiad2110.github.io/steel-compendium-zh-tw/)（可能落後本地待驗收內容）

## 本地預覽

在 repo 根目錄使用 Python 3.13、Node.js 22 以上：

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
.venv\Scripts\python.exe -m mkdocs serve -f mkdocs.zh-TW.yml
```

開啟 <http://127.0.0.1:8000/>。每批先本地驗收；部署需使用者另外指定，不會因為完成一批而自動發布。

本站預設分支與中文化整合分支為 `develop`，後續變更推送或合併至此分支。

## 授權與來源

原站程式授權見 [LICENSE](LICENSE)；遊戲內容保留 DRAW STEEL Creator License 聲明。本站使用具明確授權的繁體中文字型，不包含上游另購的 Berlingske Slab 字型。

The Draw Steel Compendium is an independent product published under the DRAW STEEL Creator License and is not affiliated with MCDM Productions, LLC. DRAW STEEL (c) 2025 MCDM Productions, LLC.

原始上游文件保存在 [.repo-docs/upstream/](.repo-docs/upstream/README.md)，僅供技術與歷史參考。
