# workflow.md — InfographicsCreation End-to-End Workflow

> 本文件定義本儲存庫的「任務編排層（orchestration layer）」。
>
> `agents.md` 繼續作為技術規格、製作細節、稽核規則與已知踩坑的主要來源；本文件不取代 `agents.md`，而是規定一個任務如何從輸入一路執行到交付、驗收與發布。

---

# 0. Workflow 定位

本專案採用：

> **One Entry Point · One SOP · One Execution Chain**

使用者不需要自行在 ChatGPT、Work、Codex 之間拆解任務，也不需要人工搬運上下文。

正常情況下，以 **Work 作為主要 orchestrator**，依本文件完成整條流程：

```text
User
  ↓
Work
  ↓
workflow.md
  ↓
agents.md
  ↓
Source Understanding
  ↓
Production
  ↓
Audit
  ↓
Artifact Delivery
  ↓
Approval Gate
  ↓
GitHub Publish
  ↓
Deployment Verification
```

核心原則：

1. 使用者只交辦一次。
2. Agent 自行依 SOP 執行必要步驟。
3. 不要求使用者手動切換到其他工具或模式。
4. 任務若涉及 repository、browser、files、GitHub 等技術操作，由目前可用的執行能力完成。
5. 只有在現有環境確實缺少必要能力時，才向使用者說明阻塞點。

---

# 1. workflow.md 與 agents.md 的分工

## workflow.md

負責：

- 任務狀態
- 執行階段
- 階段順序
- 驗收點
- Repair loop
- Artifact delivery
- Approval gate
- Publication gate
- 完成條件

## agents.md

負責：

- HTML5 + Canvas 技術規格
- KaTeX / Math rendering
- Bilingual 規則
- Layout audit
- Formula audit
- Browser render audit
- GitHub 寫入方式
- GitHub Pages
- 已知 failure modes
- 踩坑與修正 SOP

若兩份文件內容有衝突：

> **技術實作細節以 agents.md 為準；任務階段與發布控制以 workflow.md 為準。**

---

# 2. 標準使用方式

使用者最簡單的交辦方式：

```text
依照 workflow.md 與 agents.md 處理這個教材 URL。
先不要推送，完成稽核後打包 ZIP 給我。
```

或：

```text
依照 workflow.md 執行。
完成後直接發布到 GitHub Pages。
```

Agent 不應重複詢問已由 repo 規範決定的事項，例如：

- 是否 16:9
- 是否使用 Canvas
- 是否一張一 HTML
- 是否做 Formula Audit
- 是否做 Layout Audit
- 是否做 Browser Render Audit
- GitHub repository
- main branch
- Topic 目錄命名規則

只有真正缺少任務必要資訊時才詢問。

---

# 3. 任務狀態

每個任務至少維護下列狀態：

```text
TASK_SOURCE
COURSE_CODE
TOPIC_NAME
PUBLISH_ALLOWED
CURRENT_PHASE
ARTIFACT_VERSION
AUDIT_STATUS
GITHUB_STATUS
DEPLOY_STATUS
```

其中：

## PUBLISH_ALLOWED

若使用者說：

```text
先不要推送
先給我看
先打包 ZIP
不要發布
```

則：

```text
PUBLISH_ALLOWED = false
```

任務只能執行到 Artifact Delivery / Approval Gate。

若使用者明確說：

```text
推送
發布
完成後直接上 GitHub
```

才可：

```text
PUBLISH_ALLOWED = true
```

---

# 4. End-to-End State Machine

標準任務必須依照以下狀態執行：

```text
PHASE 1   Intake
    ↓
PHASE 2   Source Understanding
    ↓
PHASE 3   Knowledge Decomposition
    ↓
PHASE 4   Production Plan
    ↓
PHASE 5   HTML Production
    ↓
PHASE 6   Source / Formula Audit
    ↓
PHASE 7   Browser Render Audit
    ↓
PHASE 8   Repair Loop
    ↓
PHASE 9   Artifact Delivery
    ↓
PHASE 10  Approval Gate
    ↓
PHASE 11  GitHub Publication
    ↓
PHASE 12  Deployment Verification
    ↓
DONE
```

原則：

> 前一個 mandatory phase 未通過，不得直接跳到後一個 phase。

---

# 5. PHASE 1 — Intake

