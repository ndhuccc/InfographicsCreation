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

## 4.3 數學公式渲染：Canvas + KaTeX Hybrid Rendering

本專案預設採用：

> **Canvas 畫概念與圖形，KaTeX 排核心數學公式。**

不要再要求所有數學公式都用 Canvas `fillText()` 模擬。

### 分工原則

Canvas 負責：

- 背景
- panel
- 箭頭
- 節點
- 散點
- Gaussian curve
- bar / axis
- slider
- button
- animation
- diagram labels
- 簡短單一符號或數值

KaTeX 負責：

- 分數
- 上下標
- `\hat{}`
- `\bar{}`
- `\sum`
- `\prod`
- `\int`
- `\arg\max`
- 偏微分
- 矩陣
- 多行推導
- piecewise function
- aligned equations
- 任何核心教學公式

### 推薦 DOM 結構

```html
<div class="stage">
  <canvas id="canvas" width="1600" height="900"></canvas>
  <div id="math-layer"></div>
</div>
```

Canvas 與 `math-layer` 必須共用同一個 1600×900 logical coordinate system。

`math-layer` 應：

```css
#math-layer {
  position: absolute;
  inset: 0;
  pointer-events: none;
}
.formula {
  position: absolute;
  transform-origin: top left;
}
```

### KaTeX 使用方式

建議使用 KaTeX，因為：

- 速度快
- 數學排版品質佳
- 適合大量公式
- 適合互動式頁面
- 公式不必隨 Canvas 每一幀重畫

範例：

```javascript
katex.render(
  String.raw`\hat{\sigma}_{\mathrm{ML}}^2
  =
  \frac{1}{N}
  \sum_{k=1}^{N}(x_k-\mu)^2`,
  element,
  {
    displayMode: true,
    throwOnError: false
  }
);
```

### 公式 helper

推薦建立共用 helper，而不是到處手寫 CSS：

```javascript
addFormula({
  id: "posterior",
  tex: String.raw`
    p(\theta\mid X)
    =
    \frac{
      p(X\mid\theta)p(\theta)
    }{
      \int p(X\mid\theta)p(\theta)\,d\theta
    }
  `,
  x: 300,
  y: 300,
  width: 1000,
  align: "center",
  fontSize: 34
});
```

### Formula rendering 分級規則

| 數學內容 | 建議渲染 |
|---|---|
| `N = 5`、簡短數值 | Canvas text |
| 單一 `μ`、`σ²`、`θ` label | Canvas 或 KaTeX |
| `\hat{\mu}_{MAP}` | KaTeX |
| 分數 | KaTeX |
| Summation / Product | KaTeX |
| Integral | KaTeX |
| argmax | KaTeX |
| Partial derivative | KaTeX |
| Matrix | KaTeX |
| 多行 derivation | KaTeX |
| Piecewise function | KaTeX |

核心原則：

> **正式數學公式禁止用 Unicode 字元拼湊來取代真正的 TeX 排版。**

例如不要把核心公式只寫成：

```text
μ̂_MAP = [ μ₀ + (σ²_μ/σ²) N x̄ ] / [ 1 + (σ²_μ/σ²) N ]
```

而應使用真正 LaTeX：

```latex
\hat{\mu}_{\mathrm{MAP}}
=
\frac{
\mu_0+
\frac{\sigma_\mu^2}{\sigma^2}N\bar{x}
}{
1+
\frac{\sigma_\mu^2}{\sigma^2}N
}
```

### MathJax 何時使用

KaTeX 為預設。

只有在：

- KaTeX 不支援需要的 LaTeX
- 需要非常複雜的 AMS notation
- 需要 MathJax SVG output

時才改用 MathJax。

不要在同一頁無必要地同時載入 KaTeX 與 MathJax。

### 動態公式更新

互動 slider 改變數值時：

- Canvas 可高頻 redraw
- KaTeX 只更新真正發生改變的公式
- 不要每個 animation frame 都重新 typeset 所有公式

---

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

## 8.4 Formula Audit（MANDATORY）

只要頁面含有核心數學公式，就必須額外做 Formula Audit。

檢查：

