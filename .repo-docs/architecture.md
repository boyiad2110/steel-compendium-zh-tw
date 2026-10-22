# 中文顯示架構與工程約束

## 資料流程

固定的上游英文生成內容 → MkDocs 解析 → 中文顯示 hooks → 靜態 HTML／搜尋索引 → 瀏覽器互動與匯出。

SC Master → 僅擷取核准紀錄 → 候選快照與差異審查 → `l10n/catalog.json` → 中文建置。

網站和 CI 不讀取即時 Sheet。原英文內容與遊戲機器資料維持上游格式，中文顯示由核准對應處理；無法安全翻譯的區塊維持英文。

## 主要接點

| 路徑 | 責任 |
|---|---|
| [mkdocs.zh-TW.yml](../mkdocs.zh-TW.yml) | 繼承上游的中文設定、本站 URL、語言及 hooks |
| [core.py](../scripts/l10n/core.py) | 核准快照驗證、精確文字匹配、語境與連結適配 |
| [hooks.py](../scripts/l10n/hooks.py) | 頁面／導覽顯示、TOC、搜尋別名、匯出文字與覆蓋報告 |
| [l10n-core.js](../docs/javascripts/l10n-core.js)、[l10n.js](../docs/javascripts/l10n.js) | 核准顯示標籤與保留原文的客戶端接點 |
| [l10n-zh-TW.css](../docs/stylesheets/l10n-zh-TW.css) | 本地繁體中文字型與必要換行 |
| `docs/javascripts/sc-search-core.js`、`steel-feature-browser.js` | 中英文搜尋與顯示名稱，保留原始篩選鍵 |

中文設定停用 `roamlinks`：目前生成內容已使用明確 Markdown 連結，該外掛在 Windows 反覆掃描全站造成延遲。上游更新後若重新出現 Wiki 連結，先重新評估，不盲目延用假設。

## 不可變資料與修改位置

- 不改 SCC、內部 ID、英文 URL、錨點 ID、原始 JSON 欄位、篩選鍵、數值結果及分享格式。
- 原生計算工具讀取保留的原文／原值，不能拿中文顯示字串重新解析。翻譯不能影響擲骰、等級調整或其他數值運算。
- `docs/Browse/`、`docs/Bestiary/`、`docs/Read/`、`docs/scc/` 是上游生成內容，不直接改。
- 中文規則接線集中在 `scripts/l10n/` 與對應 JS／CSS；核准文字在 catalog，避免在程式硬寫譯文。
- `static_content/` 原有上游手寫頁仍可維護，但不得以複製整頁中文內容繞過核准快照。`mkdocs.yml`、`site.yaml` 的上游結構盡量保留；只有必要且列明理由時才修改。

## 即時導覽與原互動

Material `navigation.instant` 會替換頁面內容。掛載程式須透過 `document$.subscribe`，保持重複初始化安全、清理額外監聽器，不能只依賴 `DOMContentLoaded`。

讀取 JSON data island 時使用既有 mount 容器與上游約定，不假設換頁後 inline script 的 class／type 仍在。邏輯與 DOM 掛載保持既有 core／mount 分工；不要為翻譯另寫一套互動工具。

卡片的複製、收藏、匯出等操作留在既有 chrome 控制區，不塞入標題數值欄。修改偽元素樣式前先查看 computed style，避免被其他卡片樣式覆蓋。細節必要時查 [上游即時導覽紀錄](upstream/decisions/2026-06-11-client-scripts-navigation-instant.md) 或 [上游疑難排解](upstream/troubleshooting.md)，並對照現行程式。

## 視覺與字型

保留上游設計、色彩、元件、偏好設定與版面結構。中文字型使用具明確授權的 Noto Sans TC 後備資產並保留 OFL；不取得或發布上游另購字型，不假設其權利移轉到本站。

接受合理換行與高度增加；以閱讀完整、控制項可操作、無重疊／截斷為驗收標準，不追求中英文像素完全一致。任何超出必要中文字型與可用性修正的設計變更，另列範圍，不混入中文化批次。

變更這些核心決策時，在本文件記錄理由、影響及驗證；只有需要長期比較替代方案時才新增獨立決策文件，避免為每批翻譯製造架構文件。
