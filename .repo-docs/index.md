# 中文化專案治理入口

更新日期：2026-10-23。這裡管理 `boyiad2110/steel-compendium-zh-tw`，不是上游 `SteelCompendium/v2` 的工作區。

## 依任務讀取

| 文件 | 負責的規則／資訊 | 何時讀 |
|---|---|---|
| [AGENTS.md](../AGENTS.md) | Agent 必守界線、閱讀路由 | 每次進入 repo |
| [project.md](project.md) | 目標、P0–P4、完成定義 | 排程或調整範圍 |
| [translation.md](translation.md) | Master、核准、快照、英文回退 | 翻譯、匯入或接線 |
| [workflow.md](workflow.md) | 批次、人工驗收、發布授權 | 開始／交付每批、部署 |
| [development.md](development.md) | 本地命令、驗證、CI 實際行為 | 實作與 QA |
| [architecture.md](architecture.md) | 技術架構、不可變資料、視覺與互動約束 | 修改程式／樣式 |
| [b01-retrospective.md](b01-retrospective.md) | B01 得失、改善依據及追蹤 | 開始後續族裔或檢討交付流程 |
| [batches/README.md](batches/README.md) | 批次清單與紀錄格式 | 追蹤範圍及驗收 |
| [governance-audit.md](governance-audit.md) | 本次盤點、治理整理與未改事項 | 檢閱本次治理變更 |
| [upstream/README.md](upstream/README.md) | 上游歷史文件的使用界線 | 必要的技術追查 |

各詳細文件為其列示主題的維護位置。README 是入口，AGENTS 是必守摘要；調整流程時更新負責的詳細文件，若影響摘要再同步，避免另創同義規則檔。

## 目前工作方式

已建立核准快照與顯示接點，P0／P1 仍是部分完成。使用者曾確認公開預覽看得到中文，這不等於 P1 或所有頁面的人工驗收通過。

後續每批必開目標為 `develop` 的 PR，先引導使用者本地驗收；明確通過並完成檢查後才合併、收尾，再開始下一批。部署由使用者另行指定。工程結果、翻譯核准、人工驗收、PR 合併與發布版本各自追蹤，不能互相代替。

## 歷史文件與外部專案

`.repo-docs/upstream/` 下的全部文件為歷史參考，不是目前規則或待辦。它們可能提及不存在的上游工作區、舊版本、部署流程或字型權利；需要使用時先對照本站程式與現行文件。

`forgesteel-zh-tw` 是參考專案，不是本站治理或發布來源；本次工作不修改其文件。