- 分數線是否完整且清楚
- 上標 / 下標位置是否正確
- `\hat{}` 是否真正覆蓋正確變數
- `\bar{}` 是否位置正確
- summation 上下限是否正確
- integral 上下限與微分項 `d\theta` 是否存在
- `\arg\max`、`\arg\min` 的下標是否正確
- partial derivative 的分子分母是否正確
- matrix bracket 是否完整
- 括號大小是否合理
- 向量 / 矩陣粗體是否符合教材記號
- 公式是否超出 panel
- KaTeX DOM 是否與 Canvas 圖形、文字、slider、button 重疊
- 中文 / English 切換後公式位置是否仍安全
- slider min / max 時動態公式是否仍不 overflow
- browser zoom / responsive scaling 後是否仍對齊

核心公式若渲染失敗，不可退回用普通 Unicode 字串草率替代。

應先：

1. 修正 LaTeX
2. 調整 KaTeX font size
3. 調整公式容器 width
4. 改成 display mode
5. 拆成多行 aligned 公式
6. 必要時拆成另一張 infographic

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

# 18.5 Hybrid Canvas + KaTeX 常見踩坑與修正 SOP

這一節記錄實際在 Bayesian Inference infographic 重製時遇到的問題。後續 agent 若使用 Canvas + KaTeX hybrid rendering，必須優先檢查這些項目。

## 問題 A：瀏覽器縮放後，KaTeX 公式會相對 Canvas 漂移

### 症狀

- 初始畫面看起來正常。
- 改變瀏覽器視窗大小後：
  - Canvas 圖形位置仍然正確。
  - KaTeX 公式卻往左、右、上、下漂移。
- iframe 尺寸改變時也可能出現同樣問題。

### 根因

常見錯誤架構是：

```text
Canvas：使用 1600×900 logical coordinates，再由 CSS 自動縮放
KaTeX DOM：left/top 卻直接使用 browser CSS pixel
```

兩者不是同一個座標系。

例如 Canvas 的：

```javascript
ctx.fillText(..., 800, 400);
```

是 1600×900 logical coordinate；

但 KaTeX：

```css
left: 800px;
top: 400px;
```

是瀏覽器實際 CSS pixel。

當 viewport 不等於 1600×900 時，兩者就會分離。

### 正確做法：統一 Logical Coordinate System

Canvas 與 KaTeX 必須共享：

```text
1600 × 900 logical coordinate system
```

推薦架構：

```html
<div class="stage" id="stage">
  <canvas id="canvas" width="1600" height="900"></canvas>
  <div id="math-layer"></div>
</div>
```

其中 math layer 固定 logical size：

```css
#math-layer {
  position: absolute;
  left: 0;
  top: 0;
  width: 1600px;
  height: 900px;
  transform-origin: top left;
  pointer-events: none;
}
```

再根據 stage 實際顯示尺寸同步縮放：

```javascript
function syncMathLayer() {
  const r = stage.getBoundingClientRect();
  const sx = r.width / 1600;
  const sy = r.height / 900;

  mathLayer.style.transform =
    `scale(${sx}, ${sy})`;
}

new ResizeObserver(syncMathLayer).observe(stage);
window.addEventListener("resize", syncMathLayer);
```

這樣所有公式仍用 logical coordinate：

```javascript
addFormula({
  x: 800,
  y: 400,
  ...
});
```

但會和 Canvas 一起等比例縮放。

### 禁止做法

不要讓：

```text
Canvas logical coordinate
+
KaTeX browser pixel coordinate
```

混用。

若公式在改變瀏覽器大小時會漂移，第一個要檢查的不是 x/y 微調，而是：

> Canvas 與 DOM overlay 是否真的使用同一個 logical coordinate system。

---

## 問題 B：`wrap(..., 'center')` 文字仍然跑出卡片

### 症狀

- 卡片中的公式位置正確。
- 卡片底部說明文字卻往左或往右跑。
- 第一張卡片尤其容易跑到 Canvas 外面。
- 視窗大小改變後仍然錯，表示不是 responsive scaling 問題。

### 根因

Canvas 的：

```javascript
ctx.textAlign = "center";
```

代表傳入的 x 是「文字中心點」。

錯誤寫法：

```javascript
wrap(
  description,
  cardX + padding,
  y,
  width,
  ...,
  "center"
);
```

