# agents.md — InfographicsCreation AI Agent SOP

> 本文件是本儲存庫中 AI agent 的標準操作程序（Standard Operating Procedure, SOP）。
> 目標是讓任何後續 agent 在收到「教材網頁 URL → 製作互動式 infographic → 推送 GitHub → 由 GitHub Actions 發布成可瀏覽 HTML」的任務時，可以直接依此流程執行，不需要重新猜測專案規格。

## 0. 專案目的與最終成果

本專案用來把 Pattern Recognition、Deep Learning、Linear Algebra 等課程教材內容，轉換成：

- 16:9 教學型 infographic
- 繁體中文 + English 雙語
- HTML5 + JavaScript + Canvas 原生繪製
- 可互動
- 每張 infographic 一個獨立 HTML
- 可直接用瀏覽器開啟
- 可用 `<iframe>` 嵌入其他教材、LMS、網頁或應用
- 自動經由 GitHub Actions 部署到 GitHub Pages

GitHub repository：

```text
https://github.com/ndhuccc/InfographicsCreation
```

主要發布分支：

```text
main
```

課程內容放在：

```text
courses/<COURSE_CODE>/<TOPIC>/*.html
```

例如：

```text
courses/PR115/
├── BayesInference/
├── MaximumLikelihoodEstimation/
└── MaximumPosterioriEstimation/
```

---

# 1. 任務輸入形式

使用者最常提供以下其中一種輸入：

1. 一個教材網頁 URL
2. 一段教材文字
3. 一份 PDF / HTML / Markdown
4. 一個特定知識點，例如 `#kp10`
5. 已存在課程頁面的某個 anchor
6. 指示「根據這頁內容執行專案要求」

Agent 必須先理解內容，再製作 infographic。

不要一看到 URL 就直接開始畫圖。

---

# 2. 第一階段：讀取與理解教材來源

## 2.1 URL 輸入

收到 URL 時：

1. 讀取該頁完整內容。
2. 若 URL 含 fragment，例如 `index.html#kp10`，必須找出該 anchor 對應的實際知識點。
3. 同時讀取必要的上下文，避免只截取一小段造成概念斷裂。
4. 若該頁又連到獨立 slide HTML，可直接讀取該 slide。
5. 若內容很多，可拆成多張 infographic，不必全部塞在一張。

## 2.2 內容理解要求

製作前先建立知識結構：

```text
背景問題
  ↓
核心概念
  ↓
數學定義
  ↓
推導
  ↓
直覺
  ↓
例子
  ↓
常見誤解
  ↓
互動演示
  ↓
總結
```

不可只把原文縮短後排版。Infographic 必須呈現「知識關係」。

---

# 3. 第二階段：決定 infographic 拆頁策略

## 3.1 一個 HTML = 一張 infographic

本專案的重要規格：

> 每一張 infographic 必須是一個獨立 HTML。

不要用一個 HTML 包含多張投影片再用上一頁/下一頁切換。

原因：

- 使用者需要單獨嵌入教材
- LMS 可以只嵌某一張
- 每張可以有自己的互動
- GitHub Pages URL 穩定
- 後續其他應用容易引用

正確：

```text
01-concept.html
02-derivation.html
03-interactive-example.html
04-summary.html
```

不建議：

```text
all-slides.html
```

然後再用 JavaScript 切頁。

## 3.2 何時拆頁

以下情況應拆成不同 infographic：

- 核心直覺與完整數學推導
- 定義與互動模擬
- 方法比較
- 常見誤解
- 大樣本 / 小樣本行為
- 練習題
- 總結

目標不是頁數少，而是每張只負責一個清楚的認知任務。

---

# 4. 第三階段：HTML5 + Canvas 技術規格

## 4.1 必須是 Canvas 原生繪製

Infographic 不可以只是：

```html
<img src="page.png">
```

也不可以：

```javascript
drawImage(preRenderedPNG)
```

把整張預先生成圖片放入 Canvas。

應使用：

- `fillText()`
- `lineTo()`
- `arc()`
- `roundRect()`
- Canvas path
- JavaScript state
- slider / button interaction

逐元素繪製。

## 4.2 固定設計尺寸

