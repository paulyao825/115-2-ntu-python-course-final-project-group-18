# 資料稽核報告

最後更新：2026-05-28 session 完成後

---

## 完整、合理的部分

### `events_master.csv` — 事件 metadata

| 項目 | 狀況 |
|---|---|
| 事件總數 | **165 筆** |
| 公司分佈 | HYBE 60、SM 45、JYP 30、YG 30 |
| 團體分佈 | 11 個團體各 15 筆（TWICE、aespa、BLACKPINK、NewJeans、LE SSERAFIM、SEVENTEEN、BTS、Stray Kids、NCT、EXO、BIGBANG） |
| 事件類型 | concert 47、PR_crisis 33、activity 30、contract_member 25、comeback 21、dating 9 |
| 時間範圍 | 2021-02-27 ~ 2026-01-01（5 年） |

### `traffic_daily.csv` — 主分析 panel

| 欄位 | 覆蓋率 | 判讀 |
|---|---|---|
| `event_id × date` panel | 2,470 列 = 165 事件 × ~15 天 | 結構正確 |
| `instagram_followers` | 100% | 從 PR #8 group_instagram_weights 自動 join |

### 整體 attention 訊號覆蓋

- **61.3%** 的 event-day 至少有一個 attention 訊號
- **157/165** 事件有資料（只有 8 個完全沒訊號）
- **127/165** 事件有 5 天以上資料
- **71/165** 事件有 10 天以上資料

---

## 空缺但「正常」的部分

| 欄位 | 缺值 | 為什麼正常 |
|---|---|---|
| `events_master.member` | 84/165 (51%) | 只有「點名成員」的事件才填，團體事件留空合理 |
| `events_master.naver_source_url` | 90/165 (54%) | 不影響分析，文件追蹤用 |
| `naver_news_count` | 72% 是 0 | 一個事件 window 內，新聞集中在事件當天前後 1-3 天 |
| `naver_blog_count` | 68% 是 0 | 同上，Blog 文章更少 |
| `google_trends_score` | 80% 是 0 | 53/165 事件有 daily 資料，其餘事件搜尋量太低 Google 直接回空 |
| `naver_datalab_score` | 85% 是 0 | 韓國搜尋指數對非熱門事件門檻較高 |
| 8 個事件 0 訊號 | 5% | 多為內部成員事件（軍人退伍、轉所屬公司），媒體討論本來就少 |

---

## 真正的問題（需要處理）

### 1. 股價資料還沒抓
- `scripts/collect_stock.py` 已寫好但**從未執行**
- 沒有 `data/final/stock_daily.csv`
- 這是回歸分析的 Y 變數，必須補

### 2. YouTube 流量資料還沒抓
- `scripts/collect_youtube.py` 寫好但**從未執行**
- traffic_daily.csv 裡 youtube_views/likes/comments 全部是 0
- 之前討論「累計到今日當代理」，要跑這個 script 才有資料
- 需要 YouTube Data API v3 key 在 `.env` 裡

### 3. Naver DataLab 覆蓋偏低 (14.6%)
- 問題：`naver_query` 太具體（例：「방탄소년단 정한 군 입대」），DataLab 對低搜尋量直接回空
- 改進方法：未來可改用「團名 + 簡短關鍵字」（例：「방탄소년단 정한」）
- 不阻擋現在分析，列為 future work

---

## 補的建議順序

```bash
# 1. 抓股價（Y 變數，必抓）
python scripts/collect_stock.py

# 2. 抓 YouTube（要先在 .env 加 YOUTUBE_API_KEY）
python scripts/collect_youtube.py

# 3. 重 build panel
python scripts/build_daily_traffic.py
python scripts/validate_dataset.py
```