例如：

```javascript
wrap(a[1], x + 26, 475, 268, 30, 20, P.muted, 600, "center");
```

這裡雖然用了 center，但 x 仍是左側 padding，所以整段文字會以錯誤中心向兩側展開。

### 正確做法

如果 card width = 320：

```javascript
const cardCenterX = x + 160;

wrap(
  description,
  cardCenterX,
  475,
  268,
  30,
  20,
  P.muted,
  600,
  "center"
);
```

一般規則：

```text
textAlign = left   → x = left edge / padding position
textAlign = center → x = actual visual center
textAlign = right  → x = right edge
```

### Formula Audit 之外還要檢查文字 anchor

公式位置正確，不代表卡片內所有文字都正確。

每個 card / panel 應檢查：

- title x
- formula x
- caption x
- wrapped paragraph x

是否都遵循相同 anchor convention。

---

## 問題 C：只微調 KaTeX x/y 無法解決 responsive 漂移

### 症狀

Agent 看到公式偏移後，反覆：

```text
x - 10px
y + 5px
font-size - 2px
```

在某個 viewport 看起來好了，但換一個瀏覽器尺寸又壞掉。

### 根因

這是 structural bug，不是 local positioning bug。

### 修正順序

遇到公式漂移時必須依序：

1. 檢查 Canvas 與 math layer logical coordinate system。
2. 檢查 math layer 是否跟 stage 同比例縮放。
3. 檢查 transform-origin 是否為 top left。
4. 檢查 formula left/top 是否使用 logical coordinate。
5. 最後才做 1–5 px 的 visual baseline 微調。

不要反過來。

---

## 問題 D：KaTeX 公式在幾何上置中，但視覺上仍略高或略低

### 原因

KaTeX glyph 的 bounding box 與人眼感受到的 visual center 不完全相同。

例如：

- integral 很高
- fraction 有上下延伸
- hat / bar 會改變 visual top
- matrix bracket 會增加外框高度

### 建議做法

公式 helper 可支援：

```javascript
offsetX
offsetY
```

例如：

```javascript
addFormula({
  tex,
  x: 300,
  y: 400,
  width: 1000,
  align: "center",
  size: 32,
  offsetY: -2
});
```

但這只能做最後的 optical adjustment。

> offsetX / offsetY 不得拿來補救 coordinate-system 錯誤。

---

## 問題 E：生成後的 conversation artifact 可能是唯讀

### 症狀

已產生並上傳給使用者的 HTML，之後試圖原地修改：

```python
Path("/mnt/data/.../03-page.html").write_text(...)
```

可能得到：

```text
PermissionError: [Errno 13] Permission denied
```

### 原因

某些已 surfaced / uploaded 的 conversation artifacts 會被掛載成唯讀。

### 正確修正流程

不要一直 retry 原路徑。

應：

1. 建立新的可寫工作目錄。
2. 把原檔複製到新目錄。
3. 在新目錄修改。
4. 產生新版本檔名或 ZIP。
5. 再提供新的 artifact。

例如：

```text
kp11_bayesian_inference_infographics_katex_fixed/
        ↓ copy
kp11_bayesian_inference_infographics_katex_fixed_v2/
        ↓ edit
03-posterior-formula.html
```

或直接從 source generator 重新輸出到新目錄。

### Agent 回覆規則

遇到 PermissionError 時必須說明：

> 是 artifact 路徑唯讀，不是內容修正失敗。

不可誤判成 Python / HTML / GitHub 問題。

---

## 問題 F：版面稽核必須區分「結構性偏移」與「局部偏移」

當看到元素跑位時，依下列判斷：

### 結構性偏移

特徵：

- viewport 一變位置就變
- 多個 KaTeX 公式一起漂
- Canvas 正確、DOM overlay 不正確

優先修：

```text
coordinate system
scale
ResizeObserver
transform-origin
```

### 局部偏移

特徵：

- 只有某一個 label / caption 錯
- 不管 viewport 怎麼變，都固定往某方向偏
- 同一 card 內其他元素正常

優先修：

```text
x/y anchor
textAlign
wrap width
padding
formula offset
```

Agent 不可把兩者混為一談。

---