## 5.1 接受的輸入

- 教材 URL
- GitHub URL
- HTML
- PDF
- Markdown
- 純文字
- 特定知識點
- URL fragment / anchor，例如 `#kp10`
- 已存在的 infographic / HTML 修正任務

## 5.2 Intake 必須解析

Agent 必須確認：

```text
來源是什麼？
目標知識點是什麼？
課程代號是否已知？
是否已有 topic？
是否允許發布？
是否為新製作或修正任務？
```

若 COURSE_CODE、TOPIC_NAME 已可從上下文或 repo 結構確定，不要重複詢問。

---

# 6. PHASE 2 — Source Understanding

收到教材來源後，不得立即開始畫 infographic。

必須先：

1. 讀取完整目標內容。
2. 找到指定 anchor / KP。
3. 讀必要上下文。
4. 識別：
   - 背景問題
   - 核心概念
   - 數學定義
   - 推導
   - 直覺
   - 例子
   - 常見誤解
   - 互動機會
   - 總結
5. 確認內容是否適合拆成多張 infographic。

最低知識結構：

```text
WHY
 ↓
WHAT
 ↓
HOW
 ↓
INTUITION
 ↓
EXAMPLE
 ↓
PITFALL
 ↓
INTERACTION
 ↓
SUMMARY
```

禁止只把原文摘要後排版。

---

# 7. PHASE 3 — Knowledge Decomposition

Agent 必須把教材拆成清楚的認知任務。

每一張 infographic 應回答一個主要問題，例如：

```text
為什麼需要這個方法？
核心公式是什麼？
公式每一項代表什麼？
幾何直覺是什麼？
某參數改變會發生什麼？
常見錯誤觀念是什麼？
```

拆頁原則：

> **One infographic = One cognitive task = One standalone HTML**

不得為了減少頁數而犧牲完整性。

---

# 8. PHASE 4 — Production Plan

正式製作前建立檔案規劃。

例如：

```text
01-intuition.html
02-definition.html
03-formula.html
04-derivation.html
05-interactive-example.html
06-misconceptions.html
07-summary.html
```

每一頁至少定義：

- 教學目的
- 視覺骨架
- 主要公式
- 互動方式
- 關鍵文字
- 預期 audit states

若某頁不需要互動，不應為了「有互動」硬加無教學價值的按鈕。

---

# 9. PHASE 5 — HTML Production

技術實作遵循 `agents.md`。

預設：

```text
HTML5
JavaScript
Canvas
1600 × 900
16:9
Traditional Chinese + English
Standalone
iframe-friendly
```

正式數學：

```text
KaTeX
```

概念圖、資料圖與互動：

```text
Canvas
```

核心公式不得用 Unicode / fillText 粗略替代。

若已有 `wrapCenter()` 等標準 helper，必須優先使用。

---

# 10. PHASE 6 — Source / Formula Audit

這一階段先從 source 層確認結構性錯誤。

## 10.1 Source Audit

至少檢查：

- logical coordinate 是否一致
- math layer scaling
- ResizeObserver
- transform-origin
- center anchor
- wrap width
- literal `\n`
- dynamic state
- overflow 風險

## 10.2 Formula Source Audit

依 `agents.md` 檢查：

- fraction
- subscript / superscript
- hat / bar
- sum / product
- integral
- argmax / argmin
- partial derivative
- matrix
- vector notation

特別檢查：

```text
String.raw
```

在 `String.raw` 中，TeX command 原則上應是單一反斜線：

```javascript
String.raw`\hat{p}(x)\approx\frac{1}{b}`
```

不得因多層 generator escaping 產生錯誤最終 HTML source。

Audit 必須看：

> **最終 HTML source**

不能只看產生 HTML 的 Python / JavaScript generator。

---

# 11. PHASE 7 — Browser Render Audit

這是 mandatory phase。

不能只做：

```text
source looks correct
```

必須執行：

```text
HTML
 ↓
real browser render
 ↓
screenshot / visual inspection
```

## 11.1 每頁至少檢查

- 初始狀態

## 11.2 互動頁另外檢查

- slider min
- slider typical
- slider max
- 每個 button mode
- 展開 / 收合
- Step 1 → final
- quiz unanswered
- quiz answered
- 中文 / English（若有切換）

## 11.3 Render Audit 必查

