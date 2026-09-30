# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案目的

讓使用者上傳以 HTML5 和 Canvas 撰寫的 HTML 程式,作為課程教學使用,並透過 GitHub Pages 公開展示。GitHub Pages 只提供靜態託管,所以上傳內容必須是純前端(HTML/CSS/JS/Canvas)。

## 目錄與建置

- `courses/<課程名稱>/**/*.html`:每個課程一個目錄,存放該課程的 HTML 展示檔(圖片、JS、CSS 等資源放在同一課程目錄下)。目錄名稱即索引頁上的課程標題;每個 HTML 的 `<title>` 即展示標題(沒有則用檔名)。
- `scripts/build_site.py`:唯一的建置步驟(僅用 Python 標準函式庫)。讀取 `courses/`,輸出到 `_site/`:複製原檔、為每個 HTML 產生 `<名稱>.src.html` 原始碼頁,並產生 `index.html` 索引頁。`index.html` 是產生物,不要手動編輯或提交(`_site/` 已被 gitignore)。
- 本機預覽:`python3 scripts/build_site.py && python3 -m http.server -d _site`
- 部署:`.github/workflows/pages.yml` 在推送到 `main` 時執行建置並用 GitHub Actions 部署到 Pages(選 Actions 而非分支發佈,是因為索引頁需要在建置時自動產生)。儲存庫設定中 Pages 的 Source 必須設為 "GitHub Actions"。

目前課程:`PR115`、`IDL115`(索引頁會顯示空的課程目錄)。

新增課程或展示檔只需放進 `courses/`,索引頁會自動更新;修改索引外觀請改 `scripts/build_site.py`。