Canvas 建議使用：

```html
<canvas width="1600" height="900"></canvas>
```

即 16:9、1600 × 900。

CSS 依 viewport 縮放：

```css
.stage {
  width: min(100vw, 177.7778vh);
  height: min(56.25vw, 100vh);
  aspect-ratio: 16 / 9;
}
canvas {
  width: 100%;
  height: 100%;
}
```

---

# 5. 第四階段：雙語與文字規格

預設語言：

- 繁體中文
- English

推薦形式：

```text
最大似然估計
Maximum Likelihood Estimation
```

或：

```text
Posterior / 後驗分佈
```

專業術語可以保留英文。

避免同一個 panel 中放兩段完整翻譯造成資訊過載。

---

# 6. 第五階段：互動設計原則

互動必須服務概念，不只是裝飾。

## 6.1 好的互動例子

Likelihood：點選不同參數，例如 Suspect A / B / C，即時改變 likelihood。

MAP：拖曳 N、prior variance、prior mean、sample mean，即時觀察 MAP estimate、prior weight、data weight。

Bayesian inference：改變 N、sample mean、prior variance，即時顯示 posterior mean、posterior variance、predictive variance。

推導：使用 Step 1 / Step 2 / Step 3 逐步揭露。

## 6.2 不好的互動

只有「上一頁 / 下一頁」但頁內內容完全靜態。

這只能算 navigation，不算真正 interactive infographic。

---

# 7. 第六階段：Canvas 文字排版規範

Canvas 原生 `fillText()` 不會自動換行。

必須實作 `wrap()` 函式。

並注意 `\n` 有時可能被當成兩個普通字元，而不是換行。

因此 wrap 函式應先正規化：

```javascript
t = String(t).replace(/\\n/g, "\n");
```

任何 infographic 交付前都要檢查：

> 畫面上不可直接出現 literal `\n`。

---

# 8. 第七階段：版面稽核（MANDATORY）

這是完成 infographic 前的必要程序。

任何頁面未通過 layout audit 都不能視為完成。

## 8.1 必查項目

### 文字 ↔ 文字

檢查 title/subtitle、paragraph、formula、labels、button text、legend、caption 是否互相重疊。

### 文字 ↔ 圖形

檢查：

- 文字是否壓到曲線
- 公式是否壓到圖
- slider 是否碰到圖
- button 是否遮到文字
- label 是否蓋住資料點

### Canvas 邊界

檢查：

- 左右 overflow
- 上下截切
- 長公式超界
- 文字被 Canvas 邊緣裁掉

## 8.2 必須檢查互動狀態

不能只看初始畫面。

至少測試：

- 每個 button mode
- 展開 / 收合
- step 1 → final step
- slider 最小值
- slider 最大值
- 中文
- English
- Quiz answer 狀態

例如 N = min、N = typical、N = max 都需要檢查。

## 8.3 發現 overlap 時修正順序

優先：

1. 調整 layout
2. 調整 x / y
3. 增加 panel 高度
4. 增加 padding
5. 改善 wrap
6. 微調字級

最後才考慮刪內容。

原則：

> 不得為了避免 overflow 而直接刪掉重要教材內容。

---

# 9. 第八階段：檔名與 Topic 命名

Topic directory 使用可讀的 PascalCase，例如：

```text
MaximumLikelihoodEstimation
MaximumPosterioriEstimation
BayesInference
GradientDescent
SupportVectorMachine
```

HTML 使用：

```text
01-why-maximum-likelihood.html
02-detective-likelihood.html
03-likelihood-product.html
```

數字 prefix 可以確保首頁排序符合教學順序。

---

# 10. 第九階段：決定 GitHub 路徑

標準結構：

```text
courses/<COURSE_CODE>/<TOPIC>/
```

例如：

```text
courses/PR115/MaximumLikelihoodEstimation/
courses/PR115/MaximumPosterioriEstimation/
courses/PR115/BayesInference/
```

如果使用者尚未告知課程代號，先詢問。已經知道課程代號則不要重複詢問。

---

# 11. 第十階段：推送到 GitHub

目標 repository：

```text
ndhuccc/InfographicsCreation
```

目標 branch：

```text
main
```