## 問題 G：修正了原始檔，但使用者下載到的仍然是舊版本

### 症狀

- 本地工作目錄中的 HTML 已經修改。
- Agent 重新提供「同一個路徑」或「同名 ZIP」給使用者。
- 使用者下載後打開，內容卻仍然是修改前版本。
- Agent 誤以為修正沒有生效。

### 根因

conversation artifact / uploaded artifact 可能是不可變 snapshot。

也就是：

```text
第一次 surface：
/mnt/data/topic/page.html
        ↓
artifact snapshot A
```

之後即使同一路徑檔案被修改：

```text
/mnt/data/topic/page.html
        ↓ modified
```

先前已 surfaced 的下載引用仍可能指向 snapshot A，而不是新的檔案內容。

同理，重新產生同名 ZIP 也不能假設使用者一定拿到新 snapshot。

### 正確做法：Versioned Artifact Output

任何已對使用者提供過下載連結的成品，後續修正版不要覆寫舊 artifact。

應建立新版本：

```text
topic_v1/
topic_v2/
topic_v3/
topic_v4/
```

或：

```text
topic.zip
topic_fixed.zip
topic_fixed_v2.zip
topic_v4.zip
```

推薦：

```text
maximum_likelihood_estimation_infographics_v4/
maximum_likelihood_estimation_infographics_v4.zip
```

### 交付前驗證

提供新下載連結前必須：

1. 確認新路徑確實存在。
2. 讀回新 HTML 的修正程式碼。
3. 確認 ZIP 內包含新版本目錄。
4. 使用新 artifact path / 新 file id surface 給使用者。
5. 不要再次引用舊 snapshot 的 sandbox link。

---

## 問題 H：只看原始碼「覺得座標正確」，但實際瀏覽器仍然跑位

### 症狀

- 靜態 code review 看起來：
  - x 在 panel 中心
  - width 看起來足夠
  - formula coordinate 合理
- 但使用者截圖仍看到：
  - paragraph 跑出 panel
  - footer 被裁切
  - label 超出 card
  - formula 與文字實際視覺間距不對

### 根因

程式碼稽核只能檢查「邏輯座標合理性」，不能完全取代瀏覽器真正的 typography/layout 結果。

Canvas 與 DOM 都可能受：

- 實際字型 metrics
- browser font fallback
- KaTeX glyph bounding box
- DPR / zoom
- CSS scaling
- font weight
- CJK 字寬

影響。

### 正確做法：Render Audit 是強制程序

完成一組 infographic 後，除了 code audit，還必須實際使用瀏覽器渲染代表性頁面。

最低要求：

```text
HTML source audit
        ↓
browser render
        ↓
screenshot / visual inspection
        ↓
fix
        ↓
render again
```

對使用者已回報有問題的頁面：

> 必須實際渲染確認後才可宣告修正成功。

不能只說：

> 「我已將 x 從 300 改成 800，所以應該好了。」

---

## 問題 I：置中段落應使用專用 `wrapCenter()`，避免 anchor 再次誤用

### 問題背景

多次出現：

```javascript
wrap(text, cardX + padding, ..., "center");
```

這種錯誤。

即使 agent 知道 center anchor 規則，手動傳參數仍很容易再次寫錯。

### 標準解法

建立專用 helper：

```javascript
function wrapCenter(
  text,
  centerX,
  y,
  maxWidth,
  lineHeight = 34,
  fontSize = 24,
  color = P.muted,
  weight = 550
) {
  return wrap(
    text,
    centerX,
    y,
    maxWidth,
    lineHeight,
    fontSize,
    color,
    weight,
    "center"
  );
}
```

Card 中使用：

```javascript
wrapCenter(
  description,
  cardX + cardWidth / 2,
  textY,
  cardWidth - 2 * padding,
  ...
);
```

Panel 中使用：

```javascript
wrapCenter(
  paragraph,
  panelX + panelWidth / 2,
  textY,
  panelWidth - 2 * padding,
  ...
);
```

### 稽核原則

後續 agent 應優先搜尋：

```text
wrap(..., 'center')
wrap(..., "center")
```

若專案已提供 `wrapCenter()`，則：

> 新頁面原則上不再直接呼叫 `wrap(..., 'center')`。