- 文字 ↔ 文字
- 文字 ↔ 公式
- 文字 ↔ 圖形
- 文字 ↔ button
- 文字 ↔ slider
- 公式 ↔ 圖形
- legend ↔ plot
- caption ↔ panel
- left / right clipping
- top / bottom clipping
- overflow
- responsive drift

若畫面出現本應是 TeX command 的：

```text
hat
frac
cdot
approx
theta
sigma
sum
```

則 Formula Audit 直接 FAIL。

---

# 12. PHASE 8 — Repair Loop

任何 audit 失敗都進入 Repair Loop：

```text
FAIL
 ↓
identify root cause
 ↓
modify source
 ↓
render again
 ↓
audit again
```

直到：

```text
PASS
```

禁止：

```text
改了 source
↓
理論上應該好了
↓
直接宣告完成
```

---

# 13. Root-Cause First Policy

遇到跑位或公式問題時，先分類。

## Structural problem

特徵：

- viewport 改變才漂移
- 多個公式一起漂
- Canvas 正確、DOM overlay 錯

優先檢查：

```text
logical coordinate
scale
ResizeObserver
transform-origin
```

## Local problem

特徵：

- 只有某一 label / caption 錯
- 不管 viewport 都固定偏左或偏右

優先檢查：

```text
x/y anchor
textAlign
wrap width
padding
offset
```

不要用大量 x/y micro-adjustment 補 structural bug。

---

# 14. PHASE 9 — Artifact Delivery

所有可下載成品採版本化輸出。

第一次：

```text
topic_v1/
topic_v1.zip
```

修改後：

```text
topic_v2/
topic_v2.zip
```

再次修改：

```text
topic_v3/
topic_v3.zip
```

原因：

> conversation artifact 可能是 immutable snapshot。

因此不要假設覆寫同一路徑後，使用者一定會下載到新內容。

---

# 15. Artifact Verification

提供下載連結前必須：

1. 確認新路徑存在。
2. 讀回新 HTML。
3. 確認修正內容確實存在。
4. 檢查 ZIP 內容。
5. 確認 ZIP 指向新版本目錄。
6. 使用新的 artifact path / file reference 交付。

禁止重新引用舊 snapshot 的下載連結。

---

# 16. PHASE 10 — Approval Gate

若：

```text
PUBLISH_ALLOWED = false
```

則在此停止。

回報至少包含：

- HTML 數量
- Topic
- Audit 結果
- 主要修正事項
- ZIP
- 尚未發布

等待使用者明確指令：

```text
推送
發布
```

才可進入 PHASE 11。

若：

```text
PUBLISH_ALLOWED = true
```

則直接進入 GitHub Publication。

---

# 17. PHASE 11 — GitHub Publication

目標 repository：

```text
ndhuccc/InfographicsCreation
```

Branch：

```text
main
```

Topic path：

```text
courses/<COURSE_CODE>/<TOPIC>/
```

GitHub 寫入方式遵循 `agents.md`。

推薦 Git data：

```text
create_blob
→ create_tree
→ create_commit
→ update_ref(main)
```

正常情況：

```text
force = false
```

---

# 18. Repository Verification

commit 成功不等於完成。

推送後必須重新讀取：

```text
courses/<COURSE>/<TOPIC>?ref=main
```

確認：

- expected file count
- actual file count
- filenames
- path
- SHA
- branch
- content（必要時抽查）

---

# 19. PHASE 12 — Deployment Verification

GitHub repository 更新後，還必須驗證 Pages deployment。

流程：

```text
main updated
 ↓
Deploy Pages workflow exists
 ↓
workflow head_sha correct
 ↓
workflow completed
 ↓
conclusion = success
 ↓
live URL checked
```

不能假設：

```text
update_ref success
=
Pages deployed
```

若 Git object API 更新後沒有 workflow run，依 `agents.md` 的已知問題與 trigger 策略處理。

---

# 20. Work-first Routing Policy

本專案預設：

> **Work 是主要 orchestrator。**

使用者不應被要求把任務手動拆成：

```text
ChatGPT task
→ Codex task
→ Work task
```

對使用者而言，一個任務就是一條 workflow。

## 一般情況

Work 直接負責：

- 教材理解
- 規劃
- 檔案處理
- HTML production
- Browser audit
- GitHub
- 部署驗證

