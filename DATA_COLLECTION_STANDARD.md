# K-pop 事件資料蒐集計畫書與標準

## 一、研究目標

本專案目標是建立一份可驗證、可重現、可供 Python 分析的 K-pop 事件資料集，後續用於分析：

```text
偶像事件 -> 社群／新聞熱度變化 -> 娛樂公司股價波動
```

資料集會以 CSV 作為 Python 分析格式，並以 GitHub 作為組員協作與版本管理方式。

## 二、研究範圍

### 時間範圍

固定使用：

```text
2021-01-01 至 2026-01-01
```

此範圍涵蓋疫情後 K-pop 全球化、巡演恢復、HYBE／SM／YG／JYP 主要市場事件，以及 2021 之後較完整的平台資料。

### 公司與團體

| 公司 | 團體 |
|---|---|
| JYP | TWICE |
| SM | aespa |
| YG | BLACKPINK |
| HYBE | NewJeans, LE SSERAFIM |

建議股票代號：

| 公司 | 股票代號 |
|---|---|
| JYP | 035900.KQ |
| SM | 041510.KQ |
| YG | 122870.KQ |
| HYBE | 352820.KS |

## 三、事件分類標準

原本六類事件保留，並補充四類，以避免漏掉對股價與討論度有明顯影響的事件。

| 分類代碼 | 中文說明 | 範例 |
|---|---|---|
| dating | 戀愛 | 戀愛謠言、承認、否認、分手 |
| concert | 演唱會 | 巡演公布、售票、完售、加場、巡演結束 |
| PR_crisis | 公關危機 | 犯罪、霸凌、抽菸、失言、破音、人設爭議 |
| activity | 商業／公開活動 | 代言、時裝周、機場、簽售、綜藝 |
| contract_member | 成員與合約 | 退團、續約、解約、合約糾紛 |
| comeback | 回歸與新歌 | 預告、MV、專輯、正式回歸 |
| military | 軍白期 | 入伍、退伍、完整體回歸 |
| health_hiatus | 健康與暫停活動 | 受傷、生病、心理健康、暫停活動、復出 |
| legal_dispute | 法律爭議 | 訴訟、假處分、公司與藝人法律爭議 |
| achievement | 重大成就 | Billboard、Melon、MAMA、銷量、YouTube、Spotify 紀錄 |

另外建立控制類別：

```text
market_confounder
```

此類不是偶像事件，而是用來記錄可能影響股價的外部因素，例如財報、整體股市大跌、公司併購、產業政策等。

## 四、事件收錄標準

一個事件必須符合至少一項：

1. 有 Naver News 或韓國主流媒體報導。
2. 有公司、藝人、官方 YouTube、Weverse、官方社群公告。
3. 在 Google Trends、Naver DataLab、YouTube 或新聞量上有明顯熱度。
4. 事件可合理對應到公司股價分析時間點。

本階段只負責女團事件資料。每個團體收錄：

```text
15 筆高影響事件
```

總資料量目標：

```text
75 筆事件
```

每家公司至少要有：

- 1 個正面事件
- 1 個負面事件
- 至少 3 種不同事件分類

## 五、事件日期定義

每筆事件需要三個日期：

| 欄位 | 定義 |
|---|---|
| start_date | 事件第一次公開出現、官方公布、新聞爆出或謠言開始的日期 |
| peak_date | 新聞量、搜尋量或社群討論最高的日期 |
| end_date | 討論明顯結束、活動結束、公司最後回應，或 peak 後 7 天無重大後續 |

若無法明確判斷結束日，預設事件窗為：

```text
start_date 前 3 天 至 start_date 後 14 天
```

`duration_days` 計算方式：

```text
end_date - start_date + 1
```

## 六、來源可信度標準

來源分成四級：

| 等級 | 類型 | 範例 |
|---|---|---|
| A_official | 官方來源 | 公司公告、官方 YouTube、官方 Instagram、Weverse、交易所公告 |
| B_korean_news | 韓國媒體 | Naver News、Yonhap、Daum、Korea Herald |
| C_platform_data | 平台數據 | Google Trends、Naver DataLab、YouTube API、Spotify |
| D_secondary | 次級資料 | Soompi、Wikipedia、粉絲整理、非官方帳號 |

每個事件至少要有：

```text
1 個 A_official 或 B_korean_news 來源
```

若只有 C 或 D 類來源，該事件狀態必須標記為：

```text
needs_review
```

## 七、CSV 資料表標準

需要維護以下 CSV：