這可以從 API 層降低 anchor 錯誤。

---

## 問題 K：`String.raw` 中 LaTeX 被過度跳脫（double-escaped）

### 症狀

公式原本應該是：

```latex
\hat{p}(x)\approx \frac{1}{b}\cdot\frac{k_N}{N}
```

但瀏覽器畫面卻出現：

```text
hatp(x)
approx
frac1b
cdot
frack_NN
```

或其他 TeX command 名稱直接變成可見文字。

### 根因

若 JavaScript 使用：

```javascript
String.raw`...`
```

則 LaTeX command 前只需要 **一個反斜線**。

錯誤：

```javascript
String.raw`\\hat{p}(x)\\approx \\frac{1}{b}\\cdot\\frac{k_N}{N}`
```

在 `String.raw` 裡，`\\hat` 代表實際字串中存在兩個反斜線。KaTeX 會把前面的 `\\` 解讀成 TeX 換行命令，後面的 `hat`、`frac`、`cdot` 就可能被當成普通字母或產生錯誤布局。

正確：

```javascript
String.raw`\hat{p}(x)\approx \frac{1}{b}\cdot\frac{k_N}{N}`
```

### 特別注意：多層字串生成

如果 HTML 是由 Python / JSON / JavaScript generator 產生，必須檢查的是：

> **最終輸出的 HTML source 裡，String.raw template literal 是否真的只有一個反斜線。**

不能只看 generator source，因為：

```text
Python escaping
→ JS source escaping
→ String.raw
→ KaTeX parser
```

中間任何一層都可能多 escape 一次。

### 強制 source audit

對所有 HTML 搜尋：

