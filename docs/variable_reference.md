# 變數對照表

5 個主要資料檔的欄位說明。回歸分析以這份為準。

---

## 1. `data/templates/events_master.csv` — 事件清單（每事件 1 列，共 165 列）

| 欄位 | 中文意思 | 用法 |
|---|---|---|
| `event_id` | 事件唯一 ID | join key |
| `company` | 經紀公司 | HYBE / SM / JYP / YG |
| `ticker` | 股票代號 | 352820.KS / 041510.KQ / 035900.KQ / 122870.KQ |
| `group` | 團體名 | 11 個團體 |
| `member` | 點名成員（如有） | 個人事件才填，團體事件留空 |
| `event_category` | **事件類型** | **回歸用，做 dummy variables** |
| `event_subtype` | 細分類 | 參考用 |
| `event_title_en/zh/ko` | 三語事件標題 | 報告用 |
| `start_date` | 事件起始日 | event window 起點 |
| `peak_date` | 高峰日 | 通常 = start_date |
| `end_date` | 事件結束日 | event window 終點 |
| `duration_days` | 持續天數 | end − start |
| `event_window_before_days` | 事件前觀察窗（天數）| 元資料，目前 panel 未使用 |
| `event_window_after_days` | 事件後觀察窗（天數）| 元資料 |
| `sentiment_expected` | 預期情緒 | ⚠️ **回歸不要用，主觀標註** |
| `severity_score` | 嚴重度 1-5 | ⚠️ **回歸不要用，主觀標註** |
| `source_level` | 資料來源等級 | A_official / B_korean_news / B_media |
| `official_source_url` | 官方來源連結 | 文件追蹤 |
| `naver_source_url` | Naver 來源連結 | 文件追蹤 |
| `notes` | 備註 | 自由文字 |
| `collector` | 紀錄者 | 內部追蹤 |
| `status` | 狀態 | complete / completed |

---

## 2. `data/final/traffic_daily.csv` — 主要分析 panel（每事件每天 1 列，共 2,470 列）

| 欄位 | 中文意思 | 來源 / 用法 |
|---|---|---|
| `event_id` | 事件 ID | join key |
| `date` | 日期 (YYYY-MM-DD) | join key |
| `naver_news_count` | 該日 Naver 新聞文章數 | Naver Search API (news) |
| `naver_blog_count` | 該日 Naver Blog 貼文數 | Naver Search API (blog) |
| `naver_datalab_score` | 該日 Naver 搜尋指數 0-100 | Naver DataLab API（事件內相對值）|
| `google_trends_score` | 該日 Google Trends 指數 0-100 | pytrends（53/165 事件 daily，其餘週快照 forward-fill）|
| `youtube_views` | 影片累計觀看數 | ⚠️ **0，未抓**。建議忽略 |
| `youtube_comments` | 影片累計留言數 | ⚠️ 同上 |
| `youtube_likes` | 影片累計按讚數 | ⚠️ 同上 |
| `instagram_followers` | 該團體當下 IG 追蹤數 | 從 `group_weights` join（group-level 常數）|
| `traffic_total_raw` | 4 個 daily 訊號加總 | naver_news + naver_blog + naver_datalab + google_trends |
| `traffic_total_normalized` | traffic_total_raw 標準化 | 除以全 panel 最大值 |
| `data_quality` | 該列品質標籤 | "ok" / "missing_traffic" |

**核心 X 變數 (media_attention)**：用 `traffic_total_raw`，或自己挑 4 個 daily 訊號其中幾個組合。

---

## 3. `data/final/stock_daily.csv` — 股價資料（Y 變數來源）

| 欄位 | 中文意思 |
|---|---|
| `date` | 交易日 |
| `company` | HYBE / SM / JYP / YG |
| `ticker` | 股票代號 |
| `open` / `high` / `low` / `close` | 開高低收 |
| `adj_close` | 調整後收盤 |
| `volume` | 成交量 |
| `daily_return` | 當日報酬率 |

**Y 變數 (AR)**：用 `daily_return` 跟 market index 做 market model 估 abnormal return。

---

## 4. `data/weights/group_weights.csv` — 團體層級控制變數（11 個團體各 1 列）

| 欄位 | 中文意思 | 用法 |
|---|---|---|
| `company` | 所屬公司 | join key |
| `group` | 團體名 | join key |
| `youtube_channel_subscribers` | YT 訂閱數 | 個別指標 |
| `youtube_channel_views` | YT 頻道總觀看數 | 個別指標 |
| `youtube_channel_videos` | YT 上傳影片總數 | 個別指標 |
| `instagram_followers` | IG 追蹤數 | 個別指標 |
| `spotify_monthly_listeners` | Spotify 月聽眾 | 個別指標 |
| `*_z` 欄位 | 上述指標的 z-score | 個別指標標準化版本 |
| `fanbase_weight` | **粉絲基礎權重** | **回歸核心：z-score 平均值，當互動項 `media × fanbase_weight`** |
| `weight_method` | 權重計算方式說明 | metadata |

---

## 5. `data/weights/company_weights.csv` — 公司層級控制變數（4 家公司各 1 列）

| 欄位 | 中文意思 | 用法 |
|---|---|---|
| `company` | 公司名 | join key |
| `ticker` | 股票代號 | join key |
| `market_cap` | 市值 (KRW) | 控制變數原始值 |
| `revenue` | 年營收 (KRW) | 參考用 |
| `company_scale_weight` | **公司規模權重** | **回歸控制變數：market_cap 的 z-score** |
| `source_date` | 資料抓取日 | metadata |
| `source_url` | 資料來源 | Yahoo Finance |
| `notes` | 備註 | metadata |

---

## 回歸用變數一覽（精簡版）

| 角色 | 變數 | 檔案 | 欄位 |
|---|---|---|---|
| **Y** | abnormal return AR | stock_daily.csv | 用 daily_return 算 |
| **X1** | media_attention | traffic_daily.csv | traffic_total_raw |
| **X2 (核心互動)** | × fanbase_weight | group_weights.csv | fanbase_weight |
| **X3 (事件類別)** | event_category dummies | events_master.csv | event_category |
| **X4 (公司控制)** | market_cap | company_weights.csv | company_scale_weight |

**不要用**：`sentiment_expected`、`severity_score`、`youtube_*`（在 traffic_daily.csv 內的）