1. `Events_Master`
2. `Traffic_Daily`
3. `Sources`
4. `Group_Weights`
5. `Company_Weights`
6. `Keyword_Dictionary`
7. `Collection_Log`
8. `Crawler_Run_Log`
9. `Data_Quality_Check`

目前主要檔案路徑：

```text
data/templates/events_master.csv
config/keywords.csv
data/final/traffic_daily.csv
data/final/data_quality_report.csv
```

### Events_Master

一列代表一個事件。必要欄位：

```text
event_id, company, ticker, group, member, event_category, event_subtype,
event_title_en, event_title_zh, event_title_ko, start_date, peak_date,
end_date, duration_days, event_window_before_days, event_window_after_days,
sentiment_expected, severity_score, source_level, official_source_url,
naver_source_url, notes, collector, status
```

### Traffic_Daily

一列代表某事件某一天的流量資料。必要欄位：

```text
event_id, date, naver_news_count, naver_blog_count, naver_datalab_score,
google_trends_score, youtube_views, youtube_comments, youtube_likes,
spotify_popularity, instagram_followers, other_social_count,
traffic_total_raw, traffic_total_normalized, data_quality
```

### Sources

一列代表一個來源：

```text
event_id, source_type, platform, title, url, published_date, language,
is_official, is_primary_evidence, summary, collector, checked_date
```

### Group_Weights

用來控制團體本身人氣：

```text
company, group, spotify_followers_or_popularity, youtube_channel_subscribers,
instagram_followers, weverse_members, bubble_proxy, album_sales_proxy,
fanbase_weight, source_date, source_url, notes
```

`fanbase_weight` 計算方式：

```text
可取得人氣指標標準化後的平均值
```

### Company_Weights

用來控制公司規模：

```text
company, ticker, market_cap, revenue, operating_income,
company_scale_weight, source_date, source_url, notes
```

`company_scale_weight` 建議使用：

```text
market_cap 標準化值
```

若 market cap 缺漏，可用 revenue 作為替代。

## 八、Python Web Crawler 計畫

Python crawler 的目的不是完全自動判斷所有事件，而是協助收集可重現的資料。

Crawler 應完成：

1. 讀取 `config/keywords.csv`
2. 根據每筆事件關鍵字查詢 Naver、Google Trends、YouTube
3. 輸出乾淨 CSV
4. 記錄 crawler 執行狀態
5. 讓資料可以重新執行與驗證

### 腳本分工

| 腳本 | 功能 |
|---|---|
| `collect_naver.py` | 使用 Naver Search API 收集新聞／部落格資料 |
| `collect_google_trends.py` | 使用 PyTrends 收集 Google Trends 相對熱度 |
| `collect_youtube.py` | 使用 YouTube Data API 收集影片觀看、留言、按讚數 |
| `build_daily_traffic.py` | 將事件窗展開成每日資料表 |
| `validate_dataset.py` | 檢查資料品質與欄位完整性 |

`collect_stock.py` 保留給負責股價的組員使用，本階段不執行。

API key 不可寫死在程式碼裡，必須放在 `.env`：

```text
NAVER_CLIENT_ID=
NAVER_CLIENT_SECRET=
YOUTUBE_API_KEY=
```

## 九、資料品質標準

教授可能會問：「你們怎麼確定資料可信？」

回答標準：

- 我們以官方公告、Naver、韓國媒體和平台 API 為主要資料來源。
- 每個事件都有明確起訖日期、來源 URL 與狀態欄位。
- 不確定資料標記為 `needs_review`，不會假裝完整。
- Google Trends 與 Naver DataLab 是相對熱度，不是實際搜尋人數。
- Instagram、Weverse、Bubble 歷史資料不完整，因此只作為 fanbase proxy。
- Python crawler 會輸出 log，流程可重跑、可檢查。
- 最終整理成 CSV 並提交 GitHub，方便組員共同檢查與補資料。

## 十、驗收標準

完成資料蒐集前，必須通過：

- 每個團體至少 5 筆事件。
- 每家公司至少 1 個正面事件與 1 個負面事件。
- 每個事件至少有 1 個 Naver 或官方來源。
- `Events_Master` 的 `event_id` 不重複。
- `Traffic_Daily` 每個事件日期完整。
- 所有日期格式為 `YYYY-MM-DD`。
- `validate_dataset.py` 沒有輸出重大錯誤。
- 隨機抽查 10 筆事件，確認來源與日期合理。
- CSV 能用 pandas 正常讀取。