## Repo-heavy 情況

即使涉及：

- 搜尋大量檔案
- 修改 HTML / Markdown
- scripts
- repo-wide audit
- commit

也不要求使用者人工切換工具。

若底層執行環境使用不同專門能力，這是內部實作選擇，不應增加使用者操作負擔。

---

# 21. Interruption / Resume Policy

若任務中斷，Agent 恢復時應先確認：

```text
CURRENT_PHASE
last successful output
artifact version
GitHub status
deployment status
```

然後從最後一個未完成 phase 繼續。

禁止從頭重做造成：

- 重複 artifact
- 重複 commit
- 重複 Pages trigger
- 使用舊版本覆蓋新版本

---

# 22. Failure Reporting

如果某一步失敗，回報必須明確區分：

```text
Source failure
Production failure
Formula failure
Render failure
Artifact failure
GitHub failure
Actions failure
Pages failure
```

不可只說：

```text
失敗了
```

也不可把：

```text
artifact read-only
```

誤判成：

```text
HTML 修正失敗
```

---

# 23. Definition of Done

只有以下條件全部滿足，才可宣告「完成」。

## Content

- [ ] 教材已完整理解
- [ ] 重要概念未遺漏
- [ ] 數學正確
- [ ] 中英雙語符合教材需求

## Production

- [ ] 一張 infographic = 一個 HTML
- [ ] HTML5
- [ ] Canvas 原生繪製
- [ ] 正式公式依 agents.md 正確渲染
- [ ] standalone
- [ ] iframe-friendly
- [ ] 需要時具備有教學價值的互動

## Formula

- [ ] 分數 / 上下標 / hat / bar 正確
- [ ] sum / product / integral / argmax 正確
- [ ] 無 raw TeX command 外露
- [ ] 無不必要的 String.raw double escaping
- [ ] 無 formula overflow
- [ ] 動態公式狀態已檢查

## Layout

- [ ] 無文字互疊
- [ ] 無圖文互疊
- [ ] 無公式互疊
- [ ] 無 clipping
- [ ] 無 overflow
- [ ] center anchor 正確
- [ ] responsive / iframe 狀態正確

## Render

- [ ] 實際 browser render 已完成
- [ ] 代表性互動狀態已檢查
- [ ] screenshot / visual inspection 已完成
- [ ] FAIL 狀態已 repair 並重新 render

## Artifact

- [ ] 使用 versioned output
- [ ] 使用 versioned ZIP
- [ ] 新檔已讀回確認
- [ ] 新 artifact link 未引用舊 snapshot

## GitHub

僅在已批准發布時：

- [ ] 正確 course/topic
- [ ] main 已更新
- [ ] repo 重新讀取驗證
- [ ] 檔案數量正確
- [ ] SHA 正確

## Pages

僅在已批准發布時：

- [ ] Deploy Pages run 存在
- [ ] head_sha 正確
- [ ] workflow success
- [ ] live URL 可開啟
- [ ] live URL 顯示最新版本

---

# 24. 使用者應看到的最簡流程

理想使用體驗：

## Step A

使用者：

```text
依 workflow.md 處理這頁。
先不要推送。
```

Agent：

```text
讀教材
→ 拆知識
→ 製作
→ Formula Audit
→ Browser Render Audit
→ Repair Loop
→ 打包 ZIP
```

回覆：

```text
已完成 N 個 HTML。
Audit 通過。
尚未推送。
以下為 ZIP。
```

## Step B

使用者：

```text
推送
```

Agent：

```text
GitHub Publication
→ Repository Verification
→ Actions Verification
→ Pages Verification
```

回覆：

```text
branch
topic path
file count
commit SHA
Pages URL
post-push verification
```

---

# 25. 最終原則

本 workflow 的最高目標不是增加流程，而是：

> **讓使用者只下達一次任務，Agent 自動完成所有應做的步驟。**

因此：

> 不要把工具選擇轉嫁給使用者。

> 不要跳過 mandatory audit。

> 不要把 source-code correctness 當成 browser-render correctness。

> 不要把 commit success 當成 deployment success。

> 不要覆寫已 surfaced 的 artifact 而假設使用者會拿到新版本。

> 不要未經使用者允許就跨過 Approval Gate 發布。

> 技術細節依 agents.md；一條龍任務執行依 workflow.md。