```text
String.raw`
```

再檢查其內容是否出現：

```text
\\hat
\\frac
\\sum
\\int
\\cdot
\\approx
\\theta
\\sigma
\\mu
\\mathcal
\\boldsymbol
```

若是在 `String.raw` 中，通常都代表 over-escaped。

例外只有真的需要 TeX 換行的 `\\`，但 infographic 單行公式通常不需要。

### Browser formula audit

實際渲染後，若公式區域出現以下可見文字，立即判定 Formula Audit 失敗：

- `hat`
- `frac`
- `cdot`
- `approx`
- `sum`
- `theta`
- `sigma`

前提是這些字原本應該是 TeX command，而不是教材文字。

### 建議自動檢查

可在 build/audit script 中掃描：

```python
re.search(r'String\.raw`[^\`]*\\\\[A-Za-z]', html)
```

或等價邏輯。

若命中，必須人工確認是否為真正需要的 TeX line break。

### 離線穩定方案

對完全靜態、核心且重要的公式，可以考慮：

```text
LaTeX
→ SVG
→ inline SVG
```

把公式直接嵌入 HTML，避免 CDN 載入或 runtime typesetting 問題。

但若使用 KaTeX，仍必須優先修正 TeX source，不可用 SVG 掩蓋錯誤的 source pipeline。

---

## 問題 J：Git object API 更新 main，不代表 GitHub Actions 一定已部署

### 症狀

- `create_blob → create_tree → create_commit → update_ref(main)` 成功。
- GitHub repository 中的新 HTML 內容已存在。
- 但 GitHub Pages 仍顯示舊版本。
- 查詢 Actions 時，最新 commit 沒有 workflow run。

### 原因

不同 connector / API mutation 對 GitHub push event 的觸發行為可能不同。

即使 branch ref 已更新，也不能只假設：

```text
update_ref success
=
GitHub Actions 已啟動
```

### 正確做法

GitHub push 後分兩層驗證：

#### Repository verification

確認：

- main HEAD
- file SHA
- file content

#### Deployment verification

再確認：

- Deploy Pages workflow run 是否存在
- workflow head_sha 是否對應最新 commit
- workflow status / conclusion
- Pages 是否已更新

如果 Git object API 更新後沒有 Actions run，需使用能產生正常 push event 的寫入方式做一個安全的 trigger commit，例如一般 Contents API 的小型檔案更新。

但不要建立大量無意義 trigger commits。

推薦在專案中保留明確的 rebuild trigger 策略。

---

## Hybrid Rendering Debug Checklist

若使用者回報「公式或文字跑位」，依序執行：

- [ ] 是否只有 KaTeX 漂移？
- [ ] 是否 viewport resize 才發生？
- [ ] math-layer 是否 1600×900 logical size？
- [ ] math-layer 是否跟 stage 同比例 scale？
- [ ] transform-origin 是否為 top left？
- [ ] formula left/top 是否為 logical coordinate？
- [ ] `textAlign="center"` 的 x 是否真的是 container center？
- [ ] 是否應改用 `wrapCenter()` 而不是直接 `wrap(...,'center')`？
- [ ] wrap() 的 max width 是否小於 card width？
- [ ] formula 是否只是 optical baseline 偏差？
- [ ] 是否只需 offsetY ±1~5px？
- [ ] 是否誤把 structural problem 當成 x/y micro-adjustment？
- [ ] 原 artifact 是否唯讀？若是，改在新工作目錄輸出。
- [ ] 是否正在覆寫曾經 surface 過的 artifact 路徑？若是，改用新版本目錄 / ZIP。
- [ ] 是否只做 code audit，尚未做 browser render audit？
- [ ] GitHub repo 是否已更新，但 Pages workflow 尚未部署？

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
Add KaTeX math layer for core formulas
        ↓
Add conceptual interaction
        ↓
Check bilingual labels
        ↓
Formula Audit
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
- [ ] Canvas + KaTeX hybrid rendering（有核心公式時）
- [ ] 核心公式未使用 Unicode / fillText 粗略模擬
- [ ] standalone
- [ ] 一張一 HTML
- [ ] 可 iframe
- [ ] 有需要時提供互動

## Formula audit

- [ ] 分數 / 上下標 / hat / bar 正確
- [ ] sum / product / integral / argmax 正確
- [ ] matrix / partial derivative 正確
- [ ] KaTeX 公式沒有 overflow
- [ ] KaTeX 與 Canvas 元素沒有 overlap
- [ ] 動態公式已測 slider min / max
- [ ] 中文 / English 狀態皆已檢查
- [ ] 所有 `String.raw` LaTeX 已檢查，不存在不必要的 double backslash
- [ ] 最終 HTML source 中 TeX command 前的反斜線數量正確
- [ ] 實際瀏覽器畫面沒有顯示 `hat` / `frac` / `cdot` / `approx` 等 raw TeX command 名稱
- [ ] generator source 與最終 HTML source 都已抽查，避免多層 escaping 造成 over-escape

## Layout audit

- [ ] 無文字互疊
- [ ] 無圖文互疊
- [ ] 無公式溢出
- [ ] 無 canvas clipping
- [ ] slider min/max 已測
- [ ] button states 已測
- [ ] 展開狀態已測
- [ ] 畫面沒有顯示 literal `\n`
- [ ] 所有置中 paragraph / caption 使用真實 container center
- [ ] 優先使用 `wrapCenter()`，避免直接手算 center anchor
- [ ] 至少對代表性頁面做 browser render audit
- [ ] 使用者回報有問題的頁面已實際渲染複查
- [ ] browser render 與 code audit 結果一致
- [ ] 不同 viewport / iframe 尺寸下 Canvas 與 KaTeX 不漂移

## Artifact delivery audit

- [ ] 修正版使用新的 versioned output directory
- [ ] 修正版 ZIP 使用新檔名，不覆寫舊 artifact snapshot
- [ ] 提供下載前已讀回新檔確認修正內容存在
- [ ] 新 artifact link 指向新 snapshot，而不是先前舊連結

## GitHub

- [ ] 放在正確 course/topic
- [ ] commit 到 main
- [ ] 不破壞其他檔案
- [ ] GitHub 目錄重新讀取確認
- [ ] 檔案數量正確

## Pages

- [ ] repository main HEAD 已更新
- [ ] GitHub 上 file SHA / content 已重新讀取確認
- [ ] Deploy Pages Actions run 確實存在
- [ ] workflow head_sha 對應最新要部署的 commit
- [ ] workflow 成功完成
- [ ] build_site.py 可掃描
- [ ] topic 出現在自動 index
- [ ] live URL 可以開啟
- [ ] live URL 顯示的是最新修正版，而不是舊 deployment

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