## 11.1 優先流程

如果 agent 可以正常使用 git：

```bash
git add courses/<COURSE>/<TOPIC>/
git commit -m "Add <course> <topic> interactive infographics"
git push origin main
```

## 11.2 GitHub Connector 推送流程

若使用 GitHub Connector，推薦 Git data 流程：

```text
HTML files
  ↓
create_blob
  ↓
create_tree
  ↓
create_commit
  ↓
update_ref(main)
```

這相當於 git add → git commit → git push。

### Step A：取得 main HEAD

取得 parent commit SHA 與 base tree SHA。

### Step B：每個 HTML 建立 blob

```text
create_blob(
  repository_full_name="ndhuccc/InfographicsCreation",
  content=<HTML>,
  encoding="utf-8"
)
```

### Step C：建立 tree

每個 entry：

```json
{
  "path": "courses/PR115/BayesInference/01-page.html",
  "mode": "100644",
  "type": "blob",
  "sha": "<blob SHA>"
}
```

使用 `base_tree_sha = main HEAD tree`，確保其他 repo 檔案不受影響。

### Step D：create_commit

```text
parent_sha = current main HEAD
tree_sha   = new tree
```

### Step E：update_ref

更新 `main → new commit`，正常情況 `force=false`，不要 force push。

---

# 12. GitHub Connector 特別注意事項

某些執行環境可能會對：

```text
create_file(content="<完整 HTML + JS>")
```

做安全檢查而阻擋。

這不代表 GitHub 不能存 HTML。

若遇到這種狀況，不要放棄。改用：

```text
create_blob
→ create_tree
→ create_commit
→ update_ref
```

若 HTML 已存在於 ChatGPT conversation file，可：

```text
files.list
→ files.read
→ create_blob
```

這能避免手動重新拼接內容或 Base64 錯誤。

---

# 13. 第十一階段：推送後驗證

推送完成後，必須重新讀取：

```text
courses/<COURSE>/<TOPIC>?ref=main
```

確認：

- 檔案數量
- 檔名
- path
- branch
- SHA

例如：

```text
12 HTML expected
12 HTML found
```

不能只看到 commit success 就宣告完成。

---

# 14. GitHub Pages 架構

Pages deployment 使用：

```text
.github/workflows/pages.yml
```

目前 workflow：

```yaml
on:
  push:
    branches: [main]
```

因此 push 到 main 會自動觸發 Pages build。

Pages Source 應設定為：

```text
GitHub Actions
```

而不是 Deploy from a branch。

---

# 15. build_site.py 行為

建站腳本：

```text
scripts/build_site.py
```

它會掃描：

```text
courses/<course>/**/*.html
```

然後：

1. 複製 HTML 到 `_site/`
2. 產生 `*.src.html`
3. 複製 images / JS / CSS / data assets
4. 自動建立 `_site/index.html`
5. 首頁依 Course → Topic → Page 分組

例如：

```text
PR115
├─ BayesInference
├─ MaximumLikelihoodEstimation
└─ MaximumPosterioriEstimation
```

因此新增 infographic 時不要修改 index.html。

`_site/` 是 build artifact，不應手動提交。

---

# 16. GitHub Pages URL 規則

Pages base URL：

```text
https://ndhuccc.github.io/InfographicsCreation/
```

Source：

```text
courses/PR115/BayesInference/10-interactive-lab.html
```

Live URL：

```text
https://ndhuccc.github.io/InfographicsCreation/courses/PR115/BayesInference/10-interactive-lab.html
```

Source viewer：

```text
https://ndhuccc.github.io/InfographicsCreation/courses/PR115/BayesInference/10-interactive-lab.src.html
```

---

# 17. iframe 嵌入規則

任何 infographic 都應可：

```html
<iframe
  src="https://ndhuccc.github.io/InfographicsCreation/courses/PR115/BayesInference/10-interactive-lab.html"
  style="width:100%; aspect-ratio:16/9; border:0;">
</iframe>
```

因此 HTML 不應依賴：

- parent page JavaScript
- global shared state
- 特定 host DOM
- React runtime
- server backend

每頁需 standalone。

---

# 18. GitHub Actions 發布後檢查

Push main 後：

1. 檢查 GitHub Actions。
2. 確認 Deploy Pages workflow 啟動。
3. 確認 build 成功。
4. 開啟 GitHub Pages URL。
5. 測試至少一張 infographic。
6. 確認首頁 topic grouping 正常。

如果 Actions 尚未立刻出現，可能只是 GitHub 尚未建立或 connector 尚未同步 run。不要立即判定部署失敗。

---

# 19. 不要做的事情

- 不要把整張 infographic 轉成圖片；Canvas 必須是原生繪製。
- 不要把所有 infographic 塞進一個 HTML；每張獨立 HTML。
- 不要只做靜態 Canvas；有適合互動的概念就應加入互動。
- 不要手動維護 index.html；由 `build_site.py` 自動生成。
- 不要提交 `_site/`；它是 build artifact。
- 不要未稽核就推送；完成 HTML 後先做 layout audit。
- 不要因為 create_file 被阻擋就說「GitHub 不能推 HTML」；改用 Git object API。
- 不要直接 force update main；正常情況 `force=false`。

---

# 20. 建議完整 Agent Workflow

```text
User provides URL
        ↓
Read source page
        ↓
Identify knowledge point
        ↓
Read necessary context
        ↓
Build concept map
        ↓
Decide infographic decomposition
        ↓
Create standalone HTML5 Canvas pages
        ↓
Add conceptual interaction
        ↓
Check bilingual labels
        ↓
Check formulas
        ↓
Check \n handling
        ↓
Render important interaction states
        ↓
Layout audit
        ↓
Fix overlaps / overflow
        ↓
Re-audit
        ↓
Determine course code
        ↓
Determine topic directory
        ↓
Create Git blobs
        ↓
Create tree
        ↓
Create commit
        ↓
Update main ref
        ↓
Verify files on GitHub
        ↓
GitHub Actions runs
        ↓
build_site.py auto-generates index
        ↓
GitHub Pages deployment
        ↓
Verify live URL
```

---

# 21. Definition of Done

一組 infographic 只有同時滿足以下條件才能宣告完成：

## 教材

- [ ] 原始內容已完整理解
- [ ] 重要概念未遺漏
- [ ] 數學內容正確
- [ ] 中英雙語

## HTML

- [ ] 16:9
- [ ] HTML5
- [ ] Canvas 原生繪製
- [ ] standalone
- [ ] 一張一 HTML
- [ ] 可 iframe
- [ ] 有需要時提供互動

## Layout audit

- [ ] 無文字互疊
- [ ] 無圖文互疊
- [ ] 無公式溢出
- [ ] 無 canvas clipping
- [ ] slider min/max 已測
- [ ] button states 已測
- [ ] 展開狀態已測
- [ ] 畫面沒有顯示 literal `\n`

## GitHub

- [ ] 放在正確 course/topic
- [ ] commit 到 main
- [ ] 不破壞其他檔案
- [ ] GitHub 目錄重新讀取確認
- [ ] 檔案數量正確

## Pages

- [ ] Actions trigger
- [ ] build_site.py 可掃描
- [ ] topic 出現在自動 index
- [ ] live URL 可以開啟

---

# 22. 本專案目前已使用的 Topic 範例

PR115：

```text
courses/PR115/
├── MaximumLikelihoodEstimation/
├── MaximumPosterioriEstimation/
└── BayesInference/
```

未來新增知識點請使用相同模式：

```text
courses/PR115/<NewTopic>/
```

---

# 23. Agent 回覆使用者時應報告的資訊

完成 GitHub 推送後，回覆至少包含：

1. branch
2. topic path
3. HTML 數量
4. commit SHA
5. GitHub Pages URL 規則
6. 是否完成 post-push verification

如果某一步沒有成功，不可假裝完成。

---

# 24. 核心原則

本專案的最高優先順序：

> 教學正確性 > 可理解性 > 互動價值 > 視覺美觀 > 頁數少

以及：

> 不要為了塞進一頁而刪內容。

> 不要為了視覺漂亮而犧牲數學正確性。

> 不要把 Canvas 當圖片容器。

> 完成後一定要稽核。

> 推送後一定要驗證。